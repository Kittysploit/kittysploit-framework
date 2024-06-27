from kittysploit.core.framework.shell.base_shell import Base_shell
from kittysploit.core.base.io import print_info, print_error
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.shortcuts import prompt, CompleteStyle
from prompt_toolkit.patch_stdout import patch_stdout
import time
import socket
from colorama import Fore, Style
from prompt_toolkit.formatted_text import ANSI


class Shell(Base_shell):

    def prompt(self):
        my_prompt = f"(shell)({Fore.GREEN}{self.host}{Style.RESET_ALL})> "
        return ANSI(my_prompt)
        

    def interactive(self):
        self.banner()
        help_commands = ["help", "exit", "info"]
        print_info("Commands: " + ", ".join(help_commands))
        completer = WordCompleter(help_commands, ignore_case=True)
        history = InMemoryHistory()
        self.handler.settimeout(0.6)
        current_dir = ""
        while True:
            with patch_stdout():
                command = prompt(
                    self.prompt(),
                    completer=completer,
                    complete_in_thread=True,
                    complete_while_typing=True,
                    complete_style=CompleteStyle.READLINE_LIKE,
                    history=history,
                )

                if not self.session:
                    print_error("Client disconnected")
                    break
                elif not command:
                    continue
                elif command == "exit":
                    break
                elif command == "info":
                    print_info()
                    print_info(f"Os: {self.os}")
                    print_info(f"Platform: {self.platform}")
                    print_info(f"Version: {self.version}")
                    print_info()
                elif command == "help":
                    print_info()
                    print_info("\tHelp menu shell session")
                    print_info("\t----------------------------")
                    print_info("\texit                   exit shell")
                    print_info("\tinfo                   show info")
                    print_info("\thelp                   show help")
                    print_info()

                else:
                    cmd = command + '\n'
                    try:
                        self.handler.send(cmd.encode())
                    except Exception as e:
                        print_error(e)
                    time.sleep(0.1)
                    while True:
                        try:
                            data = self.handler.recv(4096)
                            print_info(data.decode(errors="ignore"))
                            if len(data) < 4096:
                                break
                        except socket.timeout:
                            break
    
    def execute(self, cmd, raw=False):
        cmd = cmd + '\n'
        self.handler.settimeout(0.6)
        self.handler.send(cmd.encode())
        time.sleep(0.1)
        full_data = b""
        while True:     
            try:   
                data = self.handler.recv(4096)
                full_data += data
                if len(data) < 4096:
                    break
                    
            except socket.error as e:
                if e.errno in [socket.errno.EWOULDBLOCK, socket.errno.EAGAIN]:
                    time.sleep(0.1)  # Wait briefly before retrying
                else:
                    raise
        return full_data.decode(errors="ignore")
