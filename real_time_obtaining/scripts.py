# encoding : utf-8

import MySQLdb


def do():
    mysql_conf = {
        "host": "39.106.165.57",
        "user": "root",
        "passwd": "949501wud",
        "db": "domain_valid_dns",
        "charset": "utf8"
    }
    try:
        db = MySQLdb.connect(**mysql_conf)
        cursor = db.cursor()
    except Exception as e:
        print e
        return
    get_domain_sql = "select domain from domain_ns"
    cursor.execute(get_domain_sql)
    domains = cursor.fetchall()
    with open("domain", 'w') as f:
        for d in domains:
            f.writelines(d)
            f.writelines("\n")

    print "done"


if __name__ == '__main__':
    do()
