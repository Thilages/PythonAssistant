

class ProcessCommand():
    def get_reply(self,command):
        return self.work_on_command(command)

    def print_reply(self,command,widget):
        output = self.work_on_command(command)
        widget.insert(tk.END,"Fuck you")

    def work_on_command(self,command):
        return "works"