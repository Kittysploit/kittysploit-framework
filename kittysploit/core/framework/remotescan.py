from kittysploit.core.utils.function_module import pythonize_path
from packaging import version


class RemoteScan(object):

    TYPE_MODULE = "remotescan"

    def __init__(self, target="127.0.0.1", port=0, ssl=False, cache=None):

        self.target = target
        self.port = port
        self.cache = cache
        self.ssl = ssl

    def run(self):
        raise NotImplementedError("You have to define your own 'run' method.")

    def attack(self):
        try:
            return self.run()
        except:
            return False

    def scan_lib(self, libname):
        try:
            path_lib = pythonize_path(libname)
            func = path_lib.split(".")[-1:][0].capitalize()
            load_lib = __import__(f"core.scanlib.{path_lib}", fromlist=[func])
            return getattr(load_lib, func)(self.target, self.port, self.ssl, self.cache)

        except ModuleNotFoundError as e:
            return None
        except Exception as e:
            return None

    def compare_versions(version1, compare, version2):
        v1 = version.parse(version1)
        v2 = version.parse(version2)
        if compare == "<":
            if v1 < v2:
                return True
            return False

        elif compare == ">":
            if v1 > v2:
                return True
            return False

        elif compare == "==":
            if v1 == v2:
                return True
            return False

        elif compare == ">=":
            if v1 >= v2:
                return True
            return False

        elif compare == "<=":
            if v1 <= v2:
                return True
            return False
