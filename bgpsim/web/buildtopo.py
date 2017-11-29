# -*- coding: UTF-8 -*-
import json
import ConfigParser

conf = ConfigParser.ConfigParser()
conf.read("conf/web.conf")
nodefile = conf.get("topo", "nodefile")
linkfile = conf.get("topo", "linkfile")
path_conf = conf.get("path", "confpath")

f1 = open(path_conf + nodefile, "r")  # "BGP # 1.5.0.2/29|1.2.0.19/29 # 1005 # ASN-1005 # 1.5.0.0/16"
n = [0, 0, 0, 0]
nodes = []
iprr_name = {}
ip_host = {}
ip_first_ip = {}
for line in f1.readlines():
    s = {}
    s["click"] = 0
    string = line.strip().split("#")
    if len(string) == 7:
        if string[2] == "BGP":
            s['id'] = "BGP-router" + str(n[0])
            s['name'] = str(n[0])
            n[0] += 1
            s["ASN"] = string[4]
            s["ip"] = []
            s["type"] = "BGP-router"
            s["asname"] = string[5]
            s["prefix"] = string[6]
            s["suzhuip"] = string[0]
            s["suzhuid"] = string[1]
            for ip in string[3].split("|"):
                iprr_name[ip] = s['id']
                ip_host[ip.split("/")[0]] = string[0].split("/")[0]
                ip_first_ip[ip.split("/")[0]] = string[3].split("|")[0]
                s["ip"].append(ip)
            nodes.append(s)

f1.close()
f2 = open(path_conf + linkfile, "r")  # " 1001 # 1.1.0.18/29 # 1003 # 1.1.0.19/29 # 50M # P2C"
links = []


def findn(string):
    for i in xrange(len(nodes)):
        if nodes[i]['id'] == string:
            return i
    return -1


for line in f2.readlines():
    """
        暂时还没处理
    """
    t = line.strip().split("#")

    if len(t) == 6:

        asn1 = t[0]
        ip1 = t[1]
        asn2 = t[2]
        ip2 = t[3]
        value = t[4][:-1]
        shangye = t[5]

        """
        """

        d = {
            "source": "",
            "target": "",
            "value": ""
        }
        if (ip1 not in iprr_name) or (ip2 not in iprr_name):
            print "有条link找不到对应的node"
            continue
        else:
            d["source"] = iprr_name[ip1]
            d["target"] = iprr_name[ip2]
            d["zhanshi"] = "路由器1 名称:  " + ip_first_ip[ip1.split("/")[0]].split("/")[0] + "  此接口IP地址: " + ip1 + \
                "\n路由器2 名称:  " + ip_first_ip[ip2.split("/")[0]].split("/")[0] + "  此接口IP地址: " + ip2 + "\n商业关系: " + shangye
            d["value"] = value
            d["shangye"] = shangye
            links.append(d)
    else:
        s = {}
        s["click"] = 0
        s['id'] = "switch" + str(n[3])
        s['name'] = str(n[3])
        n[3] += 1
        s["ip"] = ""
        s["type"] = "switch"
        nodes.append(s)
        for i in xrange(len(t)):
            d = {
                "target": "",
                "source": s['id'],
                "value": 1
            }
            if t[i] not in iprr_name:
                print "有条link找不到对应的node"
                continue
            else:
                d["target"] = iprr_name[t[i]]
                links.append(d)

f2.close()

json_dict = {"nodes": nodes, "links": links}

json_str = json.dumps(json_dict, sort_keys=True,
                      separators=(',', ': '))  # indent=4,
