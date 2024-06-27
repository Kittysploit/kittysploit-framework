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
	
	rhost = OptString("127.0.0.1", "Target IPv4 or IPv6 address")
	rport = OptPort(22, "Target HTTP port", "yes")
	username = OptString("ubuntu", "username", "yes")
	password = OptString("ubuntu", "password", "yes")


	def run(self):
		try:
			ssh_channel = SSHClient()
			ssh_channel.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			ssh_channel.connect(self.rhost, self.rport, self.username, self.password, look_for_keys=False, allow_agent=False)
			return self.sock
		except:
			return False