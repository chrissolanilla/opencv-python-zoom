import mediapipe as mp

mp_pose = mp.solutions.pose

def get_landmark(landmarks, name):
    return landmarks[mp_pose.PoseLandmark[name].value]

def distance(a, b):
    return ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5

def detect_gestures(landmarks):
    output = []

    left_wrist = get_landmark(landmarks, "LEFT_WRIST")
    right_wrist = get_landmark(landmarks, "RIGHT_WRIST")
    left_ear = get_landmark(landmarks, "LEFT_EAR")
    right_ear = get_landmark(landmarks, "RIGHT_EAR")
    left_shoulder = get_landmark(landmarks, "LEFT_SHOULDER")
    right_shoulder = get_landmark(landmarks, "RIGHT_SHOULDER")

    # Head scratch
    if distance(right_wrist, right_ear) < 0.15:
        output.append("Scratching head with right hand")
    elif distance(left_wrist, left_ear) < 0.15:
        output.append("Scratching head with left hand")

    # Arms crossed
    if distance(right_wrist, left_shoulder) < 0.25 and distance(left_wrist, right_shoulder) < 0.25:
        output.append("Arms crossed")

    # Shrug
    if (distance(right_shoulder, right_wrist) < 0.1 and distance(left_shoulder, left_wrist)):
        output.append("Shrugging")

    # Hand raise
    if left_wrist.y < left_shoulder.y - 0.1:
        output.append("Left hand raised")
    if right_wrist.y < right_shoulder.y - 0.1:
        output.append("Right hand raised")

    return output

