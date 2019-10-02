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
    def start_requests(self, host=DB_HOST, db=DB, port=DB_PORT, user=DB_USER, pwd=DB_PASSWORD):
        conn = pymysql.connect(
            host=host,
            db=db,
            port=port,
            user=user,
            password=pwd,
            charset='utf8',
            use_unicode=True
        )
        cursor = conn.cursor()
        #  从红盾表中选择还没有被爬过的公司名
        cursor.execute("""SELECT corp_name FROM %s WHERE LENGTH(uid) = 0 AND LENGTH(ic_code) > 14 LIMIT 1;"""%UID_TABLE)
        rows = cursor.fetchall()
        for row in rows:
            yield Request(url="https://www.qichacha.com/search?key={}".format(quote(row[0])), callback=self.next_page, meta={'corp_name': row[0]})
        conn.close()

    # 跳页
    def next_page(self, response):
        print("next_page 走过了！！！！！！！！！！！！！！！")
        print()
        corp_name = response.meta['corp_name']
        hrefs = response.xpath("""//*[@id="search-result"]/tr/td[3]/a/@href""").extract()
        for href in hrefs:
            url = "https://www.qichacha.com" + href + "#base"
            yield Request(url=url, callback=self.parse_companyInfo, meta={'corp_name': corp_name, 'dont_redirect': True, "http_handlestatus_list": [302]}, dont_filter=True)


    # 正式抓取页面内容------公司基本信息
    def parse_companyInfo(self, response):
        print("#############################")
        print("|")
        print(response.url)
        print("|")
        print("#############################")
        item = BasicsItem()

        # 公司基本信息
        item['url'] = response.url
        item['uid_chacha'] = re.findall(r"firm_\w+", response.url)[0]
        item['corp_name'] = response.xpath('//div[@id="company-top"]//div[@class="content"]/div/h1/text()').extract_first()
        item['corp_tele'] = response.xpath("""//*[@id="company-top"]/div[2]/div[2]/div[3]/div[1]/span[1]/span[2]/span/text()""").extract_first()
        item['corp_website'] = response.xpath("""//*[@id="company-top"]/div[2]/div[2]/div[3]/div[1]/span[3]/a/text()""").extract_first()
        item['corp_email'] = response.xpath("""//*[@id="company-top"]/div[2]/div[2]/div[3]/div[2]/span[1]/span[2]/a/@href""").extract_first()
        item['corp_addr'] = response.xpath('//*[@id="company-top"]/div[2]/div[2]/div[3]/div[2]/span[3]/a[1]/text()').extract_first()

        # # 工商信息表
        # com_table = response.xpath("""//*[@id="Cominfo"]/table/tbody""")
        # # 法人
        # item['faren'] = response.xpath('//h2[@class="seo font-20"]/text()').extract_first()
        # # 注册资本
        # item['registered_capital'] = com_table.xpath('//*[@id="Cominfo"]/table/tbody/tr[4]/td[2]/text()').extract()
        # # 实缴资本
        # item['issued_capital'] = com_table.xpath("""tr[2]/td[2]/text()""").extract()
        # # 经营状态：在业
        # item['corp_status'] = com_table.xpath("""tr[3]/td[2]/text()""").extract()
        # # 成立日期：2010-03-03
        # item['estab_date'] = com_table.xpath("""tr[3]/td[4]/text()""").extract()
        # # 统一社会信用代码:91110108551385082Q
        # item['socialcredit_code'] = com_table.xpath("""tr[4]/td[2]/text()""").extract()
        # # 纳税人识别号
        # item['taxpayer_code'] = com_table.xpath("""tr[4]/td[4]/text()""").extract_first()
        # # 注册号
        # item['registered_code'] = com_table.xpath("""tr[5]/td[2]/text()""").extract_first()
        # # 组织机构代码
        # item['org_code'] = com_table.xpath("""tr[5]/td[4]/text()""").extract_first()
        # # 企业类型
        # item['business_type'] = com_table.xpath("""tr[6]/td[2]/text()""").extract_first()
        # # 所属行业
        # item['industry'] = com_table.xpath("""tr[6]/td[4]/text()""").extract_first()
        # # 核准日期
        # item['issue_date'] = com_table.xpath("""tr[7]/td[2]/text()""").extract_first()
        # # 登记机关
        # item['registrar'] = com_table.xpath("""tr[7]/td[4]/text()""").extract_first()
        # # 所属地区
        # item['district'] = com_table.xpath("""tr[8]/td[2]/text()""").extract_first()
        # # 英文名
        # item['english_name'] = com_table.xpath("""tr[8]/td[4]/text()""").extract_first()
        # # 曾用名
        # item['other_name'] = com_table.xpath("""tr[9]/td[2]/text()""").extract_first()
        # # 参保人数
        # item['insured_staff_number'] = com_table.xpath("""tr[9]/td[4]/text()""").extract_first()
        # # 人员规模
        # item['scale'] = com_table.xpath("""tr[10]/td[2]/text()""").extract_first()
        # # 营业期限
        # item['term_business'] = com_table.xpath("""tr[10]/td[4]/text()""").extract_first()
        # # 经营范围
        # item['business_scope'] = com_table.xpath("""tr[12]/td[2]/text()""").extract_first()

        li_list = response.xpath('//ul[@class="company-base"]/li')
        for li_sel in li_list:
            label = li_sel.xpath('./label/text()').extract_first()
            # print label.encode('utf8')
            if u'统一社会信用代码' in label:
                item['socialcredit_code'] = li_sel.xpath('./text()').extract_first()
            elif u'注册号' in label:
                item['registration_number'] = li_sel.xpath('./text()').extract_first()
            elif u'纳税人识别号' in label:
                item['taxpayer_code'] = li_sel.xpath('./text()').extract_first()
            elif u'组织机构代码' in label:
                item['org_code'] = li_sel.xpath('./text()').extract_first()
            elif u'经营状态' in label:
                item['corp_status'] = li_sel.xpath('./text()').extract_first()
            elif u'公司类型' in label:
                item['business_type'] = li_sel.xpath('./text()').extract_first()
            elif u'成立日期' in label:
                item['estab_date'] = li_sel.xpath('./text()').extract_first()
            elif u'法定代表' in label:
                item['faren'] = li_sel.xpath('./a/text()').extract_first()
            elif u'注册资本' in label:
                item['registered_capital'] = li_sel.xpath('./text()').extract_first()
            elif u'实缴资本' in label:
                item['issued_capital'] = li_sel.xpath('./text()').extract_first()
            elif u'营业期限' in label:
                item['term_business'] = li_sel.xpath('./text()').extract_first()
            elif u'登记机关' in label:
                item['registrar'] = li_sel.xpath('./text()').extract_first()
            elif u'核准日期' in label:
                item['issue_date'] = li_sel.xpath('./text()').extract_first()
            elif u'英文名' in label:
                item['english_name'] = li_sel.xpath('./text()')[1].extract()
            elif u'曾用名' in label:
                item['other_name'] = li_sel.xpath('./text()')[1].extract()
            elif u'经营范围' in label:
                item['business_scope'] = li_sel.xpath('./text()')[1].extract()
            elif u'所属地区' in label:
                item['district'] = li_sel.xpath('./text()').extract()

        yield item

        item2 = UidItem()
        item2['uid_hongdun'] = re.findall(r"firm_\w+", response.url)[0]
        item2['corp_name_hongdun'] = response.meta['corp_name']

        yield item2

    # def parse_basics(self, response):
    #     # 抓取公司基本信息
    #
    #     wenshu = 'https://www.qichacha.com/company_getinfos?unique=' + unique + '&companyname=' + company_name + '&tab=susong&box=wenshu&p='
    #     yield Request(url=url, callback=self.parse_basics,
    #                   meta={'corp_name': corp_name, 'dont_redirect': True, "http_handlestatus_list": [302]},
    #                   dont_filter=True)
