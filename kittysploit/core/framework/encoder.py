from kittysploit.core.framework.base_module import BaseModule
from kittysploit.core.base.io import print_info, print_error, print_status

class Encoder(BaseModule):
    
    TYPE_MODULE = "encoder"

    def __init__(self):
        super(Encoder, self).__init__()    

    def run(self):
        print_error("Encoder module cannot be run")

    def encode(self):
        raise NotImplementedError("You have to define your own 'encode' method.")