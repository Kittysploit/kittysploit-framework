import threading
import queue
from colorama import init, Fore, Style
from prompt_toolkit.shortcuts import confirm as cf
from rich.console import Console
from rich.table import Table
import re

# initialize colorama
init()

# initialize message queue
message_queue = queue.Queue()

class display_message(threading.Thread):
    def __init__(self, mode="console"):
        """
        :param mode: The message mode
        """
        super(display_message, self).__init__()
        self.daemon = True
        self.mode = mode

    def run(self) -> None:
        """
        :return: None
        """

        if self.mode == "console":
            while True:
                message = message_queue.get()
                print(*message)
                #update_gui(message)
                message_queue.task_done()



def __cprint(*args, **kwargs) -> None:
    """
    :param args: arguments of print function
    :param kwargs: keyword arguments of print function
    """
    if not kwargs.pop("verbose", True):
        return

#    hook = hook_message(message_queue, args, kwargs)
#    if hook:
#        pass
    else:
        message_queue.put(args)


def color_red(message):
    return f"{Fore.RED}{message}{Style.RESET_ALL}"

def color_green(message):
    return f"{Fore.GREEN}{message}{Style.RESET_ALL}"

def color_blue(message):
    return f"{Fore.BLUE}{message}{Style.RESET_ALL}"

def print_error(*args, **kwargs) -> None:
    """Print error message."""
    colored_message = color_red("[-] ") + " ".join(str(arg) for arg in args)
    __cprint(colored_message, **kwargs)

def print_warning(*args, **kwargs) -> None:
    """Print warning message."""
    colored_message = f"{Fore.LIGHTYELLOW_EX}[!]{Style.RESET_ALL} " + " ".join(
        str(arg) for arg in args
    )
    __cprint(colored_message, **kwargs)

def print_status(*args, **kwargs) -> None:
    """Print status message."""
    colored_message = color_blue("[*] ") + " ".join(str(arg) for arg in args)
    __cprint(colored_message, **kwargs)

def print_success(*args, **kwargs) -> None:
    """Print success message."""
    colored_message = color_green("[+] ") + " ".join(str(arg) for arg in args)
    __cprint(colored_message, **kwargs)

def print_info(*args, **kwargs) -> None:
    """Print info message."""
    __cprint(*args, **kwargs)

def print_table(headers, *args, highlight=None, unique=False,**kwargs) -> None:
    """Print table."""
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    for header in headers:
        table.add_column(header, overflow="fold")

    for row in args:
        formatted_row = []
        for element in row:
            str_element = str(element)
            if highlight:
                for keyword, color in highlight.items():
                    if keyword.lower() in str_element.lower():
                        if unique:
                            str_element = re.sub(f'(?i)\\b{keyword}\\b', f"[{color}]{keyword}[/{color}]", str_element)
                        else:
                            str_element = re.sub(f'(?i){keyword}', f"[{color}]{keyword}[/{color}]", str_element)
            formatted_row.append(str_element)
        table.add_row(*formatted_row)

    console.print(table)


def print_dict(dictionary, *args, **kwargs) -> None:

    for key, value in dictionary.items():
        print_info()
        print_info(key.capitalize())
        if isinstance(value, dict):
            for _key, _value in value.items():
                print_info("\t ", _key.capitalize())
                print_info("\t\t- ", _value)
        
        elif isinstance(value, list):
            for _value in value:
                print_info("\t- ", _value)
        
        elif isinstance(value, str):
            print_info("\t- ", value)


def input_info(message):

    result = input(message)
    return result


def confirm(message):
    answer = cf(message)
    return answer
