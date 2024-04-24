import cv2
import mediapipe as mp
import numpy as np
import math
import pyautogui as pg
import time
from threading import Event

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

stop_event = Event()  # Global stop event for thread control
cap = None  # Global VideoCapture object

def calculate_distance(x1, y1, z1, x2, y2, z2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)

def get_label(index, hand, results):
    output = None
    if results.multi_handedness and index < len(results.multi_handedness):
        classification = results.multi_handedness[index].classification[0]
        label = classification.label  # "Left" or "Right"
        score = classification.score
        text = f"{label} {round(score, 2)}"

        coords = tuple(
            np.multiply(
                np.array(
                    (hand.landmark[mp_hands.HandLandmark.WRIST].x,
                     hand.landmark[mp_hands.HandLandmark.WRIST].y)
                ),
                [640, 480]
            ).astype(int)
        )

        output = text, coords
    else:
        if len(results.multi_hand_landmarks) == 1:
            text = "Right 1.0"
            coords = (10, 50)  # Default position
            output = text, coords

    return output

def isGesture(hand, image, hand_label):
    joint_list = [[12, 9, 0], [16, 13, 0], [20, 17, 0]]
    angles = []

    for joint in joint_list:
        a = np.array([hand.landmark[joint[0]].x, hand.landmark[joint[0]].y])
        b = np.array([hand.landmark[joint[1]].x, hand.landmark[joint[1]].y])
        c = np.array([hand.landmark[joint[2]].x, hand.landmark[joint[2]].y])

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        if angle > 180.0:
            angle = 360 - angle
        angles.append(angle)

    if all(angle < 30 for angle in angles):
        cv2.putText(image, "Gesture Locked", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        lm_wrist = hand.landmark[0]  # Wrist
        lm_mcp = hand.landmark[9]    # Middle MCP
        h, w, _ = image.shape
        ref_dist = calculate_distance(
            lm_wrist.x * w, lm_wrist.y * h, lm_wrist.z,
            lm_mcp.x * w, lm_mcp.y * h, lm_mcp.z
        )

        lm1 = hand.landmark[8]  # Index finger tip
        lm2 = hand.landmark[4]  # Thumb tip
        x1, y1, z1 = lm1.x * w, lm1.y * h, lm1.z
        x2, y2, z2 = lm2.x * w, lm2.y * h, lm2.z
        distance = calculate_distance(x1, y1, z1, x2, y2, z2)
        normalized_dist = distance / ref_dist if ref_dist != 0 else float('inf')

        cv2.line(image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 3)
        cv2.putText(image, f'Norm Dist: {normalized_dist:.2f}', (int(x1) + 20, int(y1) + 20),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 3)

        if normalized_dist < 0.2:
            cv2.putText(image, f"CLICKED ({hand_label})", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            if hand_label == "Right":
                pg.press('right')
                time.sleep(0.5)
            elif hand_label == "Left":
                pg.press('left')
                time.sleep(0.5)
    else:
        cv2.putText(image, "Gesture Not Locked", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

def process_frame(frame, hands, mp_drawing):
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = cv2.flip(image, 1)
    image.flags.writeable = False
    results = hands.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.multi_hand_landmarks:
        for num, hand in enumerate(results.multi_hand_landmarks):
            mp_drawing.draw_landmarks(
                image, hand, mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                mp_drawing.DrawingSpec(color=(250, 44, 250), thickness=2, circle_radius=2),
            )

            label_info = get_label(num, hand, results)
            if label_info:
                text, coord = label_info
                hand_label = text.split()[0]
                cv2.putText(image, text, coord, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                isGesture(hand, image, hand_label)

    return image

def main(frame_callback, error_callback):
    global cap
    cap = None

    # Probe camera indices and backends to find a working one
    backends = [
        ("Default", None),
        ("DSHOW", cv2.CAP_DSHOW),
        ("MSMF", cv2.CAP_MSMF)
    ]

    camera_opened = False
    for backend_name, backend in backends:
        for index in [0, 1, 2]:
            try:
                if backend is not None:
                    cap = cv2.VideoCapture(index, backend)
                else:
                    cap = cv2.VideoCapture(index)

                if cap is not None and cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        print(f"Successfully opened camera {index} with backend {backend_name}")
                        camera_opened = True
                        break
                    cap.release()
                    cap = None
            except Exception as e:
                print(f"Failed to open camera {index} with backend {backend_name}: {e}")
                if cap is not None:
                    cap.release()
                    cap = None
        if camera_opened:
            break

    if not camera_opened or cap is None or not cap.isOpened():
        error_callback("Could not open any camera. Please check your camera connections and privacy settings.")
        return

    with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5) as hands:
        while cap.isOpened() and not stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame. Exiting tracking loop...")
                break

            image = process_frame(frame, hands, mp_drawing)
            
            # Convert BGR frame to RGB for Tkinter
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            frame_callback(rgb_image)

    stop_tracking()


def start_tracking(frame_callback, error_callback):
    stop_event.clear()
    main(frame_callback, error_callback)


def stop_tracking():
    global cap
    stop_event.set()
    if cap is not None:
        try:
            cap.release()
        except Exception:
            pass
        cap = None
    cv2.destroyAllWindows()
