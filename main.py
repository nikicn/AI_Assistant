import threading  # For handling multiple threads
import tkinter as tk  # For creating the GUI
from tkinter import scrolledtext, ttk  # For adding scrolled text and themed widgets to the GUI
import random  # For generating random responses
import speech_recognition as sr  # For speech recognition
import winsound  # For playing beep sounds
import pyttsx3  # For text-to-speech conversion
import datetime  # For getting the current date and time
import requests  # For making HTTP requests
from googletrans import Translator, LANGUAGES  # For translating text
import re  # For regular expressions
import wikipediaapi  # For fetching Wikipedia content
import os  # For operating system related functions
import ctypes  # For locking the Windows workstation

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Set the speech rate (speed of the speech)
rate = engine.getProperty('rate')  # Get the current speech rate
print(f"Current speech rate: {rate}")  # Print the current speech rate
engine.setProperty('rate', 145)  # Set a new speech rate

# Set the volume of the speech
volume = engine.getProperty('volume')  # Get the current volume level
print(f"Current volume level: {volume}")  # Print the current volume level
engine.setProperty('volume', 1.0)  # Set a new volume level

def speak(text):
    """Convert text to speech and speak it out."""
    engine.say(text)  # Queue the text to be spoken
    engine.runAndWait()  # Wait until speaking is done

# Initialize Wikipedia API
wiki = wikipediaapi.Wikipedia('english')

def fetch_wikipedia_summary(query, max_sentences=2):
    """Fetch a summary of the Wikipedia page for the given query."""
    wiki = wikipediaapi.Wikipedia('english', extract_format=wikipediaapi.ExtractFormat.WIKI)  # Initialize Wikipedia API with format
    page = wiki.page(query)  # Get the Wikipedia page for the query
    if page.exists():  # Check if the page exists
        summary = page.summary.split('. ')[:max_sentences]  # Split summary into sentences and get the first few
        summary_text = '. '.join(summary)  # Join the sentences into a single text
        return summary_text + "."  # Return the summary text
    else:
        return f"Sorry, I couldn't find any information on '{query}' on Wikipedia."  # Return a failure message if page doesn't exist

# Define intents and their corresponding keywords
intents = {
    'greeting': ['hello', 'hi', 'hey'],
    'farewell': ['bye', 'goodbye'],
    'gratitude': ['thank you', 'thanks'],
    'query': ['how are you', 'what are you doing'],
    'weather': ['weather', 'temperature', 'forecast'],
    'time': ['time', 'current time'],
    'date': ['date', 'current date', "Date"],
    'reminder': ['reminder', 'remind me'],
    'joke': ['joke', 'tell me a joke'],
    'fact': ['fact', 'interesting fact'],
    'meaning': ['meaning of'],
    'translate': ['translate'],
    'who_are_you': ['who are you', 'what is your name', 'who r u'],
    'what is your name': ['What is your name?', 'what is ur name'],
    'wikipedia': ['wikipedia', 'wiki', 'information', 'search'],
    'lock': ['lock windows', 'lock']
}

# Define responses for each intent
responses = {
    'wikipedia': ['Here is some information from Wikipedia:', 'I found this on Wikipedia:', 'According to Wikipedia:'],
    'greeting': ['Hi there!', 'Hello!', 'Hey!'],
    'farewell': ['Goodbye!', 'See you later!', 'Bye!'],
    'gratitude': ['You\'re welcome!', 'No problem!', 'My pleasure!'],
    'query': ['I\'m doing well, thank you!', 'Just assisting you!', 'Feeling great, thank you for asking!'],
    'weather': ['The weather is sunny today.', 'It\'s cloudy with a chance of rain.'],
    'time': ['The current time is ' + datetime.datetime.now().strftime("%I:%M %p")],  # Get the current time and format it
    'date': ['Today, the date is: ' + datetime.datetime.now().strftime("%d %B %Y")],  # Get the current date and format it
    'reminder': ['Sure, I will remind you.', 'Reminder set successfully.'],
    'joke': ['Why don\'t scientists trust atoms? Because they make up everything!', 'I\'m reading a book on anti-gravity. It\'s impossible to put down!'],
    'fact': ['Did you know that the shortest war in history was between Britain and Zanzibar on August 27, 1896? It lasted only 38 minutes!'],
    'translate': ['Can you please provide a specific word or sentence to translate and the specified language.'],
    'who_are_you': ['I am Atlas, your Female AI assistant.'],
    'what is your name': ['My name is Atlas.']
}

# Function to lock the Windows workstation
def lock_windows():
    ctypes.windll.user32.LockWorkStation()  # Call the Windows API to lock the workstation

def fetch_word_meaning(word):
    """Fetch the meaning of a word from a dictionary API."""
    url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}'  # URL for the dictionary API
    response = requests.get(url)  # Make a request to the API
    data = response.json()  # Get the JSON response
    if isinstance(data, list) and 'meanings' in data[0]:  # Check if the response is valid
        meanings = data[0]['meanings']  # Get the meanings
        definition = [meaning['definitions'][0]['definition'] for meaning in meanings]  # Extract the definitions
        return " ".join(definition)  # Return the definitions as a single string
    else:
        return "Sorry, I couldn't find the meaning of that word."  # Return a failure message if the word isn't found

def translate_text(text, dest_language):
    """Translate the given text to the specified language."""
    translator = Translator()  # Initialize the translator
    translated_text = translator.translate(text, dest_language).text  # Translate the text
    return translated_text  # Return the translated text

def fetch_weather(location):
    """Fetch the current weather for a given location."""
    api_key = '7e760b7138d38407c12adc03973acb37'  # Replace with your OpenWeatherMap API key
    url = f'https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric'  # Weather API URL
    response = requests.get(url)  # Make a request to the API
    data = response.json()  # Get the JSON response
    if data['cod'] == 200:  # Check if the response is successful
        weather = data['weather'][0]['description']  # Get the weather description
        temperature = data['main']['temp']  # Get the temperature
        return f"The current weather in {location} is {weather} with a temperature of {temperature}°C."  # Return the weather info
    else:
        return "Sorry, I couldn't fetch the weather for that location."  # Return a failure message if location isn't found

def process_command(command):
    """Process text commands given by the user."""
    command = command.lower()  # Convert the command to lowercase
    found_intent = False  # Flag to check if an intent was found
    
    # Check for lock command
    if 'lock' in command:
        found_intent = True  # Set the flag to True
        speak("locking your device")  # Speak the response
        lock_windows()  # Lock the workstation
        display_response("User: " + command + "\n" + "Atlas: Windows locked." + "\n\n")  # Display the response
    
    # Check for meaning intent
    meaning_match = re.search(r'meaning of (\w+)', command)  # Match the pattern for "meaning of"
    if meaning_match:
        found_intent = True  # Set the flag to True
        word = meaning_match.group(1)  # Extract the word
        meaning = fetch_word_meaning(word)  # Fetch the meaning
        speak(meaning)  # Speak the meaning
        display_response("User: " + command + "\n" + "Atlas: " + meaning + "\n\n")  # Display the response
    
    # Check for translate intent
    translate_match = re.search(r'translate (.+) to (\w+)', command)  # Match the pattern for "translate"
    if translate_match:
        found_intent = True  # Set the flag to True
        text_to_translate = translate_match.group(1)  # Extract the text to translate
        dest_language = translate_match.group(2)  # Extract the destination language

        # Check if the destination language is valid
        if dest_language in LANGUAGES.values():
            translated_text = translate_text(text_to_translate, dest_language)
        else:
            dest_language_code = next((code for code, lang in LANGUAGES.items() if lang == dest_language), None)
            if dest_language_code:
                translated_text = translate_text(text_to_translate, dest_language_code)
            else:
                translated_text = f"Sorry, I don't recognize the language '{dest_language}'."

        speak(translated_text)  # Speak the translated text
        display_response("User: " + command + "\n" + "Atlas: " + translated_text + "\n\n")  # Display the response
    
    # Check for weather intent
    weather_match = re.search(r'weather in (\w+)', command)  # Match the pattern for "weather in"
    if weather_match:
        found_intent = True  # Set the flag to True
        location = weather_match.group(1)  # Extract the location
        weather = fetch_weather(location)  # Fetch the weather
        display_response("User: " + command + "\n" + "Atlas: " + weather + "\n\n")  # Display the response
    
    # Wikipedia search
    if 'wikipedia' in command:
        found_intent = True  # Set the flag to True
        query = command.replace('wikipedia', '').strip()  # Extract the query by removing 'wikipedia' and trimming spaces

# Remaining part of the code would go here...
        summary = fetch_wikipedia_summary(query)  # Fetch the Wikipedia summary for the query
        speak(summary)  # Speak the summary
        display_response("User: " + command + "\n" + "Atlas: " + summary + "\n\n")  # Display the response
    
    # Check for other intents
    if not found_intent:  # If no specific intent has been found yet
        for intent, keywords in intents.items():  # Iterate over all defined intents
            if any(keyword in command for keyword in keywords):  # Check if any keyword for the current intent is in the command
                found_intent = True  # Set the flag to True
                response = random.choice(responses[intent])  # Choose a random response for the intent
                speak(response)  # Speak the response
                display_response("User: " + command + "\n" + "Atlas: " + response + "\n\n")  # Display the response
                break  # Exit the loop since we found a matching intent
    
    if not found_intent:  # If no intent was found after checking all
        response = "Sorry, I didn't understand the command"  # Set a default response for unrecognized commands
        speak(response)  # Speak the default response
        display_response("User: " + command + "\n" + "Atlas: " + response + "\n\n")  # Display the response





#GUI Part
def display_response(response):
    """Display user input and Atlas response in the GUI."""
    conversation_log.tag_configure("user", justify='left')  # Configure the tag for user input
    conversation_log.tag_configure("atlas", justify='right')  # Configure the tag for Atlas response

    if response.startswith("User:"):  # Check if the response is from the user
        conversation_log.insert(tk.END, response, "user")  # Insert user input into the conversation log
    elif response.startswith("Atlas:"):  # Check if the response is from Atlas
        conversation_log.insert(tk.END, response, "atlas")  # Insert Atlas response into the conversation log
    conversation_log.insert(tk.END, "\n")  # Insert a newline for better readability
    conversation_log.see(tk.END)  # Scroll to the end of the conversation log

# Define wake word and stop word
WAKE_WORD = "atlas"  # The wake word to start listening
STOP_WORD = "stop"  # The word to stop listening
listening = False  # Flag to check if the assistant is listening

def wake_up():
    """Activate listening mode."""
    global listening  # Use the global listening flag
    listening = True  # Set listening to True
    play_beep_sound()  # Play a beep sound to indicate activation
    speak("Yes, how can I help you?")  # Speak a prompt

def sleep():
    """Deactivate listening mode."""
    global listening  # Use the global listening flag
    listening = False  # Set listening to False
    speak("Goodbye!")  # Speak a farewell message

def process_voice_commands():
    """Process voice commands using speech recognition."""
    global listening  # Use the global listening flag
    recognizer = sr.Recognizer()  # Initialize the speech recognizer
    with sr.Microphone() as source:  # Use the default microphone as the audio source
        recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
        
        while True:  # Continuously listen for commands
            if not listening:  # If not in listening mode
                print("Listening for the wake word...")  # Print status
                audio = recognizer.listen(source, timeout=5)  # Listen for the wake word
                print("Recognizing wake word...")  # Print status
                try:
                    command = recognizer.recognize_google(audio).lower()  # Recognize and convert the command to lowercase
                    print("You said:", command)  # Print the recognized command
                    if WAKE_WORD in command:  # Check if the wake word is in the command
                        wake_up()  # Activate listening mode
                except sr.UnknownValueError:
                    pass  # Ignore unrecognized commands
                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition service; {e}")  # Print error message
            else:  # If in listening mode
                print("Listening for commands...")  # Print status
                audio = recognizer.listen(source)  # Listen for a command
                print("Recognizing command...")  # Print status
                try:
                    command = recognizer.recognize_google(audio).lower()  # Recognize and convert the command to lowercase
                    print("You said:", command)  # Print the recognized command
                    if STOP_WORD in command:  # Check if the stop word is in the command
                        sleep()  # Deactivate listening mode
                    else:
                        process_command(command)  # Process the recognized command
                except sr.UnknownValueError:
                    print("Could not understand audio")  # Print error message for unrecognized commands
                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition service; {e}")  # Print error message

def play_beep_sound():
    """Play a beep sound."""
    winsound.Beep(500, 100)  # Play a beep sound with frequency 500 Hz and duration 100 ms

# Create the GUI with Tkinter
root = tk.Tk()  # Initialize the main application window
root.title("AI Assistant")  # Set the window title

# Create a style for the conversation log
style = ttk.Style()  # Initialize the style object
style.theme_use('clam')  # Use the 'clam' theme
style.configure("response.TLabel", font=("Helvetica", 12), wraplength=600)  # Configure the label style

# Create a scrolled text widget to display the conversation log
conversation_log = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=30, font=("Helvetica", 12))  # Initialize the scrolled text widget
conversation_log.grid(column=0, row=0, padx=10, pady=10)  # Place the widget in the grid layout

# Start voice command processing in a separate thread
threading.Thread(target=process_voice_commands).start()  # Start the voice command processing thread

root.mainloop()  # Start the Tkinter main loop


#coding ends
#project completes
#thank you for being with me in this wonderfull journey
#ok so thank you take care and bye bye



