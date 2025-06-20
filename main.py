import cv2
import mss
import numpy as np
import mediapipe as mp
from collections import deque, Counter
from detectors import detect_gestures

def run_pose_on_monitor(monitor_index=1, callback=print, stop_flag=lambda: False):
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=False)
    mp_drawing = mp.solutions.drawing_utils

    gesture_history = deque(maxlen=15)
    last_output = None

    with mss.mss() as sct:
        monitors = sct.monitors
        if monitor_index >= len(monitors):
            monitor_index = 1
        monitor = monitors[monitor_index]

        while not stop_flag():
            try:
                screenshot = np.array(sct.grab(monitor))
            except Exception as e:
                print(f"Error: {e}")
                return

            rgb = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2RGB)
            bgr = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
            results = pose.process(rgb)

            current = []
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(bgr, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                current = detect_gestures(results.pose_landmarks.landmark)

            # Ignore "Right hand raised" if also scratching head
            if any("Scratching" in g for g in current):
                current = [g for g in current if "Scratching" in g]
            elif len(current) > 1:
                # only allow one gesture (most important one)
                current = [current[0]]

            gesture_history.append(tuple(current))

            # Majority voting
            if len(gesture_history) == gesture_history.maxlen:
                all_gestures = [g for gs in gesture_history for g in gs]
                if all_gestures:
                    most_common = Counter(all_gestures).most_common(1)[0][0]
                    if most_common != last_output:
                        callback(most_common)
                        last_output = most_common
                else:
                    if last_output != "No gesture":
                        callback("No gesture")
                        last_output = "No gesture"

        cv2.destroyAllWindows()

