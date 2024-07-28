import tkinter as tk

class Transparent_entry(tk.Entry):
    def __init__(self, master="root"):
        super().__init__(master)
        self.configure(bg=master["bg"],
                       highlightthickness=0,
                       bd=0, width=70,
                       fg="green",
                       font=("Arial", 10),
                       insertbackground="green")


class Themed_label(tk.Label):
    def __init__(self, master="root", font_size="10", **kwargs, ):
        super().__init__(master, **kwargs)
        self.configure(text=">",
                       fg="green",
                       bd=0,
                       background=root["bg"],
                       highlightthickness=0,
                       font=("Arial", font_size))

class CustomConsole:
    def __init__(self, root):
        self.root = root
        self.setup_ui()

    def setup_ui(self):
        self.root.title("Custom Console")
        self.root.geometry("700x400+800+0")
        self.root.overrideredirect(True)
        self.root.wm_attributes('-transparentcolor', self.root['bg'])  # Set background color to black

        # Create the text area widget for console output and input
        self.text_area = tk.Text(self.root, wrap=tk.NONE, font=('', 14, 'bold'), blockcursor=True, background=self.root["bg"], fg="white", insertbackground="white", bd=0)
        self.text_area.pack(expand=True, fill='both')
        self.text_area.tag_configure('highlight', foreground="green")
        self.text_area.insert(tk.END, '\n                                  WELCOME MOTHER *****\n\n')
        self.text_area.mark_set('insert', 'end')

        self.text_area.bind('<Return>', self.execute_command)
        self.text_area.bind('<Key>', self.handle_key_event)
        self.text_area.focus_set()

    def execute_command(self, event):
        # Get the command from the current line where the cursor is
        line_start = self.text_area.index("insert linestart")
        command = self.text_area.get(line_start, "insert")

        self.process_command(command)

        # Reinsert the prompt after the command output
        self.text_area.mark_set('insert', 'end')
        self.text_area.yview(tk.END)  # Scroll to the end
        self.text_area.focus_set()

    def process_command(self, command):
        if command.strip() == 'hello':
            self.text_area.insert(tk.END, '\nHello, world!')
        else:
            self.text_area.insert(tk.END, f'\nUnknown command: {command}')

    def handle_key_event(self, event):
        if event.keysym in {'Left', 'Right', 'Up', 'Down'}:
            return 'break'  # Disable navigation keys

def main():
    root = tk.Tk()
    console = CustomConsole(root)
    root.mainloop()

if __name__ == "__main__":
    main()
