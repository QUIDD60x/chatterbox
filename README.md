# Chatterbox 2 - Your helpful desktop AI.
## Highly configurable, super helpful.
---
## How it works/Why I made this
This program essentially allows you to "speak" with a chatbot, and allows them to speak back. The system works as follows:

1. You speak into your microphone while recording (which will save the recording as a .wav).
2. OpenAIs Whisper translates that recording into text.
3. That translation is sent to your AI API (you will need your own).
4. The response is collected, then spoken out loud (using Azure's speech API, which you'll also need a subscription for).

And for convenience, the text input + output is collected in a local text file, and the recording is saved (until rewritten by the next input).

This program is best suited for those who find themselves asking for little bits of help while working, something I noticed in myself quite some time ago. 
***
## Quickstart

### Dependencies (for the non-azure TTS model):

* tkinter
* numpy
* openAI
* speechrecognition
* sounddevice
* keyboard
* azure.cognitiveservices.speech

You can paste `pip install openai speechrecognition sounddevice numpy keyboard tkinter azure-cognitiveservices-speech` to install all of these immediately.

### How to use:

Firstly You'll need your own ChatGPT and Azure API key. I explain it a bit more in the script, but you can either add it as an enviromental variable or specify it in the marked variable.

After that, simply install all dependencies and run it in your command line interface. You'll get a text box asking for your prompt, and the AI output. I hope you enjoy!

For any more help check the wiki, or leave me a message on discord (quidd60x).
