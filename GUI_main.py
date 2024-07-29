from tkinter import scrolledtext
import tkinter as tk
import keyboard
from speach_recognition import SpeechRecognizer
from process_command import ProcessCommand
import ctypes

def execute_command(event):
    # Get the last line of the text widget
    line_start = text_area.index("insert linestart")
    command = text_area.get(line_start, "insert")

    if command != "":  # preventing from spamming return
        process_command(command)
        # text_area.insert()

        text_area.mark_set('insert', 'end')
        # text_area.insert("insert",">")
        text_area.yview(tk.END)  # Scroll to the end
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


# Processing command in a separate file to prevent cluttering
def process_command(command):
    command_processor.work_on_command(command)
    # print_reply(result)


# Function to Print on the console
def print_reply(result,new_line=True):
    if new_line:
        text_area.insert(tk.END, f'\n>>{wrap_text(result)}')
    else:
        text_area.insert(tk.END, f'>>{wrap_text(result)}')
    # text_area.see('end')


def backspace_trigger(event):
    line_start = text_area.index("insert linestart")
    command = text_area.get(line_start, "insert")
    if command == "":
        return "break"


def close_console(e):
    root.quit()



# Basic tkinter setup
root = tk.Tk()
root.geometry("700x400+1200+20")
root.overrideredirect(True)
root.wm_attributes('-transparentcolor', root['bg'])
ctypes.windll.shcore.SetProcessDpiAwareness(2)
root.tk.call('tk', 'scaling', 2.0)
invisible_ = False
# Text area setup CHATGPT Courier Helvetica Calibri
text_area = tk.Text(root, wrap=tk.NONE, font=('Calibri', 14,"bold",'italic'),
                    blockcursor=True, background=root["bg"],
                    fg="white", insertbackground="white", bd=0,
                    highlightthickness=0,highlightbackground=root["bg"],highlightcolor=root["bg"])
text_area.pack(expand=True, fill='both', padx=10)
# text_area.insert("insert",">")


text_area.mark_set('insert', 'end')
text_area.bind('<Return>', execute_command)
text_area.bind('<Key>',
               lambda e: 'break' if e.keysym in {'Left', 'Right'} else None)  # Disable navigation keys
text_area.bind('<BackSpace>', backspace_trigger)

text_area.focus_set()
# text_area.tag_configure("margin", lmargin1=20, lmargin2=20, rmargin=20)
# esc to close the window
keyboard.on_press_key(key="esc", callback=close_console)

command_processor = ProcessCommand(callback=print_reply,widget=text_area,root=root)

root.mainloop()
