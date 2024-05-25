from prompt_toolkit.history import FileHistory
from kittysploit.core.base.config import KittyConfig
from kittysploit.core.utils.function_module import file_exists
import os

class LimitedFileHistory(FileHistory):
    def __init__(self, filename, max_size=10, *args, **kwargs):
        super().__init__(filename, *args, **kwargs)
        if not file_exists(filename):
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w") as f:
                f.write("")        
        self.my_config = KittyConfig()
        self.max_size = max_size
        size_history = self.my_config.get_config("FRAMEWORK", "size_file_history")
        if size_history:
            self.max_size = int(size_history)

    def store_string(self, string):
        try:
            super().store_string(string)
            while len(self._loaded_strings) > self.max_size:
                self._loaded_strings.pop(-1)
        except:
            pass
