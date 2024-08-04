import random
import sys
import threading
import tkinter as tk
from groq import Groq
from speach_recognition import SpeechRecognizer
import keyboard
import pyttsx3
import tempfile
import pygame
import time
import concurrent.futures
import edge_tts
from pydub.audio_segment import AudioSegment
import io
import re
import pyperclip


class CommandProcessor:
    def __init__(self, text_widget, root_window, console_callback=None):
        """
        Initializes the CommandProcessor with the given parameters.

        :param text_widget: Tkinter Text widget to display text.
        :param root_window: Tkinter root window for the application.
        :param console_callback: Function to call for console output.
        """
        self.speech_recognizer = SpeechRecognizer(callback=self.handle_speech)
        self.console_callback = console_callback
        self.text_widget = text_widget
        self.text_to_speech_engine = pyttsx3.init()

        self.root_window = root_window
        self.stop_speaking_event = threading.Event()
        self.text_to_speech_engine.setProperty('voice', self.text_to_speech_engine.getProperty('voices')[1].id)
        self.groq_client = Groq(api_key="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")
        self.speech_rate = "0"
        self.is_speaking = False
        self.is_text_to_speech_enabled = False
        self.is_recording = False
        self.last_response = ""
        self.speech_thread = None

        self.current_voice = "en-US-JennyNeural"
        self.female_voices = [
            'en-AU-NatashaNeural', 'en-GB-LibbyNeural', 'en-GB-MaisieNeural', 'en-GB-SoniaNeural',
            'en-US-AvaNeural', 'en-US-EmmaNeural', 'en-US-AnaNeural', 'en-US-JennyNeural',
        ]
        self.male_voices = [
            'en-AU-WilliamNeural', 'en-GB-RyanNeural', 'en-GB-ThomasNeural', 'en-GB-RyanNeural',
            'en-US-AndrewNeural', 'en-US-BrianNeural', 'en-US-ChristopherNeural', 'en-US-EricNeural',
        ]

        self.command_actions = {
            "startlistening": self.start_listening,
            "setfg": self.change_fg_color,
            "setbg": self.change_bg_color,
            "clear": self.clear_console,
            "fontsize": self.change_font_size,
            "echo": self.echo_command,
            "ls": self.list_commands,
            "exit": self.exit_application,
            "flipcoin": self.flip_coin,
            "copyresponse": self.copy_last_response,
            "togglespeak": self.toggle_text_to_speech,
            "setspeed": self.update_speech_rate,
            "changevoice": self.change_voice,

        }

        # Set up hotkeys
        keyboard.on_press_key("numlock", lambda _: self.start_listening())
        keyboard.on_press_key("esc", lambda _: self.exit_application())
        self.text_widget.bind("<space>", self.handle_space_key)

    def handle_space_key(self, event):
        """Handles space key event to stop speaking if necessary."""
        if self.is_speaking and not self.stop_speaking_event.is_set():
            self.stop_speaking()

    def execute_command(self, command, is_speech_command=False):
        """
        Executes the given command by finding the appropriate action and calling it.

        :param command: Command string to be executed.
        :param is_speech_command: Boolean indicating if the command is from speech input.
        """
        command_parts = command.strip().split()
        command_name = command_parts[0].lower()
        command_args = command_parts[1] if len(command_parts) > 1 else ""
        command_action = self.command_actions.get(command_name)

        if callable(command_action):
            if command_args:
                command_action(command_args)
            else:
                command_action()
        else:
            # if self.is_text_to_speech_enabled:
            #     self.text_widget.delete('1.0', tk.END)
            response = self.generate_groq_response(command)
            self.last_response = response
            # self.console_callback("----------------------------------------------------------------------<<")

            self.console_callback(response, new_line=True)
            self.text_widget.insert("insert","\n")
            if self.is_text_to_speech_enabled:
                self.speak_response(response)

        if is_speech_command:
            self.text_widget.insert('insert', '\n')
            self.text_widget.yview(tk.END)



    def update_speech_rate(self, rate):
        """Updates the speech rate for text-to-speech."""
        try:
            self.speech_rate = rate
            self.console_callback(f"Speech rate updated to: +{rate}%")
        except:
            self.console_callback("Check the Rate properly")
        self.text_widget.insert("insert","\n")

    def list_edge_voices(self):
        """Lists available edge TTS voices."""
        all_voices = self.male_voices + self.female_voices
        self.console_callback(f"Available voices: {all_voices}")
        self.text_widget.insert("insert","\n")
    def change_voice(self, voice=None):
        """Changes the voice for text-to-speech."""
        if voice is None:
            self.list_edge_voices()
            return
        elif voice == "random":
            self.current_voice = random.choice(self.female_voices)
            self.console_callback(f"Voice updated to {self.current_voice}")
        else:
            if voice in self.female_voices or voice in self.male_voices:
                self.current_voice = voice
                self.console_callback(f"Voice updated to {voice}")
            else:
                self.list_edge_voices()
                self.console_callback(f"Voice '{voice}' not found. Please choose from the available voices.")
        self.text_widget.insert("insert","\n")
    def flip_coin(self):
        """Flips a coin and prints the result."""
        self.console_callback(random.choice(["Heads", "Tails"]))
        self.text_widget.insert("insert","\n")

    def toggle_text_to_speech(self):
        """Toggles text-to-speech functionality."""
        self.is_text_to_speech_enabled = not self.is_text_to_speech_enabled
        self.console_callback(f"Text to Speech Enabled: {self.is_text_to_speech_enabled}")
        self.text_widget.insert("insert","\n")

    def fetch_audio_data(self, text):
        """
        Fetches audio data for the given text using edge TTS.

        :param text: The text to be converted to speech.
        :return: Audio data as a list of bytes.
        """
        try:
            communicate = edge_tts.Communicate(text, voice=self.current_voice, rate=f"+{self.speech_rate}%")
            audio_buffer = []
            for chunk in communicate.stream_sync():
                if chunk["type"] == "audio":
                    audio_buffer.extend(chunk["data"])
            return audio_buffer
        except Exception as e:
            print(f"Error fetching audio data: {e}")
            return []

    def clear_console(self):
        """Clears the console text widget."""
        self.text_widget.delete('1.0', tk.END)
        self.console_callback("Console cleared.", new_line=False)

    def _speak_text(self, text):
        """
        Converts the given text to speech and plays it.

        :param text: The text to be spoken.
        """
        sentences = re.split(r'(?<=[.!?])\s+', text)
        lines = [line for line in sentences if len(line) > 2]
        self.console_callback("Generating Audio...",new_line = False)
        self.text_widget.yview(tk.END)
        start_time = time.perf_counter()
        self.is_speaking = True
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(self.fetch_audio_data, line) for line in lines]
                audio_buffers = [future.result() for future in futures]

            end_time = time.perf_counter()
            print(f"Time Taken: {end_time - start_time}")
            self.console_callback(f"Audio generated in: {round(end_time-start_time,1)} sec's")

            self.text_widget.insert("insert","\n")
            self.text_widget.yview(tk.END)
            pygame.mixer.init()
            combined_audio = AudioSegment.empty()
            for buffer in audio_buffers:
                if not self.stop_speaking_event.is_set():
                    if buffer:
                        audio_stream = io.BytesIO(bytes(buffer))
                        try:
                            audio_segment = AudioSegment.from_file(audio_stream, format="mp3")
                            combined_audio += audio_segment
                        except Exception as e:
                            print(f"Error processing audio: {e}")

            # Save to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                combined_audio.export(temp_file.name, format="mp3", bitrate="320k")
                temp_file_path = temp_file.name

            # Play audio using pygame
            pygame.mixer.music.load(temp_file_path)
            pygame.mixer.music.play()

            # Wait for playback to complete or be stopped
            while pygame.mixer.music.get_busy() and not self.stop_speaking_event.is_set():
                pygame.time.wait(100)  # Wait 100ms

        except Exception as e:
            print(f"Error during speaking: {e}")
        finally:
            self.is_speaking = False

    def stop_speaking(self):
        """Stops the current speech playback."""
        self.console_callback("Stopping speech....\n")
        pygame.mixer.music.stop()
        self.stop_speaking_event.set()

    def speak_response(self, text):
        """Starts a thread to speak the given text."""
        self.stop_speaking_event.clear()
        self.speech_thread = threading.Thread(target=self._speak_text, args=(text,))
        self.speech_thread.start()

    def change_font_size(self, size):
        """Changes the font size of the text widget."""
        try:
            size = int(size)
            current_font = self.text_widget['font'].split()
            new_font = (current_font[0], size) + tuple(current_font[2:])
            self.text_widget.configure(font=new_font)
            self.console_callback(f"Font size changed to {size}.", new_line=True)
        except ValueError:
            self.console_callback(f"Invalid size: {size}. Please enter a number.", new_line=True)
        self.text_widget.insert("insert","\n")

    def start_listening(self):
        """Starts listening for speech input."""
        if not self.is_recording and not self.is_speaking:
            self.is_recording = True
            self.console_callback("Listening.... Speak")
            self.speech_recognizer.start_function()

    def copy_last_response(self):
        """Copies the last response to the clipboard."""
        pyperclip.copy(self.last_response)
        self.console_callback("Text copied successfully")
        self.text_widget.insert("insert","\n")

    def echo_command(self, message):
        """Echoes the given message back to the console."""
        self.console_callback(f"Echo: {message}", new_line=True)
        self.text_widget.insert("insert","\n")

    def list_commands(self):
        """Lists all available commands."""
        commands = list(self.command_actions.keys())
        formatted_commands = ''.join(f"{cmd} - " for cmd in commands)
        self.console_callback(formatted_commands)
        self.text_widget.insert("insert","\n")

    def exit_application(self):
        """Exits the application."""
        if self.is_speaking:
            self.stop_speaking()
            self.speech_thread.join()
        self.root_window.quit()
        pygame.quit()
        sys.exit()

    def handle_speech(self, text):
        """Handles speech input by processing the recognized text."""
        response = f"{text}"
        if self.console_callback:
            self.console_callback(response, new_line=False)
        self.execute_command(response, is_speech_command=True)
        self.is_recording = False

    def change_fg_color(self, color):
        """Changes the foreground color of the text widget."""
        try:
            self.text_widget.configure(foreground=color)
            self.console_callback(f"Foreground updated to: {color}")
        except Exception:
            self.console_callback(f'{color} does not exist. Are you colorblind?')
        self.text_widget.insert("insert","\n")

    def change_bg_color(self, color):
        """Changes the background color of the text widget and root window."""
        try:
            self.root_window.configure(background=color)
            self.text_widget.configure(background=color)
            self.console_callback(f"Blackground updated to: {color}")
        except Exception:
           self.console_callback(f'{color} does not exist. Are you colorblind?')
        self.text_widget.insert("insert","\n")


    def generate_groq_response(self, command):
        """
        Generates a response from Groq based on the command and reply type.

        :param command: The command to send to Groq.
        :param reply_type: The type of reply to generate.
        :return: The response content from Groq.
        """
        reply = self.groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Give reply only in plain paragraphs.",
                }, {
                    "role": "user",
                    "content": command,
                }
            ],
            model="llama3-8b-8192",
        )
        return reply.choices[0].message.content
