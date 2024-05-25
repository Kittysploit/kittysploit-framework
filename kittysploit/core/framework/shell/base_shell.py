from kittysploit.core.base.storage import LocalStorage
from kittysploit.core.base.io import print_status, print_info
import sys
import time

class Base_shell:

    def __init__(self, session_id):

        self.local_storage = LocalStorage()
        self.sessions = self.local_storage.get("sessions")
        self.session = self.sessions[int(session_id)]
        self.session_id = int(session_id)
        self.handler = self.session["handler"]
        self.host = self.session["host"]
        self.os = self.session["os"]
        self.platform = self.session["arch"]
        self.version = self.session["version"]
        self.user = self.session["user"]
        self.shell = self.session["shell"]

    def banner(self):

        print_info()
        print_info(f"[*] Shell: {self.shell}")
        print_info(f"[*] Os: {self.os}")
        print_info(f"[*] Platform: {self.platform}")
        print_info(f"[*] Version: {self.version}")
        print_info()

    def interactive(self):
        pass

    def execute(self, cmd, raw=False):
        pass

    def upgrade(self):
        pass

    def close(self):
        pass

    def determinate(self):
        pass

    def session_update(self, key, value):
        try:
            update_session = self.sessions[int(self.session_id)][key] = value
            self.local_storage.update(int(self.session_id), update_session)
            return True
        except:
            return False
