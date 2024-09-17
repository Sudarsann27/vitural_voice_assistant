from flask import Flask, render_template, jsonify
import speech_recognition as sr
import pyttsx3
import os
import time
from threading import Lock
from datetime import datetime
import re

app = Flask(__name__)

# Initialize the text-to-speech engine and speech recognizer
engine = pyttsx3.init()
recognizer = sr.Recognizer()
speak_lock = Lock()

# Lock to prevent overlapping speech
listening = True

def speak(text):
    with speak_lock:
        engine.say(text)
        engine.runAndWait()
def listen_for_command():
    """Listen for a command via microphone and return the recognized text."""
    global listening
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio).lower()
            return command
        except sr.UnknownValueError:
            return "Sorry, I didn't catch that."
        except sr.RequestError:
            return "Error with the speech recognition service."

# Function to save notes
def save_note():
    speak("What would you like to note down?")
    note = listen_for_command()
    with open("note.txt", "a") as f:
        f.write(f"{datetime.now()}: {note}\n")
    speak("Note saved.")

# Function to set a timer
def set_timer(command):
    seconds = extract_time(command)
    if seconds is None:
        speak("Sorry, I couldn't understand the time duration.")
    else:
        speak(f"Timer set for {seconds} seconds.")
        time.sleep(seconds)
        speak(f"Your {seconds} seconds timer is over.")

# Function to extract time from voice command
def extract_time(command):
    match = re.search(r'(\d+)\s*(second|minute|hour|seconds|minutes|hours)', command)
    if match:
        value = int(match.group(1))
        unit = match.group(2)
        if 'minute' in unit:
            return value * 60  
        elif 'hour' in unit:
            return value * 3600  
        else:
            return value  
    return None

# Function to perform calculations
operations = {
    "plus": "+", "add": "+", "addition": "+",
    "minus": "-", "subtract": "-", "subtraction": "-",
    "times": "*", "multiply": "*", "multiplication": "*",
    "divided by": "/", "divide": "/", "division": "/"
}

def parse_math_expression(command):
    for word, symbol in operations.items():
        command = command.replace(word, symbol)
    pattern = r"(\d+)\s*([\+\-\*/])\s*(\d+)"
    match = re.search(pattern, command)
    if match:
        num1 = int(match.group(1))
        operator = match.group(2)
        num2 = int(match.group(3))
        return num1, operator, num2
    return None, None, None

def perform_calculation(command):
    num1, operator, num2 = parse_math_expression(command)
    if num1 is None or operator is None or num2 is None:
        speak("Sorry, I couldn't understand the calculation.")
        return
    try:
        if operator == "+":
            result = num1 + num2
        elif operator == "-":
            result = num1 - num2
        elif operator == "*":
            result = num1 * num2
        elif operator == "/":
            if num2 == 0:
                speak("Division by zero is not allowed.")
                return
            result = num1 / num2
        speak(f"The result is {result}")
    except Exception as e:
        speak(f"An error occurred: {str(e)}")

# Function for web search
def search_google(query):
    speak("Searching Google...")
    os.system(f"start chrome https://www.google.com/search?q={query.replace(' ', '+')}")

# Flask routes
@app.route('/')
def index():
    return render_template('assistant.html')

@app.route('/listen', methods=['POST'])
def listen():
    global listening
    if listening:
        command = listen_for_command()

        if any(word in command for word in ["exit", "quit"]):
            listening = False
            speak("Goodbye! Stopping now.")
            return jsonify({"command": "Goodbye! Stopping now.", "stop": True})

        # Handle core functionalities
        if "note" in command:
            save_note()
        elif "timer" in command:
            set_timer(command)
        elif any(op in command for op in operations):
            perform_calculation(command)
        elif "search" in command:
            speak("What would you like to search for?")
            search_query = listen_for_command()
            search_google(search_query)

        response = f"You said: {command}"
        return jsonify({"command": response, "stop": False})

    return jsonify({"command": "Already stopped.", "stop": True})

if __name__ == '__main__':
    app.run(debug=True)