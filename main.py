import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import threading
import os


# s DETECTION FUNCTION

from integrated2 import detect_violations

# ==========================================
# LOGIN CREDENTIALS
# ==========================================
USERNAME = "admin"
PASSWORD = "admin123"

# ==========================================
# MAIN WINDOW
# ==========================================
root = tk.Tk()
root.title("Traffic Violation Detection System")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

root.geometry(f"{screen_width}x{screen_height}")
root.configure(bg="#0f172a")

# ==========================================
# VARIABLES
# ==========================================
video_path = ""
output_video_path = "processed_output.mp4"
is_playing = False

# ==========================================
# LOGIN FRAME
# ==========================================
login_frame = tk.Frame(
    root,
    bg="#1e293b",
    bd=0
)

login_frame.place(relx=0.5, rely=0.5, anchor="center")

# ==========================================
# LOGIN TITLE
# ==========================================
title_label = tk.Label(
    login_frame,
    text="TRAFFIC AI SYSTEM",
    font=("Arial", 28, "bold"),
    bg="#1e293b",
    fg="#38bdf8"
)

title_label.pack(pady=20)

subtitle_label = tk.Label(
    login_frame,
    text="Helmet & Triple Seat Detection",
    font=("Arial", 14),
    bg="#1e293b",
    fg="white"
)

subtitle_label.pack(pady=5)

# ==========================================
# USERNAME
# ==========================================
username_label = tk.Label(
    login_frame,
    text="Username",
    font=("Arial", 12, "bold"),
    bg="#1e293b",
    fg="white"
)

username_label.pack(anchor="w", padx=30, pady=(20, 5))

username_entry = tk.Entry(
    login_frame,
    font=("Arial", 14),
    width=30,
    bd=0,
    relief="flat"
)

username_entry.pack(ipady=8, padx=30)

# ==========================================
# PASSWORD
# ==========================================
password_label = tk.Label(
    login_frame,
    text="Password",
    font=("Arial", 12, "bold"),
    bg="#1e293b",
    fg="white"
)

password_label.pack(anchor="w", padx=30, pady=(20, 5))

password_entry = tk.Entry(
    login_frame,
    font=("Arial", 14),
    width=30,
    show="*",
    bd=0,
    relief="flat"
)

password_entry.pack(ipady=8, padx=30)

# ==========================================
# MAIN APPLICATION
# ==========================================
def open_main_application():

    global progress
    global status_label
    global path_label
    global video_label
    global browse_btn
    global process_btn

    login_frame.destroy()

    # ==========================================
    # LEFT PANEL
    # ==========================================
    left_frame = tk.Frame(root, width=350, bg="white")
    left_frame.pack(side="left", fill="y")

    title_label = tk.Label(
        left_frame,
        text="Traffic Violation Detection",
        font=("Arial", 18, "bold"),
        bg="white",
        fg="darkblue"
    )

    title_label.pack(pady=20)

    path_label = tk.Label(
        left_frame,
        text="No Video Selected",
        wraplength=300,
        bg="white",
        fg="black"
    )

    path_label.pack(pady=10)

    # ==========================================
    # PROGRESS BAR
    # ==========================================
    progress = ttk.Progressbar(
        left_frame,
        orient="horizontal",
        length=250,
        mode="determinate"
    )

    progress.pack(pady=20)

    # ==========================================
    # STATUS LABEL
    # ==========================================
    status_label = tk.Label(
        left_frame,
        text="Status : Waiting",
        bg="white",
        fg="green",
        font=("Arial", 11, "bold")
    )

    status_label.pack(pady=10)

    # ==========================================
    # RIGHT PANEL
    # ==========================================
    right_frame = tk.Frame(root, bg="black")
    right_frame.pack(side="right", fill="both", expand=True)

    video_label = tk.Label(right_frame, bg="black")
    video_label.pack(fill="both", expand=True)

    # ==========================================
    # BROWSE VIDEO
    # ==========================================
    def browse_video():

        global video_path

        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Video Files", "*.mp4 *.avi *.mov")
            ]
        )

        if file_path:

            video_path = file_path

            # Clear previous video
            video_label.config(image="")
            video_label.imgtk = None

            # Reset progress
            progress['value'] = 0

            path_label.config(text=file_path)

            status_label.config(text="Video Selected")

    # ==========================================
    # PLAY VIDEO
    # ==========================================
    def play_video(video_file):

        global is_playing

        is_playing = True

        cap = cv2.VideoCapture(video_file)

        while cap.isOpened() and is_playing:

            ret, frame = cap.read()

            if not ret:
                break

            frame = cv2.resize(frame, (950, 700))

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            img = Image.fromarray(rgb_frame)

            imgtk = ImageTk.PhotoImage(image=img)

            video_label.imgtk = imgtk

            video_label.configure(image=imgtk)

            root.update_idletasks()
            root.update()

            cv2.waitKey(20)

        cap.release()

    # ==========================================
    # PROCESS VIDEO
    # ==========================================
    def process_video():

        global output_video_path

        if not video_path:

            messagebox.showerror(
                "Error",
                "Please select a video first."
            )

            return

        # Disable buttons
        browse_btn.config(state="disabled")
        process_btn.config(state="disabled")

        # Clear old output
        video_label.config(image="")
        video_label.imgtk = None

        # Reset progress
        progress['value'] = 0

        status_label.config(text="Processing Video...")

        cap = cv2.VideoCapture(video_path)

        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        fps = cap.get(cv2.CAP_PROP_FPS)

        if fps == 0:
            fps = 30

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Delete old processed video
        if os.path.exists(output_video_path):

            try:
                os.remove(output_video_path)

            except:
                pass

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        out = cv2.VideoWriter(
            output_video_path,
            fourcc,
            fps,
            (frame_width, frame_height)
        )

        current_frame = 0

        while cap.isOpened():

            ret, frame = cap.read()

            if not ret:
                break

            # ==========================================
            # DETECT VIOLATIONS
            # ==========================================
            processed_frame = detect_violations(frame)

            out.write(processed_frame)

            # ==========================================
            # LIVE DISPLAY
            # ==========================================
            display_frame = cv2.resize(processed_frame, (950, 700))

            rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)

            img = Image.fromarray(rgb_frame)

            imgtk = ImageTk.PhotoImage(image=img)

            video_label.imgtk = imgtk

            video_label.configure(image=imgtk)

            # ==========================================
            # PROGRESS BAR
            # ==========================================
            current_frame += 1

            progress_value = (current_frame / total_frames) * 100

            progress['value'] = progress_value

            root.update_idletasks()
            root.update()

        cap.release()
        out.release()

        # Enable buttons
        browse_btn.config(state="normal")
        process_btn.config(state="normal")

        status_label.config(text="Processing Completed")

        messagebox.showinfo(
            "Success",
            "Video Processing Completed"
        )

        play_video(output_video_path)

    # ==========================================
    # START PROCESSING THREAD
    # ==========================================
    def start_processing():

        thread = threading.Thread(
            target=process_video
        )

        thread.start()

    # ==========================================
    # PLAY AGAIN
    # ==========================================
    def play_again():

        global output_video_path

        if os.path.exists(output_video_path):

            thread = threading.Thread(
                target=play_video,
                args=(output_video_path,)
            )

            thread.start()

        else:

            messagebox.showerror(
                "Error",
                "Processed video not found."
            )

    # ==========================================
    # STOP VIDEO
    # ==========================================
    def stop_video():

        global is_playing

        is_playing = False

    # ==========================================
    # BUTTONS
    # ==========================================
    browse_btn = tk.Button(
        left_frame,
        text="Browse Video",
        font=("Arial", 12, "bold"),
        bg="#2563eb",
        fg="white",
        width=20,
        height=2,
        bd=0,
        command=browse_video
    )

    browse_btn.pack(pady=20)

    process_btn = tk.Button(
        left_frame,
        text="Process Video",
        font=("Arial", 12, "bold"),
        bg="#16a34a",
        fg="white",
        width=20,
        height=2,
        bd=0,
        command=start_processing
    )

    process_btn.pack(pady=10)

    play_again_btn = tk.Button(
        left_frame,
        text="Play Again",
        font=("Arial", 12, "bold"),
        bg="#f59e0b",
        fg="white",
        width=20,
        height=2,
        bd=0,
        command=play_again
    )

    play_again_btn.pack(pady=10)

    stop_btn = tk.Button(
        left_frame,
        text="Stop Video",
        font=("Arial", 12, "bold"),
        bg="#dc2626",
        fg="white",
        width=20,
        height=2,
        bd=0,
        command=stop_video
    )

    stop_btn.pack(pady=10)

    exit_btn = tk.Button(
        left_frame,
        text="Exit",
        font=("Arial", 12, "bold"),
        bg="black",
        fg="white",
        width=20,
        height=2,
        bd=0,
        command=root.destroy
    )

    exit_btn.pack(pady=20)

# ==========================================
# LOGIN FUNCTION
# ==========================================
def login():

    username = username_entry.get()
    password = password_entry.get()

    if username == USERNAME and password == PASSWORD:

        open_main_application()

    else:

        messagebox.showerror(
            "Login Failed",
            "Invalid Username or Password"
        )

# ==========================================
# LOGIN BUTTON
# ==========================================
login_btn = tk.Button(
    login_frame,
    text="LOGIN",
    font=("Arial", 14, "bold"),
    bg="#0ea5e9",
    fg="white",
    width=25,
    height=2,
    bd=0,
    command=login
)

login_btn.pack(pady=30)

# ==========================================
# FOOTER
# ==========================================
footer_label = tk.Label(
    login_frame,
    text="AI Based Traffic Monitoring System",
    font=("Arial", 10),
    bg="#1e293b",
    fg="#94a3b8"
)

footer_label.pack(pady=10)

# ==========================================
# ENTER KEY LOGIN
# ==========================================
root.bind("<Return>", lambda event: login())

# ==========================================
# START APPLICATION
# ==========================================
root.mainloop()