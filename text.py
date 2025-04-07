
import tkinter as tk
from tkinter import scrolledtext
import speech_recognition as sr
import pyttsx3
import threading

# Initialize recognizer and TTS
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

# Flag to control the background listening
listening = False
stop_listening = None

# Function to handle speech and update GUI
def callback(recognizer, audio):
    global text_box

    try:
        text = recognizer.recognize_google(audio, language="en-IN")
        
        # Update the text box
        text_box.insert(tk.END, text + '\n')
        text_box.see(tk.END)

        # Save to file
        with open("output.txt", "a") as f:
            f.write(text + "\n")

        # Speak the text
        # tts_engine.say(text)
        # tts_engine.runAndWait()

    except sr.UnknownValueError:
        status_label.config(text="Didn't catch that.")
    except sr.RequestError as e:
        status_label.config(text=f"Error: {e}")
    except Exception as e:
        status_label.config(text=f"Exception: {e}")

# Start listening in background
def start_transcription():
    global listening, stop_listening
    if not listening:
        status_label.config(text="Listening...")
        listening = True
        stop_listening = recognizer.listen_in_background(sr.Microphone(), callback)
    else:
        status_label.config(text="Already listening.")

# Stop background listening
def stop_transcription():
    global listening, stop_listening
    if listening and stop_listening:
        stop_listening(wait_for_stop=False)
        status_label.config(text="Stopped.")
        listening = False

# Setup GUI
root = tk.Tk()
root.title("Real-Time Speech Transcription")
root.geometry("550x450")
root.resizable(False, False)

# Start button
start_button = tk.Button(root, text="🟢 Start Transcription", font=("Helvetica", 14), command=start_transcription)
start_button.pack(pady=10)

# Stop button
stop_button = tk.Button(root, text="🔴 Stop Transcription", font=("Helvetica", 14), command=stop_transcription)
stop_button.pack(pady=5)

# Text box
text_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=15, font=("Consolas", 12))
text_box.pack(padx=10, pady=10)

# Status
status_label = tk.Label(root, text="Ready", font=("Helvetica", 12), fg="green")
status_label.pack()

# Run app
root.mainloop()
