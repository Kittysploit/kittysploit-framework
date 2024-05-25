from kittysploit.core.framework.base_module import BaseModule
from kittysploit.core.framework.option import OptInteger
from kittysploit.core.framework.browser_server.base_browser_server import sio
from kittysploit.core.framework.failure import ProcedureError
from kittysploit.core.base.storage import LocalStorage
from kittysploit.core.base.io import print_error, print_status

class BrowserAuxiliary(BaseModule):

    TYPE_MODULE = "browserauxiliary"
    
    session = OptInteger(0, "Session to interact with", required=True)

    def __init__(self):
        super(BrowserAuxiliary, self).__init__()
        self._handler = None
        
    def run(self):
        raise NotImplementedError("You have to define your own 'run' method.")

    def check(self):
        raise NotImplementedError("You have to define your own 'run' method.")

    def default_options(self):
        return False
    
    def _exploit(self):
        try:
            local_storage = LocalStorage()
            _sessions = local_storage.get("sessions")
            if not self.session in _sessions:
                print_error("Session not found")
                return
            self._handler = _sessions[self.session]["handler"]
            self.run()
            print_status("Task completed")
        except ProcedureError as e:
            pass

    def _execute(self, code):
        """
        :param code: The javascript code
        :return: None
        """
        sio.emit(
            "issue_task",
            {"task_id": int(self.session), "input": code},
            room=self._handler,
            namespace="/remote",
        )
        return ""
    
    def send_js(self, code):
        """
        :param code: The javascript code
        :return: None
        """
        self._execute(code)
    