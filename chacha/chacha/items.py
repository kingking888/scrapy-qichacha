# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BasicsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    uid_chacha = scrapy.Field()
    corp_name = scrapy.Field()
    corp_tele = scrapy.Field()
    corp_website = scrapy.Field()
    corp_email = scrapy.Field()
    corp_addr = scrapy.Field()

    faren = scrapy.Field()
    registered_capital = scrapy.Field()
    issued_capital = scrapy.Field()
    corp_status = scrapy.Field()
    estab_date = scrapy.Field()
    socialcredit_code = scrapy.Field()
    taxpayer_code = scrapy.Field()
    registered_code = scrapy.Field()
    org_code = scrapy.Field()
    business_type = scrapy.Field()
    industry = scrapy.Field()
    issue_date = scrapy.Field()
    registrar = scrapy.Field()
    district = scrapy.Field()
    english_name = scrapy.Field()
    other_name = scrapy.Field()
    insured_staff_number = scrapy.Field()
    scale = scrapy.Field()
    term_business = scrapy.Field()
    business_scope = scrapy.Field()

class UidItem(scrapy.Item):
    uid_hongdun = scrapy.Field()
    corp_name_hongdun = scrapy.Field()

