from ask_ai import ask_ai, rewrite_response
from open_app import open_app, uwp_apps
from command import process_command_with_gemini, describe_image_with_gemini
from wikipedia import get_wikipedia_summary
import os
import pyttsx3
import speech_recognition as sr
import webbrowser
import wikipedia
import requests
from urllib.parse import quote
import time
from gtts import gTTS
import pygame
import pyautogui
import tempfile
import asyncio
import sys
from functools import lru_cache
from datetime import datetime
import re
from fuzzywuzzy import process

# Initialize pygame for audio playback
pygame.mixer.init()

# Command map
COMMAND_MAP = {
    'ask ai': ['ask ai', 'ask', 'query ai', 'ask the ai', 'ai query'],
    'youtube search': ['search youtube', 'youtube search', 'find on youtube'],
    'google search': ['search google', 'look up', 'google', 'search'],
    'wikipedia': ['wikipedia', 'wiki', 'tell me about'],
    'screenshot': ['take screenshot', 'capture screen', 'take a screenshot', 'screenshot please', 'screenshot'],
    'stop': ['stop', 'exit', 'quit', 'goodbye', 'shut down'],
    'who am i': ['who am i', 'who am i?', 'who is this'],
    'who are you': ['who are you', 'who are you?', 'who is axon'],
    'open app': ['open', 'launch', 'start', 'run'],
    'describe screen': ['what\'s on my screen', 'describe my screen', 'what is on my screen', 'screen contents']  # New command
}

def get_input(prompt):
    user_input = input(prompt)
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(prompt + user_input + "\n")
    return user_input

def speak(text):
    """
    Text-to-Speech with pyttsx3 primary, gTTS fallback. Also logs the spoken text.
    """
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 200)
        engine.setProperty('volume', 0.9)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"pyttsx3 error: {e}, using gTTS fallback")
        try:
            with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as fp:
                tts = gTTS(text=text, lang='en', slow=True)
                tts.save(fp.name)
                pygame.mixer.music.load(fp.name)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(5)
                pygame.mixer.music.unload()
        except Exception as e2:
            print(f"gTTS error: {e2}")
    print(f"Axon: {text}")
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(f"Axon: {text}\n")

def process_command(query):
    command, args = process_command_with_gemini(query, COMMAND_MAP)
    if command:
        return command, args

    normalized_query = normalize_text(query)
    all_phrases = [phrase for cmd, phrases in COMMAND_MAP.items() for phrase in phrases]
    best_match = process.extractOne(normalized_query, all_phrases, score_cutoff=80)
    if best_match:
        matched_phrase, score = best_match[0], best_match[1]
        for cmd, phrases in COMMAND_MAP.items():
            if matched_phrase in phrases:
                args = normalized_query.replace(matched_phrase, '').strip()
                return cmd, args
    return None, query

def normalize_text(text):
    text = text.lower()
    text = re.sub(r'\b(a|the|please|could you|can you|would you|kindly|now|for)\b', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    return re.sub(r'\s+', ' ', text).strip()

# Initialize recognizer
try:
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 4000
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.8
    recognizer.phrase_threshold = 0.3
    recognizer.non_speaking_duration = 0.5
except Exception as e:
    print(f"Speech recognition init error: {e}")
    recognizer = None

def takeCommand(timeout=5):
    if not recognizer:
        print("Speech recognition unavailable, enter command: ")
        return input().strip().lower()
    try:
        with sr.Microphone() as source:
            print("Listening... 🎤")
            recognizer.adjust_for_ambient_noise(source, duration=1.0)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=timeout)
            print("Recognizing...")
            return recognizer.recognize_google(audio, language='en-US').lower()
    except sr.WaitTimeoutError:
        print("No speech detected")
    except sr.UnknownValueError:
        print("Didn't catch that")
    except Exception as e:
        print(f"Speech error: {e}")
    return ""

async def taskExec(input_mode):
    while True:
        if input_mode == "voice":
            print("\nListening for command...")
            query = takeCommand()
            if not query:
                continue
        else:
            query = get_input("\nEnter command (or 'exit' to stop): ").strip().lower()
            if query == 'exit':
                speak("Goodbye, sir!")
                break

        command, args = process_command(query)
        if not command:
            speak("Command not recognized")
            continue

        if command == "stop":
            speak("Goodbye, sir!")
            break
        elif command == "who am i":
            response = (
                # "Your bio"
            )
            speak(response)
        elif command == "who are you":
            response = (
                "I'm Axon, your personal assistant, inspired by Tony Stark's Iron Man suit system. "
                "I'm here to help with tasks, answer questions, and manage your needs. "
                "Always learning, I aim to assist you seamlessly. How can I serve you today?"
            )
            speak(response)
        elif command == "ask ai":
            question = args or (takeCommand() if input_mode == "voice" else get_input("Enter question: ").strip())
            if question:
                response = ask_ai(question)
                speak(response)
        elif command == "youtube search":
            if args:
                webbrowser.open(f"https://www.youtube.com/results?search_query={quote(args)}")
                speak("Here's what I found on YouTube")
        elif command == "google search":
            if args:
                webbrowser.open(f"https://www.google.com/search?q={quote(args)}")
                speak(f"Searching Google for {args}")
            else:
                speak("Please provide a search query")
        elif command == "wikipedia":
            if args:
                try:
                    result = get_wikipedia_summary(args)
                    with open("log.txt", "a", encoding="utf-8") as f:
                        f.write(f"Wikipedia result: {result}\n")
                    speak(result)
                except:
                    speak("Couldn't find that on Wikipedia")
        elif command == "screenshot":
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            pyautogui.screenshot().save(filename)
            speak("Screenshot saved")
        elif command == "open app":
            if args:
                open_app(args)
                speak(f"Opening {args}")
            else:
                speak("Please specify an app to open")
        elif command == "describe screen":
            # Capture screenshot
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                screenshot_path = temp_file.name
                pyautogui.screenshot().save(screenshot_path)
            
            try:
                # Analyze screenshot with Gemini
                description = describe_image_with_gemini(screenshot_path)
                if description:
                    speak(description)
                else:
                    speak("Sorry, I couldn't analyze what's on your screen.")
            finally:
                # Clean up temporary file
                if os.path.exists(screenshot_path):
                    os.remove(screenshot_path)

async def main():
    speak("Initializing Axon... How may I assist you, sir?")
    print("\nSelect input mode:")
    print("1. Voice Input")
    print("2. Manual Type Input")
    while True:
        choice = get_input("Choose (1 or 2): ").strip()
        if choice in ['1', '2']:
            break
        print("Invalid choice. Please enter 1 or 2.")
    input_mode = "voice" if choice == '1' else "manual"
    await taskExec(input_mode)

if __name__ == "__main__":
    asyncio.run(main())
