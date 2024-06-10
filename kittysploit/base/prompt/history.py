from prompt_toolkit.history import FileHistory
from kittysploit.core.base.config import KittyConfig
from kittysploit.core.utils.function_module import file_exists
import os

class LimitedFileHistory(FileHistory):
    def __init__(self, filename, max_size=200, *args, **kwargs):
        super().__init__(filename, *args, **kwargs)
        self.filename = filename 
        if not file_exists(self.filename):
            os.makedirs(os.path.dirname(self.filename), exist_ok=True)
            with open(self.filename, "w") as f:
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
                self._loaded_strings.pop(0)

        except:
            pass


    def ensure_file_size_limit(self):
        try:
            with open(self.filename, 'r+') as f:
                lines = f.readlines()
                # Calculer le nombre de lignes à garder
                lines_to_keep = self.max_size * 3
                if len(lines) > lines_to_keep:
                    # Conserver uniquement les dernières `lines_to_keep` lignes
                    lines = lines[-lines_to_keep:]
                    f.seek(0)
                    f.writelines(lines)
                    f.truncate()  # Supprimer le reste du fichier
        except FileNotFoundError:
            pass  # Le fichier sera créé lors du premier appel à `store_string`