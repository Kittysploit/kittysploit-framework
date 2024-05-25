from kittysploit.core.framework.base_module import BaseModule
from kittysploit.core.framework.failure import ProcedureError

class Auxiliary(BaseModule):

    TYPE_MODULE = "auxiliary"

    def __init__(self):
        super(Auxiliary, self).__init__()
        self.current_version = 0

    def run(self):
        raise NotImplementedError("You have to define your own 'run' method.")

    def check(self):
        raise NotImplementedError("You have to define your own 'run' method.")

    def default_options(self):
        return False

    def _exploit(self):
        try:
            self.run()
        except ProcedureError as e:
            pass
