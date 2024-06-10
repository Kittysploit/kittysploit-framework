from kittysploit import *
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
import re

class Module(Plugin):

    __info__ = {"name": "default_password", 
         "description": "default_password"
         }

    def __init__(self):

        self.db = TinyDB(
            "data/default_password.json", storage=CachingMiddleware(JSONStorage)
        )

    def run(self, *args, **kwargs):
        
        parser = ModuleArgumentParser(description=self.__doc__, prog="default_password")
        parser.add_argument("-s", dest="search", help="search", type=str)
        if args[0] == "":
            parser.print_help()
            return
        try:
            pargs = parser.parse_args(shlex.split(args[0]))
            if pargs is None:
                return
            else:
                if isinstance(pargs.search, str):

                    requete = Query()
                    results = self.db.search(
                        requete.productvendor.search(pargs.search, flags=re.IGNORECASE)
                    )
                    creds_found = [
                        [
                            result["productvendor"],
                            result["username"],
                            result["password"],
                        ]
                        for result in results
                    ]
                    if creds_found:
                        headers = ["Product", "Username", "Password"]
                        print_info()
                        print_table(headers, *creds_found)
                    else:
                        print_info("No credentials found")

        except:
            pass
