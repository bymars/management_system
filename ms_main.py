import getopt, sys, time, random, string
from ms_email import MailSender
from ms_email import MailReceiver
from ms_alipay import AlipayAcct

def main():
  if len(sys.argv) != 5:
    usage()
    exit(1)

  username = sys.argv[1]
  password = sys.argv[2]
  mail_user = sys.argv[3]
  mail_pass = sys.argv[4]
  from_addr = sys.argv[5]
  to_addr = sys.argv[6]

  sender = MailSender(mail_user, mail_pass, proxy_addr='127.0.0.1', proxy_port=1080)
  receiver = MailReceiver(mail_user, mail_pass, proxy_addr='127.0.0.1', proxy_port=1080)

  acct = AlipayAcct(username, password)
  acct.login()
  (retcode, result) = acct.get_balance()

  if retcode == 'succ':
    subject = time.strftime('%Y-%m-%d',time.localtime(time.time())) + ' Balance:' + result
    sender.send_mail(from_addr, to_addr, subject)
  elif retcode == 'qrcode':
    subject = ''.join(random.sample(string.ascii_letters, 32))
    sender.send_mail(from_addr, to_addr, subject, attachment = result)
    message = receiver.wait_mail_by_title(subject)
    if 'done' in message['Subject']:
      (retcode, result) = acct.get_balance()
      subject2 = time.strftime('%Y-%m-%d',time.localtime(time.time())) + ' Balance:' + result
      sender.send_mail(from_addr, to_addr, subject2)
  elif retcode == 'login':
    subject = ''.join(random.sample(string.ascii_letters, 32))
    sender.send_mail(from_addr, to_addr, subject, attachment = result)

def usage():
  print('python3 ms_main.py <account> <password> <email_user> <email_pass> <from_addr> <to_addr>')

if __name__ == '__main__':
  main()
