# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 20:45:39 2017

@author: zyl
"""
import os
import ConfigParser  

conf = ConfigParser.ConfigParser()  
conf.read("/home/yupeng/quagga/attack_info.cfg")  

control_ip = conf.get("control_ip", "control_ip")
route_ip_list = []
route_ip_list.append(conf.get("route_ip", "route_ip"))
route_ip_list.append(conf.get("attack_ip", "attack_ip"))
keep_hold = conf.get("keep_hold", "keep_hold")
reconnect_time = conf.get("reconnect_time", "reconnect_time")
up_down = conf.get("up_down", "up_down")
dump_time = conf.get("dump_time", "dump_time")
bot_ip_route = conf.get("bot_ip", "bot_ip_1")

#更改bgpd.conf并重启服务
for ip in route_ip_list:
    os.system('docker exec ' + ip + '  python /home/quagga/change_bgpd_conf.py ' + keep_hold + ' ' +  reconnect_time)
#限制带宽
os.system('docker exec ' + route_ip_list[1] + ' /home/quagga/tc-control.sh ' + up_down + ' &')
print 'wondershaper success.'
#确定重启成功
os.system('docker exec ' + route_ip_list[1] + '  python /home/quagga/ping_test.py ' + bot_ip_route)
print 'bgp restart success.'
#在被攻击机器执行tcpdump抓BGP包
os.system('docker exec ' + route_ip_list[1] + ' python /home/quagga/tcpdump_bgp.py ' + bot_ip_route + ' ' + dump_time + ' &')
#在控制机执行bot_control.py
os.system('docker exec ' + control_ip + ' python /home/quagga/bot_control.py &')




