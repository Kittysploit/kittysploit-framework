from kittysploit.core.framework.base_module import BaseModule
from kittysploit.core.framework.failure import ProcedureError
from kittysploit.core.framework.option import OptBool, OptString, OptInteger, OptPayload
from kittysploit.core.base.io import print_info, print_error, print_status


class Payload(BaseModule):

    TYPE_MODULE = "payload"

    def generate(self):
        raise NotImplementedError("You have to define your own 'run' method.")

    def _exploit(self):
        print_status("This module is a payload module. Use 'generate' command to generate a payload.")
        return True
