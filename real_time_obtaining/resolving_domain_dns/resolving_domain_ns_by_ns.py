#encoding:utf-8
"""
向域名的权威域名服务器查询域名IP和CNAME
"""
import dns
import random
import dns.query
import dns.resolver
from resolving_ip_cname_by_dns import obtaining_domain_ip
from collections import defaultdict


def query_domain_ns_by_ns(domain, authoritative_ns, authoritative_ips=None, timeout=2):
    """
    向域名的NS权威服务器查询域名的IP记录，若有CNAME，则获取CNAME的记录
    :param domain: stirng, 要查询的域名，注意为主域名
    :param authoritative_ns: string，域名的权威服务器名称
    :param authoritative_ips: list, 域名的权威服务器IP地址集合，默认为None
    :param timeout: int, 超时时间
    :returns
        domain_ns, list，域名的来自授权权威的NS记录
        domain_ns_ip, defaultdict(list)，域名的ns服务器的IP地址
        ns_status, string, 获取信息的状态
    """

    domain_ns = []
    domain_ns_ip = defaultdict(list)
    ns_status = 'FALSE'

    # 若无权威的IP地址，则首先解析出IP地址
    if not authoritative_ips:
        authoritative_ips, _, auth_ip_cname_status = obtaining_domain_ip(authoritative_ns)
        if auth_ip_cname_status != "TRUE":
            return domain_ns, domain_ns_ip, ns_status

    query = dns.message.make_query(domain, dns.rdatatype.NS)
    random.shuffle(authoritative_ips)
    # 获取权威信息地址
    for ip in authoritative_ips:
        try:
            response = dns.query.udp(query, ip, timeout=timeout)
            # 获取additional块中的A记录信息，可能无
            try:
                for i in response.additional:
                    r = str(i.to_text())
                    for i in r.split('\n'):  # 注意
                        i = i.split(' ')
                        rc_name, rc_type, rc_data = i[0].lower()[:-1], i[3], i[4]
                        if rc_type == 'A':
                            if rc_data.strip():
                                domain_ns_ip[rc_name].append(rc_data)
            except Exception, e:
                print '异常：%s' % str(e)

            # 获取NS地址
            for rrset in response.answer:
                r = str(rrset.to_text())
                for i in r.split('\n'):  # 注意
                    i = i.split(' ')
                    rc_type, rc_data = i[3], i[4]
                    if rc_type == 'NS':
                        if rc_data.strip():
                            domain_ns.append(rc_data[:-1].lower())
            ns_status = 'TRUE'
            break
        except dns.resolver.NoAnswer:
            ns_status = 'NO ANSWERS'
            break
        except dns.resolver.NXDOMAIN:
            ns_status = "NXDOMAIN"  # 只执行一次
            break
        except dns.resolver.NoNameservers:
            ns_status = 'NO NAMESERVERS'
            break
        except dns.resolver.Timeout:
            ns_status = 'TIMEOUT'
        except Exception, e:
            ns_status = str(e)
            break
    domain_ns = filter(None,domain_ns)  # 去掉空字符串
    return domain_ns, domain_ns_ip, ns_status


if __name__ == '__main__':

    print query_domain_ns_by_ns ('hitwh.edu.cn','dns2.hitwh.edu.cn')
    print query_domain_ns_by_ns ('baidu.com', 'dns.baidu.com')
    print query_domain_ns_by_ns ('toutiao.com', 'vip4.alidns.com')
