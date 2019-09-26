#! /usr/bin/env python
# coding:utf-8
"""
whois client API server
=======================
Author@Wangjunxiong
Data@2019.9.26
"""

from flask import Flask
from gevent import monkey
from gevent.pywsgi import WSGIServer

monkey.patch_all()
app = Flask("Obtaining Dns")
app.config.update(DEBUG=True)

file_name = "effective_ApiNode.txt"
_port = 8048


def start():
    """API start"""
    _start = "API Server start\n"
    _start += "* For dns obtaining\n"
    _start += "* wud@WangJunxiong\n"
    http_server = WSGIServer(('', _port), app)
    http_server.serve_forever()


@app.route('/monitor/realtime/<domain>')
def obtaining(domain):
    """Get domain dns real time"""
    pass


@app.route('/check')
def check():
    """Get server status.
       but we this instance we do not need now.
    """


if __name__ == '__main__':
    start()