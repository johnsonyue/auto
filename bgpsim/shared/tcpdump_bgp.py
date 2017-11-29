# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 20:39:57 2017
要两个参数：监听的ip 监听时间
结果：生成一个ip_日期_时间的日志（第一行为是否打断，后面为具体BGP包）
@author: zyl
"""
import datetime
import sys
import os
import time
import re
def output_change(file_name):
    f = open(file_name,'r')
    lines = f.readlines()
    result = 'result:no disconnection.'
    time_list = []
    content = {}
    for i in range(len(lines)):
        if 'Keepalive' in lines[i] or 'Open' in lines[i] or 'Notification' in lines[i] or 'Update' in lines[i]:
            if 'Notification' in lines[i]:
                result = 'result:disconnection.'
            message = ''
            for j in range(i-1,-1,-1):
                pattern = '^\d'
                if re.match(pattern, lines[j][0], flags=0) != None:
                    start = j
                    message_time = lines[j].split()[0]
                    break
            for k in range(start,i+1):
                message = message + lines[k]
            if message_time not in time_list:
                time_list.append(message_time)
            content[message_time] = message 
    f.close()
    f = open(file_name.replace('ori_',''),'w')
    f.write(result + '\n')
    for t in time_list:
        f.write(content[t])
    f.close()

name_ip = sys.argv[1]
ip = sys.argv[2]
listen_time = sys.argv[3]

kill_arg = 'killall tcpdump'

#ip_info = os.popen('ip a').read()
#lines = ip_info.split('\n')
#
#eth = 'None'
#for i in range(len(lines)):
#    if ip in lines[i]:
#        eth = lines[i].split()[-1]
ip_sub = ip.split('.')  
prefix = ip_sub[0] + '.' + ip_sub[1] + '.0.0'
ip_info = os.popen('route -n | grep ' + prefix).read()

eth = 'None'
if prefix in  ip_info:
    eth = ip_info.split()[-1]
if eth == 'None':
    print 'ip not have interface'
    os._exit(0)
now_time = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
file_name = '/home/quagga/ori_' + name_ip + '_' + now_time + '.txt'
os.system('tcpdump -n -i ' +  eth + ' tcp -vv > ' + file_name + ' &')
time.sleep(int(listen_time))
os.system('killall tcpdump')
output_change(file_name)



        
        
          
            
            