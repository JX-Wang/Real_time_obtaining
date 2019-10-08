# encoding:utf-8
"""
从顶级域名权威服务器开始，解析出域名的ns记录，以及其对应的IP地址
"""
from collections import defaultdict
import random
import dns
import dns.name
import dns.query
import dns.resolver


def get_authoritative_nameserver(domain, tld_ns_ip):
    """

    :param domain: string, 要查询的域名
    :param tld_ns_ip: string,顶级域名权威服务器的授权服务器IP地址
    :return:
        ns_status: string, 探测的状态
        ns_by_tld_ns: list, 域名在顶级域名权威服务器上的ns记录
        ns_ip_by_tld_ns: defaultdict(list), 域名的ns记录的A记录,列表格式
    """
    n = dns.name.from_text(domain)
    depth = 3  # 从域名的第三级开始，包括根，例如www.baidu.com，则是从baidu.com.进行探测
    # 配置本地递归服务器
    default_dns_resolver = dns.resolver.Resolver(configure=False)
    default_dns_resolver.timeout = 2
    nameservers = ['114.114.114.114','1.2.4.8','119.29.29.29','180.76.76.76']
    random.shuffle(nameservers)
    default_dns_resolver.nameservers = nameservers

    nameserver = tld_ns_ip  # 初始化权威服务器IP地址
    is_last = False
    ns_by_tld_ns = []  # 声明
    ns_ip_by_tld_ns = defaultdict(list) # 声明
    while not is_last:
        ns_by_tld_ns = []  # 每次循环初始化
        ns_ip_by_tld_ns = defaultdict(list)  # 每次循环初始化
        s = n.split(depth)
        is_last = s[0].to_unicode() == u'@'  # 是否到最后一级
        sub_domain = s[1]

        # print 'Looking up %s on %s' % (sub_domain, nameserver)
        query = dns.message.make_query(sub_domain, dns.rdatatype.NS)
        try:
            response = dns.query.udp(query, nameserver, timeout=2)
        except dns.resolver.Timeout:
            return "TIMEOUT", ns_by_tld_ns, ns_ip_by_tld_ns
        except Exception, e:
            return 'ERROR:%s' % str(e), ns_by_tld_ns, ns_ip_by_tld_ns

        rcode = response.rcode()
        if rcode != dns.rcode.NOERROR:
            if rcode == dns.rcode.NXDOMAIN:
                return 'NXDOMAIN', ns_by_tld_ns, ns_ip_by_tld_ns
            else:
                return 'ERROR:%s' % dns.rcode.to_text(rcode), ns_by_tld_ns, ns_ip_by_tld_ns

        if len(response.authority) > 0:
            response_rc = response.authority
        elif len(response.answer) > 0:
            response_rc = response.answer
        else:
            return "ERROR:无结果", ns_by_tld_ns, ns_ip_by_tld_ns

        for r in response_rc:
            for i in str(r.to_text()).split('\n'):
                i = i.split(' ')
                rc_type, rc_data = i[3], i[4]
                if rc_type == 'NS':
                    if rc_data.strip():
                        ns_name = rc_data[:-1].lower()
                        ns_by_tld_ns.append(ns_name)
                        # ns_ip_by_tld_ns[ns_name].append(rc_data)

        for r in response.additional:
            for i in str(r.to_text()).split('\n'):
                i = i.split(' ')
                rc_name, rc_type, rc_data = i[0].lower()[:-1], i[3], i[4]
                if rc_type == 'A':
                    if rc_data.strip(): # 特别注意，有A记录才记录
                        ns_ip_by_tld_ns[rc_name].append(rc_data)
        if not ns_by_tld_ns:
            return "ERROR:无结果", ns_by_tld_ns, ns_ip_by_tld_ns
        else:
            ns_ips = []
            for i in ns_ip_by_tld_ns.values():
                ns_ips.extend(i)
            ns_ips = list(set(ns_ips))
            if ns_ips:
                nameserver = random.choice(ns_ips)
            else:
                authority_ns = random.choice(ns_by_tld_ns)
                try:
                    nameserver = default_dns_resolver.query(authority_ns, 'A').rrset[0].to_text()
                except Exception, e:
                    return 'ERROR:%s' % str(e), ns_by_tld_ns, ns_ip_by_tld_ns

        depth += 1
    return 'TRUE', ns_by_tld_ns, ns_ip_by_tld_ns


if __name__ == '__main__':
    # domain = 'qzhubo.com'
    # domain = 'sina.com.cn'
    # tld_ns_ip = '192.26.92.30'
    # tld_ns_ip = '203.119.25.1'
    domain = 'ifeng.com'
    tld_ns_ip = '198.41.0.4'
    print get_authoritative_nameserver(domain, tld_ns_ip)