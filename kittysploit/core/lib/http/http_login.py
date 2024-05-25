from kittysploit.core.framework.base_module import BaseModule
from kittysploit.core.framework.option import OptString
from kittysploit.core.framework.failure import fail, ErrorDescription
from kittysploit.core.base.io import *


class Http_login(BaseModule):

    username = OptString("admin", "A specific username to authenticate as", True)
    password = OptString("admin", "A specific password to authenticate with", True)

    def __init__(self):
        setattr(fail, "LoginFailed", ErrorDescription("Login failed"))
