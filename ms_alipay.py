import time
import sys
from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.common.exceptions import NoSuchElementException

class AlipayAcct(object):

  LOGIN_URL = 'https://auth.alipay.com/login/index.htm'
  BAO_URL = 'https://bao.alipay.com/yeb/asset.htm'
  SECURITY_URL_SUFFIX = 'checkSecurity.htm'
  LOGIN_SHOW_SEL = 'li[data-status=show_login]'
  LOGIN_USER_SEL = '#J-input-user'
  LOGIN_PASS_SEL = '#password_rsainput'
  LOGIN_CODE_SEL = '#J-input-checkcode'
  LOGIN_BTN_SEL = '#J-login-btn'
  SECURITY_INPUT_SEL = '#riskackcode'
  SECURITY_BTN_SEL = 'input[seed=JSubmit-btn]'
  BALANCE_SEL = '.eye-val'
  QR_SEL = '.qrcode-cnt'

  def __init__(self, username, password):
    Display(visible = 0, size = (1920, 1080)).start()
    self.browser = webdriver.Chrome()
    self.username = username
    self.password = password

  def get_page(self, url):
    self.browser.get(url)
    self.browser.implicitly_wait(3)

  def save_screenshot(self, filename):
    self.browser.save_screenshot(filename)

  def save_ele_screenshot(self, selector, filename):
    ele = self.browser.find_element_by_css_selector(selector)
    ele.screenshot(filename)

  def click_element(self, selector):
    ele = self.browser.find_element_by_css_selector(selector)
    ele.click()
    time.sleep(1)

  def input_to_element(self, selector, s):
    ele = self.browser.find_element_by_css_selector(selector)
    ele.clear()
    for i in s:
      ele.send_keys(i)
      time.sleep(0.5)

  def get_element_text(self, selector):
    ele = self.browser.find_element_by_css_selector(selector)
    return ele.text

  def login(self):
    self.get_page(AlipayAcct.LOGIN_URL)
    self.click_element(AlipayAcct.LOGIN_SHOW_SEL)
    self.input_to_element(AlipayAcct.LOGIN_USER_SEL, self.username)
    self.input_to_element(AlipayAcct.LOGIN_PASS_SEL, self.password)
    self.click_element(AlipayAcct.LOGIN_BTN_SEL)
    if self.browser.current_url == AlipayAcct.LOGIN_URL:
      self.save_screenshot('login.png')
      return ('login', 'login.png')
    else:
      return ('succ', '')

  def login_with_checkcode(self, checkcode):
    self.input_to_element(AlipayAcct.LOGIN_USER_SEL, self.username)
    self.input_to_element(AlipayAcct.LOGIN_PASS_SEL, self.password)
    self.input_to_element(AlipayAcct.LOGIN_CODE_SEL, checkcode)
    self.click_element(AlipayAcct.LOGIN_BTN_SEL)
    if self.browser.current_url.endswith(AlipayAcct.SECURITY_URL_SUFFIX):
      self.save_screenshot('security.png')
      return ('security', 'security.png')
    else:
      return ('succ', '')

  def login_with_security(self, security):
    self.input_to_element(AlipayAcct.SECURITY_INPUT_SEL, security)
    self.click_element(AlipayAcct.SECURITY_BTN_SEL)

  def get_balance(self):
    self.get_page(AlipayAcct.BAO_URL)
    if self.browser.current_url == AlipayAcct.BAO_URL:
      try:
        result = ('succ', self.get_element_text(AlipayAcct.BALANCE_SEL))
      except NoSuchElementException as e:
        self.save_screenshot('qr.png')
        result = ('qrcode', 'qr.png')
    else:
      self.save_screenshot('error.png')
      result = ('error', 'error.png')
    return result

