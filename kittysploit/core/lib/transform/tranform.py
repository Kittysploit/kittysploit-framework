from kittysploit.core.framework.base_module import BaseModule
import hashlib

class Transform(BaseModule):

    def base64_encode(self, data):
        """This method encode data to base64"""
        return data.encode("base64")

    def base64_decode(self, data):
        """This method decode base64 data"""
        return data.decode("base64")

    def hex_encode(self, data):
        """This method encode data to hex"""
        return data.encode("hex")

    def hex_decode(self, data):
        """This method decode hex data"""
        return data.decode("hex")

    def url_encode(self, data):
        """This method encode data to url"""
        return data.escape(data)

    def url_decode(self, data):
        """This method decode url data"""
        return data.unescape(data)

    def rot13_encode(self, data):
        """This method encode data to rot13"""
        return data.encode("rot13")

    def rot13_decode(self, data):
        """This method decode rot13 data"""
        return data.decode("rot13")

    def xor_encode(self, data, key):
        """This method encode data to xor"""
        return data.encode("xor", key)

    def xor_decode(self, data, key):
        """This method decode xor data"""
        return data.decode("xor", key)

    def md5(self, data):
        """This method hash data to md5"""
        return hashlib.md5(data).hexdigest()

    def sha1(self, data):
        """This method hash data to sha1"""
        return hashlib.sha1(data).hexdigest()

    def sha256(self, data):
        """This method hash data to sha256"""
        return hashlib.sha256(data).hexdigest()

    def addslash_singlequote(self, data):
        """This method add slash to single quote"""
        return data.replace("'", "\\'")
