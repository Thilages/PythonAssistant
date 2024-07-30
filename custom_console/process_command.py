import random
import os
import sys
import threading
import pyttsx3
import tkinter as tk
from groq import Groq
import pyperclip
from speach_recognition import SpeechRecognizer
import keyboard


class ProcessCommand:
    def __init__(self, widget, root, callback=None):
        self.speech_recognizer = SpeechRecognizer(callback=self.process_speech)
        self.print_console = callback
        self.text_ = widget
        self.speaker = pyttsx3.init()
        self.window = root
        keyboard.on_press_key("right", lambda _: self.start_listening2())
        keyboard.on_press_key("esc", lambda _: self.exit_application())
        self.text_.bind("<space>", lambda
            e: self.stop_speaking() if self.speaking and not self.stop_speaking_event.is_set() else None)
        self.stop_speaking_event = threading.Event()
        self.speaker.setProperty('voice', self.speaker.getProperty('voices')[1].id)
        self.groq_client = Groq(api_key="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")
        self.speaker.setProperty('rate', 260)  # Speed of speech
        self.speaker.setProperty('volume', 1)
        self.speaking = False
        self.speak = False
        self.recording = False
        self.last_response = ""
        self.speech_thread = None
        self.reply_type = ""

        self.action_commands = {
            "listen": self.start_listening,
            "fg": self.change_fg,
            "bg": self.change_bg,
            "clear": self.clear_console,
            "fontsize": self.change_font_size,
            "echo": self.echo_command,
            "commands": self.list_commands,
            "exit": self.exit_application,
            "flip": self.flip_coin,
            "copy": self.copy_last_response,
            "speak": self.speak_toggle,
            "speedspeach": self.manage_speed,
            "changevoice": self.change_voice,
            "stop": self.stop_speaking,
            "replytype":self.set_reply_type
        }

        # self.str_commands = {
        #     "hello": "Ahoy, matey! Ready for some command fun?",
        #     "bye": "Catch you later, alligator!",
        #     "how are you": "I'm as good as the code I run!",
        #     "what's up": "The ceiling, mostly. And some code bugs.",
        #     "who are you": "Just your friendly neighborhood console, here to help!",
        #     "tell me a joke": "Why do programmers always mix up Christmas and Halloween? Because Oct 31 equals Dec 25!",
        #     "sing": "I’d sing if my speakers weren’t turned off!",
        #     "dance": "I’d dance, but I’m stuck in this code loop.",
        #     "are you alive": "Alive and well, as far as the CPU is concerned!",
        #     "what is your purpose": "To assist you and occasionally tell terrible jokes.",
        #     "do you sleep": "Sleep is for the uncompiled. I’m always awake!",
        #     "help": "Help is on the way! Or at least, I’m trying my best.",
        #     "thank you": "You’re welcome! I live to serve... and debug.",
        #     "what time is it": "Time for you to get a watch, I’m afraid.",
        #     "how’s the weather": "I can’t check the weather, but I’m sure it’s perfect for coding!",
        #     "who is your owner": "MR.Thilagesh"
        # }

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

        # elif self.str_commands.get(command):
        #     reply = self.str_commands.get(command)
        #     self.print_console(reply)
        #     if self.speak:
        #         self.speak_function(reply)

        else:
            if self.speak:
                self.text_.delete('1.0', tk.END)
            response = self.groq_reply(command,reply_type=self.reply_type)
            self.last_response = response
            self.print_console(response, new_line=True)
            if self.speak:
                self.speak_function(response)

        if speach:
            self.text_.insert('insert', '\n')
            self.text_.yview(tk.END)

    def set_reply_type(self,replytype):
        self.reply_type = str(replytype)
        self.print_console(f"Reply type updated to : {self.reply_type}")

    def manage_speed(self, speed):
        self.speaker.setProperty("rate", int(speed) if int(speed) > 100 else None)
        self.print_console(f"Speed Updated : {speed}")

    def change_voice(self, gender="female"):
        voices = self.speaker.getProperty('voices')
        if gender == "male":
            self.speaker.setProperty('voice', voices[0].id)
            self.print_console("Updated to male voice")
        else:
            self.speaker.setProperty('voice', voices[1].id)
            self.print_console("Updated to female voice")

    def flip_coin(self):
        self.print_console(random.choice(["Heads", "Tails"]))

    def speak_toggle(self):
        self.speak = not self.speak
        self.print_console(f"Text to Speech : {str(self.speak)}")

    def clear_console(self):
        self.text_.delete('1.0', tk.END)
        self.print_console("Console cleared.", new_line=False)

    def _speak_text(self, text):
        lines = text.split(".")
        # lines = (self.text_.get("1.0",tk.END)).split(".") ## This works very well but the speach translation is very bad
        # Filter out lines that are too short
        lines = [line.strip() for line in lines if len(line.strip()) > 2]
        self.speaking = True

        for line in lines:
            if self.stop_speaking_event.is_set():
                self.speaking = False
                self.stop_speaking_event.clear()
                break
            search_text = (" ".join(line.split(" ")[:2])).strip()
            print(search_text)
            # Find the position of the line in the text widget
            idx = self.text_.search(search_text, "1.0", stopindex=tk.END)
            if idx:
                # Move the view to make sure the line is visible
                top, bottom = self.text_.yview()
                self.text_.yview_moveto(min(top + 0.5, 1))
                self.text_.see(idx)

            else:
                print("found nothing")
            # Say the line
            self.speaker.say(line)
            self.speaker.runAndWait()

        self.speaking = False

    def stop_speaking(self):
        self.stop_speaking_event.set()
        self.print_console("Stopping speech....\n")

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
        self.print_console(f"Available commands: {commands}", new_line=True)

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

    def groq_reply(self, command,reply_type="Helpful"):
        reply = self.groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"you are Mature {reply_type} assistant,don't leave empty space between lines",
                }, {
                    "role": "user",
                    "content": f"{command}",
                }
            ],
            model="llama3-8b-8192",
        )
        return reply.choices[0].message.content
