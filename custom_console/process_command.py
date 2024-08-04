import random
import os
import sys
import threading
import tkinter as tk
from groq import Groq
from speach_recognition import SpeechRecognizer
import keyboard
import pyttsx3
import time
import concurrent.futures
import pydub
import edge_tts
from pydub.playback import play
from pydub.audio_segment import AudioSegment
import io
import re


class ProcessCommand:
    def __init__(self, widget, root, callback=None):
        self.speech_recognizer = SpeechRecognizer(callback=self.process_speech)
        self.print_console = callback
        self.text_ = widget
        self.speaker = pyttsx3.init()
        self.window = root
        keyboard.on_press_key("numlock", lambda _: self.start_listening2())
        keyboard.on_press_key("esc", lambda _: self.exit_application())
        self.text_.bind("<space>", lambda e: self.stop_speaking() if self.speaking and not self.stop_speaking_event.is_set() else None)
        self.stop_speaking_event = threading.Event()
        self.speaker.setProperty('voice', self.speaker.getProperty('voices')[1].id)
        self.groq_client = Groq(api_key="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")
        self.rate = "0"
        self.speaking = False
        self.speak = False
        self.recording = False
        self.last_response = ""
        self.speech_thread = None
        self.reply_type = ""
        self.voice = "en-US-JennyNeural"
        self.female_voice = [
            'en-AU-NatashaNeural', 'en-GB-LibbyNeural', 'en-GB-MaisieNeural', 'en-GB-SoniaNeural',
            'en-US-AvaNeural', 'en-US-EmmaNeural', 'en-US-AnaNeural', 'en-US-JennyNeural',
        ]
        self.male_voice = [
            'en-AU-WilliamNeural', 'en-GB-RyanNeural', 'en-GB-ThomasNeural', 'en-GB-RyanNeural',
            'en-US-AndrewNeural', 'en-US-BrianNeural', 'en-US-ChristopherNeural', 'en-US-EricNeural',

        ]

        self.action_commands = {
            "start_listening": self.start_listening,
            "set_fg": self.change_fg,
            "set_bg": self.change_bg,
            "clear": self.clear_console,
            "font_size": self.change_font_size,
            "echo": self.echo_command,
            "ls": self.list_commands,
            "exit": self.exit_application,
            "flip_coin": self.flip_coin,
            "copy_response": self.copy_last_response,
            "toggle_speak": self.speak_toggle,
            "set_speed": self.manage_speed,
            "change_voice": self.change_voice,
            "set_reply": self.set_reply_type
        }

    def work_on_command(self, command, speach=False):
        action_parts = command.strip().split()
        command_name = action_parts[0].lower()
        command_args = action_parts[1].lower() if len(action_parts) > 1 else []
        command_ = self.action_commands.get(command_name)

        if callable(command_):
            if command_args:
                command_(command_args)
            else:
                command_()
        else:
            if self.speak:
                self.text_.delete('1.0', tk.END)
            response = self.groq_reply(command, reply_type=self.reply_type)
            self.last_response = response
            self.print_console(response, new_line=True)
            if self.speak:
                self.speak_function(response)

        if speach:
            self.text_.insert('insert', '\n')
            self.text_.yview(tk.END)

    def set_reply_type(self, replytype):
        self.reply_type = str(replytype)
        self.print_console(f"Reply type updated to : {self.reply_type}")

    def manage_speed(self, speed):
        self.rate = speed
        self.print_console(f"Speed Updated : +{speed}%")

    def list_edge_voices(self):
        voice_list = self.male_voice + self.female_voice
        self.print_console(f"Available voices: {voice_list}")

    def change_voice(self, voice=None):
        if voice is None:
            # If no voice is specified, list available voices
            self.list_edge_voices()
            return
        elif voice == "random":
            self.voice = random.choice(self.female_voice)
            self.print_console(f"Voice updated to {self.voice}")
        else:
            if voice in self.female_voice or voice in self.male_voice:
                self.voice = voice
                self.print_console(f"Voice updated to {voice}")
            else:
                self.list_edge_voices()
                self.print_console(f"Voice '{voice}' not found. Please choose from the available voices.")

    def flip_coin(self):
        self.print_console(random.choice(["Heads", "Tails"]))

    def speak_toggle(self):
        self.speak = not self.speak
        self.print_console(f"Text to Speech : {str(self.speak)}")

    def audio_data(self, text):
        communicate = edge_tts.Communicate(text, voice=self.voice, rate=f"+{self.rate}%")
        audio_buffer = []
        for chunk in communicate.stream_sync():
            if chunk["type"] == "audio":
                audio_buffer.extend(chunk["data"])
        return audio_buffer

    def clear_console(self):
        self.text_.delete('1.0', tk.END)
        self.print_console("Console cleared.", new_line=False)

    def _speak_text(self, text):

        sentences = re.split(r'(?<=[.!?])\s+', text)
        lines = [line for line in sentences if len(line) > 2]

        start = time.perf_counter()
        self.speaking = True
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit tasks for each text and store futures in a list
            futures = [executor.submit(self.audio_data, text) for text in lines]

            # Collect results in the order of submission
            audio_buffers = [future.result() for future in futures]

        end = time.perf_counter()

        print(f"Time Taken : {end - start}")

        for buffer in audio_buffers:
            if not self.stop_speaking_event.is_set():
                combined_audio = AudioSegment.empty()
                # Use in-memory buffer
                audio_stream = io.BytesIO(bytes(buffer))
                try:
                    audio_segment = AudioSegment.from_file(audio_stream, format="mp3")
                    combined_audio += audio_segment
                    play(audio_segment)
                except Exception as e:
                    print(f"Error processing audio: {e}")


        self.speaking = False

    def stop_speaking(self):
        self.print_console("Stopping speech....\n")
        self.stop_speaking_event.set()

    def speak_function(self, text):
        self.stop_speaking_event.clear()
        self.speech_thread = threading.Thread(target=self._speak_text, args=(text,))
        self.speech_thread.start()

    def change_font_size(self, size):
        try:
            size = int(size)
            current_font = self.text_['font'].split()
            new_font = (current_font[0], size) + tuple(current_font[2:])
            self.text_.configure(font=new_font)
            self.print_console(f"Font size changed to {size}.", new_line=True)
        except ValueError:
            self.print_console(f"Invalid size: {size}. Please enter a number.", new_line=True)

    def start_listening(self):
        if not self.recording and not self.speaking:
            self.recording = True
            self.print_console("Listening....Speak")
            self.speech_recognizer.start_function()

    def start_listening2(self):
        if not self.recording and not self.speaking:
            self.recording = True
            self.print_console("alt has been pressed", new_line=False)
            self.print_console("Listening....Speak\n")
            self.speech_recognizer.start_function()

    def copy_last_response(self):
        pyperclip.copy(self.last_response)
        self.print_console("Text copied successfully")

    def echo_command(self, message):
        self.print_console(f"Echo: {message}", new_line=True)

    def list_commands(self):
        commands = list(self.action_commands.keys())
        formatted_commands = ''.join(f"{cmd}||" for cmd in commands)
        self.print_console(formatted_commands)

    def exit_application(self):
        if self.speaking:
            self.stop_speaking()
            self.speech_thread.join()
        self.window.quit()
        sys.exit()

    def process_speech(self, text):
        response = f"{text}"
        if self.print_console:
            self.print_console(response, new_line=False)
        self.work_on_command(response, speach=True)
        self.recording = False

    def change_fg(self, color):
        try:
            self.text_.configure(foreground=color)
        except:
            self.print_console(f'{color} does not exist. Are you colorblind?')

    def change_bg(self, color):
        try:
            self.window.configure(background=color)
            self.text_.configure(background=color)
        except:
            self.print_console(f'{color} does not exist. Are you colorblind?')

    def groq_reply(self, command, reply_type="Helpful"):
        reply = self.groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"give reply only in plain paragraphs",
                }, {
                    "role": "user",
                    "content": f"{command}",
                }
            ],
            model="llama3-8b-8192",
        )
        return reply.choices[0].message.content
