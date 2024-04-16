import cv2
import mediapipe as mp
import numpy as np
import math
import pyautogui as pg
import time

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

def calculate_distance(x1, y1, z1, x2, y2, z2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)

def isGesture(hand, image, hand_label):
    pass

def process_frame(frame, hands, mp_drawing):
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return image
