# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from chacha.items import *
from chacha.settings import *
from urllib.request import quote
import  re
import pymysql


class QichachaSpider(scrapy.Spider):
    name = 'qichacha'
    allowed_domains = ['qichacha.com']
    http_handlestatus_list = [301, 302, 500]

    cookies={}
    # 搜索
    # def start_requests(self, host=DB_HOST, db=DB, port=DB_PORT, user=DB_USER, pwd=DB_PASSWORD):
    #     conn = pymysql.connect(
    #         host=host,
    #         db=db,
    #         port=port,
    #         user=user,
    #         password=pwd,
    #         charset='utf8',
    #         use_unicode=True
    #     )
    #     cursor = conn.cursor()
    #     #  从红盾表中选择还没有被爬过的公司名
    #     cursor.execute("""SELECT corp_name FROM %s WHERE LENGTH(uid) = 0 AND LENGTH(ic_code) > 14 LIMIT 1;"""%UID_TABLE)
    #     rows = cursor.fetchall()
    #     for row in rows:
    #         yield Request(url="https://www.qichacha.com/search?key={}".format(quote(row[0])), callback=self.next_page, meta={'corp_name': row[0]})
    #     conn.close()

    def start_requests(self):
        yield Request(url="https://www.qichacha.com/firm_3065012a7bc3f9583a8d09fb9d2f38b8.html", callback=self.parse_companyInfo,
                      meta={'corp_name': "上海蔚来汽车有限公司"})

    # 跳页
    def next_page(self, response):
        corp_name = response.meta['corp_name']
        hrefs = response.xpath("""//*[@id="search-result"]/tr/td[3]/a/@href""").extract()
        for href in hrefs:
            print("###############################")
            print("{}".format(href))
            print("###############################")
            url = "https://www.qichacha.com" + href + "#base"
            yield Request(url=url, callback=self.parse_companyInfo, meta={'corp_name': corp_name, 'dont_redirect': True, "http_handlestatus_list": [302]}, dont_filter=True)


    # 正式抓取页面内容------公司基本信息
    def parse_companyInfo(self, response):
        item = BasicsItem()

        # 公司基本信息
        item['url'] = response.url
        item['uid_chacha'] = re.findall(r"firm_\w+", response.url)[0]
        item['corp_name'] = response.xpath('//div[@id="company-top"]//div[@class="content"]/div/h1/text()').extract_first().strip()
        item['corp_tele'] = response.xpath("""normalize-space(//*[@id="company-top"]/div[2]/div[2]/div[3]/div[1]/span[1]/span[2]/span/a)""").extract_first()
        item['corp_website'] = response.xpath("""normalize-space(//*[@id="company-top"]/div[2]/div[2]/div[3]/div[1]/span[3]/a)""").extract_first()
        item['corp_email'] = response.xpath("""normalize-space(//*[@id="company-top"]/div[2]/div[2]/div[3]/div[2]/span[1]/span[2]/a[1])""").extract_first()
        item['corp_addr'] = response.xpath('normalize-space(//*[@id="company-top"]/div[2]/div[2]/div[3]/div[2]/span[3]/a[1])').extract_first()

        # 其他企业信息
        selector = response.xpath('//*[@id="Cominfo"]/table')
        item['socialcredit_code'] = selector.xpath('normalize-space(//td[contains(text(), "统一社会信用代码")]/following-sibling::td[1])').extract_first()
        item['registered_code'] = selector.xpath('normalize-space(//td[contains(text(), "注册号")]/following-sibling::td[1])').extract_first()
        item['taxpayer_code'] = selector.xpath('normalize-space(//td[contains(text(), "纳税人识别号")]/following-sibling::td[1])').extract_first()
        item['org_code'] = selector.xpath('normalize-space(//td[contains(text(), "组织机构代码")]/following-sibling::td[1])').extract_first()
        item['corp_status'] = selector.xpath('normalize-space(//td[contains(text(), "经营状态")]/following-sibling::td[1])').extract_first()
        item['business_type'] = selector.xpath('normalize-space(//td[contains(text(), "企业类型")]/following-sibling::td[1])').extract_first()
        item['estab_date'] = selector.xpath('normalize-space(//td[contains(text(), "成立日期")]/following-sibling::td[1])').extract_first()
        item['faren'] = selector.xpath('normalize-space(//td[contains(text(), "法定代表")]/following-sibling::td[1])').extract_first()
        item['registered_capital'] = selector.xpath('normalize-space(//td[contains(text(), "注册资本")]/following-sibling::td[1])').extract_first()
        item['issued_capital'] = selector.xpath('normalize-space(//td[contains(text(), "实缴资本")]/following-sibling::td[1])').extract_first()
        item['term_business'] = selector.xpath('normalize-space(//td[contains(text(), "营业期限")]/following-sibling::td[1])').extract_first()
        item['registrar'] = selector.xpath('normalize-space(//td[contains(text(), "登记机关")]/following-sibling::td[1])').extract_first()
        item['issue_date'] = selector.xpath('normalize-space(//td[contains(text(), "英文名")]/following-sibling::td[1])').extract_first()
        item['english_name'] = selector.xpath('normalize-space(//td[contains(text(), "登记机关")]/following-sibling::td[1])').extract_first()
        item['other_name'] = selector.xpath('normalize-space(//td[contains(text(), "曾用名")]/following-sibling::td[1])').extract_first()
        item['business_scope'] = selector.xpath('normalize-space(//td[contains(text(), "经营范围")]/following-sibling::td[1])').extract_first()
        item['district'] = selector.xpath('normalize-space(//td[contains(text(), "所属地区")]/following-sibling::td[1])').extract_first()
        item['industry'] = selector.xpath('normalize-space(//td[contains(text(), "所属行业")]/following-sibling::td[1])').extract_first()
        item['insured_staff_number'] = selector.xpath('normalize-space(//td[contains(text(), "参保人数")]/following-sibling::td[1])').extract_first()
        item['scale'] = selector.xpath('normalize-space(//td[contains(text(), "人员规模")]/following-sibling::td[1])').extract_first()

        item2 = UidItem()
        item2['uid_hongdun'] = re.findall(r"firm_\w+", response.url)[0]
        item2['corp_name_hongdun'] = response.meta['corp_name']

        return item, item2

    # def parse_basics(self, response):
    #     # 抓取公司基本信息
    #
    #     wenshu = 'https://www.qichacha.com/company_getinfos?unique=' + unique + '&companyname=' + company_name + '&tab=susong&box=wenshu&p='
    #     yield Request(url=url, callback=self.parse_basics,
    #                   meta={'corp_name': corp_name, 'dont_redirect': True, "http_handlestatus_list": [302]},
    #                   dont_filter=True)
