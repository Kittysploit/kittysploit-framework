from kittysploit.core.framework.base_module import BaseModule
from kittysploit.core.framework.option import OptInteger
from kittysploit.core.base.sessions import Sessions
from kittysploit.core.framework.failure import ProcedureError
from kittysploit.core.base.storage import LocalStorage

class Post(BaseModule):
    
    TYPE_MODULE = "post"
    
    session = OptInteger(0, "Session to interact with", required=True)

    def __init__(self):
        super(Post, self).__init__()
        self.local_storage = LocalStorage()

    def default_options(self):
        return False
        
    def run(self):
        raise NotImplementedError("You have to define your own 'run' method.")

    def _exploit(self):
        try:
            self.run()
        except ProcedureError as e:
            pass

    def current_session(self, data):
        self._sessions = self.local_storage.get("sessions")
        s = self._sessions[int(self.session)]
        if data in s.keys():
            return s[data]
        return ""

    def cmd_exec(self, command, output=True, timeout=2):
        current_session = Sessions()
        all_sessions = current_session.get_sessions()
        if int(self.session) in all_sessions:
            result = current_session.execute(self.session, command)
            if output:
                return result