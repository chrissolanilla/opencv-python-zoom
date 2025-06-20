import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
import threading
from main import run_pose_on_monitor  # we'll define this next
import mss

class PoseApp(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Body Language Interpreter")
        self.set_default_size(600, 400)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        self.monitor_combo = Gtk.ComboBoxText()
        self.populate_monitors()
        vbox.pack_start(Gtk.Label(label="Select Monitor:"), False, False, 0)
        vbox.pack_start(self.monitor_combo, False, False, 0)

        self.start_button = Gtk.Button(label="Start Detection")
        self.start_button.connect("clicked", self.on_start_clicked)
        vbox.pack_start(self.start_button, False, False, 0)

        self.output_box = Gtk.TextView()
        self.output_box.set_editable(False)
        self.output_buffer = self.output_box.get_buffer()
        # vbox.pack_start(Gtk.ScrolledWindow().add(self.output_box), True, True, 0)
        scroll = Gtk.ScrolledWindow()
        scroll.add(self.output_box)
        vbox.pack_start(scroll, True, True, 0)
        self.stop_event = threading.Event()
        self.detection_thread = None

    def populate_monitors(self):
        with mss.mss() as sct:
            self.monitors = sct.monitors[1:]  # skip monitor[0] = full desktop
            for i, mon in enumerate(self.monitors):
                label = f"Monitor {i + 1}: {mon['width']}x{mon['height']} at ({mon['left']},{mon['top']})"
                self.monitor_combo.append_text(label)
            self.monitor_combo.set_active(0)

    def on_start_clicked(self, widget):
        if self.detection_thread and self.detection_thread.is_alive():
            self.stop_event.set()
            self.start_button.set_label("Start Detection")
            self.monitor_combo.set_sensitive(True)
            return

        self.stop_event.clear()
        selected = self.monitor_combo.get_active()
        if selected == -1:
            return
        self.start_button.set_label("Stop Detection")
        self.monitor_combo.set_sensitive(False)

        self.detection_thread = threading.Thread(
            target=self.run_detection_thread, args=(selected + 1,)
        )
        self.detection_thread.daemon = True
        self.detection_thread.start()

    def run_detection_thread(self, monitor_index):
        def callback(gesture):
            GLib.idle_add(self.append_output, gesture)
        run_pose_on_monitor(monitor_index, callback, stop_flag=self.stop_event.is_set)

    def append_output(self, text):
        end = self.output_buffer.get_end_iter()
        self.output_buffer.insert(end, text + "\n")
        mark = self.output_buffer.create_mark(None, self.output_buffer.get_end_iter(), False)
        self.output_box.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)

win = PoseApp()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

