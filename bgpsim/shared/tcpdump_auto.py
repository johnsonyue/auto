# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 20:39:57 2017

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
        if 'Keepalive' in lines[i] or 'Open' in lines[i] or 'Notification' in lines[i]:
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

ip = sys.argv[1]
listen_time = sys.argv[2]

kill_arg = 'killall tcpdump'
ip_info = os.popen('ifconfig').read()

lines = ip_info.split('Link encap:Ethernet')

eth = 'None'
for i in range(len(lines)):
    if ip in lines[i]:
        eth = lines[i-1].strip()


if eth == 'None':
    print 'ip not have interface'
    os._exit(0)
now_time = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
file_name = '/home/quagga/ori_' + ip + '_' + now_time + '.txt'
os.system('tcpdump -n -i ' +  eth + ' tcp -vv > ' + file_name + ' &')
time.sleep(int(listen_time))
os.system('killall tcpdump')
output_change(file_name)



        
        
          
            
            