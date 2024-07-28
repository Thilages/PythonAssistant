from tkinter import scrolledtext
import tkinter as tk
import keyboard
from speach_recognition import SpeechRecognizer
def execute_command(event):

    line_start = text_area.index("insert linestart")
    command = text_area.get(line_start, "insert")


    if command != "":
        process_command(command)
        text_area.mark_set('insert', 'end')
        text_area.yview(tk.END)  # Scroll to the end
        text_area.focus_set()
    else:
        return "break"
def wrap_text( text, limit=75):
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
def process_command(command):
    commands = {
            'hello': "Hello mother father",
            'clr': None,
            'clear': None,
            'wtf': None,
            '-help': "ASK Me (Thilagesh)",
            'theme':"theme",
            'listen':'listen'
        }

    command = command.lower()
    result = commands.get(command,None)


    if result is None and command in {'clr', 'clear', 'wtf'}:
        text_area.delete("1.0",tk.END)
    elif result == "theme":
        print("trigere")
        root.configure(background="black")
        text_area.configure(background="black")
    elif result == "listen":
        recognizer.start_function()
    elif result == None:
        result = "No such command exists"
        command_result(result)
    else:
        command_result(result)

def command_result(result):
    global text_area
    text_area.insert(tk.END, f'\n{wrap_text(result)}')


    # Create the main window
root = tk.Tk()

root.geometry("700x400+840+0")
root.overrideredirect(True)
root.wm_attributes('-transparentcolor', root['bg'])

recognizer = SpeechRecognizer()
start_recording = recognizer.start_function
# Create the text area widget for console output and input
text_area = tk.Text(root, wrap=tk.NONE, font=('Courier New', 14,'bold'),blockcursor=True,background=root["bg"],fg="white",insertbackground="white",bd=0)

text_area.pack(expand=True, fill='both',padx=10)
text_area.tag_configure('highlight', foreground="green")
text_area.insert(tk.END, '\n')

def backspace_trigger(event):
    line_start = text_area.index("insert linestart")
    command = text_area.get(line_start, "insert")
    if command == "":
        return "break"


text_area.mark_set('insert', 'end')
text_area.bind('<Return>', execute_command)
text_area.bind('<Key>', lambda e: 'break' if e.keysym in {'Left', 'Right', 'Up', 'Down'} else None)  # Disable navigation keys
text_area.bind('<BackSpace>',backspace_trigger)
text_area.focus_set()


recognizer.set_text_widget(text_area)
def quit(e):
    root.quit()
keyboard.on_press_key(key="esc",callback=quit)
keyboard.on_press_key("alt",lambda _:start_recording())
root.mainloop()
