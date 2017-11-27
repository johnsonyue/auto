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


ip = sys.argv[1]

kill_arg = 'killall ping'


now_time = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
file_name = '/home/quagga/ping_' + ip + '_' + now_time + '.txt'
os.system('ping ' + ip + ' > ' + file_name + ' &')
time.sleep(0.1)
end = 0
while True:
    f = open(file_name,'r')
    for line in f:
        if 'bytes from' in line and 'icmp_seq' in line:
            f.close()
            end = 1
            break
    if end == 1:
        break
    f.close()
    time.sleep(1)
        
os.system(kill_arg)




        
        
          
            
            