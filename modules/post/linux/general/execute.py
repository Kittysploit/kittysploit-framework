from kittysploit import *

class Module(Post):
    
    __info__ = {
        "name": "Execute command",
        "description": "Execute command",
        "session": SessionType.SHELL
    }
    
    cmd = OptString("ls", "Command to execute", True)
    
    def run(self):
        data = self.cmd_exec(self.cmd)
        print_info(data)