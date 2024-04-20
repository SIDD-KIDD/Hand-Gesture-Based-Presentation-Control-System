import cv2
import mediapipe as mp
import numpy as np
import math
import pyautogui as pg
import time
from threading import Event

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

stop_event = Event()
cap = None

def start_tracking(frame_callback, error_callback):
    pass

def stop_tracking():
    pass
