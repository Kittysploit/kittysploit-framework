import platform
from typing import Text
from functools import wraps
import time
import os
import shlex
import requests
from datetime import datetime
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import Terminal256Formatter
from rich.console import Console
import inspect
from kittysploit.core.base.io import (
    print_error,
    print_info,
    print_status,
    print_success,
    print_table,
    input_info,
    print_dict,
    color_green,
)
from kittysploit.core.base.exceptions import KittyException
from kittysploit.core.base.storage import LocalStorage
from kittysploit.core.base.config import KittyConfig
from kittysploit.core.base.sessions import Sessions
from kittysploit.core.base.api import API
from kittysploit.core.base.jobs import Jobs
from kittysploit.core.utils.module_parser import ModuleArgumentParser, MyParserException
from kittysploit.core.utils.function_module import file_exists
from kittysploit.core.utils.pattern import pattern_create, pattern_offset
from kittysploit.core.database.importer import load_modules, load_plugins, clean_modules, init_count_modules
from kittysploit.core.utils.function_module import (
    check_and_load_module,
    module_metadata,
)
from kittysploit.core.database.schema import *
from kittysploit.core.base.assembly.syscall import syscall
from kittysploit.core.base.assembly.architectures import ARCHS
from kittysploit.core.framework.remotescanlauncher.remotescan import RemoteScan
from kittysploit.core.framework.remotescanlauncher.portscan import Scanner
from kittysploit.core.framework.browser_server.main_browser_server import (
    start_browser_server,
)
from kittysploit.core.base.commands_list import GLOBAL_COMMANDS
from kittysploit.base.update_framework import Update_framework
from kittysploit.base.update_cve import Update_cve
from kittysploit.base.version import __version__

console = Console()

def module_required(fn):
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        if not self.current_module:
            print_error("You have to activate any module with 'use' command.")
            return
        return fn(self, *args, **kwargs)

    name = "module_required"
    try:
        wrapper.__decorators__.append(name)
    except AttributeError:
        wrapper.__decorators__ = [name]
    return wrapper


class Base_command:

    def __init__(self):
        self.current_module = None
        self.current_options = None

    @module_required
    def get_opts(self, *args):
        for opt_key in args:
            try:
                opt_description = self.current_module.exploit_attributes[opt_key][2]
                opt_required = str(self.current_module.exploit_attributes[opt_key][1])
                opt_display_value = self.current_module.exploit_attributes[opt_key][0]
                if self.current_module.exploit_attributes[opt_key][3]:
                    continue
            except (KeyError, IndexError, AttributeError):
                pass
            else:
                self.current_options.append(
                    (opt_key, opt_display_value, opt_required, opt_description)
                )
                yield opt_key, opt_display_value, opt_required, opt_description

    @module_required
    def get_opts_advanced(self, *args):
        for opt_key in args:
            try:
                opt_description = self.current_module.exploit_attributes[opt_key][2]
                opt_required = str(self.current_module.exploit_attributes[opt_key][1])
                opt_display_value = self.current_module.exploit_attributes[opt_key][0]
                if self.current_module.exploit_attributes[opt_key][3]:
                    self.current_options.append(
                        (opt_key, opt_display_value, opt_required, opt_description)
                    )
                    yield opt_key, opt_display_value, opt_required, opt_description
            except (KeyError, IndexError, AttributeError):
                pass

    def check_options_required(self, ignore=None) -> bool:
        if ignore is None:
            ignore = []
        missing_required = []
        for option in self.current_module.options:
            if option in ignore:
                continue
            required = self.current_module.exploit_attributes[option][1]
            value = self.current_module.exploit_attributes[option][0]
            if required == True and not value:
                missing_required.append(option)

        if not missing_required:
            return True
        else:
            message = "Missing options: "
            for i in missing_required:
                message += i
                message += " "

            print_error(message)
            print_status("Type: show options")
            return False

    def get_command_handler(self, command) -> callable:
        try:
            command_handler = getattr(self, "command_{}".format(command))
        except AttributeError:
            raise KittyException("Unknown command: '{}'".format(command))
        return command_handler

    def execute_command(self, command, *args, **kwargs) -> None:
        try:
            command_handler = getattr(self, "command_{}".format(command))
            command_handler(args, **kwargs)
        except AttributeError:
            raise KittyException("Unknown command: '{}'".format(command))


class Show_command:

    def _show_info(self, *args, **kwargs) -> None:
        self.command_info()
    
    def _show_all(self, *args, **kwargs) -> None:
        console.print("\nExploits")
        self._show_exploits()
        console.print("\nAuxiliary")
        self._show_auxiliary()
        console.print("\nPost")
        self._show_post()
        console.print("\nBrowser exploits")
        self._show_browser_exploits()
        console.print("\nBrowser auxiliary")
        self._show_browser_auxiliary()
        console.print("\nPayloads")
        self._show_payloads()
        console.print("\nEncoders")
        self._show_encoders()
        console.print("\nPlugins")
        self._show_plugins()
        console.print("\nListeners")
        self._show_listeners()
        console.print("\nBackdoors")
        self._show_backdoors()
        console.print("\nRemotescan")
        self._show_remotescan()
        console.print("\nLocalscan")
        self._show_localscan()
        console.print("\nDev")
        self._show_dev()

    def _show_auxiliary(self, *args, **kwargs) -> None:
        auxiliary = (
            db.query(Modules.name, Modules.rank, Modules.description)
            .filter(Modules.type_module == "auxiliary")
            .filter(Modules.dev_mode == False)
            .all()
        )
        headers = ["Name", "Rank", "Description"]
        print_table(headers, *auxiliary)

    def _show_exploits(self, *args, **kwargs) -> None:
        exploits = (
            db.query(Modules.name, Modules.rank, Modules.description)
            .filter(Modules.type_module == "exploit")
            .filter(Modules.dev_mode == False)
            .all()
        )
        headers = ["Path", "Rank", "Name"]
        print_table(headers, *exploits)

    def _show_post(self, *args, **kwargs) -> None:
        exploits = (
            db.query(Modules.name, Modules.rank, Modules.description)
            .filter(Modules.type_module == "post")
            .filter(Modules.dev_mode == False)
            .all()
        )
        headers = ["Path", "Rank", "Name"]
        print_table(headers, *exploits)

    def _show_payloads(self, *args, **kwargs) -> None:
        payloads = (
            db.query(Modules.name, Modules.rank, Modules.description)
            .filter(Modules.type_module == "payload")
            .filter(Modules.dev_mode == False)
            .all()
        )
        headers = ["Path", "Rank", "Name"]
        print_table(headers, *payloads)

    def _show_encoders(self, *args, **kwargs) -> None:
        encoders = (
            db.query(Modules.name, Modules.rank, Modules.description)
            .filter(Modules.type_module == "encoder")
            .filter(Modules.dev_mode == False)
            .all()
        )
        headers = ["Path", "Rank", "Name"]
        print_table(headers, *encoders)

    def _show_listeners(self, *args, **kwargs) -> None:
        listeners = (
            db.query(Modules.path, Modules.rank, Modules.name)
            .filter(Modules.type_module == "listener")
            .filter(Modules.dev_mode == False)
            .all()
        )
        headers = ["Module", "Rank", "Name"]
        print_table(headers, *listeners)

    def _show_backdoors(self, *args, **kwargs) -> None:
        backdoors = (
            db.query(Modules.path, Modules.rank, Modules.name)
            .filter(Modules.type_module == "backdoor")
            .filter(Modules.dev_mode == False)
            .all()
        )
        headers = ["Module", "Rank", "Name"]
        print_table(headers, *backdoors)

    def _show_remotescan(self, *args, **kwargs) -> None:
        remotescan = (
            db.query(Modules.path, Modules.rank, Modules.name)
            .filter(Modules.type_module == "remotescan")
            .filter(Modules.dev_mode == False)
            .all()
        )
        headers = ["Module", "Rank", "Name"]
        print_table(headers, *remotescan)

    def _show_localscan(self, *args, **kwargs) -> None:
        localscan = (
            db.query(Modules.path, Modules.rank, Modules.name)
            .filter(Modules.type_module == "localscan")
            .filter(Modules.dev_mode == False)
            .all()
        )
        headers = ["Module", "Rank", "Name"]
        print_table(headers, *localscan)

    def _show_browser_auxiliary(self, *args, **kwargs) -> None:
        browser_auxiliary = (
            db.query(Modules.name, Modules.rank, Modules.description)
            .filter(Modules.type_module == "browser_auxiliary")
            .filter(Modules.dev_mode == False)
            .all()
        )
        headers = ["Name", "Rank", "Description"]
        print_table(headers, *browser_auxiliary)

    def _show_browser_exploits(self, *args, **kwargs) -> None:
        browser_exploits = (
            db.query(Modules.name, Modules.rank, Modules.description)
            .filter(Modules.type_module == "browser_exploit")
            .filter(Modules.dev_mode == False)
            .all()
        )
        headers = ["Name", "Rank", "Description"]
        print_table(headers, *browser_exploits)

    def _show_dev(self, *args, **kwargs) -> None:
        dev = (
            db.query(Modules.path, Modules.type_module, Modules.rank, Modules.name)
            .filter(Modules.dev_mode == True)
            .all()
        )
        headers = ["Module", "Type", "Rank", "Name"]
        print_table(headers, *dev)

    def _show_plugins(self, *args, **kwargs) -> None:
        plugins = (
            db.query(Modules.name, Modules.description)
            .filter(Modules.type_module == "plugin")
            .filter(Modules.dev_mode == False)
            .all()
        )
        headers = ["Name", "Description"]
        print_table(headers, *plugins)

    @module_required
    def _show_options(self, *args, **kwargs):
        target_names = ["target", "port", "ssl"]
        target_opts = [
            opt for opt in self.current_module.options if opt in target_names
        ]
        module_opts = [
            opt for opt in self.current_module.options if opt not in target_opts
        ]
        payload_opts = []
        if hasattr(self.current_module, "_payload_options"):
            payload_opts = [
                opt
                for opt in self.current_module.options
                if opt in self.current_module._payload_options
            ]
            module_opts = [opt for opt in module_opts if opt not in payload_opts]
        headers = ["Name", "Current settings", "Required", "Description"]
        if target_opts:
            console.print()
            console.print("Target options:")
            print_table(headers, *self.get_opts(*target_opts))

        if module_opts:
            console.print()
            console.print(f"Module options : [red]{str(self.current_module._module_path)}[/red]")
            print_table(headers, *self.get_opts(*module_opts))

        if payload_opts:
            console.print()
            console.print(
                f"Payload option ([red]{self.current_module._current_payload._Module__info__['name']}[/red]):"
            )
            print_table(headers, *self.get_opts(*payload_opts))

    @module_required
    def _show_advanced(self, *args, **kwargs):

        module_opts = [opt for opt in self.current_module.options]
        headers = ["Name", "Current settings", "Required", "Description"]
        if module_opts:
            console.print()
            console.print("Module options advanced:")
            print_table(headers, *self.get_opts_advanced(*module_opts))
            console.print()

    def get_plugins(self, *args, **kwargs):
        plugins = db.query(Modules).filter(Modules.type_module == "plugin").all()
        for plugin in plugins:
            self.plugins_help[plugin.name] = plugin.description
            self.plugins.append(plugin.name)
            GLOBAL_COMMANDS.append(plugin.name)


class All_commands(Base_command, Show_command):

    global_help = """Global commands:
    help                                       Print this help menu
    use <module>                               Select a module for use
    search <search term>                       Search for appropriate module
    search_cve <cve id>                        Search cve id in database
    banner                                     Print the banner
    load                                       Load a .sc file
    clear                                      Clean screen 
    sleep                                      Do nothing for the specified number of seconds
    tor [-h]                                   Check tor
    myip                                       Show your IP address
    busy_port                                  Show all ports that are in use
    echo <text>                                Print text
    auto_attack [-h]                           Execute auto attack list when session created
    jobs [-h]                                  Display jobs
    sessions [-h]                              Display sessions
    browser_server <port>                      Start browser server for execute javascript   
    scan [-h]                                  Scan port of target
    remotescan [-h]                            Run remotescan on target
    localscan [-h]                             Run localscan on session
    update                                     Update framework
    output                                     List output directory 
    api_session <port>                         Start api for control sessions in remote, default port:8008
    exit                                       Exit kittysploit
    """

    module_workspace = """Workspace commands:
    workspace [-h]                             Manage workspaces
    target [-h]                                Manage targets of workspace
    reset_default_workspace                    Reset a default workspace
    duplicate_workspace <new name>             Duplicate current workspace
    """

    module_creds = """Creds commands:
    creds                                      List all credentials in the database
    """

    module_help = """Module commands:
    run                                        Run the selected module with the given options
    check                                      Check if a given target is vulnerable
    massrun <files with targets>               Run the selected module with the given options on a lot of target
    back                                       Unselect the current module
    set <option name> <option value>           Set an option for the selected module
    show [info|options|version]                Print information, options, or versions if multiple versions exist
    payloads                                   Show available payloads for module selected
    encoders                                   Show available encoders for payload selected	
    version                                    Show all versions if multiple versions exist. For change: set version [number]
    generate [-h]                              Only with payload module, generate a payload with selected format
    """

    module_asm = """Assembly commands:
    archs                                      Show all architecture
    setarch <arch>                             Change architecture
    asm <assembly code>                        Assembly code
    syscall <name>                             Show info of syscall
    disass <raw bytes>                         Disassemble code
    """

    module_developer = """Developer commands:
    edit                                       Edit current module
    cat                                        Show source code of current module
    pyshell                                    Run python shell          
    doc <lib>                                  Show all methods of lib
    new_module                                 Create new module
    pattern_create <number>                    Create pattern              
    pattern_research <pattern>                 Search pattern offset
    ascii                                      Display ascii table
    """

    module_db = """Database commands:
    db_reload                                  Reload all modules in database
    reload                                     Reload current module in database
    update_cve                                 Update last cve	
    db_clean                                   Clean all database
    """
    
    module_config = """Config commands:
    config                                     Show all configuration
    config_set <section> <key> <value>         Set configuration
    """

    def __init__(self):

        self.local_storage = LocalStorage()
        self.current_module = None
        self.current_options = []
        self.my_config = KittyConfig()
        self.sessions = Sessions()
        self.jobs = Jobs()
        self.plugins = []
        self.plugins_help = {}
        self.api = API()
        self.current_arch = "x86"
        self.current_workspace = "default"

    def _prompt_ui(self) -> Text:
        my_prompt = self.my_config.get_config("FRAMEWORK", "prompt")
        if not my_prompt:
            my_prompt = "kitty"
        count_sessions = len(self.sessions.get_sessions())
        return f"[{str(count_sessions)}\] {my_prompt}> "

    def _banner(self) -> Text:
        
        update = Update_framework()
        check_is_update = update.check_update()
        update_banner = ""
        if check_is_update:
            update_banner = f"[{color_green('New update available')}]"    
        banner = f"""

       =[ KittySploit v{__version__} {update_banner}
+ -- --=[ {self.local_storage.get('exploits')} exploits - {self.local_storage.get('auxiliary')} auxiliary - {self.local_storage.get('post')} post
+ -- --=[ {self.local_storage.get('browser_exploits')} browser_exploits - {self.local_storage.get('browser_auxiliary')} browser_auxiliary
+ -- --=[ {self.local_storage.get('payloads')} payloads - {self.local_storage.get('encoders')} encoders - {self.local_storage.get('plugins')} plugins
+ -- --=[ {self.local_storage.get('listeners')} listeners - {self.local_storage.get('backdoors')} backdoors - {self.local_storage.get('bots')} bots
+ -- --=[ {self.local_storage.get('remotescan')} remotescan - {self.local_storage.get('localscan')} localscan
+ -- --=[ {self.local_storage.get('cve')} cve - {self.local_storage.get('dev')} dev\n"""
        return banner

    def command_help(self, *args, **kwargs) -> None:
        """
        :param args: arguments of 'help' command
        :param kwargs: keyword arguments of 'help' command
        :return: None
        """
        print_info()
        print_info(self.global_help)
        print_info(self.module_workspace)
        print_info(self.module_creds)
        print_info(self.module_help)
        print_info(self.module_asm)
        print_info(self.module_developer)
        print_info(self.module_db)
        print_info(self.module_config)
        if len(self.plugins) != 0:
            print_info("Plugins:")
            for i in self.plugins_help:
                space = 43 - len(i)
                print_info("    " + i + " " * int(space) + self.plugins_help[i])
        print_info("\n")

    def command_clear(self, *args, **kwargs) -> None:
        """
        :param args: arguments of 'clear' command
        :param kwargs: keyword arguments of 'clear' command
        :return: None
        """
        os.system("cls" if os.name == "nt" else "clear")

    def command_banner(self, *args, **kwargs) -> None:
        """
        :param args: arguments of 'banner' command
        :param kwargs: keyword arguments of 'banner' command
        :return: None
        """
        print_info(self._banner())

    def command_exit(self, *args, **kwargs) -> None:
        """
        :param args: arguments of 'exit' command
        :param kwargs: keyword arguments of 'exit' command
        :return: None
        """
        self.jobs.exist_jobs()
        raise SystemExit()

    def command_pyshell(self, *args, **kwargs) -> None:
        """
        :param args: arguments of 'pyshell' command
        :param kwargs: keyword arguments of 'pyshell' command
        :return: None
        """
        print_info()
        py_version = platform.python_version()
        print_info(f"Python {py_version} console")
        time.sleep(0.5)
        while True:
            command = input_info(">>> ")
            if "exit" in command or "quit" in command:
                break
            try:
                exec(command)
            except SystemExit:
                return
            except (EOFError, KeyboardInterrupt):
                return
            except Exception as e:
                print_error(str(e))

    def command_echo(self, *args, **kwargs) -> None:
        """
        :param args: arguments of 'echo' command
        :param kwargs: keyword arguments of 'echo' command
        :return: None
        """
        print_info(args[0])

    def command_test(self, *args, **kwargs) -> None:
        headers = ["Name", "Version", "CVE", "Description"]
        print_table(headers, ["name", "version", "cve", "description"])

    def command_db_reload(self, *args, **kwargs) -> None:
        """
        :param args: arguments of 'db_reload' command
        :param kwargs: keyword arguments of 'db_reload' command
        :return: None
        """

        load_modules()
        load_plugins()
        init_count_modules()
        print_status("Database reloaded")
    
    def command_db_clean(self, *args, **kwargs) -> None:
        """
        :param args: arguments of 'db_clean' command
        :param kwargs: keyword arguments of 'db_clean' command
        :return: None
        """
        clean_modules()
        init_count_modules()
        print_status("Database cleaned")
    
    def command_reload(self, *args, **kwargs) -> None:
        """
        :param args: arguments of 'reload' command
        :param kwargs: keyword arguments of 'reload' command
        :return: None
        """
        if self.current_module:
            self.current_module = check_and_load_module(self.current_module._module_path)()
            print_success("Module reloaded")
        else:
            print_error("No module selected")

    @module_required
    def command_cat(self, *args, **kwargs) -> None:
        """
        :param args: arguments of 'cat' command
        :param kwargs: keyword arguments of 'cat' command
        :return: None
        """

        module_source = inspect.getsource(self.current_module.__class__)
        highlighted_code = highlight(module_source, PythonLexer(), Terminal256Formatter())
        print_info()
        print_info(highlighted_code)
        

    def command_use(self, module_path, *args, **kwargs) -> None:
        module_loaded = check_and_load_module(module_path)()
        if module_loaded:
            key_to_check = "name"
            if key_to_check not in module_metadata(module_loaded):
                print_error(
                    f"Module '{module_path}' doesn't have a '{key_to_check}' attribute"
                )
                return
            self.current_module = module_loaded
            self.current_module._module_path = module_path
            defaultOptions = self.current_module.default_options()
            if defaultOptions:
                for key, value in defaultOptions.items():
                    self.command_set(f"{key} {value}")

    @module_required
    def command_check(self, *args, **kwargs) -> None:
        if self.check_options_required():
            try:
                print_status("Checking target ...")
                self.current_module.check()
            except SyntaxError as e:
                print_error(e)
            except AttributeError as e:
                print_error(e)
            except NameError as e:
                print_error(e)
            except KeyboardInterrupt as e:
                print_error(e)
            except ValueError as e:
                print_error(e)

    @module_required
    def command_run(self, *args, **kwargs) -> None:
        if self.check_options_required():
            try:
                print_status("Running module ...")
                self.current_module._exploit()
            except SyntaxError as e:
                print_error(e)
            except AttributeError as e:
                print_error(e)
            except NameError as e:
                print_error(e)
            except KeyboardInterrupt as e:
                print_error(e)
            except ValueError as e:
                print_error(e)
    
    @module_required
    def command_run_background(self, *args, **kwargs) -> None:
        if self.check_options_required():
            if self.current_module.TYPE_MODULE == "listener":
                try:
                    print_status("Running module in background ...")
                    self.current_module._exploit_background()

                except SyntaxError as e:
                    print_error(e)
                except AttributeError as e:
                    print_error(e)
                except NameError as e:
                    print_error(e)
                except KeyboardInterrupt as e:
                    print_error(e)
                except ValueError as e:
                    print_error(e)
            else:
                print_error("This module must be a listener")
            
    
    @module_required
    def command_generate(self, *args, **kwargs) -> None:
        """Generate payload with selected format"""
        if self.current_module.TYPE_MODULE == "payload":
            parser = ModuleArgumentParser(
                description=self.command_generate.__doc__, prog="generate"
            )
            parser.add_argument(
                "-l", action="store_true", dest="list", help="list all formats and encoders available"
            )
            parser.add_argument("-e", dest="encode", help="encode payload")
            parser.add_argument(
                "-f", dest="format", help="format of payload", metavar="<format>"
            )
            try:
                pargs = parser.parse_args(shlex.split(args[0]))
                if args[0] == "":
                    parser.print_help()
                else:
                    if pargs is None:
                        return

            except MyParserException as e:
                print_error(e)            

    def command_show(self, *args, **kwargs):
        sub_command = args[0]
        try:
            getattr(self, "_show_{}".format(sub_command))(*args, **kwargs)
        except AttributeError:
            print_error("Unknown 'show' sub-command '{}'. ".format(sub_command))

    @module_required
    def command_info(self, *args, **kwargs) -> None:
        metadata = module_metadata(self.current_module)
        print_dict(metadata)

    def command_sleep(self, seconds, *args, **kwargs):
        if seconds:
            time.sleep(int(seconds))

    @module_required
    def command_back(self, *args, **kwargs) -> None:
        self.current_module = None

    @module_required
    def command_set(self, *args, **kwargs) -> None:
        key, _, value = args[0].partition(" ")
        if key in self.current_module.options:
            setattr(self.current_module, key, "{}".format(value))
            self.current_module.exploit_attributes[key][0] = value
            print_success("{} => {}".format(key, value))

        else:
            print_error(
                "You can't set option '{}'.\nAvailable options: {}".format(
                    key, self.current_module.options
                )
            )

    def command_update(self, *args, **kwargs) -> None:
        """
        :param args: arguments of 'update' command
        :param kwargs: keyword arguments of 'update' command
        :return: None
        """
        u = Update_framework()
        u.update()
        init_count_modules()

    def command_browser_server(self, *args, **kwargs) -> None:
        """Start server for browser attack"""
        parser = ModuleArgumentParser(
            description = self.command_browser_server.__doc__, prog="browser_server"
        )
        parser.add_argument(
            "-p",
            dest="port",
            help="number of port",
            metavar="<port number>",
            type=int
        )
        
        try:
            pargs = parser.parse_args(shlex.split(args[0]))
            if args[0] == "":
                parser.print_help()
            else:
                if isinstance(pargs.port, int):
                    myip = self.check_ip()
                    # check que le port n'est pas déjà utilisé
                    import socket, errno
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    try:
                        s.bind(("0.0.0.0", int(pargs.port)))
                    except socket.error as e:
                        if e.errno == errno.EADDRINUSE:
                            print_error("Port busy, please select another port")
                            return
                    self.jobs.create_job("Browser server", f":{pargs.port}", start_browser_server, [myip, pargs.port])
                    print_info()
                    print_status("Browser server started")
                    print_status(f"Url: http://0.0.0.0:{pargs.port}")
                    print_status(f"Url: http://{myip}:{pargs.port}")
                    print_info()
        
        except MyParserException as e:
            print_error(e)            

    def command_sessions(self, *args, **kwargs) -> None:
        """Active session manipulation and interaction."""
        parser = ModuleArgumentParser(
            description=self.command_sessions.__doc__, prog="sessions"
        )
        parser.add_argument(
            "-i",
            dest="interact",
            help="pop a shell on a given session",
            metavar="<session_id>",
            type=int,
        )
        parser.add_argument(
            "-k",
            dest="kill",
            help="kill the selected session",
            metavar="<session_id>",
            type=int,
        )
        parser.add_argument(
            "-l", action="store_true", dest="list", help="list all active sessions"
        )
        parser.add_argument(
            "-n",
            nargs=2,
            dest="rename",
            help="rename session",
            metavar=("<session_id>", "<rename>"),
            type=str,
        )
        parser.add_argument(
            "-c",
            dest="check",
            help="check info session (platform, version)",
            metavar=("<session_id>"),
            type=int,
        )
        parser.add_argument(
            "-b",
            dest="bot",
            help="create bot with this session",
            metavar=("<session_id>"),
            type=int,
        )
        parser.add_argument(
            "-u",
            dest="upgrade",
            help="try to upgrade shell",
            metavar=("<session_id>"),
            type=int,
        )
        parser.add_argument(
            "-x",
            nargs=2,
            dest="execute",
            help="execute command on session",
            metavar=("<session_id>", "<cmd>"),
            type=str,
        )

        try:
            pargs = parser.parse_args(shlex.split(args[0]))
            if args[0] == "":
                parser.print_help()
            else:
                if pargs is None:
                    return
                if isinstance(pargs.interact, int):
                    all_sessions = self.sessions.get_sessions()
                    if pargs.interact in all_sessions:
                        self.local_storage.set("in_session", pargs.interact)
                        self.sessions.interactive(pargs.interact)
                    else:
                        print_error("Session doesn't exist")

                if isinstance(pargs.execute, list):
                    all_sessions = self.sessions.get_sessions()
                    if int(pargs.execute[0]) in all_sessions:
                        result = self.sessions.execute(pargs.execute[0], pargs.execute[1])
                        print_info(result)
                    else:
                        print_error("Session doesn't exist")

                if pargs.list:
                    all_sessions = self.sessions.get_sessions()
                    if all_sessions:
                        sessions_data = list()
                        headers = [
                            "Id",
                            "Name",
                            "User",
                            "Os",
                            "Platform",
                            "Version",
                            "Shell",
                            "Host",
                            "Port",
                        ]
                        for session_id in all_sessions.keys():
                            session_name = all_sessions[session_id]["name"]
                            session_user = all_sessions[session_id]["user"]
                            session_platform = all_sessions[session_id]["arch"]
                            session_os = all_sessions[session_id]["os"]
                            session_version = all_sessions[session_id]["version"]
                            session_shell = all_sessions[session_id]["shell"]
                            host = all_sessions[session_id]["host"]
                            port = all_sessions[session_id]["port"]
                            sessions_data.append(
                                (
                                    str(session_id),
                                    session_name,
                                    session_user,
                                    session_os,
                                    session_platform,
                                    session_version,
                                    session_shell,
                                    host,
                                    port,
                                )
                            )
                        console.print("")
                        console.print("Active sessions")
                        print_table(headers, *sessions_data)
                    else:
                        print_info("No active sessions")
                        
                if isinstance(pargs.rename, list):
                    session_id, new_name = pargs.rename.split(" ")
                    all_sessions = self.sessions.get_sessions()
                    if int(session_id) in all_sessions:
                        all_sessions[session_id]['name'] = new_name
                    else:
                        print_error("Session id doesn't exist")

                if isinstance(pargs.kill, int):
                    session_id = pargs.kill
                    all_sessions = self.sessions.get_sessions()
                    if int(session_id) in all_sessions:
                        session_type = all_sessions[session_id]['shell']
                        if session_type == "shell":
                            result = self.sessions.delete_shell_session()
                            if result:
                                try:
                                    all_sessions[session_id]['handler'].close()
                                except:
                                    pass
                                print_success("Session killed")
                            else:
                                print_error("Error for kill session")
                    else:
                        print_error("Session id doesn't exist")
                    
                if isinstance(pargs.upgrade, int):
                    all_sessions = self.sessions.get_sessions()
                    if pargs.upgrade in all_sessions:
                        self.sessions.upgrade(pargs.upgrade)
                
                if isinstance(pargs.bot, int):
                    all_sessions = self.sessions.get_sessions()
                    session_id = pargs.bot
                    if int(session_id) in all_sessions:
                        session_type = all_sessions[session_id]['shell']
                        if session_type != 'javascript':
                            pass
                
        except MyParserException as e:
            print_error(e)

    def command_workspace(self, *args, **kwargs):
        """Select a workspace"""
        parser = ModuleArgumentParser(
            description=self.command_workspace.__doc__, prog="workspace"
        )
        parser.add_argument(
            "-a", dest="add", help="add a new workspace", metavar="<name>", type=str
        )
        parser.add_argument(
            "-d", dest="delete", help="delete wordspace", metavar="<name>", type=str
        )
        parser.add_argument(
            "-l", action="store_true", dest="list", help="list all workspace"
        )
        parser.add_argument(
            "-s", dest="select", help="select workspace", metavar=("<name>"), type=str
        )

        try:
            pargs = parser.parse_args(shlex.split(args[0]))
            if args[0] == "":
                parser.print_help()
            else:
                if pargs is None:
                    return
                if pargs.list:
                    try:
                        all_workspace = db.query(Workspace).all()
                        for workspace in all_workspace:
                            if self.local_storage.get("workspace") == workspace.name:
                                print_success(workspace.name)
                            else:
                                print_status(workspace.name)
                    except:
                        print_error("Error in workspace list")
                        
                if isinstance(pargs.add, str):
                    try:
                        check = (
                            db.query(Workspace)
                            .filter(Workspace.name == pargs.add)
                            .first()
                        )
                        if check:
                            print_error("Workspace already exist")
                        else:
                            try:
                                new_workspace = Workspace(pargs.add)
                                db.add(new_workspace)
                                db.commit()
                                print_success(f"New workspace created: {pargs.add}")
                            except:
                                print_error("Error with creation")
                    except:
                        print_error("Error with database")

                if isinstance(pargs.delete, str):
                    try:
                        if pargs.delete != "default":
                            delete_workspace = (
                                db.query(Workspace)
                                .filter(Workspace.name == pargs.delete)
                                .first()
                            )
                            if delete_workspace:
                                db.delete(delete_workspace)
                                db.commit()
                                print_success("Workspace deleted")
                            else:
                                print_error("Workspace not found")
                        else:
                            print_error(
                                "You can't delete 'default' workspace but you can: workspace --init"
                            )
                    except:
                        print_error("Error with database")

                if isinstance(pargs.select, str):
                    try:
                        selected = (
                            db.query(Workspace)
                            .filter(Workspace.name == pargs.select)
                            .first()
                        )
                        if selected:
                            self.local_storage.set("workspace", pargs.select)
                            print_success(f"Workspace changed : {pargs.select}")
                        else:
                            print_error("No workspace found")

                    except:
                        print_error("Error with database")

        except MyParserException as e:
            print_error(e)

    def command_target(self, *args, **kwargs):
        """Show target on workspace"""
        parser = ModuleArgumentParser(
            description=self.command_target.__doc__, prog="target"
        )
        parser.add_argument(
            "-a", dest="add", help="add a new target", metavar="<name>", type=str
        )
        parser.add_argument(
            "-d", dest="delete", help="delete target", metavar="<name>", type=str
        )
        parser.add_argument("-l", action="store_true", dest="list", help="list targets")
        try:
            pargs = parser.parse_args(shlex.split(args[0]))
            if args[0] == "":
                parser.print_help()
            else:
                if pargs is None:
                    return

                else:
                    if pargs.list:
                        try:
                            all_targets = (
                                db.query(Workspace_data)
                                .filter(
                                    Workspace_data.name
                                    == self.local_storage.get("workspace"),
                                    Workspace_data.target == True,
                                )
                                .all()
                            )
                            if all_targets:
                                for target in all_targets:
                                    print_info(f"\t [+]{target.ip}")
                            else:
                                print_error("No target in this workspace")
                        except:
                            pass
                    if isinstance(pargs.add, str):
                        try:
                            add_target = Workspace_data(
                                name=self.local_storage.get("workspace"),
                                target=True,
                                ip=pargs.add,
                            )
                            db.add(add_target)
                            db.commit()
                            print_success("New target add")
                        except:
                            print_error("Error in database")

                    if isinstance(pargs.delete, str):
                        try:
                            delete_target = (
                                db.query(Workspace_data)
                                .filter(Workspace_data.ip == pargs.delete)
                                .all()
                            )
                            for i in delete_target:
                                db.delete(i)
                            db.commit()
                            print_success("Target deleted")
                        except:
                            print_error("Error in database")
        except MyParserException as e:
            print_error(e)

    def command_api_session(self, *args, **kwargs):
        """Start api for control session in remote."""
        parser = ModuleArgumentParser(
            description=self.command_api_session.__doc__, prog="api_session"
        )
        parser.add_argument(
            "-p",
            dest="port",
            help="start api at port",
            metavar="<port>",
            type=int,
            default=8008,
        )
        try:
            pargs = parser.parse_args(shlex.split(args[0]))
            if args[0] == "":
                parser.print_help()
            else:
                if pargs is None:
                    return
                if pargs.port:
                    user = self.my_config.get_config("API", "username")
                    if not user:
                        user = "kitty"
                    password = self.my_config.get_config("API", "password")
                    if not password:
                        password = "kitty"
                    self.jobs.create_job(
                        "Rest api", f":{pargs.port}", self.api.run, [pargs.port]
                    )
                    print_success(f"Rest api started at :{pargs.port}")
                    print_status(f"Username: {user}")
                    print_status(f"Password: {password}")
        except MyParserException as e:
            print_error(e)

    def command_update_cve(self, *args, **kwargs):
        cve = Update_cve()
        cve.check_for_update()
        init_count_modules()

    def command_reset_default_workspace(self, *args, **kwargs):

        # Clean remotescan and remotescan_data
        remotescan = (
            db.query(Remotescan).filter(Remotescan.workspace == "default").all()
        )
        for r in remotescan:
            r_data = (
                db.query(Remotescan_data)
                .filter(Remotescan_data.remotescan_id == r.id)
                .all()
            )
            for i in r_data:
                db.delete(i)
            db.delete(r)
        db.commit()

        # Clean localscan and localscan_data
        localscan = db.query(Localscan).filter(Localscan.workspace == "default").all()
        for l in localscan:
            l_data = (
                db.query(Localscan_data)
                .filter(Localscan_data.remotescan_id == l.id)
                .all()
            )
            for i in l_data:
                db.delete(i)
            db.delete(l)
        db.commit()

        # Clean workspace data
        workspace_data = (
            db.query(Workspace_data).filter(Workspace_data.name == "default").all()
        )
        for w in workspace_data:
            db.delete(w)
        db.commit()
        print_status("Clean done!")
    
    def command_duplicate_workspace(self, *args, **kwargs):
        new_name = args[0]
        try:
            check = (
                db.query(Workspace)
                .filter(Workspace.name == new_name)
                .first()
            )
            if check:
                print_error("Workspace already exist")
            else:
                try:
                    new_workspace = Workspace(new_name)
                    db.add(new_workspace)
                    db.commit()
                    print_success(f"New workspace created: {new_name}")
                except:
                    print_error("Error with creation")
                    return 
        except:
            print_error("Error with database")
            return
        
        try:
            get_data = db.query(Workspace_data).filter(Workspace_data.name == self.current_workspace).all()
            for i in get_data:
                new_data = Workspace_data(name=i.name,
                                    target=i.target,
                                    ip=i.ip,
                                    port=i.port)
                db.session.add(new_data)
                db.session.commit()
            print_success("Duplication done!")
        except:
            print_error("Error with duplication")

    def command_doc(self, lib, *args, **kwargs):
        if lib:
            classname = lib.split(".")[-1].capitalize()
            try:
                base_module = __import__(
                    lib, fromlist=["BaseModule"]
                )
            except:
                print_error("Lib not found")
                return
            all_class_base_module = getattr(base_module, "BaseModule")
            function_basemodule = []
            for function_found in dir(all_class_base_module):
                if not function_found.startswith("__") or not function_found.startswith("_"):
                    function_basemodule.append(function_found)
            try:
                lib_called = __import__(lib, fromlist=[classname])
            except IndentationError as e:
                print_error(e)
                return
            except ModuleNotFoundError as e:
                print_error(e)
                return
            try:
                lib_loaded = getattr(lib_called, classname)()
            except AttributeError as e:
                print_error(e)
                return
            for i in dir(lib_loaded):
                if not i.startswith("__") or not i.startswith("_"):
                    if i not in function_basemodule:
                        try:
                            my_function = getattr(lib_loaded, i)
                            if callable(my_function):
                                print_success(i)
                                print_info(f"\t- {my_function.__doc__}")
                        except:
                            continue

    def command_jobs(self, *args, **kwargs):
        """Active jobs manipulation and interaction."""
        parser = ModuleArgumentParser(
            description=self.command_jobs.__doc__, prog="jobs"
        )
        parser.add_argument(
            "-k", dest="kill", help="kill a job", metavar="<job_id>", type=int
        )
        parser.add_argument(
            "-l", action="store_true", dest="list", help="list all active jobs"
        )
        try:
            pargs = parser.parse_args(shlex.split(args[0]))
            if args[0] == "":
                parser.print_help()
            else:
                if pargs.list:
                    jobs_data = list()
                    headers = ["ID", "Name", "Info"]
                    jobs = self.local_storage.get("jobs")
                    if jobs:
                        for job_id in jobs.keys():
                            jobs_data.append(
                                (
                                    str(job_id),
                                    jobs[job_id]["job_name"],
                                    jobs[job_id]["module_name"],
                                )
                            )

                        console.print("")
                        console.print("Active jobs")
                        print_table(headers, *jobs_data)
                    else:
                        print_error("No active jobs")

                if isinstance(pargs.kill, int):
                    self.jobs.delete_job(pargs.kill)
                    print_success("Job killed")

        except MyParserException as e:
            print_error(e)

    def command_remotescan(self, *args, **kwargs):
        """Execute scan for detect remote vulns"""
        parser = ModuleArgumentParser(description=self.command_remotescan.__doc__, prog="remotescan")
        parser.add_argument("-t", dest="target", help="run remotescan with target", metavar="<target>")
        parser.add_argument("-l", action="store_true", dest="list", help="show list of all scan on this workspace",)
        parser.add_argument("-i", dest="info", help="show result on a target", metavar="<id>", type=int)
        parser.add_argument("-d", dest="delete", help="delete result", metavar="<id>")
        parser.add_argument("-n", dest="number", help="number of threads, default: 32", metavar="<number>", type=int)
        parser.add_argument("-p", dest="protocol", help="don't scan port and run module in selected port with protocol e.g: -p 2222:ssh,443:https,8888:https", metavar="<port:protocol>")
        parser.add_argument("-r", dest="report", help="create a pdf report", metavar="<id>")
        try:
            pargs = parser.parse_args(shlex.split(args[0]))
            if args[0] == "":
                parser.print_help()
                return
            else:
                if pargs is None:
                    return
                
                if isinstance(pargs.target, str):
                    threads_number = 32
                    if isinstance(pargs.number, int):
                        threads_number = pargs.number
                    print_success("Remote Scan start...")
                    remotescan = RemoteScan(pargs.target, threads_number, "default")
                    print_status("Scan target port...")
                    ports = remotescan.scan_target()
                    if ports:
                        for port in ports:
                            print_info(f"\tPort {port} open")
                    print_success("Loading modules...")
                    number = remotescan.get_all_modules()
                    print_success(f"{number} modules found")
                    remotescan.run()

                if pargs.list:
                    all_remotescan = (
                        db.query(Remotescan)
                        .filter(Remotescan.workspace == "default")
                        .all()
                    )
                    if all_remotescan:
                        all_remotescan = [(r.id, r.target, r.workspace, r.status,) for r in all_remotescan]
                        print_table(["Id", "Target", "workspace", "Info"], *all_remotescan)
                    else:
                        print_error("No scan in this workspace")
                
                if isinstance(pargs.info, int):
                    try:
                        data = (
                            db.query(Remotescan_data.port, Remotescan_data.name, Remotescan_data.cve, Remotescan_data.info, Remotescan_data.modules)
                            .filter(Remotescan_data.remotescan_id == pargs.info)
                            .all()
                        )
                        if data:
                            headers= ['Port', 'Name', 'Cve', 'Info', 'Module']
                            print_table(headers, *data)

                        else:
                            print_error("No result")
                    except:
                        print_error("Error with database")

        except MyParserException as e:
            print_error(e)

    def command_search_cve(self, cve, *args, **kwargs):
        """Search cve id or keyword in database (cve_id or summary)
            e.g: search_cve 2019-0708; search_cve rdp
        """
        if cve:
            cve_base = cve.lower()
            cve = f"%{cve_base}%"  # for search in database
            cve_data = (
                db.query(Cve.cve_id, Cve.summary, Cve.cvss2, Cve.cvss3)
                .filter(Cve.cve_id.like(cve) | Cve.summary.like(cve))
                .all()
            )
            if cve_data:
                headers = ["Cve_id", "Description", "Cvss2", "Cvss3"]
                print_table(headers, *cve_data, highlight={cve_base: "red"})
            else:
                print_error("No cve found")
    
    def command_search(self, search, *args, **kwargs):
        """Search for appropriate module"""
        if search:
            search_base = search.lower()
            search = f"%{search}%"
            search_data = (
                db.query(Modules.path, Modules.description)
                .filter(Modules.name.like(search) | Modules.description.like(search))
                .all()
            )
            if search_data:
                headers = ["Path", "Description"]
                print_table(headers, *search_data, highlight={search_base: "red"})
            else:
                print_error("No module found")
    
    def command_load(self, file, *args, **kwargs):
        """Load a .sc file"""
        try:
            with open(f"scripts/{file}.sc", "r") as f:
                for line in f:
                    try:
                        self.execute_command(line.strip())
                    except KittyException as e:
                        print_error(e)
        except FileNotFoundError as e:
            print_error(e)
    
    
    def command_tor(self, *args, **kwargs):
        """Check tor connection"""
        parser = ModuleArgumentParser(description=self.command_tor.__doc__, prog="tor")
        parser.add_argument("-c", "--check", action="store_true", dest="check", help="check tor connection")
        parser.add_argument("-e", "--enable", action="store_true", dest="enable", help="enable tor connection")
        parser.add_argument("-d", "--disable", action="store_true", dest="disable", help="disable tor connection")
        parser.add_argument("-s", "--status", action="store_true", dest="status", help="status of tor in config file")
        try:
            pargs = parser.parse_args(shlex.split(args[0]))
            if args[0] == "":
                parser.print_help()
            else:
                if pargs.check:
                    import requests
                    my_config = KittyConfig()
                    host = my_config.get_config("TOR", "host")
                    port = my_config.get_config("TOR", "port")
                    if not host:
                        host = "127.0.0.1"
                    if not port:
                        port = 9050
                    
                    try:
                        proxies = {
                            'http': f'socks5h://{host}:{port}',
                            'https': f'socks5h://{host}:{port}'
                        }
                        print_status("Checking tor ...")
                        tor = requests.get("https://check.torproject.org/", proxies=proxies, timeout=15)
                        if "Congratulations. This browser is configured to use Tor." in tor.text:
                            print_success("Tor is working")
                        else:
                            print_error("Tor is not working")

                    except requests.exceptions.ConnectionError as e:
                        print_error("Tor is not working")
                if pargs.enable:
                    my_config = KittyConfig()
                    my_config.modify_config("TOR", "enable", "True")
                    print_success("Tor enabled")
                
                if pargs.disable:
                    my_config = KittyConfig()
                    my_config.modify_config("TOR", "enable", "False")
                    print_success("Tor disabled")
                
                if pargs.status:
                    my_config = KittyConfig()
                    tor = my_config.get_config("TOR", "enable")
                    if tor == "True":
                        print_success("Tor is enabled in config file")
                    else:
                        print_error("Tor is disabled in config file")
                
        except MyParserException as e:
            print_error(e)
    
    def command_config(self, *args, **kwargs):
        # display all configuration file
        my_config = KittyConfig()
        my_config.print_config()
    
    def command_config_set(self, *args, **kwargs):
        # set configuration
        my_config = KittyConfig()
        data = args[0].split(" ")
        section = data[0]
        key = data[1]
        value = data[2]
        done = my_config.modify_config(section, key, value)
        if done:
            print_success(f"Set: {section} {key} {value}")
        else:
            print_error("Error with set configuration")
    
    def command_busy_port(self, *args, **kwargs):
        # show all ports that are in use
        ports = self.get_busy_ports()
        if ports:
            print_table(["Busy port"], *ports)
        else:
            print_error("No port in use")
    
    def get_busy_ports(self):
        # get all ports that are in use
        import socket
        ports = []
        for port in range(1, 65535):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(("127.0.0.1", port))
            if result == 0:
                ports.append((port,))
            sock.close()
        return ports
    
    @module_required
    def command_edit(self, *args, **kwargs):
        from prompt_toolkit import PromptSession
        from prompt_toolkit.shortcuts import confirm
        from prompt_toolkit.lexers import PygmentsLexer
        from prompt_toolkit.key_binding import KeyBindings
        from pygments.lexers.python import PythonLexer
        
        bindings = KeyBindings()

        # When you press Ctrl+D
        @bindings.add("c-d")
        def _(event):
            
            event.app.exit(result=session.default_buffer.document.text)

        session = PromptSession(lexer=PygmentsLexer(PythonLexer), key_bindings=bindings)

        # Read the current module code
        with open("modules/"+self.current_module._module_path+".py", 'r') as file:
            code = file.read()

        # Edit the code
        new_code = session.prompt("Edit the code (press Ctrl+D when done):\n", multiline=True, default=code)

        # Ask for confirmation before saving
        if confirm("Do you want to save the changes?"):
            with open("modules/"+self.current_module._module_path+".py", 'w') as file:
                file.write(new_code)
    
    
    def command_history(self, *args, **kwargs):
        import re
        # read history file
        if file_exists("kittysploit/log/history.log"):
            with open("kittysploit/log/history.log", "r") as f:
                for line in f:
                    if re.match(r'^\+', line):
                        print_info(line.strip())
        else:
            print_error("No history found")
    
    def command_sound(self, *args, **kwargs):
        from kittysploit.core.utils.sound import play_sound
        play_sound("data/sound/sound.wav")
    
    def command_scan(self, *args, **kwargs):
        # scan port of target
        parser = ModuleArgumentParser(description=self.command_scan.__doc__, prog="scan")
        parser.add_argument("-t", dest="target", help="scan port of target", metavar="<target>")
        parser.add_argument("-p", dest="port", help="port to scan", metavar="<port>", default="20-1024")
        try:
            pargs = parser.parse_args(shlex.split(args[0]))
            if args[0] == "":
                parser.print_help()
                return
            if pargs.target:
                scan = Scanner(pargs.target, pargs.port, workspace="default")
                print_status("Scanning port ...")
                port_found = scan.scan()
                rows = [(port,) for port in port_found]
                print_table([f"Port open for {pargs.target}"], *rows)                
                
        except MyParserException as e:
            print_error(e)

    def command_pattern_create(self, number, *args, **kwargs):
        if number.isdigit():
            result = pattern_create(number)
            print_info(result)            
        else:
            print_error("Number is required! e.g: pattern_create 100")
    
    def command_pattern_offset(self, pattern, *args, **kwargs):
        if pattern:
            result = pattern_offset(pattern)
            print_status("Offset found: ",result)
        else:
            print_error("Pattern is required! e.g: pattern_offset Aa0A")
    
    def command_ascii(self, *args, **kwargs):
        from rich.table import Table

    	# Create a console
        console = Console()

        # Create a table
        table = Table(show_header=True, header_style="bold magenta")
        for i in range(4):
            table.add_column(f"Dec {i+1}", style="red")
            table.add_column(f"Hex {i+1}", style="green")
            table.add_column(f"Char {i+1}")

        # Add rows to the table
        for i in range(32):  # 15 rows
            row = []
            for j in range(4):  # 6 columns
                index = i + j * 32
                if index < 128:
                    if index == 26 or index == 27 or index == 10:
                        row.extend([str(index), hex(index), ""])
                    else:
                        row.extend([str(index), hex(index), chr(index)])
                else:
                    row.extend(['', '', ''])
            table.add_row(*row)

        # Print the table
        console.print(table)
    
    def command_new_module(self, *args, **kwargs) -> None:
        """Create a basic new module"""
        parser = ModuleArgumentParser(
            description=self.command_new_module.__doc__, prog="new_module"
        )
        parser.add_argument(
            "-n", 
            dest="name", 
            help="name of new module", 
            metavar="<name>",
            type=str,
        )
        parser.add_argument(
            "-t",
            dest="type_module",
            help="type of new module",
            metavar="<type_module>",
            type=str,
        )
        parser.add_argument(
            "-s",
            dest="show",
            help="show all type of module",
            action="store_true"
        )
        try:
            if args[0] == "":
                parser.print_help()
                return
            else:
                pargs = parser.parse_args(shlex.split(args[0]))
                if isinstance(pargs.name, str) and isinstance(pargs.type_module, str):
                    new_module = self.create_module(pargs.name, pargs.type_module)
                else:
                    print_error("Missing args, must be: new_module -n test -t auxiliary")
                if pargs.show:
                    header = ["Type of modules"]
                    content = [("exploit",),("auxiliary",)]
                    print_table(header, *content)
                                
        except MyParserException as e:
            print_error(e)
        
    def command_myip(self, *args, **kwargs):
        myip = self.check_ip()
        print_status(f"Your IP address: {myip}")
    
    def check_ip(self):
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP
    
    def create_module(self, name, type_module):
        # create new module
        template = None
        if type_module == "exploit":
            template = "exploit"
        elif type_module == "auxiliary":
            template = "auxiliary"
        elif type_module == "post":
            template = "post"
        elif type_module == "payload":
            template = "payload"
        elif type_module == "browserexploit":
            template = "browserexploit"
        elif type_module == "browserauxiliary":
            template = "browserauxiliary"
        else:
            print_error("Type module not found")
            return

        if template:
            with open(f"kittysploit/core/base/template_modules/{template}.py", "r") as f:
                data = f.read()
                data = data.replace("%MODULE_NAME%", name)

            dev_dir = "modules/dev"
            if not os.path.exists(dev_dir):
                print_status("Create dev directory")
                os.makedirs(dev_dir)

            if not os.path.exists(f"modules/dev/{type_module}_{name}.py"):
                with open(f"modules/dev/{type_module}_{name}.py", "a") as f:
                    f.write(data)
                    print_success(f"New module created: dev/{type_module}_{name}")
                loading = input_info("Do you want to load this module? [y/N]")
                if loading.lower() == "y":
                    self.command_use(f"dev/{type_module}_{name}")
            
            else:
                print_error("Module already exist")
    
    def command_syscall(self, syscall_function, arch=None):
        # show all syscall
        if syscall_function:
            syscall(self.current_arch, syscall_function)
        else:
            print_error("Syscall function is required! e.g: syscall open")

    def command_asm(self, *args, **kwargs):
        from kittysploit.core.base.assembly.assembler import Assembler
        asm = Assembler(self.current_arch)
        result = asm.assemble(code=args[0])
        if result:
            r = ["\\x%.2x" % x for x in result[0]]
            raw = "".join(r)
            hex_string = raw.replace("\\x", "")
            print_status(f"Bytes count: {len(result[0])}")
            print_status(f"Raw bytes: {raw}")
            print_status(f"Hex string: {hex_string}")

    def command_disass(self, *args, **kwargs):
        from kittysploit.core.base.assembly.disassembler import Disassembler
        disass = Disassembler(self.current_arch)
        result = disass.disassemble(code=args[0])
        if result:
            for i in result:
                adress = color_green(f"0x{i[0]:x}")
                print_info(f"\t{adress}:\t{i[1]}\t{i[2]}")
                
    def command_archs(self, *args, **kwargs):
        # show all archs
        archs = ARCHS
        archs_list_of_lists = [[arch] for arch in archs]
        print_table(["Architectures"], *archs_list_of_lists, highlight={self.current_arch: "green"}, unique=True)
        
    def command_arch_set(self, *args, **kwargs):
        # set arch
        if args[0] in ARCHS:
            self.current_arch = args[0]
            print_success(f"Architecture set: {args[0]}")
        else:
            print_error("Architecture not found")
            print_info("Use 'archs' command to show all architectures")
    
    def command_creds(self, *args, **kwargs):
        
        get_creds = db.query(Credentials).all()
        headers = ["Module", "Host", "Username", "Password", "Data"]
        console.print("Credentials")
        print_table(headers, *get_creds)
    
    def command_output(self, *args, **kwargs):
        from datetime import datetime
        if os.path.exists("output"):
            files = []
            for file in os.listdir("output"):
                file_path = os.path.join("output", file)
                creation_time = os.path.getctime(file_path)
                formatted_time = datetime.fromtimestamp(creation_time).strftime('%d-%m-%Y %H:%M:%S')
                file_type = "Folder" if os.path.isdir(file_path) else "File"
                files.append((file, formatted_time, file_type))
            print_table(["File", "Time creation", "Type"], *files)
        else:
            print_error("No output directory")

    @module_required
    def command_payloads(self, *args, **kwargs):
        list_payload = []
        arch = None
        platform = None
        category = None
        info = module_metadata(self.current_module)
        if "arch" in info:
            arch = info['arch']['name']
        if "plarform" in info:
            platform = info['platform']['name']
        if "category" in info['payload']:
            category = info['payload']['payload_cateogry']
        
        db.query(Modules).filter(Modules.type_module=="payload").filter()
#            print()

#    def command_route(self, *args, **kwargs):
#        routes = db.query(Route).all()
#        headers = ["Id", "Destination", "Gateway", "Genmask", "Iface"]
#        if routes:
#            routes_data = [(r.id, r.destination, r.gateway, r.genmask, r.iface) for r in routes]
#            print_table(headers, *routes_data)
#        else:
#            print_error("No route found")
        
#    def command_route_add(self, *args, **kwargs):
        
#        parser = ModuleArgumentParser(description=self.command_route_add.__doc__, prog="route_add")
#        parser.add_argument("-d", dest="destination", help="destination", metavar="<destination>")
#        parser.add_argument("-g", dest="gateway", help="gateway", metavar="<gateway>")
#        parser.add_argument("-m", dest="genmask", help="genmask", metavar="<genmask>")
#        parser.add_argument("-i", dest="iface", help="iface", metavar="<iface>")
#        try:
#            pargs = parser.parse_args(shlex.split(args[0]))
#            if args[0] == "":
#                parser.print_help()
#                return
#            if pargs.destination and pargs.gateway and pargs.genmask and pargs.iface:
#                new_route = Route(destination=pargs.destination, gateway=pargs.gateway, genmask=pargs.genmask, iface=pargs.iface)
#                db.add(new_route)
#                db.commit()
#                print_success("New route added")
#            else:
#                print_error("Missing args")
#        except MyParserException as e:
#            print_error(e)