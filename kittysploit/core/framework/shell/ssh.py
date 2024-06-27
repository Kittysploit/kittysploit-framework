from kittysploit.core.framework.shell.base_shell import Base_shell
from kittysploit.core.base.io import print_info, print_error, input_info
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.shortcuts import prompt, CompleteStyle
from prompt_toolkit.patch_stdout import patch_stdout
import time
import termios
import os, sys
import tty
import socket
if os.name == 'posix':
    import select
if os.name == 'nt':
    import msvcrt

class Ssh(Base_shell):

    def prompt(self):
        return f"(ssh){self.host} > "

    def interactive(self):
        self.banner()
        help_commands = ["help", "exit", "info"]
        print_info("Commands: " + ", ".join(help_commands))
        completer = WordCompleter(help_commands, ignore_case=True)
        history = InMemoryHistory()
        current_dir = "~"
        while True:
            with patch_stdout():
                command = prompt(
                    f"{current_dir}> ",
                    completer=completer,
                    complete_in_thread=True,
                    complete_while_typing=True,
                    complete_style=CompleteStyle.READLINE_LIKE,
                    history=history,
                )
                if not command: 
                    continue
                elif command == "exit": 
                    break
                elif command.startswith('cd'):
                    # Update the current directory
                    path = command.split(' ', 1)[1]
                    if path == '..':
                        current_dir = '/'.join(current_dir.split('/')[:-1])
                        if not current_dir:
                            current_dir = '/'
                    else:
                        if not path.startswith('/'):
                            path = current_dir + '/' + path
                        # Execute cd command to test if the directory exists
                        stdin, stdout, stderr = self.handler.exec_command(f'cd {path} && pwd')
                        new_dir = stdout.read().decode().strip()
                        if new_dir:
                            current_dir = new_dir
                        else:
                            print_info(stderr.read().decode())
                else:
                    stdin, stdout, stderr = self.handler.exec_command(f'cd {current_dir} && {command}')
                    print_info(stdout.read().decode(), end='')
                    print_info(stderr.read().decode(), end='')


    def posix_shell(chan):
        oldtty = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())
            tty.setcbreak(sys.stdin.fileno())
            chan.settimeout(0.0)

            while True:
                r, w, e = select.select([chan, sys.stdin], [], [])
                if chan in r:
                    try:
                        x = chan.recv(1024)
                        if len(x) == 0:
                            print('\r\n*** EOF\r\n')
                            break
                        sys.stdout.write(x.decode())
                        sys.stdout.flush()
                    except socket.timeout:
                        pass
                if sys.stdin in r:
                    x = sys.stdin.read(1)
                    if len(x) == 0:
                        break
                    chan.send(x)
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)

    def windows_shell(chan):
        while True:
            if msvcrt.kbhit():
                x = msvcrt.getch()
                if x == b'\r':
                    x = b'\n'
                chan.send(x)
            if chan.recv_ready():
                x = chan.recv(1024)
                if len(x) == 0:
                    print('\r\n*** EOF\r\n')
                    break
                sys.stdout.write(x.decode('utf-8'))
                sys.stdout.flush()