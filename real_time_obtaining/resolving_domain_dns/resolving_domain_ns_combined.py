# encoding:utf-8
"""
结合顶级域名和域名的权威服务器，获取域名的ns记录，获取逻辑详见开发文档
@author: 程亚楠
"""

import random
from resolving_domain_ns_by_tld import get_authoritative_nameserver # 获取域名dns
from resolving_domain_ns_by_ns import query_domain_ns_by_ns  # 获取域名dns
from resolving_domain_ns_by_dns import obtaining_domain_ns_by_dns
from collections import defaultdict
from resolving_ip_cname_by_dns import obtaining_domain_ip

root_ns_ip = [
'198.41.0.4',
'199.9.14.201',
'192.33.4.12',
'199.7.91.13',
'192.203.230.10',
'192.5.5.241',
'192.112.36.4',
'198.97.190.53',
'192.36.148.17',
'192.58.128.30',
'193.0.14.129',
'199.7.83.42',
'202.12.27.33'
]


def resolving_domain_ns_by_tld(main_domain, tld_ns_ip):
    """
    向顶级域名权威服务器请求域名的NS记录
    :param main_domain:  string，主域名
    :param tld_ns_ip: list，域名对应的顶级域名的权威服务器ip地址集合
    :return
        ns_by_tld: list，通过顶级域名权威获取的域名的ns名称
        ns_ip_by_tld: dict, 通过顶级域名权威获取的域名的ns的IP地址
    方法介绍：
       1）将域名发送到其顶级域名到权威服务器IP地址集合中，查询域名的ns记录
       2）若返回True，则不再向其他权威服务器发送
       3）若返回其他，则继续向其他地址发送，直到结束
    """
    ns_by_tld = []
    ns_ip_by_tld = {}
    if not tld_ns_ip:
        return ns_by_tld, ns_ip_by_tld
    for ip in tld_ns_ip:
        ns_status, ns_by_tld, ns_ip_by_tld = get_authoritative_nameserver(main_domain, ip)  # 向根节点--》顶级权威获取域名的权威地址
        if ns_status == 'TIMEOUT':  # 获取成功则停止
            continue
        else:
            break  # 停止探测
    return list(set(ns_by_tld)), ns_ip_by_tld


def resolving_domain_ns_by_ns(main_domain, ns_by_tld, ns_ip_by_tld=None):
    """
    向域名自身的权威服务器请求ns，获取其上的的ns记录集合
    :param main_domain: string，主域名
    :param ns_by_tld: list，tld解析的域名的ns权威服务器地址名称集合
    :param ns_ip_by_tld: defaultdict，tld解析的域名的ns权威服务器的IP地址名称集合
    :return list domain_ns: 经过验证后的有效域名ns地址集合
    """

    if ns_ip_by_tld is None:
        ns_ip_by_tld = defaultdict(list)

    ns_by_ns = []
    ns_ip_by_ns = defaultdict(list)
    random.shuffle(ns_by_tld)  # 随机
    ns_status = 'FALSE'
    for ns in ns_by_tld:
        ip = ns_ip_by_tld.get(ns)
        ns_by_ns, ns_ip_by_ns, ns_status = query_domain_ns_by_ns(main_domain, ns, ip)
        if ns_status == 'TIMEOUT':
            continue
        else:
            break
    # 做这个步骤的原因：在一些网络中，无法访问某些域名的权威服务器，原因可能是防火墙管制，所以要进行第二次验证。
    # 这种情况导致增加探测次数，降低探测效率
    if ns_status == 'TRUE':
        return ns_by_ns, ns_ip_by_ns
    else:
        ns_by_ns, ns_ip_by_ns, ns_status = obtaining_domain_ns_by_dns(main_domain)
        return ns_by_ns, ns_ip_by_ns


def get_last_ns_ip(domain_ns, ns_by_tld_ip, ns_by_ns_ip):
    """
    得到域名的权威DNS服务器的IP地址
    :param domain_ns: list，域名的权威服务器名称集合
    :param ns_by_tld_ip: defaultdict(list), 来自顶级域名的域名权威服务器的IP地址
    :param ns_by_ns_ip: defaultdict(list), 来自域名权威的域名权威服务器的IP地址
    :return:
        domain_ns_ip: defaultdict, 域名的权威服务器的IP地址列表
    """
    domain_ns_ip = defaultdict(list)
    for ns in domain_ns:
        ns_ip = ns_by_ns_ip.get(ns)
        tld_ip = ns_by_tld_ip.get(ns)
        if ns_ip:  # 首先查看权威服务器上是否含有IP
            if '#' in ','.join(ns_ip):
                new_ns_ip,_,_ = obtaining_domain_ip(ns)
            else:
                new_ns_ip = ns_ip
        else:
            if tld_ip:  # 第二查看顶级权威服务器上是否含有IP
                if '#' in ','.join(tld_ip):
                    new_ns_ip, _, _ = obtaining_domain_ip(ns)
                else:
                    new_ns_ip = tld_ip
            else:  # 上述两个地方都无，则在线获取其IP地址
                new_ns_ip, _, _ = obtaining_domain_ip(ns)  # 在线获取
        domain_ns_ip[ns] = new_ns_ip  # 无论ns是否有IP地址，都会返回
    return domain_ns_ip


def compared_ns_ip(new_ns_ip, old_ns_ip):
    """
    比较新旧域名权威服务器的A记录（IP）是否一致
    :param new_ns_ip:
    :param old_ns_ip:
    :return: 0:不更新；1：更新
    """
    is_update = 0
    for ns in new_ns_ip:
        new_ip = new_ns_ip[ns]
        old_ip = old_ns_ip.get(ns)
        if old_ip == ['']:
            old_ip = []
        new_ip.sort()
        old_ip.sort()

        if not set(new_ip).issubset(set(old_ip)):  # 若不包含在里面，则更新
            is_update = 1
            break
    return is_update


def resolving_domain_ns(main_domain):
    """
    结合顶级域名和域名权威服务器解析域名的NS记录
    :param main_domain: string, 域名对应的主域名
    :param tld_ns_ip: list, 域名的顶级域名对应的权威服务器IP地址集合
    :param old_ns: list, 域名原有的ns地址
    :param old_ns_ip: defaultdict, 域名的ns地址的ip地址
    :return:
        domain_ns, list, 域名的ns域名集合
        domain_ns_ip, defaultdict, 域名的ns名称的ip地址
        update_mysql，是否需要更新mysql的标记位，0：不更新；1：更新
    """
    tld_ns_ip = resolving_tld_ns(main_domain)
    ns_by_tld, ns_by_tld_ip = resolving_domain_ns_by_tld(main_domain, tld_ns_ip)   # 通过顶级域名权威获取域名的ns
    if ns_by_tld:  # 顶级域名权威服务器返回域名ns记录不为空
        ns_by_ns, ns_by_ns_ip = resolving_domain_ns_by_ns(main_domain, ns_by_tld, ns_by_tld_ip)  # 通过域名的权威服务器获取权威ns地址
        return ns_by_ns
    else:
        return []


def resolving_tld_ns(main_domain):
    """向根服务器查询顶级域名的IP地址"""
    ns_by_root, ns_by_tld_ip = resolving_domain_ns_by_tld(main_domain, root_ns_ip)   # 通过顶级域名权威获取域名的ns
    tld_ns_ip = []
    for k in ns_by_tld_ip:
        tld_ns_ip.extend(ns_by_tld_ip[k])
    return tld_ns_ip


def main():
    main_domain = 'hit.com'
    print resolving_domain_ns(main_domain)


if __name__ == '__main__':
    main()
