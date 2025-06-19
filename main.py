import cv2
import mediapipe as mp
from detectors import detect_gestures

def main():
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=False)
    mp_drawing = mp.solutions.drawing_utils

    video_path = 'videos/croppedVideo.mp4'
    cap = cv2.VideoCapture(video_path)

    output_path = 'outputs/annotated.mp4'
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = cap.get(cv2.CAP_PROP_FPS)
    w, h = int(cap.get(3)), int(cap.get(4))
    out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            gestures = detect_gestures(results.pose_landmarks.landmark)
            for g in gestures:
                print(g)

        out.write(frame)
        cv2.imshow('Pose Detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

