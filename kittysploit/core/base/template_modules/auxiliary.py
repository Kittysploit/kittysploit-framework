from kittysploit import *

class Module(Auxiliary):

    __info__ = {
        "name": "%MODULE_NAME%",
        "description": "my new module",
        "author": ["your_name"],
        "cve": "",
        "rank": Rank.HIGH,
        "platform": Platform.GENERIC,
        "arch": Arch.PHP,
        "disclosure": "DD/MM/YYYY",
        "references": [""],
    }

    def run(self):
        print_success("Module executed")