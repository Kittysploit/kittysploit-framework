from kittysploit import *

class Module(RemoteScan):

    __info__ = {
        "name": "check login",
        "description": "Login page found",
        "cve": "",
        "status": "low",
        "module": "auxiliary/scanner/http_login",
    }	
    
    def run(self):
        http = self.scan_lib('http/http_func')
        result = http.http_request(
                method = "GET",
                path = "/")
        if 'type="password"' in result.text:
            return True
        return False