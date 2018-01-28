import smtplib
import imaplib
import email
import os
import time
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEBase, MIMEMultipart
from email.header import Header
from email.utils import parseaddr, formataddr

from socks_imap import Socks_IMAP4_SSL
from socks_smtp import Socks_SMTP_SSL

DEFAULT_IMAP_URL = 'imap.gmail.com'
DEFAULT_SMTP_URL = 'smtp.gmail.com'

class MailReceiver(object):
  def __init__(self, username, password,
               imap_url = DEFAULT_IMAP_URL,
	       proxy_addr=None,
	       proxy_port=None,
	       proxy_type="socks5"):
    self.imap = Socks_IMAP4_SSL(imap_url, proxy_addr=proxy_addr, proxy_port=proxy_port, proxy_type=proxy_type)
    self.imap.login(username, password)

  def get_message_from_uid(self, uid):
    result, data = self.imap.uid('fetch', uid, '(RFC822)')
    raw_email = str(data[0][1], encoding = 'utf-8')
    return email.message_from_string(raw_email)

  def get_latest_mail(self):
    self.imap.select('inbox')
    result, data = self.imap.uid('search', None, "ALL")
    latest_email_uid = data[0].split()[-1]
    return self.get_message_from_uid(latest_email_uid)

  def search_mail_by_title(self, title):
    self.imap.select('inbox')
    result, data = self.imap.uid('search', None, '(HEADER Subject "%s")' % title)
    if not data[0]:
      return None
    else:
      uid = data[0].split()[-1]
      return self.get_message_from_uid(uid)

  def wait_mail_by_title(self, title):
    while True:
      mail = self.search_mail_by_title(title)
      if mail is None:
        time.sleep(1)
      else:
        return mail

class MailSender(object):
  def __init__(self, username, password,
               smtp_url = DEFAULT_SMTP_URL,
	       proxy_addr=None,
	       proxy_port=None,
	       proxy_type="socks5"):
    self.smtp = Socks_SMTP_SSL(smtp_url, proxy_addr=proxy_addr, proxy_port=proxy_port, proxy_type=proxy_type)
    self.smtp.login(username, password)

  def _format_addr(self, s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

  def send_mail(self, sender, receiver, subject, text = '', attachment = None):
    msg = ''
    message = MIMEMultipart()
    message['From'] = self._format_addr('Robot <%s>' % sender)
    message['To'] =  self._format_addr('Master <%s>' % receiver)
    message['Subject'] = Header(subject, 'utf-8')
    message.attach(MIMEText(text, 'plain', 'utf-8'))

    if not attachment is None and os.path.exists(attachment):
      with open(attachment, 'rb') as f:
        mime = MIMEBase('image', 'png', filename='image.png')
        mime.add_header('Content-Disposition', 'attachment', filename='image.png')
        mime.add_header('Content-ID', '<0>')
        mime.add_header('X-Attachment-Id', '0')
        mime.set_payload(f.read())
        encoders.encode_base64(mime)
        message.attach(mime)
    self.smtp.sendmail(sender, [receiver], message.as_string())

