from kittysploit import *
from paramiko import SSHClient
import paramiko

class Module(Listener):

	__info__ = {
		"name": "Connect to ssh",
        "description": "Connect to ssh server and spawn a command shell",
        "module": "listeners/multi/ssh_client",
		"handler": Handler.BIND,
        "session_type": SessionType.SSH
	}
	
	rhost = OptString("iocrm.be", "Target IPv4 or IPv6 address")
	rport = OptPort(54321, "Target HTTP port", "yes")
	username = OptString("ubuntu", "username", "yes")
	password = OptString("app-systeme-ch13", "password", "yes")


	def run(self):
		try:
			self.sock = SSHClient()
			self.sock.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			self.sock.connect(self.rhost, self.rport, self.username, self.password, look_for_keys=False, allow_agent=False)
			return True
		except:
			return False