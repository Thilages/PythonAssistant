import tkinter as tk  # Base tkinter import
from speach_recognition import SpeechRecognizer  # Speech Recognizer
from process_command import CommandProcessor  # File to process commands
import ctypes  # For increasing pixel quality
import pygetwindow as gw  # To make the window stay on top


# This executes whenever the Enter key is pressed
def execute_command(event):
    # Get the last line of the text widget
    line_start = text_area.index("insert linestart")
    command = text_area.get(line_start, "insert")

    if command != "":  # Preventing from spamming return
        # Processing command in a separate file to prevent cluttering
        command_processor.execute_command(command)
        text_area.mark_set('insert', 'end')
        text_area.focus_set()
    else:
        return "break"


# Function to wrap text to a specified character limit
def wrap_text(text, limit=55):
    wrapped_lines = []
    while len(text) > limit:
        break_point = text.rfind(' ', 0, limit)
        if break_point == -1:
            break_point = limit
        wrapped_lines.append(text[:break_point])
        text = text[break_point:].lstrip()
    wrapped_lines.append(text)
    return '\n'.join(wrapped_lines)


# Function to print on the console
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
        try:
            window = windows[0]
            window.activate()
        except:
            pass
    else:
        print("Window not found. Retrying...")
    root.after(1000, keep_on_top)


def focus_text_area(e):
    text_area.focus_set()


# Functions to enable window dragging
def start_drag(event):
    global drag_start_x, drag_start_y
    drag_start_x = event.x
    drag_start_y = event.y

def do_drag(event):
    x = root.winfo_pointerx() - drag_start_x
    y = root.winfo_pointery() - drag_start_y
    root.geometry(f"+{x}+{y}")

def stop_drag(event):
    pass  # You can add functionality here if needed


# Basic tkinter setup
root = tk.Tk()
root.title("My Console")
root.geometry("700x1000+1210+10")
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
text_area.bind('<BackSpace>', backspace_trigger)
root.bind('<Button-1>', focus_text_area)
text_area.focus_set()

# Bind dragging functionality
root.bind('<Button-1>', start_drag)
root.bind('<B1-Motion>', do_drag)
root.bind('<ButtonRelease-1>', stop_drag)

keep_on_top()

command_processor = CommandProcessor(console_callback=print_reply, text_widget=text_area, root_window=root)

root.mainloop()
