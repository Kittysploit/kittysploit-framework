from kittysploit import *
import socket

class Module(Listener):
	__info__ = {
		"name": "Listen shell udp",
		"description": "Connect back to attacker and spawn a command shell",
		"module": "listeners/multi/reverse_udp",
		"handler": Handler.REVERSE,
		"session_type": SessionType.SHELL
	}
	
	lhost = OptString("127.0.0.1", "Target IPv4 or IPv6 address", "yes")
	lport = OptPort(4444, "Target HTTP port", "no")

	def run(self):
		try:
			print_status(f"Start server on {self.lhost}:{self.lport}")
			print_status("Waiting connection...") 
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.sock.bind((self.lhost, self.lport))
			self.sock.listen(5)
			client, address = self.sock.accept()
			return client
		except KeyboardInterrupt:
			return False
		except OSError:
			print_error("Port busy")
			return False

	def shutdown(self):
		try:
			if self.sock:
				self.sock.shutdown(socket.SHUT_RDWR)
				self.sock.close()
		except OSError as e:
			pass