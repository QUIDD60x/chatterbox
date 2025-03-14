import tkinter as tk # I mainly use TKinter for the GUI, but it's got some other nice uses.
import threading # Working with threading to help balance it all out, I hope it actually makes some kind of improvement.
import sounddevice as sd
import numpy as np
import wave
import keyboard # I like having the control+r keybind for easy access, so I'm keeping this around.
import openai
import pyttsx3 # Temporary TTS module until I get myself an Azure TTS custom AI.
import io

# Audio settings
SAMPLE_RATE = 44100 # CD quality HZ, best bang for your buck.
CHANNELS = 1 # no need for stereo realistically, 1 is mono.
FILENAME = "recorded_audio.wav" # Saves a copy of your recording to your device (mostly for debugging purposes).

# Global variables
recording = False
audio_data = []
chatbot_response = ""

# NOTICE: THIS WILL NOT WORK WITHOUT AN OPENAI API KEY!! You WILL need to pay for one (unless you've just got one on hand). to add it, you can simply add:
# api_key = "apiKeyHere". HOWEVER, I set mine to be an enviromental variable, by doing:
# setx OPENAI_API_KEY "your_api_key_here". For more information, click here -> https://platform.openai.com/docs/libraries#create-and-export-an-api-key


# Was originally going to have the prompt load from a system file, but I couldn't get it to work. For now it'll just be this (once I implement Azure TTS I may have to change it anyways).
def load_system_prompt():
    try:
        with open("prompt.txt", "r", encoding="utf-8") as file:
            return file.read().strip()
    except FileNotFoundError:
        return "Something went wrong loading the system prompt! Please say something scary or fourth wall breaking to help the devs notice something's wrong."

SYSTEM_PROMPT = load_system_prompt()

# Text-to-speech engine initilization and the customizations to make it more my taste (getting Azure TTS soon).
engine = pyttsx3.init()
rate = engine.getProperty('rate')
engine.setProperty('rate', 200)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Function to play the chatbot response.
def play_response():
    if chatbot_response:
        engine.say(chatbot_response)
        engine.runAndWait()

# Recording callback function.
def callback(indata, frames, time, status):
    if status:
        print(status)
    if recording:
        audio_data.append(indata.copy())

# Start/stop recording function.
def toggle_recording():
    global recording, audio_data

    if recording:
        recording = False
        status_label.config(text="Recording Stopped. Processing...")
    else:
        recording = True
        audio_data = []
        status_label.config(text="Recording...")

        # Starts recording in a new thread (pretty sure I did this right, first time using this module).
        threading.Thread(target=record_audio, daemon=True).start()

# Records audio function.
def record_audio():
    global chatbot_response

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype=np.int16, callback=callback):
        while recording:
            pass  # Keeps recording until `recording` is set to false.

    if not audio_data:
        status_label.config(text="No audio recorded.")
        return

    # Saves as WAV file.
    audio_array = np.concatenate(audio_data, axis=0)
    with wave.open(FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_array.tobytes())

    status_label.config(text="Transcribing...")

    # Converts audio to text.
    transcribed_text = audio_to_text(FILENAME)
    transcript_label.config(text=f"Transcript: {transcribed_text}")

    # Gets chatbot response.
    chatbot_response = send_to_chatbot(transcribed_text)
    response_label.config(text=f"Chatbot: {chatbot_response}")

    # Auto-play response.
    play_response()

    status_label.config(text="Ready.")

# Converts audio to text.
def audio_to_text(filename):
    with open(filename, 'rb') as audio_file:
        response = openai.Audio.transcribe(model="whisper-1", file=audio_file, language="en")
    return response["text"]

# Sends text to chatbot.
def send_to_chatbot(user_input):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini", # Using 4o-mini for the best bang for my buck, feel free to use whatever though.
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},  # Loads the prompt here, you could just replace this with a string if you really wanted.
                {"role": "user", "content": user_input},
            ],
        )
        return completion['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

# GUI setup using TKinter, pretty ugly at the moment but I'm working on it.
root = tk.Tk()
root.title("Voice Assistant")

# Status label.
status_label = tk.Label(root, text="Press 'Record' or Ctrl+R to start.", font=("Arial", 12))
status_label.pack(pady=5)

# Record button.
record_button = tk.Button(root, text="Record", command=toggle_recording, font=("Arial", 12))
record_button.pack(pady=5)

# Transcript label.
transcript_label = tk.Label(root, text="Transcript: ", wraplength=400, font=("Arial", 10), justify="left")
transcript_label.pack(pady=5)

# Chatbot response label.
response_label = tk.Label(root, text="Chatbot: ", wraplength=400, font=("Arial", 10), justify="left")
response_label.pack(pady=5)

# Replay button.
replay_button = tk.Button(root, text="Replay Response", command=play_response, font=("Arial", 12))
replay_button.pack(pady=5)

# Listen for Ctrl+R keypress.
def listen_for_keypress():
    while True:
        keyboard.wait('ctrl+r')
        root.after(0, toggle_recording)  # Run on main thread to hopefully keep everything lag free.

# Starts keypress listener in separate thread.
threading.Thread(target=listen_for_keypress, daemon=True).start()

# Runs GUI.
root.mainloop()
