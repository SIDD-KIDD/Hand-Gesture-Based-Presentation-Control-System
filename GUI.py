import customtkinter as ctk
from PIL import Image, ImageTk
import threading
import Backend

# Initialize CustomTkinter
ctk.set_appearance_mode("Dark")

class HandGestureApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hand Gesture Based Presentation Control System")
        self.geometry("800x600")
        self.resizable(False, False)  # Fixed window size
        self.configure(bg="#f3e5f5")  # Light purple background

        # Variables
        self.video_running = False
        self.video_thread = None

        # UI Elements
        self.create_widgets()

        # Bind window close event to clean up camera resources
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        # Header Label
        self.header_label = ctk.CTkLabel(
            self,
            text="Hand Gesture Based Control System",
            font=("Arial Bold", 24),
            fg_color="#6a1b9a",  # Dark purple header
            corner_radius=10,
            text_color="white",
            height=50,
        )
        self.header_label.pack(fill="x", pady=10)

        # Start/Stop Button
        self.start_stop_button = ctk.CTkButton(
            self,
            text="Start Tracking",
            command=self.toggle_video,
            font=("Arial Bold", 16),
            fg_color="#7b1fa2",  # Vibrant purple button
            hover_color="#9c27b0",
        )
        self.start_stop_button.pack(pady=15)

        # Video Label (hidden by default)
        self.video_label = ctk.CTkLabel(self, text="")

        # Instruction Area
        self.instruction_frame = ctk.CTkFrame(self, fg_color="#ede7f6", corner_radius=10)  # Light purple frame
        self.instruction_frame.pack(pady=15, padx=20, fill="both", expand=True)

        instruction_text = (
            "Instructions:\n"
            "1. Ensure your webcam is enabled and working.\n"
            "2. Perform gestures in a well-lit environment for better recognition.\n"
            "3. Use the 'Start Tracking' button to begin gesture detection.\n"
            "4. To perform a desired click:\n"
            "   a) Close your middle, ring, and pinky fingers as shown below.\n"
            "   b) Touch the thumb and index finger tips to perform a click:\n"
            "      - Right hand: Right arrow click\n"
            "      - Left hand: Left arrow click"
        )

        instruction_label = ctk.CTkLabel(
            self.instruction_frame,
            text=instruction_text,
            font=("Arial", 14),
            anchor="w",
            justify="left",
            text_color="#4a148c",  # Darker purple for contrast
        )
        instruction_label.pack(pady=15, padx=15, anchor="w")

        # Instruction Images in a Frame
        image_frame = ctk.CTkFrame(self.instruction_frame, fg_color="#ffffff", corner_radius=10)
        image_frame.pack(pady=10, padx=10, fill="x", expand=False)

        try:
            # Load and display first image using ctk.CTkImage to support scaling and fix warnings
            img1 = Image.open("res\\img1.jpg")
            img1_ctk = ctk.CTkImage(light_image=img1, dark_image=img1, size=(200, 200))

            img_label1 = ctk.CTkLabel(image_frame, image=img1_ctk, text="")
            img_label1.image = img1_ctk
            img_label1.pack(side="left", padx=20, pady=8)

            # Load and display second image using ctk.CTkImage
            img2 = Image.open("res\\img2.jpg")
            img2_ctk = ctk.CTkImage(light_image=img2, dark_image=img2, size=(200, 200))

            img_label2 = ctk.CTkLabel(image_frame, image=img2_ctk, text="")
            img_label2.image = img2_ctk
            img_label2.pack(side="left", padx=20, pady=8)

        except Exception as e:
            error_label = ctk.CTkLabel(
                self.instruction_frame,
                text=f"Error loading images: {e}",
                font=("Arial", 12),
                text_color="red",
            )
            error_label.pack(pady=10)

    def toggle_video(self):
        if not self.video_running:
            self.start_video()
        else:
            self.stop_video()

    def start_video(self):
        print("Gesture tracking started.")
        self.video_running = True
        self.start_stop_button.configure(
            text="Stop Tracking", fg_color="#4a148c", hover_color="#6a1b9a"
        )
        # Hide instruction panel, show video view
        self.instruction_frame.pack_forget()
        self.video_label.pack(pady=10)

        # Clear any old image on the label
        self.video_label.configure(image=None)
        
        self.video_thread = threading.Thread(
            target=Backend.start_tracking, 
            args=(self.update_frame, self.handle_error), 
            daemon=True
        )
        self.video_thread.start()

    def stop_video(self):
        print("Gesture tracking stopped.")
        Backend.stop_tracking()
        self.video_running = False
        self.start_stop_button.configure(
            text="Start Tracking", fg_color="#7b1fa2", hover_color="#9c27b0"
        )
        # Hide video view, restore instructions
        self.video_label.pack_forget()
        self.instruction_frame.pack(pady=15, padx=20, fill="both", expand=True)

    def update_frame(self, rgb_image):
        # Convert RGB numpy array to PIL Image
        pil_img = Image.fromarray(rgb_image)
        # Resize frame to fit GUI layout nicely (keeping 4:3 aspect ratio)
        pil_img_resized = pil_img.resize((560, 420), Image.Resampling.LANCZOS)
        # Create CTkImage for scaling support on HighDPI displays
        ctk_img = ctk.CTkImage(light_image=pil_img_resized, dark_image=pil_img_resized, size=(560, 420))
        # Thread-safe update of UI elements using after()
        self.after(0, self._set_image, ctk_img)

    def _set_image(self, ctk_img):
        if self.video_running:
            self.video_label.configure(image=ctk_img)
            self.video_label.image = ctk_img

    def handle_error(self, error_message):
        # Schedule the error dialog and UI reset on the main thread
        self.after(0, self._show_error, error_message)

    def _show_error(self, error_message):
        self.stop_video()
        from tkinter import messagebox
        messagebox.showerror("Camera Error", error_message)

    def on_close(self):
        if self.video_running:
            self.stop_video()
        self.destroy()

# Run the App
if __name__ == "__main__":
    app = HandGestureApp()
    app.mainloop()
