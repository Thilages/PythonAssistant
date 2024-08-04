import tkinter as tk  # Base tkinter import
from speach_recognition import SpeechRecognizer  # Speech Recognizer
from process_command import ProcessCommand  # File to process commands
import ctypes  # For increasing pixel quality
import pygetwindow as gw  # To make the window stay on top


# This executes when ever the enter is pressed
def execute_command(event):
    # Get the last line of the text widget
    line_start = text_area.index("insert linestart")
    command = text_area.get(line_start, "insert")

    if command != "":  # preventing from spamming return
        # Processing command in a separate file to prevent cluttering
        command_processor.work_on_command(command)
        text_area.mark_set('insert', 'end')
        text_area.focus_set()
    else:
        return "break"


# Copied from CHATGPT
def wrap_text(text, limit=50):
    """Wrap text to a specified character limit."""
    wrapped_lines = []
    while len(text) > limit:
        # Find the last space within the limit
        break_point = text.rfind(' ', 0, limit)
        if break_point == -1:  # No space found, break at limit
            break_point = limit
        wrapped_lines.append(text[:break_point])
        text = text[break_point:].lstrip()  # Remove leading spaces from the next line
    wrapped_lines.append(text)  # Add the last part
    return '\n'.join(wrapped_lines)


# Function to Print on the console
def print_reply(result, new_line=True):
    if new_line:
        text_area.insert(tk.END, f'\n>>{wrap_text(result)}')
    else:
        text_area.insert(tk.END, f'>>{wrap_text(result)}')


# Preventing from spamming backspace
def backspace_trigger(event):
    line_start = text_area.index("insert linestart")
    command = text_area.get(line_start, "insert")
    if command == "":
        return "break"


def keep_on_top():
    windows = gw.getWindowsWithTitle("My Console")
    if windows:
        window = windows[0]
        window.activate()
        text_area.focus_set()
    else:
        print("Window not found. Retrying...")
    root.after(1000, keep_on_top)


def focus_text_area():
    text_area.focus_set()


# Basic tkinter setup
root = tk.Tk()
root.title("My Console")
root.geometry("700x400+1200+20")
root.overrideredirect(True)
root.wm_attributes('-transparentcolor', root['bg'])
ctypes.windll.shcore.SetProcessDpiAwareness(2)
root.tk.call('tk', 'scaling', 2.0)
root.attributes("-topmost", True)

# Text area setup CHATGPT Courier Helvetica Calibri
text_area = tk.Text(root, wrap=tk.NONE, font=('Calibri', 14, "bold", 'italic'),
                    blockcursor=True, background=root["bg"],
                    fg="white", insertbackground="white", bd=0,
                    highlightthickness=0, highlightbackground=root["bg"], highlightcolor=root["bg"])
text_area.pack(expand=True, fill='both', padx=10)

text_area.mark_set('insert', 'end')
text_area.bind('<Return>', execute_command)
# text_area.bind('<Key>',
               # lambda e: 'break' if e.keysym in {'Left', 'Right'} else focus_text_area())  # Disable navigation keys
text_area.bind('<BackSpace>', backspace_trigger)
root.bind('<Button-1>', focus_text_area)
text_area.focus_set()

keep_on_top()

command_processor = ProcessCommand(callback=print_reply, widget=text_area, root=root)

root.mainloop()
