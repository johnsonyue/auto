# -*- coding: UTF-8 -*-
import tornado.web
import tornado.ioloop
import os
import sys
import json
import ConfigParser
from buildtopo import nodes, links, iprr_name, ip_host, ip_first_ip, json_str, path_conf


conf = ConfigParser.ConfigParser()
conf.read("conf/web.conf")
shared_dir = conf.get("path", "sharepath")
dockerpath = conf.get("path", "dockerpath")
remotepath = conf.get("path", "remotepath")

canshu = {}
canshu["first_flag"] = True
nodes2 = []


class Ping2Handler(tornado.web.RequestHandler):

    def get(self):

        self.write(str(2.2))


class PinHandler(tornado.web.RequestHandler):

    def get(self):
        filename = "ping-" + self.get_argument("file") + ".txt"
        rtt = 0
        icmp_seq = 0
        try:
            fpin = open("conf/" + filename, "r")
            ping = fpin.readlines()[-1].strip()
            icmp_seq = int(ping.split(" ")[4].split("=")[-1])
            rtt = float(ping.split(" ")[6].split("=")[-1])
            fpin.close()
        except Exception as e:
            icmp_seq = 0
            rtt = 0

        self.write(json.dumps({"icmp_seq": icmp_seq, "rtt": rtt}, sort_keys=True,
                              separators=(',', ': ')))

# if "icmp_seq" not in canshu:
        #     canshu["icmp_seq"] = icmp_seq
        # else:
        #     last_seq = canshu["icmp_seq"]
        #     if icmp_seq == last_seq:
        #         rtt = "0"
        #     canshu["icmp_seq"] = icmp_seq
        # self.write(rtt)


class PingstartHandler(tornado.web.RequestHandler):

    def get(self):
        start = self.get_argument("start")
        ip1 = self.get_argument("ip1")
        ip2 = self.get_argument("ip2")
        if start == "0":
            filename = "ping-" + ip1 + "-" + ip2 + ".txt"
            first_ip = ip_first_ip[ip1].split("/")[0]
            # ssh

            os.popen("./remote " + first_ip + " \"docker exec " + first_ip + " bash -c \'ping -n " + ip2 + "\'\" > conf/" + filename+";echo all clear")
            # print("./ssh-run.sh " + host_ip1 + " \"docker exec " + first_ip + " bash -c \'ping -n " + ip2 + "\'\" > conf/" + filename)

            self.write("ip1:" + ip1 + "\nip2:" + ip2)
        elif start == "1":
            first_ip = ip_first_ip[ip1].split("/")[0]
            # ssh
            os.popen("./remote " + first_ip + " \"docker exec " + first_ip + " bash -c \'killall ping\'\""+";echo all clear")
            self.write("ok")
        else:
            print 2
            self.write("start错误")


class JsoHandler(tornado.web.RequestHandler):

    def get(self):
        self.write(json_str)


class JsoHandler2(tornado.web.RequestHandler):

    def get(self):
        nodes2 = []
        # if canshu["first_flag"]:
        #     canshu["first_flag"] = False
        # n_control = -1
        # n_attack = -1

        n_js = []
        js_ips = canshu["IPs"].split(" ")
        name_attack = []
        name_control = ""
        name_js = []
        for key in iprr_name:
            if key.split("/")[0] == canshu["IP1"]:  # or key.split("/")[0] == canshu["route_ip"]:
                name_attack.append(iprr_name[key])
            elif key.split("/")[0] == canshu["control_ip"]:
                name_control = iprr_name[key]
            elif key.split("/")[0] in js_ips:
                name_js.append(iprr_name[key])

        for i in xrange(len(nodes)):
            nodes2.append(nodes[i])
            if nodes[i]["id"] == name_control:
                nodes2[i]["type"] = "host_control"
            elif nodes[i]["id"] in name_attack:
                if nodes2[i]["type"] == "host":
                    nodes2[i]["type"] = "host_attack"
                elif nodes2[i]["type"] == "router":
                    nodes2[i]["type"] = "router_attack"
                elif nodes2[i]["type"] == "BGP-router":
                    nodes2[i]["type"] = "BGP-router_attack"
            elif nodes[i]["id"] in name_js:
                n_js.append(i)
        for i in n_js:
            nodes2[i]["type"] = "host_js"

        self.write(json.dumps({"nodes": nodes2, "links": links}, sort_keys=True,
                              separators=(',', ': ')))


class ShoHandler(tornado.web.RequestHandler):

    def get(self):
        if "IP1" not in canshu:
            self.write("还没有发动过攻击！！")
        else:
            IP1 = canshu["IP1"]
            control_ip = canshu["control_ip"]
            IPs = canshu["IPs"]
            date = canshu["date"]
            time = canshu["time"]
            chixu = canshu["chixu"]
            meici = canshu["meici"]
            jiange = canshu["jiange"]
            wait = canshu["wait"]
            fuzai = canshu["fuzai"]
            fengzhi = canshu["fengzhi"]
            bandwidth = canshu["bandwidth"]
            route_ip = canshu["route_ip"]
            keepalive = canshu["keepalive"]
            holdtime = canshu["holdtime"]
            reconnect_time = canshu["reconnect_time"]
            dump_time = canshu["dump_time"]
            params = [IP1, control_ip, IPs, wait, date + " " +
                      time.replace("-", ":"), chixu, meici, jiange, fuzai, fengzhi, bandwidth]
            self.render("show.html", params=params)

    def post(self):
        IP1 = self.get_argument("attack_IP_address")
        control_ip = self.get_argument("control_IP_address")
        IPs = self.get_argument("js_IP_address")
        date = self.get_argument("date").replace("/", "-")
        time = self.get_argument("time").replace(":", "-")
        chixu = self.get_argument("chixu")
        meici = self.get_argument("meici")
        jiange = self.get_argument("jiange")
        wait = self.get_argument("wait")
        fuzai = self.get_argument("fuzai")
        fengzhi = self.get_argument("fengzhi")
        bandwidth = self.get_argument("bandwidth")
        keepalive = self.get_argument("keeptime")
        holdtime = self.get_argument("holdtime")
        reconnect_time = self.get_argument("reconnect_time")
        dump_time = self.get_argument("dump_time")
        route_ip = self.get_argument("route_ip")

        if wait == "":
            wait = "None"

        # print "attack_ip:%s\nbot_ip:%s\nwait:%s\nstart_time:%s-%s\nattack_time:%s\nper_attack_time:%s\nattack_frequency:%s\nlength:%s\nmax:%s\n" %\
        #     (IP1, IPs, wait, date, time, chixu, meici, jiange, fuzai, fengzhi)

        canshu["IP1"] = IP1
        canshu["control_ip"] = control_ip
        canshu["IPs"] = IPs
        canshu["date"] = date
        canshu["time"] = time
        canshu["chixu"] = chixu
        canshu["meici"] = meici
        canshu["jiange"] = jiange
        canshu["wait"] = wait
        canshu["fuzai"] = fuzai
        canshu["fengzhi"] = fengzhi
        canshu["bandwidth"] = bandwidth
        canshu["route_ip"] = route_ip
        canshu["keepalive"] = keepalive
        canshu["holdtime"] = holdtime
        canshu["reconnect_time"] = reconnect_time
        canshu["dump_time"] = dump_time
        params = [IP1, control_ip, IPs, wait, date + "-" + time, chixu, meici, jiange, fuzai, fengzhi, bandwidth]

        # 传文件
        info = open(shared_dir + "attack_info.cfg", 'w')
        #info = open("conf/attack_info2.cfg", 'w')
        info.write("[attack_ip]\nattack_ip = %s\n" % (IP1))
        info.write("[wait]\nwait = %s\n" % (wait))
        info.write("[start_time]\nstart_time = %s-%s\n" % (date, time))
        info.write("[attack_time]\nattack_time = %s\n" % (chixu))
        info.write("[per_attack_time]\nper_attack_time = %s\n" % (meici))
        info.write("[attack_frequency]\nattack_frequency = %s\n" % (jiange))
        info.write("[length]\nlength = %s\n" % (fuzai))
        info.write("[max]\nmax = %s\n" % (fengzhi))
        info.write("[control_ip]\ncontrol_ip = %s\n" % (control_ip))
        info.write("[route_ip]\nroute_ip = %s\n" % (route_ip))
        info.write("[keep_hold]\nkeep_hold = %s %s\n" % (keepalive, holdtime))
        info.write("[reconnect_time]\nreconnect_time = %s\n" % (reconnect_time))
        info.write("[up_down]\nup_down = %s\n" % (bandwidth))
        info.write("[dump_time]\ndump_time = %s\n" % (dump_time))
        info.write("[bot_ip]\n")

        ips = IPs.split(" ")
        for n in xrange(len(ips)):
            info.write("bot_ip_" + str(n + 1) + " = " + ips[n] + "\n")

        info.close()

        #os.popen("python " + shared_dir + "auto.py > conf/attack_result.txt")
        print ("./ssh-run.sh "+control_ip+" \"sh -c 'cat >"+shared_dir+"attack_info.cfg << EOT\\n$(cat "+shared_dir+"attack_info.cfg)'\"")
        os.system("./ssh-run.sh "+control_ip+" \"sh -c 'cat >"+shared_dir+"attack_info.cfg << EOT\\n$(cat "+shared_dir+"attack_info.cfg)'\"")
        self.render("show.html", params=params)
        print ("./remote "+control_ip+" \"" + shared_dir + "auto_run 2>&1 \" | tee "+remotepath+"conf/attack_result.txt")
        os.system("./remote "+control_ip+" \"" + shared_dir + "auto_run 2>&1 \" | tee "+remotepath+"conf/attack_result.txt")
        # os.popen("./ssh-run.sh " + control_ip + " \"docker exec " + control_ip +
        #          " bash -c \'python " + dockerpath + "bot_control.py &\'\"")
        # print("./ssh-run.sh " + control_ip + " \"docker exec " + control_ip +
        #       " bash -c \'python /home/quagga/bot_control.py &\'\"")
        # os.popen("./ssh-run.sh " + host_ip + " \"docker exec " + IP1 +
        #          " bash -c \'" + dockerpath + "tc-control.sh " + bandwidth + "\'\"")
        # print("./ssh-run.sh " + IP1 + " \"docker exec " + IP1 +
        #       " bash -c \'/home/quagga/tc-control.sh " + bandwidth + "\'\"")
        #self.render("show.html", params=params)


class MainHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("form.html")


class PgHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("ping.html")


class GrapHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("graph3.html")


class XieHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("xielou.html")

    def post(self):
        asn = self.get_argument("zhixing")
        aslist = self.get_argument("aslist")
        # 传文件

        f_xielou = open(shared_dir + "leak.conf", "w")
        f_xielou.write("[leak]\n")
        f_xielou.write("asn=%s\nleaks=[%s]" % (asn, aslist))
        f_xielou.close()

        os.popen("python " + shared_dir + "leak_bgp.py -l")

        self.render("xielou.html")


class RoutetableHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("routetable.html")


class Traceroute2Handler(tornado.web.RequestHandler):

    def get(self):
        self.render("traceroute2.html")


class LLHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("liuliang.html")


class VtyshHandler(tornado.web.RequestHandler):

    def get(self):
        flag = self.get_argument("start")
        asn = self.get_argument("asn")
        if flag == "0":
            os.popen("python " + shared_dir + "print_router.py --asn=" + asn + " | sed s/\\\\r//g > conf/routertable-" + asn + ".txt")
            self.write("1")
        else:
            result = ""
            f_rtable = open("conf/routertable-" + asn + ".txt", "r")
            result = f_rtable.read()
            f_rtable.close()
            self.write(result)


class HuifuHandler(tornado.web.RequestHandler):

    def get(self):
        # print "python " + shared_dir + "leak_bgp.py -l"
        os.popen("python " + shared_dir + "leak_bgp.py -r")
        self.write("ok")


class TracerouteHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("traceroute.html")


class TcpdumpHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("tcpdump.html")


class NewpingHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("p_and_t.html")


class Trace2Handler(tornado.web.RequestHandler):

    def get(self):
        flag = self.get_argument("start")
        if flag == "0":
            asn1 = self.get_argument("asn1")
            asn2 = self.get_argument("asn2")
            os.popen("python " + shared_dir + "print_router.py --asn=" + asn1 + "  > conf/traceroute2" + asn1 + "-" + asn2 + ".txt")
            self.write("1")
        else:
            file = self.get_argument("file")
            result = ""
            f_rtable = open("conf/traceroute2-" + file + ".txt", "r")
            result = f_rtable.read()
            f_rtable.close()
            self.write(result)


class TcpHandler(tornado.web.RequestHandler):

    def get(self):
        f_path = open(shared_dir + "web_tcpdump_filename.txt")
        filename = f_path.read().strip()
        f_path.close()
        result = ""
        f_result = open(filename)
        result = f_result.read()
        f_result.close()
        self.write(result)


msg = {}
msg["wrong"] = "未traceroute过"


class TraceHandler(tornado.web.RequestHandler):

    def get(self):
        start = self.get_argument("start")
        msg["wrong"] = ""
        if start == "0":
            msg["wrong"] = ""
            ip1 = self.get_argument("ip1")
            ip2 = self.get_argument("ip2")
            filename = "traceroute-" + ip1 + "-" + ip2 + ".txt"
            if ip1 in ip_host:
                first_ip = ip_first_ip[ip1].split("/")[0]
                # ssh
                os.popen("./remote " + first_ip + " \"docker exec " + first_ip + " bash -c \'traceroute " + ip2 + "\'\" > conf/" + filename+";echo all clear")
            else:
                msg["wrong"] = "输入的ip不存在于网络中"

        elif start == "1":
            # 判断是否完成
            self.write("0")
        elif start == "2":
            filename = "traceroute-" + self.get_argument("file") + ".txt"
            try:
                f_traceresult = open("conf/" + filename, "r")
                result = f_traceresult.read()
                f_traceresult.close()
                self.write(result)
            except Exception as e:
                msg["wrong"] += " 命令有错，没有成功写入文件"
                print e
                self.write("输入的ip不存在于网络中 或 命令有错，没有成功写入文件")
        elif start == "3":
            ip1 = self.get_argument("ip1")
            ip2 = self.get_argument("ip2")
            filename = "traceroute-" + ip1 + "-" + ip2 + ".txt"
            try:
                f_traceresult = open("conf/" + filename, "r")
                lines = f_traceresult.readlines()
                f_traceresult.close()

                nowid = {}
                n = 0
                for key in iprr_name:
                    if key.split("/")[0] == ip1:
                        nowid[chr(n + ord('A'))] = iprr_name[key]
                        n += 1
                        break
                for line in lines:
                    line = line.strip()
                    neirong = line.split(" ")

                    if len(neirong) == 13:
                        for key in iprr_name:
                            if key.split("/")[0] == neirong[3][1:-1]:
                                nowid[chr(n + ord('A'))] = iprr_name[key]
                                n += 1
                                break

                self.write(json.dumps(nowid, sort_keys=True, separators=(',', ': ')))

            except Exception as e:
                msg["wrong"] += " 命令有错，没有成功写入文件"
                print e
                self.write("输入的ip不存在于网络中 或 命令有错，没有成功写入文件")


class SnikeHandler(tornado.web.RequestHandler):

    def get(self):
        start = self.get_argument("start")
        ip = self.get_argument("ip")
        if start == "0":
            if ip in ip_host:
                first_ip = ip_first_ip[ip].split("/")[0]
                # ssh
                os.popen("./ssh-run.sh " + first_ip + " \"docker exec " + first_ip + " bash -c \'sh " + dockerpath + "get-host-ip-address.sh\'\" ")
                os.popen("./ssh-run.sh " + first_ip + " \"cat " + shared_dir + "host-ip-address \" > conf/host-ip-address")
                f_eth = open("conf/host-ip-address", "r")
                ethname = ""
                for line in f_eth.readlines()[2:]:
                    line = line.strip()
                    eth = line.split(":")[0]
                    ethip = line.split(":")[1]
                    if ethip == ip:
                        ethname = eth
                        break
                if ethname == "":
                    print "找不到网卡"
                    self.write("ip wrong!")
                else:
                    os.popen("./ssh-run.sh " + first_ip + " \"docker exec " + first_ip + " bash -c \'sh " + dockerpath + "snike.sh " + ethname + " \'\" > conf/router_interface_flow-" + ip + ".info")
                    self.write("ok")
            else:
                print "ip no!"
                self.write("ip wrong!")

        elif start == "1":
            filename = "router_interface_flow-" + self.get_argument("ip") + ".info"
            try:
                f_flowresult = open("conf/" + filename, "r")
                result = f_flowresult.readlines()[-1].strip().split(" ")[-1]
                # print result
                f_flowresult.close()
                self.write(result)
            except Exception as e:
                self.write("wrong")
        elif start == "2":
            if ip in ip_host:
                first_ip = ip_first_ip[ip].split("/")[0]
                ethname = ""
                # ssh
                os.popen("./ssh-run.sh " + first_ip + " \"docker exec " + first_ip + " bash -c \'sh " + dockerpath + "get-host-ip-address.sh\'\" ")
                f_eth = open(shared_dir + "host-ip-address", "r")
                for line in f_eth.readlines():
                    line = line.strip()
                    eth = line.split(":")[0]
                    ethip = line.split(":")[1]
                    if ethip == ip:
                        ethname = eth
                        break
                if ethname == "":
                    self.write("ip wrong!")
                else:
                    os.popen("./ssh-run.sh " + first_ip + " \"docker exec " + first_ip + " bash -c \'ps aux | grep 'snike.sh' | awk '{print $2}' | xargs kill \'\"")
                    self.write("ok")
            else:
                self.write("ip wrong!")


class DefaultHandler(tornado.web.RequestHandler):

    def get(self):
        try:
            # conf = ConfigParser.ConfigParser()
            # conf.read("/home/yupeng/quagga/attack_info.cfg")
            dic = {}
            conf = ConfigParser.ConfigParser()
            conf.read(shared_dir + "attack_info.cfg")
            sections = conf.sections()
            for sec in sections:
                if sec == "keep_hold":
                    dic["keeptime"] = conf.items(sec)[0][1].split(" ")[0]
                    dic["holdtime"] = conf.items(sec)[0][1].split(" ")[1]
                elif sec == "bot_ip":
                    ip_list = []
                    items = conf.items(sec)
                    for item in items:
                        ip_list.append(item[1])
                    dic[sec] = " ".join(ip_list)
                else:
                    items = conf.items(sec)
                    # it = []
                    for item in items:
                        dic[item[0]] = item[1]
                # dic[sec] = items[1]

            cfg_json = json.dumps(dic, sort_keys=True, separators=(',', ': '))

            self.write(cfg_json)
        except Exception as e:
            print e
            self.write("nothing")


class PTHandler(tornado.web.RequestHandler):

    def get(self):
        try:
            # conf = ConfigParser.ConfigParser()
            # conf.read("/home/yupeng/quagga/attack_info.cfg")
            dic = {}
            f_pt = open("conf/p_and_t.cfg", "r")
            for line in f_pt.readlines():
                line = line.strip()
                dic[line.split("=")[0]] = line.split("=")[1]

            cfg_json = json.dumps(dic, sort_keys=True, separators=(',', ': '))

            self.write(cfg_json)
        except Exception as e:
            print e
            self.write("nothing")


class ResultHandler(tornado.web.RequestHandler):

    def get(self):
        try:
            fr = open("conf/attack_result.txt", "r")
            result = fr.read()

            fr.close()
        except Exception as e:
            result = ""
        self.write(result)


class GraphHandler(tornado.web.RequestHandler):

    def get(self):

        self.write()


settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static")
}


if __name__ == "__main__":

    # tornado.options.parse_command_line()
    application = tornado.web.Application(
        handlers=[
            (r"/", GrapHandler),
            (r"/form", MainHandler),
            (r"/show", ShoHandler),
            (r"/xielou", XieHandler),
            (r"/pinggraph", PgHandler),
            (r"/tcpdump", TcpdumpHandler),
            (r"/traceroute", TracerouteHandler),
            (r"/traceroute2", Traceroute2Handler),
            (r"/routetable", RoutetableHandler),
            (r"/liuliang", LLHandler),
            (r"/newping", NewpingHandler),

            (r"/myjson", JsoHandler),
            (r"/myjson2", JsoHandler2),
            (r"/ping", PinHandler),
            (r"/ping2", Ping2Handler),
            (r"/pingstart", PingstartHandler),
            (r"/trace", TraceHandler),
            (r"/trace2", Trace2Handler),
            (r"/tcp", TcpHandler),
            (r"/huifu", HuifuHandler),
            (r"/vtysh", VtyshHandler),
            (r"/default_form", DefaultHandler),
            (r"/attack_result", ResultHandler),
            (r"/tcp", TcpHandler),
            (r"/p_and_t", PTHandler),
            (r"/snike", SnikeHandler)
        ],
        debug=False,
        **settings
    )

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.bind(8880)
    http_server.start(0)
    # http_server.listen(8880)
    tornado.ioloop.IOLoop.instance().start()
