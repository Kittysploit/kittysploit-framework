import configparser
from typing import Text
from kittysploit.core.base.io import print_error, print_info
from kittysploit.base.kitty_path import base_path
import os
from rich.console import Console

console = Console()

class KittyConfig:

    def __init__(self):
        """
        :return: None
        """
        self.config = configparser.ConfigParser()

        self.config_file_path = os.path.join(base_path(), "config", "config_file.ini")
        # check if file exists
        if not self.config.read(self.config_file_path):
            print_error("Config file not found")
            exit(1)
        self.config.read(self.config_file_path)

    def save(self):
        """Save the configuration to the file."""
        with open(self.config_file_path, 'w') as configfile:
            self.config.write(configfile)

    def get_config(self, section, param) -> Text:
        """
        :param section: section
        :param param: parameter
        :return: value
        """
        return self.config[section][param]

    def set_config(self, section, param, value) -> None:
        """
        :param section: section
        :param param: parameter
        :param value: value
        :return: None
        """
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config[section][param] = value

    def get_boolean(self, section, param) -> bool:
        """ """
        return self.config.getboolean(section, param)


    def modify_config(self, section, param, value) -> bool:
        """
        :param section: section
        :param param: parameter
        :param value: value
        :return: None
        """
        if not self.config.has_section(section):
            return False
        self.config[section][param] = value
        self.save()
        return True

    def print_config(self):
        """Print the entire configuration."""
        console.print("[bold cyan]Configuration:[/bold cyan]")
        console.print()
        for section in self.config.sections():
            console.print(f"[bold magenta][{section}][/bold magenta]")
            for key in self.config[section]:
                console.print(f"[green]{key:<20}[/green] = [yellow]{self.config[section][key]}[/yellow]")
        console.print()

def create_config_file() -> None:
    """
    create config file for the given configuration section and parameter
    """
    config_file_path = os.path.join(base_path(), "config", "config_file.ini")
    config = configparser.ConfigParser()
    config.add_section("FRAMEWORK")
    config.add_section("UI")
    config.add_section("API")
    config.add_section("TOR")
    config.add_section("WEB")
    config.add_section("REMOTESCAN")
    config["FRAMEWORK"]["prompt"] = "kitty"
    config["FRAMEWORK"]["show_banner"] = "True"
    config["FRAMEWORK"]["load_modules_before_start"] = "True"
    config["FRAMEWORK"]["reset_workspace_before_start"] = "True"
    config["FRAMEWORK"]["size_file_history"] = "10"
    config["UI"]["username"] = "kitty"
    config["UI"]["password"] = "kitty"
    config["API"]["username"] = "kitty"
    config["API"]["password"] = "kitty"
    config["TOR"]["enable"] = "False"
    config["TOR"]["host"] = "127.0.0.1"
    config["TOR"]["port"] = "9050"
    config["WEB"]["cookie"] = "None"
    config["WEB"]["user-agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"
    config["REMOTESCAN"]["user"] = "anonymous"
    config["REMOTESCAN"]["password"] = "anonymous"
    with open(config_file_path, "w") as configfile:
        config.write(configfile)
    configfile.close()
