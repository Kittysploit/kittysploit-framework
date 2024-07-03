import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

class Cache_http:
    
    def __init__(self, url, port):
        self.url = url
        self.port = port
    
    def put_cache(self):
        print("request:", self.url, self.port)
        result = requests.get(f"http://{self.url}:{self.port}", verify=False)
        print(result)
        return result