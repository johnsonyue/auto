# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 19:22:39 2017
要三个参数：keepalive时间 holdtime时间 bgp重连时间
作用：修改/etc/quagga/bgpd.conf 并重启服务
@author: zyl
"""
import sys
import os
hold_time = sys.argv[1] + ' ' + sys.argv[2]
reconnect = sys.argv[3]
bgpd_dir = '/etc/quagga/bgpd.conf'
str = ''
have_hold_time = 0
have_reconnect = 0
f = open(bgpd_dir,'r')
hold_time_insert = 0
for line in f:
    if 'neighbor'in line and 'remote-as' in line:
        if hold_time_insert == 0:
            str = str + 'timers bgp ' + hold_time + '\n'
            hold_time_insert = 1
    if 'timers bgp' not in line and 'timers connect' not in line: 
        str = str + line
    if 'neighbor'in line and 'remote-as' in line:
        neighbor = line.split('remote-as')[0]
        str = str + neighbor + 'timers connect ' + reconnect + '\n'
f.close()      
f = open(bgpd_dir,'w')
f.write(str)
f.close()
os.system('service bgpd restart')