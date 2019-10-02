# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


from chacha.items import *
from chacha.settings import *
from chacha.dbconfig import DBConfig



class ChachaPipeline(object):
    def __init__(self):
        self.conn = DBConfig()

    def process_item(self, item, spider):
        if item.__class__ == BasicsItem:
            return self.storeBasicsItem(item, spider)
        elif item.__class__ == UidItem:
            return self.storeUidItem(item, spider)

    def storeBasicsItem(self, item, spider):
        sql = """INSERT IGNORE INTO %s (url, uid_chacha, corp_name, corp_tele, corp_website, corp_email,
        corp_addr, faren, registered_capital, issued_capital, corp_status, estab_date, socialcredit_code,
        taxpayer_code, registered_code, org_code, business_type, industry, issue_date, registrar, district,
        english_name, other_name, insured_staff_number, scale, term_business, business_scope
        )"""% ITEM_BASICS_TABLE + "VALUES (%s, %s, %s, %s)"
        data = [item['url'], item['uid_chacha'], item['corp_name'], item['corp_tele'], item['corp_website'],
                item['corp_email'], item['corp_addr'], item['faren'], item['registered_capital'],
                item['issued_capital'], item['corp_status'], item['estab_date'], item['socialcredit_code'],
                item['taxpayer_code'], item['registered_code'], item['org_code'], item['business_type'],
                item['industry'], item['issue_date'], item['registrar'], item['district'], item['english_name'],
                item['other_name'], item['insured_staff_number'], item['scale'], item['term_business'],
                item['business_scope']
                ]
        self.conn.insert_by_sql(sql, data)
        return item


    def storeUidItem(self, item, spider):
        sql = """UPDATE %s SET uid = '%s' WHERE corp_name = '%s'""" %(UID_TABLE, item['uid_hongdun'], item['corp_name_hongdun'])
        self.conn.insert_by_sql(sql)
        return item
