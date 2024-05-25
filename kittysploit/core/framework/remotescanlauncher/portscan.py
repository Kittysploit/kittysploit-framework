import socket
import re
from kittysploit.core.utils.locked_iterator import LockedIterator
import threading


class Scanner:

    def __init__(self, target, port=None, workspace=None):

        self.target = target
        self.port = self.read_port(port)
        self.workspace = workspace
        self.port_open = []

    def scan(self):
        data = LockedIterator(self.port)
        self.run_threads(32, data)
        return self.port_open

    def test_port(self, data, threads_running):
        for port in data:
            if port is None:
                break
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(3)
                status = sock.connect_ex((self.target, int(port)))
                if status == 0:
                    self.port_open.append(port)
            if not threads_running.is_set():
                break  # Exit the loop if the threads_running event is cleared

    def read_port(self, port_str):
        ports = port_str.split(",")
        port_list = []
        for port in ports:
            if re.match("^\d+$", port):
                port_list.append(int(port))
            elif re.match("^\d+-\d+$", port):
                p_start = int(port.split("-")[0])
                p_end = int(port.split("-")[1])
                p_range = list(range(p_start, p_end + 1))
                port_list.extend(p_range)
            else:
                continue
        return port_list

    def run_threads(self, threads_count, data):
        threads = []
        threads_running = threading.Event()
        threads_running.set()

        for thread_id in range(threads_count):
            thread = threading.Thread(
                target=self.test_port,
                args=(data, threads_running),
                name="thread-{}".format(thread_id),
            )
            threads.append(thread)
            thread.start()

        try:
            for thread in threads:
                thread.join()

        except KeyboardInterrupt:
            threads_running.clear()

        for thread in threads:
            thread.join()
