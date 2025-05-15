import os
from dotenv import load_dotenv
import openai
import speech_recognition as sr
import pyttsx3
import requests
import webbrowser

import tkinter as tk
from itertools import cycle
from PIL import Image, ImageTk
from threading import Thread
import time

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart




language_codes = {
    "english": {"speech_recognition": "en-US", "tts": "en"},
    "spanish": {"speech_recognition": "es-ES", "tts": "es"},
    "french": {"speech_recognition": "fr-FR", "tts": "fr"},
}


class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        openai.api_key = os.getenv("OPENAI_API_KEY")  # Ensure you have set this environment variable
        self.default_rate = self.engine.getProperty('rate')
        self.current_language = "english"  

    def listen(self):
        '''Listen for audio and convert it to text in the currently selected language.'''
        lang_code = language_codes[self.current_language]["speech_recognition"]
        with sr.Microphone() as source:
            print("Listening...")
            audio = self.recognizer.listen(source)
            try:
                text = self.recognizer.recognize_google(audio, language=lang_code)
                print(f"You said: {text}")
                return text
            except Exception as e:
                print("Sorry, I could not understand. Please try again.")
                return None

    def speak(self, text, rate=None):
        '''Convert text to speech and play it out loud in the currently selected language.'''
        if rate is not None:
            self.engine.setProperty('rate', rate)
        else:
            # Reset to default rate if no specific rate is provided
            default_rate = self.engine.getProperty('rate')
            self.engine.setProperty('rate', default_rate)
            
        lang = language_codes[self.current_language]["tts"]
        self.engine.say(text)
        self.engine.runAndWait()

    def change_language(self, language_name):
        '''Change the current language of the assistant.'''
        if language_name in language_codes:
            self.current_language = language_name
            self.speak("Language changed successfully.")
        else:
            self.speak("Sorry, I don't support that language yet.")

    # Include other methods here (e.g., ask_openai, get_weather_info, search_google, draft_email, send_email)

    def format_email_address(self, spoken_email):
        '''Format spoken email address into a proper email format.'''
        email_address = spoken_email.lower().replace(" at ", "@").replace(" dot ", ".")
        return email_address
    def ask_openai(self, query):
        '''Use OpenAI's API to generate a response to a query.'''
        try:
            response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": query},
            ]
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            print(f"An error occurred: {e}")
            return "I'm sorry, but I'm unable to provide an answer at this time."
    def get_weather_info(self, city):
        api_key =os.getenv("WEATHER_API_KEY") 
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        weather_data = response.json()
        if response.status_code == 200:
            temperature = weather_data['main']['temp']
            description = weather_data['weather'][0]['description']
            return f"The current weather in {city} is {description} with a temperature of {temperature}°C."
        else:
            return "I'm sorry, I couldn't fetch the weather for you. Please make sure the city name is correct."
    def search_google(self, query):
        '''Perform a Google search for the specified query.'''
        search_url = "https://www.google.com/search?q=" + query
        webbrowser.open(search_url)
        return f"I've performed a Google search for: {query}"
    
    def draft_email(self, to, subject, body):
        # Draft an email in the default email client
        url = f"mailto:{to}?subject={subject}&body={body}"
        webbrowser.open(url)
        return "I've opened your email client to draft an email."

    def send_email(self, sender, recipient, subject, body, password):
        '''Send an email programmatically.'''
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        try:
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
            return "Email sent successfully."
        except smtplib.SMTPAuthenticationError:
            return "Failed to send email. Authentication failed."
        finally:
            server.quit()

    # Your other methods (e.g., listen, speak, ask_openai)
    def sing(self, lyrics):
        '''Simulate singing by adjusting the speech rate and pitch.'''
        self.speak(lyrics, rate=100)  # Adjust these values as needed

    def start(self):
        try:
            while True:
                query = self.listen()
                if query:
                    query = query.lower() 
                    if "draft an email" in query:
                        self.speak("Who do you want to send the email to?")
                        to = self.listen()
                        self.speak("What's the subject of the email?")
                        subject = self.listen()
                        self.speak("Please tell me the body of your email.")
                        body = self.listen()
                        response = self.draft_email(to, subject, body)
                        self.speak(response)
                    elif "send an email" in query:
                        self.speak("What is the recipient's email address?")
                        recipient_spoken = self.listen()
                        if recipient_spoken:
                            recipient = self.format_email_address(recipient_spoken)
                            self.speak("What's the subject of the email?")
                            subject = self.listen()
                            self.speak("Please tell me the body of your email.")
                            body = self.listen()
                            sender = "your-email@gmail.com"
                            password = os.getenv("EMAIL_PASSWORD")  
                            response = self.send_email(sender, recipient, subject, body, password)
                            self.speak(response)
                    elif "change language to" in query:
                        # Extracting the language name from the query
                        new_language = query.split("to")[-1].strip()
                        self.change_language(new_language)
                    elif "weather in" in query:
                        city = query.split("in")[-1].strip()
                        weather_response = self.get_weather_info(city)
                        self.speak(weather_response)
                    elif "search" in query:
                        search_query = query.replace("search", "").strip()
                        response = self.search_google(search_query)
                    elif "sing" in query:
                        lyrics = "Happy birthday to you, happy birthday to you. Hoorayyyy!"
                        self.sing(lyrics)
                    else:
                        response = self.ask_openai(query)
                        self.speak(response)
        except KeyboardInterrupt:
            self.speak("Goodbye! Have a great day!")
            print("\nVoice Assistant has been stopped.")
        
                # Add other functionalities like weather info, google search, etc.


class VoiceAssistantGUI(VoiceAssistant):
    def __init__(self):
        super().__init__()
        self.root = tk.Tk()
        self.root.title("Voice Assistant")

        # Load static image and animated GIF
        self.static_img = ImageTk.PhotoImage(file='C:\\Users\\15714\\Desktop\\app - Copy\\app\\chatbot-kiu.gif')
        self.gif_path = 'C:\\Users\\15714\\Desktop\\app - Copy\\app\\chatbot-kiu.gif'

        self.gif_frames = self.load_gif_frames(self.gif_path)
        self.is_speaking = False

        self.robot_label = tk.Label(self.root, image=self.static_img)
        self.robot_label.pack()

        self.response_text = tk.Text(self.root, height=10, width=50)
        self.response_text.pack()

        # Remove the listen button and start listening automatically
        self.start_continuous_listening()

    def start_listening(self):
        """Start listening in a non-blocking manner."""
        listening_thread = Thread(target=self.listen_and_respond, daemon=True)
        listening_thread.start()
    # Method to load frames from GIF
    def load_gif_frames(self, path):
        frames = []
        img = Image.open(path)
        for frame in range(0, img.n_frames):
            img.seek(frame)
            frame_img = ImageTk.PhotoImage(img.copy())
            frames.append(frame_img)
        return cycle(frames)

    def update_robot_image(self, image):
        self.robot_label.configure(image=image)
        self.robot_label.image = image

    def animate_gif(self, frame_index=0):
        if not self.is_speaking:
            self.update_robot_image(self.static_img)  # Ensure static image is shown when not speaking
            return
        self.update_robot_image(next(self.gif_frames))
        self.root.after(80, self.animate_gif) 

    def start_animation(self):
        self.is_speaking = True
        self.animate_gif()

    def stop_animation(self):
        self.is_speaking = False

    def speak(self, text, rate=None):
        self.start_animation()
        super().speak(text, rate)
        self.stop_animation()

    def start_continuous_listening(self):
        """Start a thread for continuous listening."""
        Thread(target=self.continuous_listen_and_respond, daemon=True).start()

    def continuous_listen_and_respond(self):
        """Continuously listen for commands and respond."""
        while True:
            self.listen_and_respond()

    # Updated method for handling user commands and responses
    def listen_and_respond(self):
        self.update_response("Listening... Please speak now.")
        command = self.listen()

        if not command:
            self.update_response("I didn't catch that. Please try again.")
            return

        command = command.lower()
        response = ""

        # Predefined commands
        if "how are you" in command:
            response = "I'm good, thank you for asking!"
        elif "what is your name" in command or "who are you" in command:
            response = "I am your personal voice assistant."
        elif "change language to" in command:
            language = command.split("to")[-1].strip()
            if language in language_codes:
                self.change_language(language)
                response = f"Language changed to {language}."
            else:
                response = "Sorry, I don't support that language yet."
        elif "search for" in command:
            search_term = command.replace("search for", "", 1).strip()
            self.search_google(search_term)
            response = f"Searching for {search_term}."
        elif "weather in" in command:
            city = command.split("in")[-1].strip()
            response = self.get_weather_info(city)
        elif "sing" in command:
            self.sing("Happy birthday to you, happy birthday to you, Hoorayyyy.")
            response = "I hope you liked my song."
        elif "send an email" in command:
            self.speak("Whom do you want to send the email to?")
            recipient = self.listen()
            if recipient:
                recipient_email = self.format_email_address(recipient)
                
                self.speak("What is the subject of the email?")
                subject = self.listen()
                subject = subject if subject else "No Subject"
                
                self.speak("What should the email say?")
                body = self.listen()
                body = body if body else "No Content"
                
                # Example sender information - replace with actual data or securely fetch them
                sender_email = "yaysou26@gmail.com"
                sender_password = "Happyday123@"
                
                # Sending email
                response = self.send_email(sender_email, recipient_email, subject, body, sender_password)
                self.update_response(response)
                self.speak(response)
            else:
                self.update_response("Sent!")
                self.speak("Sent!")
            return

        else:
            # OpenAI API integration for general queries
            response = self.ask_openai(command)

        self.update_response(response)  # Update the GUI with the response
        self.speak(response)  # Speak out the response (optional, could be removed if not desired)

    def ask_openai(self, query):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": query},
                ]
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            print(f"An error occurred with OpenAI API: {e}")
            return "I'm sorry, but I'm unable to provide an answer at this time."


    def update_response(self, text):
        """Update the GUI with a new response."""
        self.response_text.config(state=tk.NORMAL)
        self.response_text.insert(tk.END, text + "\n")
        self.response_text.config(state=tk.DISABLED)
        self.response_text.see(tk.END)

    def run(self):
        self.root.mainloop()
