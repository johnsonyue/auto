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
time.sleep(0.1)
end = 0
f = os.popen('ping ' + ip)
while True:
    line=f.readline().strip()
    if not line:
        f = os.popen('ping ' + ip)
        time.sleep(1)
        continue
    if line[-2:] == "ms":
            print line
            os.system(kill_arg)
            break




        
        
          
            
            
