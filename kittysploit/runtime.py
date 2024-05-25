import sys
import os, time
from kittysploit.core.database.importer import init_count_modules
from kittysploit.base.kitty_path import base_path
from kittysploit.core.base.io import confirm

major, minor = sys.version_info[0:2]
if major < 3 and minor < 6:
    sys.exit("Sorry, Python < 3.6 is not supported")

config_file_path = os.path.join(base_path(), "config", "config_file.ini")
database_file_path = os.path.join(base_path(), "database", "kittyDatabase.db")

# check if config file exists
if not os.path.exists(config_file_path):
    from kittysploit.core.base.config import create_config_file

    create_config_file()

# check if database exists
if not os.path.exists(database_file_path):
    from kittysploit.core.database.schema import create_db
    from kittysploit.core.database.importer import load_modules, load_plugins
    create_db()
    first_loading = confirm("First starting, would you loaded all modules in database?")
    if first_loading:
        load_modules()
        load_plugins()
        time.sleep(1)
    
def main_console():
    from kittysploit.core.base.console import Console

    init_count_modules()
    console = Console()
    console.start()
