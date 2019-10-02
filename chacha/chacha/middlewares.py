# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import random
import scrapy
import logging
import pymysql
import time
from chacha.settings import *
from chacha.useragents import USER_AGENT
import platform
from PIL import Image, ImageEnhance
import json
import re
import random
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains
from scrapy.http import HtmlResponse
import pytesseract


class UserAgentDownloaderMiddleware(object):

    def __init__(self, user_agent=USER_AGENT):
        self.USER_AGENT = user_agent

    def process_request(self, request, spider):
        request.headers.setdefault(b"User-Agent", random.choice(self.USER_AGENT))

class HttpProxyDownloaderMiddleware(object):

    # 一些异常情况汇总
    EXCEPTIONS_TO_CHANGE = (TimeoutError, ConnectionRefusedError)

    def __init__(self, host=DB_HOST, db=DB, port=DB_PORT, user=DB_USER, pwd=DB_PASSWORD):
        # 链接数据库 decode_responses设置取出的编码为str
        self.conn = pymysql.connect(
            host=host,
            db=db,
            port=port,
            user=user,
            password=pwd,
            charset='utf8',
            use_unicode=True
        )
        self.cursor = self.conn.cursor()
        self.logger = logging.getLogger('web')

    def random_proxy(self):
        """
        随机获取有效代理，首先尝试获取最高分数代理，如果不存在，按照排名获取，否则异常
        :return: 随机代理
        """
        self.cursor.execute("""SELECT proxy FROM {} a WHERE score = (SELECT MAX(b.score) FROM {} b);""".format(IP_TABLE, IP_TABLE))
        result = self.cursor.fetchall()
        if len(result):
            proxy = random.choice(result)[0]
            full_proxy = "http://" + proxy
            self.logger.warning("#############" + str(full_proxy) + "试用中##############")
            return proxy, full_proxy
        else:
            raise PoolEmptyError

    def assign_max_score(self, proxy):
        """
        将代理设置为MAX_SCORE
        :param proxy: 代理
        :return: 设置结果
        """
        print('代理', proxy, '可用，设置为', MAX_SCORE)
        self.cursor.execute("""UPDATE %s SET score = %d WHERE proxy = '%s';""" % (IP_TABLE, MAX_SCORE, proxy))
        self.conn.commit()

    def decrease_score(self, proxy):
        """
        代理值从最高分100开始减25分，小于最小值则删除
        :param proxy: 代理
        :return: 修改后的代理分数
        """
        self.cursor.execute("""SELECT score FROM %s WHERE proxy = '%s';""" % (IP_TABLE, proxy))
        result = self.cursor.fetchone()
        score = result[0]
        if score and score > MIN_SCORE:
            print('代理', proxy, '当前分数', score, '减 25')
            self.cursor.execute("""UPDATE %s SET score = %d WHERE proxy = '%s';""" % (IP_TABLE, score - 25, proxy))
            self.conn.commit()
        else:
            print('代理', proxy, '当前分数', score, '移除')
            self.cursor.execute("""DELETE FROM %s WHERE proxy = '%s';""" % (IP_TABLE, proxy))
            self.conn.commit()
            logging.warning("#################" + proxy + "不可用，已经删除########################")

    def process_request(self, request, spider):
        # 随机选取一个分数最高的 IP
        proxy, full_proxy = self.random_proxy()
        request.meta["proxy"] = full_proxy
        request.meta["raw_proxy"] = proxy

    def process_response(self, request, response, spider):
        http_status = response.status
        # 根据response的状态判断 ，200的话ip设置为MAX_SCORE重新写入数据库，返回response到下一环节
        if http_status == 200:
            proxy = request.meta["raw_proxy"]
            self.assign_max_score(proxy)
            return response
        # 403有可能是因为user-agent不可用引起，和代理ip无关，返回请求即可
        elif http_status == 403:
            self.logger.warning("#########################403重新请求中############################")
            return request.replace(dont_filter=True)
        # 其他情况姑且被判定ip不可用，score 扣一分，score为0的删掉
        else:
            proxy = request.meta["raw_proxy"]
            self.decrease_score(proxy)
            return request.replace(dont_filter=True)

    def process_exception(self, request, exception, spider):
        # 其他一些timeout之类异常判断后的处理，ip不可用删除即可
        if isinstance(exception, self.EXCEPTIONS_TO_CHANGE) and request.meta.get('proxy', False):
            proxy = request.meta["raw_proxy"]
            self.decrease_score(proxy)
            self.logger.debug("Proxy {}链接出错{}.".format(request.meta['proxy'], exception))
            return request.replace(dont_filter=True)

class RandomDelayDownloaderMiddleware(object):
    def __init__(self):
        self.delay = RANDOM_DELAY

    def process_request(self, request, spider):
        delay = random.randint(0, self.delay)
        logging.debug("### random delay: %s s ###" % delay)
        time.sleep(delay)


class SeleniumDownloaderMiddleware(object):
    def __init__(self):
        self.timeout = 30
        self.executable_path = EXECUTABLE_PATH
        chrome_options = webdriver.ChromeOptions()
        if HEADLESS:
            chrome_options.add_argument('--headless')
        # 去除 --ingor
        chrome_options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
        # chrome_options.add_argument('--disable-gpu')
        if platform.system() == 'Windows':
            self.browser = webdriver.Chrome(executable_path=self.executable_path, chrome_options=chrome_options)
        else:
            chrome_options.add_argument('no-sandbox')  # 针对linux root用户
            self.browser = webdriver.Chrome(chrome_options=chrome_options)

        self.browser.maximize_window()
        self.browser.set_page_load_timeout(self.timeout)
        self.browser.implicitly_wait(self.timeout)
        self.wait = WebDriverWait(self.browser, self.timeout)

    def close_spider(self, spider):
        self.browser.quit()

    def spoof_track(self, distance):
        '''
        模拟滑动快慢轨迹
        :param distance: 需要移动的距离
        :return: 移动轨迹track[0.2,]
        '''
        track = []  # 移动轨迹
        current = 0  # 当前位置
        mid = distance * 4 / 5  # #减速阀值 4/5加速. 1/5加速
        t = 0.2  # 计算间隔
        v = 0  # 速度v

        while current < distance:
            if current < mid:
                # 加速度
                a = 2
            else:
                a = -3
            v_0 = v
            v = v_0 + a * t  # 当前速度 = 初速度+加速*加速时间
            move = v_0 * t + 1 / 2 * a * t * t  # 移动距离

            current += move  # 当前移动距离
            track.append(round(move))  # 加入轨迹:浮点型

        return track

    def move_track(self, slider, distance):
        '''
        :param slider: 滑块
        :param distance: 需要移动的距离
        :return:
        '''
        action = ActionChains(self.browser)  # 实例化一个action对象
        action.click_and_hold(action).perform()  # 鼠标左键按下不放
        track = self.spoof_track(distance)  # 模拟滑动快慢轨迹

        for x in track:
            action.move_by_offset(xoffset=x, yoffset=0).perform()
        time.sleep(0.5)
        action.release().perform()
        time.sleep(0.5)

    def dump_cookies(self):
        """
        登录完成后,将cookies保存到本地文件
        """
        dictCookies = self.browser.get_cookies()
        jsonCookies = json.dumps(dictCookies)

        with open(COOKIES_FILE_PATH, "w") as f:
            f.write(jsonCookies)


    def process_request(self, request, spider):
        # 指定需要 selenium 处理的特殊情况
        if "https://www.qichacha.com/user_login?back=%2F" in request.url:
            self.browser.get(request.url)
            self.browser.find_element_by_xpath('//*[@id="normalLogin"]').click()  # 转到登录的js界面
            self.browser.find_element_by_xpath('//*[@id="nameNormal"]').send_keys(QCC_ACCOUNT)  # 账号
            self.browser.find_element_by_xpath('//*[@id="pwdNormal"]').send_keys(QCC_PASSWORD)  # 密码

            slider_button = self.wait.until(EC.presence_of_element_located(By.ID, 'nc_1_n1z')) # 找到滑动板块的按钮
            self.move_track(slider_button, 263)
            time.sleep(1)
            self.browser.find_element_by_xpath('//*[@id="user_login_normal"]/button').click()  # 点击登录
            time.sleep(5)

            # alert 是 企查查 登录出现问题时弹出的
            alert = self.browser.find_element_by_class_name('nc-lang-cnt').text
            if alert == "哎呀，出错了，点击刷新再来一次":
                # 点击刷新直到出现滑块才停止
                while True:
                    self.browser.find_element_by_xpath('//*[@id="dom_id_one"]/div/span/a').click()

                    if slider_button:
                        print("CCCCCCCCCCCCC")
                        break
                self.move_track(slider_button, 263)
                self.dump_cookies()
                time.sleep(3)


            elif alert == "请在下方输入验证码":
                while True:
                    self.browser.save_screenshot(r"E:aa.png")  # 截取登录页面
                    # 定位验证码位置及大小
                    location = self.browser.find_element_by_xpath(
                        '//*[@id="nc_1__imgCaptcha_img"]/img').location  # 获取验证码x,y轴坐标
                    size = self.browser.find_element_by_xpath(
                        '//*[@id="nc_1__imgCaptcha_img"]/img').size  # 获取验证码的长宽
                    coderange = (int(location['x']), int(location['y']), int(location['x'] + size['width']),
                                 int(location['y'] + size['height']))  # 计算验证码整体坐标
                    img = Image.open(r"E:aa.png").crop(coderange)  # 打开截图, 使用Image的crop函数，从截图中再次截取我们需要的区域
                    # 下面对图片做了一些处理，能更好识别一些，相关处理再百度看吧
                    img = img.convert('RGBA')  # 转换模式：L | RGB
                    img = img.convert('L')  # 转换模式：L | RGB
                    img = ImageEnhance.Contrast(img)  # 增强对比度
                    img = img.enhance(2.0)  # 增加饱和度
                    img.save("E:bb.png")
                    # 再次读取识别验证码
                    img = Image.open("E:bb.png")
                    time.sleep(3)
                    text = pytesseract.image_to_string(img).strip()  # 使用image_to_string识别验证码# 打印识别的验证码
                    print(text)
                    # 识别出来验证码去特殊符号，用到了正则表达式，这是我第一次用，之前也没研究过，所以用的可能粗糙，请见谅
                    b = ''
                    for i in text:
                        pattern = re.compile(r'[a-zA-Z0-9]')
                        m = pattern.search(i)
                        if m != None:
                            b += i
                    # 输出去特殊符号以后的验证码
                    print(b)

                    time.sleep(2)
                    if b == '':
                        print("EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
                        time.sleep(2)
                        self.browser.find_element_by_xpath('//*[@id="nc_1__btn_1"]').click()  # 点击刷新验证码
                    else:
                        # 把b的值输入验证码输入框
                        time.sleep(10)
                        # spider.browser.find_element_by_xpath('//*[@id="nc_1_captcha_input"]').send_keys( b)  # 输入验证码
                        self.browser.find_element_by_xpath(
                            '//*[@id="nc_1_scale_submit"]/span').click()  # 点击提交
                    time.sleep(2)

                    if self.browser.find_element_by_class_name('nc-lang-cnt').text == "验证通过":  # 出现验证通过，停止
                        break

                self.browser.find_element_by_xpath('//*[@id="user_login_normal"]/button').click()  # 点击登录
                self.dump_cookies()
                time.sleep(3)

            # 不需要重新刷新出现滑块也不需要填验证码，一次滑块就通过的情况
            else:
                self.dump_cookies()


class CookieDownloaderMiddleware(object):

    def process_request(self, request, spider):
        if "https://www.qichacha.com/user_login?back=%2F" in request.url:
            return HtmlResponse(url=request.url, encoding="utf-8")
        with open(COOKIES_FILE_PATH, 'r', encoding='utf-8') as f:  # 读取login保存的cookies值
            listcookies = json.loads(f.read())
        cookies_dict = ''  # 通过构建字典类型的cookies
        for cookie in listcookies:
            sss = cookie['name'] + "=" + cookie['value'] + ";"
            cookies_dict = cookies_dict + sss
        print(cookies_dict)
        request.headers.setdefault(b"Cookie", cookies_dict)