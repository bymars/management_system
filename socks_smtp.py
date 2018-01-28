import ssl

from socks import create_connection
from socks import PROXY_TYPE_SOCKS4
from socks import PROXY_TYPE_SOCKS5
from socks import PROXY_TYPE_HTTP

from smtplib import SMTP
from smtplib import SMTP_PORT
from smtplib import SMTP_SSL_PORT

class Socks_SMTP(SMTP):
  PROXY_TYPES = {"socks4": PROXY_TYPE_SOCKS4,
                 "socks5": PROXY_TYPE_SOCKS5,
		 "http": PROXY_TYPE_HTTP}
  def __init__(self, host, port=SMTP_PORT, proxy_addr=None, proxy_port=None,
               rdns=True, username=None, password=None, proxy_type="socks5"):

    self.proxy_addr = proxy_addr
    self.proxy_port = proxy_port
    self.rdns = rdns
    self.username = username
    self.password = password
    print('proxy_type:' + proxy_type)
    self.proxy_type = Socks_SMTP.PROXY_TYPES[proxy_type.lower()]

    SMTP.__init__(self, host, port)

  def _get_socket(self, host, port, timeout):
    if self.proxy_addr is None:
      return SMTP._get_socket(self, host, port, timeout)
    else:
      return create_connection((host, port),
		               proxy_type=self.proxy_type,
		               proxy_addr=self.proxy_addr,
                               proxy_port=self.proxy_port,
                               proxy_rdns=self.rdns,
                               proxy_username=self.username,
                               proxy_password=self.password)

class Socks_SMTP_SSL(Socks_SMTP):
  def __init__(self, host='', port=SMTP_SSL_PORT, keyfile=None, certfile=None,
               ssl_context=None, proxy_addr=None, proxy_port=None, rdns=True,
               username=None, password=None, proxy_type="socks5"):

    if ssl_context is not None and keyfile is not None:
      raise ValueError("ssl_context and keyfile arguments are mutually exclusive")
    if ssl_context is not None and certfile is not None:
      raise ValueError("ssl_context and certfile arguments are mutually exclusive")

    self.keyfile = keyfile
    self.certfile = certfile
    if ssl_context is None:
      ssl_context = ssl._create_stdlib_context(certfile=certfile, keyfile=keyfile)

    self.ssl_context = ssl_context

    Socks_SMTP.__init__(self, host, port, proxy_addr=proxy_addr, proxy_port=proxy_port,
		        rdns=rdns, username=username, password=password, proxy_type=proxy_type)

  def _get_socket(self, host, port, timeout):
    sock = Socks_SMTP._get_socket(self, host, port, timeout)
    # server_hostname = self.host if ssl.HAS_SNI else None
    return self.ssl_context.wrap_socket(sock, server_hostname=self._host)

