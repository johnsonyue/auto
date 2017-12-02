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
route_ip = (conf.get("route_ip", "route_ip"))
attack_ip = (conf.get("attack_ip", "attack_ip"))
keep_hold = conf.get("keep_hold", "keep_hold")
reconnect_time = conf.get("reconnect_time", "reconnect_time")
up_down = conf.get("up_down", "up_down")
dump_time = conf.get("dump_time", "dump_time")
bot_ip_route = conf.get("bot_ip", "bot_ip_1")
bot_ip_list = map ( lambda x:x[1], conf.items("bot_ip"))

#更改bgpd.conf并重启服务
os.system('docker exec ' + attack_ip + '  python /home/quagga/change_bgpd_conf.py ' + keep_hold + ' ' +  reconnect_time)
os.system('docker exec ' + route_ip + '  python /home/quagga/change_bgpd_conf.py ' + keep_hold + ' ' +  reconnect_time)
#限制带宽
os.system('docker exec ' + attack_ip + ' /home/quagga/tc-back.sh ' + up_down + ' &')
print 'tc cleared'
#确定重启成功
for b in bot_ip_list:
  print('docker exec ' + attack_ip + '  python /home/quagga/ping_test.py ' + b)
  os.system('docker exec ' + attack_ip + '  python /home/quagga/ping_test.py ' + b)
  print('docker exec ' + control_ip + '  python /home/quagga/ping_test.py ' + b)
  os.system('docker exec ' + control_ip + '  python /home/quagga/ping_test.py ' + b)
print 'bgp restart success.'
os.system("ps -ef | grep bot_sub | awk '{print $2}' | xargs -I {} kill {}; docker ps | awk '{print $NF}' | tail -n +2 | xargs -I {} bash -c \"docker exec {} python /home/quagga/bot_sub.py &\"")
print 'reset bots'
#在控制机执行bot_control.py
print('docker exec ' + control_ip + ' python /home/quagga/bot_control.py')
os.system('docker exec ' + control_ip + ' python /home/quagga/bot_control.py')
#在被攻击机器执行tcpdump抓BGP包
print('docker exec ' + attack_ip + ' python /home/quagga/tcpdump_bgp.py ' + attack_ip + ' ' + bot_ip_route + ' ' + dump_time + ' &')
os.system('docker exec ' + attack_ip + ' python /home/quagga/tcpdump_bgp.py ' + attack_ip + ' ' + bot_ip_route + ' ' + dump_time + ' &')
#限制带宽
os.system('docker exec ' + attack_ip + ' /home/quagga/tc-control.sh ' + up_down + ' &')
print 'wondershaper success.'




