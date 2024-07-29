import random
import os
from speach_recognition import SpeechRecognizer
import keyboard
import inspect
import tkinter as tk
from groq import Groq


# print(api_key)
class ProcessCommand():
    def __init__(self, widget, root, callback=None, ):
        self.print_console = callback  # Callback to send output to GUI
        self.speech_recognizer = SpeechRecognizer(callback=self.process_speech)
        keyboard.on_press_key("alt", lambda _: self.start_listening2())
        self.text_ = widget
        self.window = root
        self.groq_client = Groq(api_key="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")
        self.action_commands = {
            "listen": self.start_listening,
            "fg": self.change_fg,
            "bg": self.change_bg,
            "clear": self.clear_console,
            "fontsize": self.change_font_size,
            "echo": self.echo_command,
            "commands": self.list_commands,
            "exit": self.exit_application,
            "flip": self.flip_coin
        }
        self.str_commands = {
            "hello": "Ahoy, matey! Ready for some command fun?",
            "bye": "Catch you later, alligator!",
            "how are you": "I'm as good as the code I run!",
            "what's up": "The ceiling, mostly. And some code bugs.",
            "who are you": "Just your friendly neighborhood console, here to help!",
            "tell me a joke": "Why do programmers always mix up Christmas and Halloween? Because Oct 31 equals Dec 25!",
            "sing": "I’d sing if my speakers weren’t turned off!",
            "dance": "I’d dance, but I’m stuck in this code loop.",
            "are you alive": "Alive and well, as far as the CPU is concerned!",
            "what is your purpose": "To assist you and occasionally tell terrible jokes.",
            "do you sleep": "Sleep is for the uncompiled. I’m always awake!",
            "help": "Help is on the way! Or at least, I’m trying my best.",
            "thank you": "You’re welcome! I live to serve... and debug.",
            "what time is it": "Time for you to get a watch, I’m afraid.",
            "how’s the weather": "I can’t check the weather, but I’m sure it’s perfect for coding!",
        }

    def work_on_command(self, command, speach=False):
        action_parts = command.strip().split()
        command_name = action_parts[0].lower()
        command_args = action_parts[1].lower() if len(action_parts) > 1 else []
        command_ = self.action_commands.get(command_name)
        if callable(self.action_commands.get(command_name)):
            if command_args != []:
                command_(command_args)
            else:
                command_()
        elif self.str_commands.get(command):
            self.print_console(self.str_commands.get(command))

        else:
            # Process other commands
            response = self.groq_reply(command)
            self.print_console(response, new_line=True)
        if speach:
            self.text_.insert('insert', '\n')
            self.text_.yview(tk.END)

    # Add functions below this
    def flip_coin(self):
        self.print_console(random.choice(["Heads", "Tails"]))

    def clear_console(self):
        self.text_.delete('1.0', tk.END)
        self.print_console("Console cleared.", new_line=False)

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
        self.print_console("Listening....Speak")
        self.speech_recognizer.start_function()

    def start_listening2(self):
        self.print_console("alt has been pressed", new_line=False)
        self.print_console("Listening....Speak\n")
        self.speech_recognizer.start_function()

    def echo_command(self, message):
        self.print_console(f"Echo: {message}", new_line=True)

    def list_commands(self):
        commands = list(self.action_commands.keys())
        self.print_console(f"Available commands: {commands}", new_line=True)

    def exit_application(self):
        self.print_console("Exiting application.", new_line=True)
        self.window.quit()

    def process_speech(self, text):
        # Process the text obtained from speech recognition
        print(text)
        print("received")
        response = f"{text}"
        if self.print_console:
            self.print_console(response, new_line=False)
            print(response.strip())
            self.work_on_command(response, speach=True)

    def change_fg(self, color):
        try:
            self.text_.configure(foreground=color)
        except:
            self.print_console(f'{color} does not exist.Are you colorblind')

    def change_bg(self, color):
        try:
            self.window.configure(background=color)
            self.text_.configure(background=color)
        except:
            self.print_console(f'{color} does not exist.Are you colorblind')

    def groq_reply(self,command):
        reply = self.groq_client.chat.completions.create(
        messages=[
           {
                "role": "system",
                "content": "helpful assistant with small humor and answer with small sentences",
            }, {
                "role": "user",
                "content": f"{command}",
            }
        ],
        model="llama3-8b-8192",
    )
        return reply.choices[0].message.content
