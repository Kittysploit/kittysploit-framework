from kittysploit.core.framework.base_module import BaseModule
from kittysploit.core.framework.option import OptString, OptPort, OptBool
from kittysploit.core.framework.failure import ProcedureError
from kittysploit.core.base.config import KittyConfig
from kittysploit.core.base.io import print_info, print_error, print_warning
import requests
import socket


class Http_client(BaseModule):
    """Normal option"""

    target = OptString(
        "127.0.0.1", "Target IPv4, IPv6 address: 192.168.1.1", required=True
    )
    port = OptPort(80, "Target HTTP port", required=True)
    uripath = OptString("/", "Path", required=True)

    """ Advanced option """
    user_agent = OptString(
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
        "The User-Agent header to use for all requests",
        required=False,
        advanced=True,
    )
    ssl = OptBool(False, "SSL enabled: true/false", required=False, advanced=True)
    tor = OptBool(False, "Use Tor proxy: true/false", required=False, advanced=True)
    tor_port = OptPort(9050, "Tor proxy port", required=False, advanced=True)
    tor_host = OptString("127.0.0.1", "Tor proxy host", required=False, advanced=True)
                         
    def __init__(self):
        super().__init__()
        self.session = requests.Session()

    def http_request(
        self,
        method="GET",
        host=None,
        port=None,
        path="/",
        ssl=False,
        timeout=8,
        output=True,
        session=False,
        tor=False,
        **kwargs
    ):
        """This method do a http/https request

        argument: 	method --> required
                    host=None (if none, target option is take)
                    port=None (if none, port option is take)
                    path = '/'
                    ssl=False
                    session=False

        return:     response object
        """

        if not host:
            url = self._normalize_url(self.target, self.port, path, self.ssl)
        else:
            if not port:
                port = self.port
            url = self._normalize_url(host, port, path, ssl)

        if tor:
            proxies = {
                "http": 'socks5://127.0.0.1:9050',
                "https": 'socks5://127.0.0.1:9050'
            }
            kwargs.setdefault("proxies", proxies)
        else:
            my_config = KittyConfig()
            if my_config.get_boolean("TOR", "enable"):
                proxies = {
                    "http": 'socks5://{}:{}'.format(
                        my_config.get_config("TOR", "host"),
                        my_config.get_config("TOR", "port")
                    ),
                    "https": 'socks5://{}:{}'.format(
                        my_config.get_config("TOR", "host"),
                        my_config.get_config("TOR", "port")
                    )
                }
                kwargs.setdefault("proxies", proxies)
            # check in config file
            
        
        if session:
            session = self.session
        else:
            session = requests

        kwargs.setdefault("timeout", timeout)
        kwargs.setdefault("verify", False)
        kwargs.setdefault("allow_redirects", True)
        try:
            return getattr(session, method.lower())(url, **kwargs)
        except (requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema):
            print_error("Invalid URL format: {}!".format(url))
        except requests.exceptions.ConnectionError:
            print_error("Connection error: {}!".format(url))
        except requests.exceptions.ReadTimeout:
            print_warning("Timeout waiting for response.")
        except requests.RequestException as e:
            print_error("Request error: {}!".format(str(e)))
        except socket.error:
            print_error("Socket is not connected!")
        except Exception as e:
            print_error("Error: {}!".format(str(e)))

        raise ProcedureError()

    def http_get(
        self,
        host=None,
        port=None,
        path="/",
        ssl=False,
        timeout=8,
        output=True,
        session=False,
        **kwargs
    ):
        """
        Perform an HTTP GET request.

        Arguments:
            host: str, optional, target host (if not provided, the 'target' option is used)
            port: int, optional, target port (if not provided, the 'port' option is used)
            path: str, optional, URL path (default is '/')
            ssl: bool, optional, use SSL (default is False)
            timeout: int, optional, request timeout in seconds (default is 8)
            output: bool, optional, whether to print output (default is True)
            session: bool, optional, whether to use a session (default is False)
            **kwargs: Additional keyword arguments to pass to the request

        Returns:
            Response object
        """
        return self.http_request(
            method="GET",
            host=host,
            port=port,
            path=path,
            ssl=ssl,
            timeout=timeout,
            output=output,
            session=session,
            **kwargs
        )

    def http_post(
        self,
        host=None,
        port=None,
        path="/",
        ssl=False,
        timeout=8,
        output=True,
        session=False,
        **kwargs
    ):
        """
        Perform an HTTP GET request.

        Arguments:
            host: str, optional, target host (if not provided, the 'target' option is used)
            port: int, optional, target port (if not provided, the 'port' option is used)
            path: str, optional, URL path (default is '/')
            ssl: bool, optional, use SSL (default is False)
            timeout: int, optional, request timeout in seconds (default is 8)
            output: bool, optional, whether to print output (default is True)
            session: bool, optional, whether to use a session (default is False)
            **kwargs: Additional keyword arguments to pass to the request

        Returns:
            Response object
        """
        return self.http_request(
            method="POST",
            host=host,
            port=port,
            path=path,
            ssl=ssl,
            timeout=timeout,
            output=output,
            session=session,
            **kwargs
        )

    def _normalize_url(self, host, port, path, ssl=False):
        """This method normalize url"""
        url = ""
        if ssl:
            if not host.startswith("https://"):
                url = "https://"
        else:
            if not host.startswith("http://"):
                url = "http://"

        url += "{}:{}{}".format(host, port, path)
        return url

    def _http_test_connect(self):
        """Test connection to HTTP server

        return:   Boolean (True if test connection was successful, False otherwise)
        """

        response = self._http_request(method="GET", path="/")
        if response:
            return True
        return False
