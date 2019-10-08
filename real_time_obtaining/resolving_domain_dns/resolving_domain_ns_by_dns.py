# encoding:utf-8
"""
利用DNS递归服务器，获取域名的NS服务器
"""
import dns.resolver
import random
from collections import defaultdict


def obtaining_domain_ns_by_dns(main_domain, timeout=2):
    """
    向DNS递归服务器请求域名的ns记录，以及ns的IP地址
    :param main_domain: string，域名的主域名
    :param timeout: int, 超时时间
    :return:
        ns: list, 域名的ns记录
        ns_ip: defaultdict(list), 域名的各个ns的A记录
        ns_status: string，获取记录的状态情况
    """

    ns = []
    ns_ip = defaultdict(list)
    resolver = dns.resolver.Resolver(configure=False)
    resolver.timeout = timeout
    resolver.lifetime=timeout*3
    nameservers = ['114.114.114.114', '1.2.4.8', '119.29.29.29', '180.76.76.76']

    try:
        random.shuffle(nameservers)
        resolver.nameservers = nameservers
        dns_resp = dns.resolver.query(main_domain, 'NS')
        try:
            for i in dns_resp.response.additional:
                r = str(i.to_text())
                for i in r.split('\n'):  # 注意
                    i = i.split(' ')
                    rc_name, rc_type, rc_data = i[0].lower()[:-1], i[3], i[4]
                    if rc_type == 'A':
                        if rc_data.strip():
                            ns_ip[rc_name].append(rc_data)
        except Exception, e:
            print str(e)

        for r in dns_resp.response.answer:
            r = str(r.to_text())
            for i in r.split('\n'):
                i = i.split(' ')
                ns_domain, rc_type, rc_data = i[0], i[3], i[4]
                if ns_domain[:-1].strip() != main_domain:
                    continue
                if rc_type == 'NS':
                    if rc_data.strip():
                        ns.append(str(i[4][:-1]).lower())
        ns_status = 'TRUE'
        ns.sort()
    except dns.resolver.NoAnswer:
        ns_status = 'NO ANSWERS'
    except dns.resolver.NXDOMAIN:
        ns_status = "NXDOMAIN"  # 尝试一次
    except dns.resolver.NoNameservers:
        ns_status = 'NO NAMESERVERS'  # 尝试一次
    except dns.resolver.Timeout:
        ns_status = 'TIMEOUT'
    except Exception, e:
        ns_status = 'UNEXPECTED ERRORS:'+str(e)

    return ns, ns_ip, ns_status


if __name__ == '__main__':
    print obtaining_domain_ns_by_dns('jd.com')
