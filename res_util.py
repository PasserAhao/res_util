import time
import os, requests

from lxml import etree
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.options import Options
from selenium.common import WebDriverException


class BaseRequest:
    def __init__(self, *args, **kwargs):
        self.cookie = None

    def __get_cookie(self, file_path=None, *args, **kwargs):
        """
        读取Cookie
        :param path:存放Coookie的地址
        :return: 无
        """
        if not file_path:
            file_path = "./cookie.json"
            # 判断cookie文件是否存在，存在自动读取，不存在则未空
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    self.cookie = f.read()

            return
        # 如果传入cookie文件，则读取
        with open(file_path, "r") as f:
            self.cookie = f.read()

    def send_res(self, url, headers=None, encode=None, is_text=True, is_content=None, is_html=None,
                 has_cookie_path=None, *args,
                 **kwargs):
        """
        默认返回文本数据
        :param url: URL连接
        :param is_text: 返回文本数据
        :param is_content: 返回二进制数据
        :param is_html: 返回HTML数据
        :param has_cookie_path: 读取Cookie路径
        :return: 请求响应
        """
        self.__get_cookie(has_cookie_path)
        response = None
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36',
            'cookie': self.cookie
        }

        if headers:
            header = headers
        if encode:
            response = requests.get(url=url, headers=header).content.decode(encoding=encode)
        elif is_text:
            response = requests.get(url=url, headers=header).text
        elif is_content:
            response = requests.get(url=url, headers=header).content
        elif is_html:
            response = requests.get(url=url, headers=header).text
            response = etree.HTML(response)

        return response

    def save_res_to_html(self, data=None, file_name="page.html"):
        with open(file_name, 'w', encoding="utf8") as f:
            f.write(data)

    def wash_int(self, data, *args, **kwargs):
        """
        检查是否是整数类型的数据
        :param data: 数据
        :return: 整形的数据
        """
        try:
            return int(data)
        except Exception:
            raise Exception("格式错误，请输入纯数字类型的数据")

    def wash_str(self, data: str, *args, **kwargs):
        """
        删除字符串中的非法数据
        :param data:
        :return:
        """
        list1 = [" ", "\n", "\t", "\r", "\\r", "\\n", "\\", "\xa0", "\xe9", "\xe5"]
        for i in list1:
            data = data.replace(i, "")
        return data

    def wash_url(self, url, key, value, *args, **kwargs):
        """
        该函数可以让你修改对应参数的值，一般用来初始化页码
        :param url:需要改动的URL地址
        :param key: 需要改动的参数
        :param value: 改动参数的值
        :return: 修改后的URL
        """
        d = {}
        url, params = url.split("?")
        for item in params.split("&"):
            k, v = item.split("=")
            d[k] = v

        d[key] = value

        key_list = []
        for key, value in d.items():
            key_list.append(str(key) + "=" + str(value))
        key_str = "&".join(key_list)

        result = url + "?" + key_str

        return result

    def dead_time(self, dead_time=None):
        """
        时间格式: 2018-10-26 00:00:00
        :param data: 时间
        :return: 无
        """
        now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        if now_time > dead_time:
            print("==============!!!程序已过期，请联系开发解除=============")
            input("===================输入回车退出程序===================")
            quit()


resq = BaseRequest()


class GetCookie:

    def __init__(self, *args, **kwargs):
        self.options = ChromeOptions()
        self.web = None

    def __transfer_cookie_to_str(self, cookies_list, *args, **kwargs):
        """
        将Cookie翻译成为字符串类型【淘宝可用，】
        :param cookies_list: Cookie列表
        :return: Cookie字符串
        """
        if not cookies_list:
            return

        s = ""
        for item in cookies_list:
            name = item.get("name", "")
            value = item.get('value', "")
            s += "%s=%s;" % (name, value)

        return s.rstrip(";")

    def __write_cookie_to_file(self, cookie, *args, **kwargs):
        """
        将cookie写入本地
        :param cookie: Cookie
        :return: 无
        """
        cookies_str = self.__transfer_cookie_to_str(cookie)
        if not cookies_str:
            raise Exception("============================获取cookie异常============================")

        with open("cookie.json", "w") as f:
            f.write(cookies_str)
        print("============================获取cookie成功============================")
        self.web.quit()

    def connect_bro(self, web, is_noheader, *args, **kwargs):
        """
        连接浏览器
        :return:
        """
        chrome_options = None
        if is_noheader:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
        # 规避风险
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 实现规避检测
        # self.options.add_experimental_option('excludeSwitches', ['enable-logging']) # 禁止打印日志

        try:
            if web == "chrome":
                self.web = webdriver.Chrome(executable_path='./chromedriver', chrome_options=chrome_options,
                                            options=self.options)
                print("===========================谷歌浏览器启动成功==========================")
            else:
                raise Exception("======================没有配置该浏览器，请手动配置======================")
        except WebDriverException as e:
            print("===========================未检测到浏览器驱动==========================")
            quit()

    def to_url(self, url, is_get_cookie=False, file_name=None, is_html=False):
        self.web.get(url)
        if file_name:
            resq.save_res_to_html(self.web.page_source, file_name=file_name)
        if is_get_cookie:
            self.__write_cookie_to_file(self.web.get_cookies())
        if is_html:
            return etree.HTML(self.web.page_source)
        else:
            return self.web.page_source

    def login_taobao(self, user=None, pwd=None, web="chrome", is_noheader=True, *args, **kwargs):
        """
        淘宝登录
        :param user: 账号
        :param pwd: 密码
        :param web: 选择连接的浏览器
        :param is_noheader: 是否无头浏览
        :param args:
        :param kwargs:
        :return: 无
        """
        self.connect_bro(web, is_noheader)
        url = "https://login.taobao.com/member/login.jhtml"
        self.web.get(url)
        print("===============================尝试登录===============================")
        # 账号密码登录
        self.web.find_element("id", "fm-login-id").send_keys(user)
        time.sleep(0.1)
        self.web.find_element("id", "fm-login-password").send_keys(pwd)
        time.sleep(0.5)
        self.web.find_element("xpath", '//*[@id="login-form"]/div[4]/button').click()
        input("===========！！！请在手机上确认登录,确认后输入回车获取cookie============")
        print("===========================正处在获取cookie===========================")
        self.__write_cookie_to_file(self.web.get_cookies())

    def lodin_jingdong(self, user=None, pwd=None, web="chrome", is_noheader=True, *args, **kwargs):
        """
        京东登录
        :param user: 账号
        :param pwd: 密码
        :param web: 选择连接的浏览器
        :param is_noheader: 是否无头浏览
        :param args:
        :param kwargs:
        :return: 无
        """
        self.connect_bro(web, is_noheader)
        url = "https://passport.jd.com/new/login.aspx"
        self.web.get(url)
        print("===============================尝试登录===============================")
        # 账号密码登录
        # self.web.find_element("xpath", '//*[@id="content"]/div[2]/div[1]/div/div[3]/a').click()
        # self.web.find_element("id", "loginname").send_keys(user)
        # time.sleep(0.1)
        # self.web.find_element("id", "nloginpwd").send_keys(pwd)
        # time.sleep(0.5)
        # self.web.find_element("id", 'loginsubmit').click()
        input("===========！！！请在手机上扫码登录,确认后输入回车获取cookie============")
        print("===========================正处在获取cookie===========================")
        self.__write_cookie_to_file(self.web.get_cookies())


bro = GetCookie()
