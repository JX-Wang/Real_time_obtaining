# encoding : utf-8
import MySQLdb
TABLE = 'ns_test'


class TEST(object):
    def __init__(self):
        mysql_conf = {
            "host": "39.106.165.57",
            "user": "root",
            "passwd": "949501wud",
            "db": "TEST",
            "charset": "utf8"
        }
        try:
            self.db = MySQLdb.connect(**mysql_conf)
            self.cursor = self.db.cursor()
        except Exception as e:
            raise e

    def test_inser_db(self, domain, ns):
        sql = "INSERT INTO {table} (domain, ns) VALUE ('{domain}', '{ns}')".format(table=TABLE,
                                                                                   domain=domain,
                                                                                   ns=';'.join(ns))
        print sql
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print e
            self.db.rollback()


TEST = TEST()

