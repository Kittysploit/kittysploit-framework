from kittysploit.core.base.storage import LocalStorage
from kittysploit.core.framework.shell.javascript import Javascript
from kittysploit.core.framework.shell.shell import Shell
from kittysploit.core.framework.shell.ssh import Ssh
from kittysploit.core.base.io import print_info, print_status
from kittysploit.core.utils.sound import play_and_stop
from kittysploit.core.base.config import KittyConfig

class Sessions:

    def __init__(self):
        """
        :return: None
        """
        self.local_storage = LocalStorage()
        if not self.local_storage.get("sessions"):
            self.local_storage.set("sessions", dict())

    def get_sessions(self) -> dict:
        """
        :return: dict
        """
        return self.local_storage.get("sessions")

    def add_session(
        self,
        session_arch,
        session_os,
        session_version,
        session_shell,
        session_host,
        session_port,
        session_handler,
        session_user="",
        session_listener="",
        session_option={},
    ):

        session_id = 0
        while session_id in self.local_storage.get("sessions") or session_id < len(self.local_storage.get("sessions")):
            session_id += 1

            
        sessions = {
            session_id: {
                "name": "",
                "arch": session_arch,
                "os": session_os,
                "version": session_version,
                "shell": session_shell,
                "host": session_host,
                "port": session_port,
                "handler": session_handler,
                "user": session_user,
                "listener": session_listener,
                "options": session_option,
            }
        }
        config = KittyConfig()
        sound = config.get_config("FRAMEWORK", "session_sound")
        if sound:
            if sound == "True":
                play_and_stop("data/sound/notify.wav", timeout=0.8)

        self.local_storage.update("sessions", sessions)
        return session_id

    def delete_web_session(self, sid):
        sessions = self.local_storage.get("sessions")
        for i in sessions.keys():
            if sessions[i]["handler"] == sid:
                del sessions[i]
                break
    
    def delete_shell_session(self, session_id):
        sessions = self.local_storage.get("sessions")
        try:
            del sessions[session_id]
            return True
        except:
            return False

    def execute(self, session_id, command, raw=False):
        """Execute a command on a session"""
        sessions = self.local_storage.get("sessions")
        session = sessions[int(session_id)]

        if session["shell"] == "javascript":
            javascript = Javascript(session_id)
            output = javascript.execute(command, raw=raw)
            return output
        
        if session["shell"] == "shell":
            shell = Shell(session_id)
            output = shell.execute(command, raw=raw)
            return output

    def interactive(self, session_id):
        sessions = self.local_storage.get("sessions")
        session = sessions[int(session_id)]

        if session["shell"] == "javascript":
            print_info()
            print_info("[+] Session opened")
            javascipt = Javascript(session_id)
            javascipt.interactive()

        if session["shell"] == "shell":
            print_info()
            print_info("[+] Session opened")
            shell = Shell(session_id)
            shell.interactive()
        
        if session["shell"] == "ssh":
            print_info()
            print_info("[+] Session opened")
            ssh = Ssh(session_id)
            ssh.interactive()
    
    def upgrade(self, session_id):
        sessions = self.local_storage.get("sessions")
        session = sessions[int(session_id)]
        
        if session["shell"] == "shell":
            shell = Shell(session_id)
            shell.upgrade()
        else:
            print_status("Impossible to upgrade this session")