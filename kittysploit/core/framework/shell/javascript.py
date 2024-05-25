from kittysploit.core.framework.shell.base_shell import Base_shell
from kittysploit.core.base.io import print_info, print_error, input_info
from kittysploit.core.framework.browser_server.base_browser_server import sio
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.shortcuts import prompt, CompleteStyle
from prompt_toolkit.patch_stdout import patch_stdout


class Javascript(Base_shell):

    def prompt(self):
        return f"(javascript){self.host} > "

    def interactive(self):
        self.banner()
        help_commands = ["help", "exit", "info"]
        print_info("Commands: " + ", ".join(help_commands))
        completer = WordCompleter(help_commands, ignore_case=True)
        history = InMemoryHistory()
        while True:
            with patch_stdout():
                command = prompt(
                    "javascript> ",
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
                    print_info("\tHelp menu javascript session")
                    print_info("\t----------------------------")
                    print_info("\texit                   exit shell")
                    print_info("\tinfo                   show info")
                    print_info("\thelp                   show help")
                    print_info()
                else:
                    try:
                        self.sessions[int(self.session_id)]
                    except:
                        print_error("Client disconnected")
                        break

                    sio.emit(
                        "issue_task",
                        {"task_id": str(self.session_id), "input": command},
                        room=self.handler,
                        namespace="/remote",
                    )

    def execute(self, cmd, raw=False):
        sio.emit(
            "issue_task",
            {"task_id": int(self.session_id), "input": cmd},
            room=self.handler,
            namespace="/remote",
        )
        return ""
