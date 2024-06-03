from kittysploit.base.version import __version__
from kittysploit.core.base.io import print_error, print_info
import requests
import re
import subprocess
from packaging import version


class Update_framework(object):

    def __init__(self):
        self.local_version = __version__

    def update(self):

        try:
            data = requests.get(
                "https://raw.githubusercontent.com/Kittysploit/kittysploit-framework/main/kittysploit/base/version.py"
            ).content
            if data:
                match = re.search(r'__version__ = "(.*?)"', data.decode("utf-8"))
                if match:
                    remote_version = match.group(1)
                    if version.parse(remote_version) > version.parse(self.local_version):
                        print_info("New version available: {}".format(remote_version))
                        print_info("Updating framework...")
                        subprocess.call(
                            [
                                "pip3",
                                "install",
                                "git+https://github.com/Kittysploit/Kittysploit/kittysploit-framework",
                                "--ignore-installed",
                            ],
                            shell=False,
                        )
                    else:
                        print_info(f"Your version '{self.local_version}' is up to date")
            else:
                print_error("Error connection to server")

        except Exception as e:
            print_error(str(e))
            return
