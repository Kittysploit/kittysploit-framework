import sys
import os
from core.base.console import Console
from core.database.importer import init_count_modules

major, minor = sys.version_info[0:2]
if major < 3 and minor < 6:
    sys.exit("Sorry, Python < 3.6 is not supported")

# check if config file exists
if not os.path.exists("config/config_file.ini"):
    from core.base.config import create_config_file

    create_config_file()

if not os.path.exists("database/kittydb.db"):
    from core.database.schema import create_db

    create_db()


init_count_modules()

console = Console()
console.start()
