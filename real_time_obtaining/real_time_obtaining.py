#! /usr/bin/env python
# coding:utf-8
"""
whois client API server
=======================
Author@Wangjunxiong
Data@2019.9.26
"""

from flask import Flask, request
from gevent import monkey
from gevent.pywsgi import WSGIServer
import random

from resolving_domain_dns.resolving_domain_ns_combined import resolving_domain_ns
from ab_test import TEST

monkey.patch_all()
app = Flask("Obtaining Dns")
app.config.update(DEBUG=True)
TYPE = ['A', 'NS', 'AAAA', 'CNAME']
_port = 8048
f = open("domain", 'r')
DOMAIN = f.readlines()


def start():
    """API start"""
    _start = "API Server start\n"
    _start += "* For dns obtaining\n"
    _start += "* wud@WangJunxiong\n"
    http_server = WSGIServer(('', _port), app)
    http_server.serve_forever()


@app.route('/monitor/realtime/domain')
def obtaining():
    """Get domain dns real time"""
    domain = request.args.get('domain')
    req_type = request.args.get('type')
    # print domain, req_type
    ns_rst = resolving_domain_ns(domain)
    count = len(ns_rst)
    rst = {
            "domain": domain,
            "type": req_type,
            "count": count,
            "record": ns_rst
    }

    TEST.test_inser_db(domain=domain, ns=ns_rst)
    return rst


@app.route('/check')
def check():
    """Get server status.
       but we this instance we do not need now.
    """


@app.route('/abtest')
def abtest():
    """
    ab pressure test
    :return: NULL
    """
    domain = random.choice(DOMAIN).strip()
    print domain
    ns_rst = resolving_domain_ns(domain)
    print ns_rst
    TEST.test_inser_db(domain=domain, ns=ns_rst)
    return "Done"


if __name__ == '__main__':
    start()

"""
test url

http://39.106.165.57:8048/monitor/realtime/domain?domain=wudly.cn&type=NS


"""