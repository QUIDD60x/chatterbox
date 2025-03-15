import tkinter as tk # I mainly use TKinter for the GUI, but it's got some other nice uses.
from tkinter import *
import threading # Working with threading to help balance it all out, I hope it actually makes some kind of improvement.
import sounddevice as sd
import numpy as np
import wave
import keyboard # I like having the control+r keybind for easy access, so I'm keeping this around.
import openai
import pyttsx3 # Temporary TTS module until I get myself an Azure TTS custom AI.
import requests
from datetime import datetime
import pytz

# Audio settings
SAMPLE_RATE = 44100 # CD quality HZ, best bang for your buck.
CHANNELS = 1
FILENAME = "recorded_audio.wav"                                 # ***----- PYTTSX3 VERSION -----***

# Global variables
recording = False
audio_data = []
chatbot_response = ""
user_timezone = "America/Los_Angeles" # Change this to your own timezone for custom time responses.

# NOTICE: THIS WILL NOT WORK WITHOUT AN OPENAI API KEY!! You WILL need to pay for one (unless you've just got one on hand). to add it, you can simply add:
# api_key = "apiKeyHere". HOWEVER, I set mine to be an enviromental variable, by doing:
# setx OPENAI_API_KEY "your_api_key_here". For more information, click here -> https://platform.openai.com/docs/libraries#create-and-export-an-api-key                                                                                                                                                                                          haha setx is like sex

openWeatherMapAPIKey = "none" # UPCOMING FEATURE: You can put your Open Weather API key here to have accurate results of your local forecast!


# Load system prompt (got it to work!)
def load_system_prompt():
    try:
        with open("prompt.txt", "r", encoding="utf-8") as file:
            return file.read().strip()
    except FileNotFoundError:
        return "uh oh, system prompt wasn't loaded correctly! Please say something scary to help the devs realize something went wrong."

SYSTEM_PROMPT = load_system_prompt()

# Text-to-speech engine initilization and the customizations to make it more my taste (getting Azure TTS soon).
engine = pyttsx3.init()
engine.setProperty('rate', 200)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Plays the chatbot response verbally.
def play_response():
    if chatbot_response:
        engine.say(chatbot_response)
        engine.runAndWait()

# Recording callback function
def callback(indata, frames, time, status):
    if status:
        print(status)
    if recording:
        audio_data.append(indata.copy())

# Should be obvious, lets you toggle recording. The way it's implemented should be safest, previously it would check every repeat to see if you pressed the button (and would cause lots of stuttering).
def toggle_recording():
    global recording, audio_data
    if recording:
        recording = False
        status_label.config(text="Recording Stopped. Processing...")
    else:
        recording = True
        audio_data = []
        status_label.config(text="Recording...")
        threading.Thread(target=record_audio, daemon=True).start()

# What actually records the audio
def record_audio():
    global chatbot_response
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype=np.int16, callback=callback):
        while recording:
            pass
    if not audio_data:
        status_label.config(text="No audio recorded.")
        return
    audio_array = np.concatenate(audio_data, axis=0)
    with wave.open(FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_array.tobytes())
    status_label.config(text="Transcribing...")
    transcribed_text = audio_to_text(FILENAME)
    transcript_label.config(text=f"Transcript: {transcribed_text}")
    with open('input.txt', 'w') as file:
        file.write(transcribed_text)
    chatbot_response = send_to_chatbot(transcribed_text)
    response_label.config(text=f"Chatbot: {chatbot_response}")
    with open('output.txt', 'w') as file:
        file.write(chatbot_response)
    play_response()
    status_label.config(text="Ready.")

# Uses whisper1 to translate your speech to text. Very reliable, next to no mistakes when speaking clearly. So cool!
def audio_to_text(filename):
    with open(filename, 'rb') as audio_file:
        response = openai.Audio.transcribe(model="whisper-1", file=audio_file, language="en")
    return response["text"]

# ***--- Specific Checks ---*** #

def check_user_request(user_input):
    user_input = user_input.lower().strip()  # Strip spaces to avoid blank input issues

    if "time" in user_input: # This checks for your time
        timezone = user_timezone
        return get_time(timezone)
    
    return None

# I plan on putting in specific voice checks here (such as asking for the weather, time, etc).
def get_time(timezone=user_timezone):
    try:
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz).strftime("%I:%M %p")  # 12-hour format with AM/PM
        return f"The current time in {timezone} is {current_time}."
    except Exception as e:
        return "I couldn't determine the time."

# Where all the magic happens.
def send_to_chatbot(user_input):
    user_input = user_input.strip()  # Remove accidental spaces/newlines

    if not user_input:  
        return "I didn't catch that. Can you say it again?"  # Prevents blank input

    special_response = check_user_request(user_input)
    if special_response:
        return special_response  # Returns time instead of sending to the AI
    
    print(f"User Input: '{user_input}'")  # Debugging line to check input

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ],
        )
        return completion['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

# uhhhhhhhhhhhhhhh
def send_text_prompt():
    user_input = inputText.get()
    if user_input:
        transcript_label.config(text=f"Transcript: {user_input}")
        chatbot_response = send_to_chatbot(user_input)
        response_label.config(text=f"Chatbot: {chatbot_response}")
        play_response()

# TKINTER STUFF! Not going to bother explaining this, I doubt it's of any importance.
root = Tk()
root.title("Speech to Speech Voice Assistant")

status_label = tk.Label(root, text="Press 'Record' or Ctrl+R to start.", font=("Exo", 12))
status_label.pack(pady=5)

record_button = tk.Button(root, text="Record", command=toggle_recording, font=("Exo", 12))
record_button.pack(pady=5)

transcript_label = tk.Label(root, text="Transcript: ", wraplength=400, font=("Exo", 10), justify="left")
transcript_label.pack(pady=5)

inputText = StringVar() # Couldn't figure this text box for the life of me, thanks chatGPT for the help lol TODO: Add alternate text in the box
inputText_entry = tk.Entry(root, textvariable=inputText, font=("Exo", 10), width=50)
inputText_entry.pack(pady=5)

send_button = tk.Button(root, text="Send", command=send_text_prompt, font=("Exo", 10))
send_button.pack(pady=5)

response_label = tk.Label(root, text="Chatbot: ", wraplength=400, font=("Exo", 10), justify="left")
response_label.pack(pady=5)

replay_button = tk.Button(root, text="Replay Response", command=play_response, font=("Exo", 12))
replay_button.pack(pady=5)

# I like also being able to press a keybind for quick recordings. TODO: Add a quick stop keybind to immediately end or restate a prompt.
def listen_for_keypress():
    while True:
        keyboard.wait('ctrl+r')
        root.after(0, toggle_recording)

threading.Thread(target=listen_for_keypress, daemon=True).start()
root.mainloop()
