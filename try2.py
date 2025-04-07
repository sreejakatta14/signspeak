import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import cv2
import numpy as np
from tensorflow.keras.models import load_model
import speech_recognition as sr

# ==== Load Sign Language Model ====
model = load_model('cnn8grps_rad1_model.h5')
class_names = ['Hello', 'I Love You', 'No', 'Please', 'Stop', 'Thank You', 'Yes', 'You']  # adjust if needed

# ==== GUI Setup ====
root = tk.Tk()
root.title("Live Sign and Speech Recognition")
root.geometry("1000x700")
root.resizable(False, False)

speech_label = tk.Label(root, text="🎤 Speech to Text", font=("Helvetica", 14, "bold"))
speech_label.pack(pady=(10, 0))
speech_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=120, height=10, font=("Consolas", 12))
speech_box.pack(pady=5)

sign_label = tk.Label(root, text="🖐️ Sign to Text", font=("Helvetica", 14, "bold"))
sign_label.pack(pady=(10, 0))
sign_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=120, height=5, font=("Consolas", 12))
sign_box.pack(pady=5)

status_label = tk.Label(root, text="Status: Ready", font=("Helvetica", 12), fg="green")
status_label.pack(pady=10)

# ==== Speech Recognition ====
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

# ==== Sign Recognition with Live Webcam Preview ====
def start_sign():
    def sign_loop():
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            status_label.config(text="Could not open webcam.")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            # Draw ROI
            x1, y1, x2, y2 = 100, 100, 350, 350
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            roi = frame[y1:y2, x1:x2]
            img = cv2.resize(roi, (64, 64))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = img.reshape(1, 64, 64, 1).astype('float32') / 255.0

            prediction = model.predict(img)
            class_index = np.argmax(prediction)
            label = class_names[class_index]

            # Put label on frame
            cv2.putText(frame, f"Prediction: {label}", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Show frame
            cv2.imshow("Sign Language Detection", frame)

            # Write to sign box and file
            sign_box.insert(tk.END, label + '\n')
            sign_box.see(tk.END)
            with open("output_sign.txt", "a") as f:
                f.write(label + "\n")

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(2)

        cap.release()
        cv2.destroyAllWindows()

    threading.Thread(target=sign_loop, daemon=True).start()

# ==== Buttons ====
tk.Button(root, text="🎤 Start Speech Transcription", font=("Helvetica", 12), command=start_speech).pack(pady=5)
tk.Button(root, text="🖐️ Start Sign Recognition", font=("Helvetica", 12), command=start_sign).pack(pady=5)

# ==== Start GUI ====
root.mainloop()
