from kittysploit.core.base.storage import LocalStorage

class Hooking:
    
    def __init__(self):
        self.local_storage = LocalStorage()
    
    def add_prompt(self, text):
        self.local_storage.set("hook_prompt", text)

    def delete_prompt(self):
        self.local_storage.delete("hook_prompt")
    