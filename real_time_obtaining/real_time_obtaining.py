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
from resolving_domain_dns.resolving_domain_ns_combined import resolving_domain_ns
monkey.patch_all()
app = Flask("Obtaining Dns")
app.config.update(DEBUG=True)
TYPE = ['A', 'NS', 'AAAA', 'CNAME']
_port = 8048


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
    print domain, req_type
    ns_rst = resolving_domain_ns(domain)
    count = len(ns_rst)
    rst = {
            "domain": domain,
            "type": req_type,
            "count": count,
            "record": ns_rst
    }
    print rst
    return rst


@app.route('/check')
def check():
    """Get server status.
       but we this instance we do not need now.
    """


if __name__ == '__main__':
    start()