from chacha.settings import *
import pymysql


class DBConfig(object):
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
        # # 初始化表格1 ------ 基础表格
        # self.cursor.execute\
        #     ("""Create TABLE IF NOT EXISTS '%s' (
        #     url VARCHAR(200),
        #     uid_chacha VARCHAR(200) KEY,
        #     corp_name VARCHAR(100),
        #     corp_tele VARCHAR(100),
        #     corp_website VARCHAR(100),
        #     corp_email VARCHAR(100),
        #     corp_addr VARCHAR(2000),
        #     faren VARCHAR(30),
        #     registered_capital VARCHAR(30),
        #     issued_capital VARCHAR(30),
        #     corp_status VARCHAR(30),
        #     estab_date DATE,
        #     socialcredit_code VARCHAR(30) KEY,
        #     taxpayer_code VARCHAR(30) KEY,
        #     registered_code VARCHAR(30) KEY,
        #     org_code VARCHAR(30),
        #     business_type VARCHAR(200),
        #     industry VARCHAR(200),
        #     issue_date DATE,
        #     registrar VARCHAR(100),
        #     district VARCHAR(100),
        #     english_name VARCHAR(100),
        #     other_name VARCHAR(100),
        #     insured_staff_number VARCHAR(30),
        #     scale VARCHAR(30),
        #     term_business VARCHAR(100),
        #     business_scope VARCHAR(2000),
        #     );""" % ITEM_BASICS_TABLE)
        #
        # if_exists = self.conn.commit()
        #
        # # 设置数据库可以储存中文
        # if if_exists == 1:
        self.cursor.execute("""ALTER TABLE %s CHANGE corp_name corp_name VARCHAR(100) character SET utf8 collate utf8_unicode_ci default '';"""%ITEM_BASICS_TABLE)
        self.conn.commit()
        self.cursor.execute("""ALTER TABLE %s CHANGE corp_website corp_website VARCHAR(100) character SET utf8 collate utf8_unicode_ci default '';"""%ITEM_BASICS_TABLE)
        self.conn.commit()
        self.cursor.execute("""ALTER TABLE %s CHANGE faren faren VARCHAR(30) character SET utf8 collate utf8_unicode_ci default '';"""%ITEM_BASICS_TABLE)
        self.conn.commit()
        self.cursor.execute("""ALTER TABLE %s CHANGE registered_capital registered_capital VARCHAR(30) character SET utf8 collate utf8_unicode_ci default '';"""%ITEM_BASICS_TABLE)
        self.conn.commit()
        self.cursor.execute("""ALTER TABLE %s CHANGE issued_capital issued_capital VARCHAR(30) character SET utf8 collate utf8_unicode_ci default '';"""%ITEM_BASICS_TABLE)
        self.conn.commit()
        self.cursor.execute("""ALTER TABLE %s CHANGE corp_status corp_status VARCHAR(30) character SET utf8 collate utf8_unicode_ci default '';"""%ITEM_BASICS_TABLE)
        self.conn.commit()
        self.cursor.execute("""ALTER TABLE %s CHANGE business_type business_type VARCHAR(200) character SET utf8 collate utf8_unicode_ci default '';"""%ITEM_BASICS_TABLE)
        self.conn.commit()
        self.cursor.execute("""ALTER TABLE %s CHANGE industry industry VARCHAR(200) character SET utf8 collate utf8_unicode_ci default '';"""%ITEM_BASICS_TABLE)
        self.conn.commit()
        self.cursor.execute("""ALTER TABLE %s CHANGE registrar registrar VARCHAR(100) character SET utf8 collate utf8_unicode_ci default '';"""%ITEM_BASICS_TABLE)
        self.conn.commit()
        self.cursor.execute("""ALTER TABLE %s CHANGE district district VARCHAR(100) character SET utf8 collate utf8_unicode_ci default '';"""%ITEM_BASICS_TABLE)
        self.conn.commit()
        self.cursor.execute("""ALTER TABLE %s CHANGE other_name other_name VARCHAR(100) character SET utf8 collate utf8_unicode_ci default '';"""%ITEM_BASICS_TABLE)
        self.conn.commit()
        self.cursor.execute("""ALTER TABLE %s CHANGE term_business term_business VARCHAR(100) character SET utf8 collate utf8_unicode_ci default '';"""%ITEM_BASICS_TABLE)
        self.conn.commit()
        self.cursor.execute("""ALTER TABLE %s CHANGE business_scope business_scope VARCHAR(2000) character SET utf8 collate utf8_unicode_ci default '';"""%ITEM_BASICS_TABLE)


        # # 初始化表格2 ------ 基础表格
        # self.cursor.execute \
        #     ("""Create TABLE IF NOT EXISTS %s (
        #         corp_name VARCHAR(100),
        #         ic_code VARCHAR(30) KEY,
        #         legal_person VARCHAR(10),
        #         addr VARCHAR(2000),
        #         uid VARCHAR(200),
        #         );""" % ITEM_RISK_TABLE)
        #
        # if_exists = self.conn.commit()
        #
        # if if_exists == 1:
        #     # 设置数据库可以储存中文
        #     self.cursor.execute(
        #         """ALTER TABLE %s CHANGE corp_name corp_name VARCHAR(100) character SET utf8 collate utf8_unicode_ci default '';""" % ITEM_TABLE)
        #     self.conn.commit()
        #     self.cursor.execute(
        #         """ALTER TABLE %s CHANGE legal_person legal_person VARCHAR(40) character SET utf8 collate utf8_unicode_ci default '';""" % ITEM_TABLE)
        #     self.conn.commit()
        #     self.cursor.execute(
        #         """ALTER TABLE %s CHANGE addr addr VARCHAR(2000) character SET utf8 collate utf8_unicode_ci default '';""" % ITEM_TABLE)
        #     self.conn.commit()

    def insert_by_sql(self, sql, data=None):
        self.cursor.execute(sql, data)
        try:
            self.conn.commit()
        except:
            self.conn.rollback()
            print(str(data['ic_code']) + "导入失败")

