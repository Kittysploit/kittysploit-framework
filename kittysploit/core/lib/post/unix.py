from kittysploit.core.framework.base_module import BaseModule
from kittysploit.core.lib.post.file import File
from kittysploit.core.base.io import print_error

class Unix(File):
    
	def __init__(self):
		super(File, self).__init__()
	
	def user_exists(self, user) -> bool:

		etc_passwd = ["/etc/passwd","/etc/security/passwd","/etc/master.passwd"]
		for i in etc_passwd:
			etc_file = self.read_file(i)
			if user in etc_file:
				return True
		print_error("User doesn't exist")
		return False
		
