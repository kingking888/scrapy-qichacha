# -*- coding: utf-8 -*-

# Scrapy settings for qiye project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'chacha'

SPIDER_MODULES = ['chacha.spiders']
NEWSPIDER_MODULE = 'chacha.spiders'

"""
########### DBConfig START ###########
"""
# DBConfig
DB_HOST = '127.0.0.1'
DB = 'citic'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWORD ='123456'
DB_CHARSET = 'utf8'
# IP DBConfig
IP_TABLE = 'proxies'
# Item Storage DBConfig
ITEM_BASICS_TABLE = 'qichacha_basics'
ITEM_RISK_TABLE = 'qichacha_risk'
# UID Storage hongdun
UID_TABLE = 'test_hongdun'


"""
########### QichachaConfig START ###########
"""
QCC_ACCOUNT = "18898730133"
QCC_PASSWORD = "qichacha123@"
COOKIES_FILE_PATH = "/home/qlq/PycharmProjects/chacha/chacha/cookies.json"

"""
########### ProxyPoolConfig START ###########
"""
# 代理分数
MAX_SCORE = 100
MIN_SCORE = 0
INITIAL_SCORE = 10
VALID_STATUS_CODES = [200, 302]

class PoolEmptyError(Exception):
    def __init__(self):
        Exception.__init__(self)

    def __str__(self):
        return repr('当前ip池已枯竭')


"""
########### SeleniumConfig START ###########
"""
SELENIUM_TIMEOUT = 25           # selenium浏览器的超时时间，单位秒
LOAD_IMAGE = True               # 是否下载图片
WINDOW_HEIGHT = 900             # 浏览器窗口大小
WINDOW_WIDTH = 900
EXECUTABLE_PATH = "/usr/local/share/"
HEADLESS = False

"""
########### SpidersConfig START ###########
"""
# 随机沉睡秒数范围，如果启用了 DOWNLOAD_DELAY，总DELAY时长为 RANDOM_DELAY + DOWNLOAD_DELAY
RANDOM_DELAY = 0

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 3

# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False
REDIRECT_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language':'zh-CN,zh;q=0.9',
    'Cache-Control':'max-age=0',
    'Connection': 'keep-alive',
    'Cookie':r'QCCSESSID=lmsmvs6tmohcp6sgd64clspvf1; UM_distinctid=16d698b840e435-041fb63598e67c-1528110c-15f900-16d698b840f5ba; _uab_collina=156943381424742700303077; acw_tc=7793462515693763206345077e438898c26b13251c77a9a9b1ba2151a8; zg_did=%7B%22did%22%3A%20%2216d698b891b69-050d22c5207795-1528110c-15f900-16d698b891c28d%22%7D; CNZZDATA1254842228=694822442-1569371772-null%7C1569917728; Hm_lvt_3456bee468c83cc63fb5147f119f1075=1569433816,1569710308,1569891355,1569976114; Hm_lpvt_3456bee468c83cc63fb5147f119f1075=1569976119; zg_de1d1a35bfa24ce29bbf2c7eb17e6c4f=%7B%22sid%22%3A%201569976113703%2C%22updated%22%3A%201569976123520%2C%22info%22%3A%201569433815340%2C%22superProperty%22%3A%20%22%7B%7D%22%2C%22platform%22%3A%20%22%7B%7D%22%2C%22utm%22%3A%20%22%7B%7D%22%2C%22referrerDomain%22%3A%20%22%22%2C%22zs%22%3A%200%2C%22sc%22%3A%200%2C%22cuid%22%3A%20%22c5596e73201b0529fd9d46fdc456d4e4%22%7D',
    'Host': 'www.qichacha.com',
    'Upgrade-Insecure-Requests': 1,
}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'chacha.middlewares.UserAgentDownloaderMiddleware': 50,
    # 'chacha.middlewares.HttpProxyDownloaderMiddleware': 100,
    # 'chacha.middlewares.SeleniumDownloaderMiddleware': 150,
    # 'chacha.middlewares.CookieDownloaderMiddleware': 200,
    'chacha.middlewares.RandomDelayDownloaderMiddleware': 250,
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'chacha.pipelines.ChachaPipeline': 300,
}