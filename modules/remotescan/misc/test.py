from kittysploit import *


class Module(RemoteScan):

    __info__ = {
        "name": "Test",
        "description": "Test",
        "cve": "",
        "severity": Severity.INFO,
        "module": "auxiliary/scanner/http/robots",
        "protocol": Protocol.HTTP,
    }

    def run(self):
        return False
