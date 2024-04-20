import customtkinter as ctk
from PIL import Image, ImageTk
import threading
import Backend

ctk.set_appearance_mode("Dark")

class HandGestureApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hand Gesture Based Presentation Control System")
        self.geometry("800x600")
        self.resizable(False, False)
        self.configure(bg="#f3e5f5")

        self.video_running = False
        self.create_widgets()

    def create_widgets(self):
        self.header_label = ctk.CTkLabel(self, text="Hand Gesture Based Control System", font=("Arial Bold", 24))
        self.header_label.pack(pady=20)

        self.start_stop_button = ctk.CTkButton(self, text="Start Tracking", command=self.toggle_video)
        self.start_stop_button.pack(pady=10)

        self.video_label = ctk.CTkLabel(self, text="")
        self.video_label.pack(pady=10)

    def toggle_video(self):
        pass
