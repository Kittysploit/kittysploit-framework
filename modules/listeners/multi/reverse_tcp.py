from kittysploit import *
import socket

class Module(Listener):

    __info__ = {
        "name": "reverse shell tcp",
        "handler": Handler.REVERSE_TCP,
        "module": "listeners/multi/reverse_tcp",
        "session_type": SessionType.SHELL,
    }

    lhost = OptString("127.0.0.1", "Target IPv4 or IPv6 address", True)
    lport = OptPort(4444, "Target HTTP port", True)

    def run(self):
        try:
            print_status(f"Start server on {self.lhost}:{self.lport}")
            print_status("Waiting connection...")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.lhost, self.lport))
            self.sock.listen(5)
            client, address = self.sock.accept()
            return (client, address[0], address[1])
        except KeyboardInterrupt:
            return False
        except OSError as e:
            return False

    def shutdown(self):
        try:
            if self.sock:
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
        except OSError as e:
            pass
