import ftplib

class Cache_ftp:
    
    def __init__(self, target, port):
        self.target = target
        self.port = port
    
    def put_cache(self):
        ftp_client = ftplib.FTP()
        banner = ftp_client.connect(self.target, self.port, 4.0)
        return banner