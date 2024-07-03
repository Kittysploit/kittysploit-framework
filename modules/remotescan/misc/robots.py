from kittysploit import *


class Module(RemoteScan):

    __info__ = {
        "name": "File robots.txt found",
        "description": "File robots.txt found",
        "cve": "",
        "cvssv3": "",
        "severity": Severity.INFO,
        "module": "auxiliary/scanner/http/robots",
        "protocol": Protocol.HTTP,
    }

    def run(self):
        return True
