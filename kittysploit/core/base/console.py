from prompt_toolkit.shortcuts import prompt, CompleteStyle
from prompt_toolkit.completion import WordCompleter, Completer, Completion
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.history import FileHistory
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import set_title
from kittysploit.base.prompt.corrections import corrections
from kittysploit.base.prompt.history import LimitedFileHistory
from kittysploit.core.base.io import display_message, print_error, print_info
from kittysploit.core.base.commands import All_commands
from kittysploit.core.base.commands_list import GLOBAL_COMMANDS, SUB_COMMANDS
from kittysploit.core.base.exceptions import KittyException
from kittysploit.core.base.config import KittyConfig
from kittysploit.core.base.sessions import Sessions
from kittysploit.core.utils.function_module import (
    module_metadata,
    humanize_path,
    index_modules,
)
from kittysploit.core.misc.logo import kitty_logo
from kittysploit.core.misc.citation import citation
from kittysploit.core.base.storage import LocalStorage
import os
from typing import List, Text
from time import sleep
import random
from colorama import Fore, Style

class BaseCompleter:

    def available_modules_completion(self, text) -> List[str]:
        """Looking for tab completion hints using setup.py entry_points.

        May need optimization in the future!

        :param text: argument of 'use' command
        :return: list of tab completion hints
        """
        all_possible_matches = filter(lambda x: x.startswith(text), self.modules)
        matches = set()
        for match in all_possible_matches:
            head, sep, tail = match[len(text) :].partition(".")
            if not tail:
                sep = ""
            matches.add("".join((text, head, sep)))
        return list(map(humanize_path, matches))

    def complete_doc(self, text, *args, **kwargs):

        libs = []
        for root, dirs, files in os.walk("kittysploit/core/lib"):
            _, package, root = root.rpartition("kittysploit.core.lib.")
            root = root.replace(os.sep, ".")
            files = filter(
                lambda x: not x.startswith("__") and x.endswith(".py"), files
            )
            if root == "lib":
                libs.extend(map(lambda x: "".join(("", os.path.splitext(x)[0])), files))
            else:
                libs.extend(
                    map(lambda x: ".".join((root, os.path.splitext(x)[0])), files)
                )

        if text:
            return [lib for lib in libs if lib.startswith(text)]
        else:
            return libs

    def complete_use(self, text, *args, **kwargs):
        if text:
            return self.available_modules_completion(text)
        else:
            return self.modules

    def complete_show(self, text, *args, **kwargs):
        if text:
            return [command for command in SUB_COMMANDS if command.startswith(text)]
        else:
            return SUB_COMMANDS

    def complete_set(self, text, *args, **kwargs):
        if text:
            return [
                "".join((attr, ""))
                for attr in self.commands.current_module.options
                if attr.startswith(text)
            ]
        else:
            return self.commands.current_module.options


class Console(BaseCompleter):

    def __init__(self):
        super(BaseCompleter, self).__init__()
        display_message("console").start()
        self.my_config = KittyConfig()
        self.commands = All_commands()
        self.history = LimitedFileHistory(os.path.join("kittysploit/log/log_history"))
        self.sessions = Sessions()
        self.modules = index_modules()
        self.local_storage = LocalStorage()
        set_title("KittySploit")

    def prompt(self) -> Text:
        """
        :return: prompt
        """

        my_prompt = self.my_config.get_config("FRAMEWORK", "prompt")
        if not my_prompt:
            my_prompt = "kitty"
        count_sessions = len(self.sessions.get_sessions())
        myprompt = ""
        if self.local_storage.get("hook_prompt"):
            myprompt = self.local_storage.get("hook_prompt")
        if self.commands.current_module:
            metadata = module_metadata(self.commands.current_module)
            module_name = metadata["name"]
            my_prompt = f"[{Fore.GREEN}{str(count_sessions)}{Style.RESET_ALL}]{myprompt}{my_prompt}({Fore.GREEN}{module_name}{Style.RESET_ALL})> "

        else:
            my_prompt = (
                f"[{Fore.GREEN}{str(count_sessions)}{Style.RESET_ALL}]{myprompt}{my_prompt}> "
            )
        return ANSI(my_prompt)

    def parse_command_line(self, line):
        """
        :param line: command line
        :return: command, arguments and keyword arguments"""
        kwargs = dict()
        command, _, arg = line.strip().partition(" ")
        return command, arg.strip(), kwargs

    def get_completions(self, document, complete_event):
        """
        :param document: document
        :param complete_event: event
        :return: completions
        """
        text = document.text
        word_before_cursor = document.get_word_before_cursor()
        if text:
            try:
                cmd, args, _ = self.parse_command_line(text)
                complete_function = getattr(self, "complete_" + cmd)(
                    args
                )  # + word_before_cursor
                for i in complete_function:
                    yield Completion(i, -len(args))
            except:
                for word in GLOBAL_COMMANDS:
                    if word.startswith(word_before_cursor):
                        yield Completion(word + " ", -len(word_before_cursor))
        else:
            for word in GLOBAL_COMMANDS:
                if word.startswith(word_before_cursor):
                    yield Completion(word + " ", -len(word_before_cursor))

    def start(self) -> None:
        self.commands.get_plugins()
        bindings = KeyBindings()

        @bindings.add(" ")
        def _(event):
            """
            When space is pressed, we check the word before the cursor, and
            autocorrect that.
            """
            b = event.app.current_buffer
            w = b.document.get_word_before_cursor()

            if w is not None:
                if w in corrections:
                    b.delete_before_cursor(count=len(w))
                    b.insert_text(corrections[w])

            b.insert_text(" ")

        banner = self.my_config.get_boolean("FRAMEWORK", "show_banner")
        if banner:
            print_info(kitty_logo)
            print_info(random.choice(citation))
            self.commands.execute_command("banner")
        while True:

            try:
                my_command = prompt(
                    self.prompt,
                    history=self.history,
                    completer=self,
                    complete_in_thread=True,
                    complete_while_typing=True,
                    complete_style=CompleteStyle.READLINE_LIKE,
                    refresh_interval=0.5,
                    key_bindings=bindings,
                )
                command, args, kwargs = self.parse_command_line(my_command)
                command = command.lower()
                if not command:
                    continue
                if command in self.commands.plugins:
                    try:
                        load_plugin = __import__(
                            "plugins.{}".format(command), fromlist=["Module"]
                        )
                        plugin = getattr(load_plugin, "Module")()
                        plugin.run(args, **kwargs)
                        continue
                    except SyntaxError as e:
                        print_error(e)
                command_handler = self.commands.get_command_handler(command)
                command_handler(args, **kwargs)
                sleep(0.3)
            except KittyException as e:
                print_error(e)
            except (EOFError, SystemExit):
                break
            except NameError as e:
                print_error(e)
            except KeyboardInterrupt:
                print_error("Interrupted")
                break
            except FileNotFoundError as e:
                print_error(e)
            except:
                print_error("Unknown error")
    
    def process_command(self, command: str):
        command, args, kwargs = self.parse_command_line(command)
        command = command.lower()
        if not command:
            return
        if command in self.commands.plugins:
            try:
                load_plugin = __import__(
                    "plugins.{}".format(command), fromlist=["Module"]
                )
                plugin = getattr(load_plugin, "Module")()
                plugin.run(args, **kwargs)
                return
            except SyntaxError as e:
                print_error(e)
        command_handler = self.commands.get_command_handler(command)
        command_handler(args, **kwargs)
        sleep(0.3)
