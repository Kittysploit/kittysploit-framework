from kittysploit import *
import socket
from threading import Thread, Lock
from time import sleep

class Module(Plugin):

    __info__ = {"name": "Listener like Netcat", 
                "description": "Listener like Netcat",
                }

    def __init__(self):
        self.lock = Lock()
        self.s = socket.socket()
        self.conn = None
        self.stop_threads = False
        self.port = 6000
        self.stop_loop = True

    def initialize(self):
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.s.bind(("0.0.0.0", self.port))
            print_success(f"Listening on :{self.port}")
            print_success("Write 'exit' to close connection")
            print_success("Wait client...")
            return True
        except:
            print_error(f"You must be root to bind port {self.port}")
            return False

    def listen(self):
        self.s.listen(1)
        try:
            self.conn, addr = self.s.accept()
            self.conn.settimeout(3)
            print_success(f"Connection established: {addr[0]}")
            recv = Thread(target=self.recv)
            recv.start()
        except OSError:
            if self.lock.acquire():
                self.lock.release()

    def recv(self):

        while True:
            if self.stop_threads:
                try:
                    if self.conn:
                        self.conn.close()
                        self.s.close()
                    break
                except OSError:
                    pass
            elif self.conn:
                try:
                    data = self.conn.recv(4096)
                    if data:
                        print_info(data.decode(errors="ignore").strip())
                except socket.timeout:
                    pass
                except OSError:
                    if self.conn is not None:
                        self.conn.close()
                        self.s.close()
                    break
            else:
                sleep(1)

    def run(self, *args, **kwargs):

        parser = ModuleArgumentParser(description=self.__doc__, prog="listen")
        parser.add_argument("-p", dest="port", help="port to listen", type=int, default=6000)
        if args[0] == "":
            parser.print_help()
            return
        try:
            pargs = parser.parse_args(shlex.split(args[0]))
            if pargs is None:
                return
            else:
                if isinstance(pargs.port, int):
                    self.port = pargs.port
                    init = self.initialize()
                    if init:
                        listen = Thread(target=self.listen)
                        listen.start()
                        while self.stop_loop:
                            try:
                                data = input()
                                if self.conn:
                                    if data == "exit":
                                        print_success("Exit listener")
                                        self.stop_threads = True
                                        self.s.shutdown(2)
                                        self.s.close()
                                        break
                                    data = data + "\n"
                                    self.conn.send(data.encode())
                                else:
                                    if data == "exit":
                                        self.s.shutdown(2)
                                        self.s.close()
                                        break
                                    print_status("Wait client...")
                            except KeyboardInterrupt as e:
                                print_error("KeyboardInterrupt")
                                self.stop_threads = True
                                self.s.shutdown(2)
                                self.s.close()
                                break

        except:
            pass

    def stop(self):
        self.stop_threads = True
        self.stop_loop = False
        self.s.shutdown(2)
        self.s.close()
