from kittysploit.core.framework.base_module import BaseModule
from kittysploit.core.base.storage import LocalStorage
from kittysploit.core.base.io import print_success, print_status
from kittysploit.core.base.jobs import Jobs
import threading


class Listener(BaseModule, threading.Thread):

    TYPE_MODULE = "listener"

    def __init__(self):
        super(Listener, self).__init__()
        self.sock = None
        self.stop_flag = threading.Event()
        self.local_storage = LocalStorage()
        self.mute = False

    def run(self):
        raise NotImplementedError("You have to define your own 'send_protocol' method.")

    def _exploit_background(self):
        port = ""
        if "lhost" in self.exploit_attributes:
            port = self.exploit_attributes["lport"][0]
        elif "rhost" in self.exploit_attributes:
            port = self.exploit_attributes["rport"][0]
        if port:
            self.mute = True
            Jobs().create_job("Listener", f":{port}", self._exploit)

    def _exploit(self):
        from kittysploit.core.base.sessions import Sessions

        module = self.run()
        if module:

            self.local_storage.set("session_found", True)

            info = self._Module__info__
            if "handler" in info:
                handler = info["handler"]
                session = Sessions()
                session.add_session(
                    session_arch="",
                    session_os="",
                    session_version="",
                    session_shell=info["session_type"],
                    session_host=module[1],
                    session_port=module[2],
                    session_handler=module[0],
                    session_user="",
                    session_listener=info["module"],
                    session_option=self.exploit_attributes,
                )
            if not self.mute:
                print_success("Session opened")
            return True

        else:
            return False

    def default_options(self):
        return False

    def shutdown(self):
        raise NotImplementedError("Shutdown is not implemented")

    def stop(self):
        print_status("Stopping the listener...")
        self.stop_flag.set()
