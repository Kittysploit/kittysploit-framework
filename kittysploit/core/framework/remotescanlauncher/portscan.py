from kittysploit.core.utils.locked_iterator import LockedIterator
from kittysploit.core.base.io import print_error
from kittysploit.core.framework.remotescanlauncher.port_list import PORT
import threading
import ipaddress
from urllib.parse import urlparse
import socket
import re

class Scanner:

    def __init__(self, target, workspace=None):

        self.target = target
        self.port = [21, 80, 443, 665, 8008]
        self.workspace = workspace
        self.port_open = []

    def normalize_input(self, input_url):
        try:
            ip = ipaddress.ip_address(input_url)
            return str(ip)
        except ValueError:
            pass

        parsed_url = urlparse(input_url)
        scheme = parsed_url.scheme
        netloc = parsed_url.netloc

        if not scheme and not netloc:
            netloc = input_url
            scheme = 'http'

        if not scheme:
            scheme = 'http'

        if not netloc:
            netloc = parsed_url.path
            path = ''
        else:
            path = parsed_url.path

        # Extraction du port si disponible
        if ':' in netloc:
            host, port = netloc.split(':')
        else:
            host = netloc

        return host

    def scan(self):
        data = LockedIterator(self.port)
        self.run_threads(64, data)

        return self.port_open

    def test_port(self, data, threads_running):
        host = self.normalize_input(self.target)
        for port in data:
            if port is None:
                break
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(1)
                    status = sock.connect_ex((host, int(port)))
                    if status == 0:
                        self.port_open.append(port)
                    sock.close()
            except Exception as e:
                print_error(f"Error while scanning port {port}: {e}")

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
            print_error("Scan interrupted by user")
        except Exception as e:
            print_error(f"Error while scanning: {e}")
