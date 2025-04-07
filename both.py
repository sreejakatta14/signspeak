import tkinter as tk
from tkinter import scrolledtext
import speech_recognition as sr
import threading
import cv2
import time
import numpy as np
from tensorflow.keras.models import load_model

# ==== LOAD SIGN LANGUAGE MODEL ====
model = load_model('cnn8grps_rad1_model.h5')
class_names = ['Hello', 'I Love You', 'No', 'Please', 'Stop', 'Thank You', 'Yes', 'You']  # adjust if needed

# ==== GUI SETUP ====
root = tk.Tk()
root.title("Live Sign and Speech Recognition")
root.geometry("800x600")
root.resizable(False, False)

speech_label = tk.Label(root, text="🎤 Speech to Text", font=("Helvetica", 14, "bold"))
speech_label.pack(pady=(10, 0))
speech_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=90, height=10, font=("Consolas", 12))
speech_box.pack(pady=5)

sign_label = tk.Label(root, text="🖐️ Sign to Text", font=("Helvetica", 14, "bold"))
sign_label.pack(pady=(10, 0))
sign_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=90, height=10, font=("Consolas", 12))
sign_box.pack(pady=5)

status_label = tk.Label(root, text="Status: Ready", font=("Helvetica", 12), fg="green")
status_label.pack(pady=10)

# ==== SPEECH SETUP ====
recognizer = sr.Recognizer()

def speech_callback(recognizer, audio):
    try:
        text = recognizer.recognize_google(audio, language="en-IN")
        speech_box.insert(tk.END, text + '\n')
        speech_box.see(tk.END)
        with open("output_speech.txt", "a") as f:
            f.write(text + "\n")
    except sr.UnknownValueError:
        status_label.config(text="Didn't catch that.")
    except sr.RequestError as e:
        status_label.config(text=f"Speech API Error: {e}")
    except Exception as e:
        status_label.config(text=f"Speech Exception: {e}")

def start_speech():
    status_label.config(text="Speech: Listening...")
    threading.Thread(target=lambda: recognizer.listen_in_background(sr.Microphone(), speech_callback), daemon=True).start()

# ==== SIGN RECOGNITION ====
def start_sign():
    def sign_loop():
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            status_label.config(text="Could not open webcam.")
            return

        status_label.config(text="Sign: Detecting...")

        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            # Crop region of interest (ROI)
            roi = frame[100:350, 100:350]
            img = cv2.resize(roi, (64, 64))  # adjust based on model input size
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = img.reshape(1, 64, 64, 1)  # model expects (batch, height, width, channels)
            img = img.astype('float32') / 255.0

            # Predict
            prediction = model.predict(img)
            class_index = np.argmax(prediction)
            label = class_names[class_index]

            sign_box.insert(tk.END, label + '\n')
            sign_box.see(tk.END)
            with open("output_sign.txt", "a") as f:
                f.write(label + "\n")

            time.sleep(2)  # wait before next prediction

    threading.Thread(target=sign_loop, daemon=True).start()

# ==== BUTTONS ====
tk.Button(root, text="🎤 Start Speech Transcription", font=("Helvetica", 12), command=start_speech).pack(pady=5)
tk.Button(root, text="🖐️ Start Sign Recognition", font=("Helvetica", 12), command=start_sign).pack(pady=5)

# ==== START GUI ====
root.mainloop()
