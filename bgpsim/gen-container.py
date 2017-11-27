import os
import sys
import re
from IPy import IP

import socket
import struct

def ip_str2int(ip):
  packedIP = socket.inet_aton(ip)
  return struct.unpack("!L", packedIP)[0]
def ip_int2str(i):
  return socket.inet_ntoa(struct.pack('!L',i)) 

def plen_to_netmask(plen):
	val = 0xffffffff ^ (2 ** (32 - plen) - 1)
	return ip_int2str(val)

if len(sys.argv) < 3:
        print "command paramter less than 2"
        print "eg, python " + sys.argv[0] + " host-asinfo.ip_level  asrela.txt.ip_level "
        exit()

## get logical id of host(phisical machine)
os.system("chmod +x ./get-host-ip-address.sh; ./get-host-ip-address.sh")
f = open("host-ip-address", 'r')
host_ip_addresses = f.readlines()

# 1. get host ip address list
ip_address_list = []
for i in range(len(host_ip_addresses)):
	host_ip_addresses[i] = host_ip_addresses[i].strip()
	temp_list = host_ip_addresses[i].split(":")

	ip_address_list.append(temp_list[1])
	
f.close()

# 2. read host-asinfo.ip_level file, and get ip list in the file
f = open(sys.argv[1])
asinfoLines = f.readlines()

ip_list_in_file = []
for i in range(len(asinfoLines)):
	asinfoLines[i] = asinfoLines[i].strip()
	
	ip_in_file = asinfoLines[i].split("#")[0]

	if ip_in_file not in ip_list_in_file:
		ip_list_in_file.append(ip_in_file)
f.close()

# 3. judge which ip_address in ip_list_in_file
host_ip = ""
for i in ip_address_list:
	if i in ip_list_in_file:
		host_ip = i
		break	

if host_ip == "":
	print "ERROR: all of local phisical ip addresses not in file: host-asinfo.ip_level"
	exit()

## get host ip address END
# print host_ip


## generate containers with host-asinfo.ip_level, asrela.txt.ip_level
f = open(sys.argv[2], 'r')
linkLines = f.readlines()
for i in range(len(linkLines)):
	linkLines[i] = linkLines[i].strip()

f.close()


##### basic information for using
asinfoLines = asinfoLines
linkLines = linkLines
#####


# 1. generate networks 
print "Creating required networks ..."

# interface_hostip_dict:  interface appears in host-asinfo.txt.ip_level -> host_ip
interface_hostip_dict = {}
for i in range(len(asinfoLines)):
	temp_list = asinfoLines[i].split("#")
	hostip_in_node_file = temp_list[0]

	temp_ip_list = temp_list[3].split("|")

	for j in temp_ip_list:
		interface_hostip_dict[j] = hostip_in_node_file


# network_dict: network_number -> docker network name
network_dict = {}
for i in range(len(linkLines)):
	temp_list = linkLines[i].split("#")
	
	interface_1 = temp_list[1]
	interface_2 = temp_list[3]

	if interface_hostip_dict[interface_1] != host_ip or interface_hostip_dict[interface_2] != host_ip:
		continue

	# get network number
	resFile = os.popen("ipcalc " + interface_1 + " | grep 'Network:'")
	res = resFile.readlines()[0][:-1]
        network_number = re.split(" +", res)[1]
	# print network_number
	# get END
	
	if network_number in network_dict:
		continue

	os.system("docker network create net_" + str(i + 1) + " --subnet " + network_number)
	
	network_dict[network_number] = "net_" + str(i + 1)

for i in network_dict:
        print "Created Network: " + i + ", Name: " + network_dict[i]
print "Created required networks successfully."


# 2. loop every line of host-asinfo.txt.ip_level
for i in range(len(asinfoLines)):
	temp_list = asinfoLines[i].split("#")

	if temp_list[0] != host_ip:
		continue

	deviceType = temp_list[2]
	ipList = temp_list[3].split("|") # ipList[0] is lo:0 interface, x.x.x.x/x
	asn = temp_list[4]

	hostname = "-".join( ipList[0].split("/")[0].split(".") )
	container_name = ipList[0].split("/")[0]

	is_inter_host_container = False
	
	inner_host_ip = []
	inner_host_network_number = []
	for ip_index in range(1, len(ipList)):
		network_number = (os.popen("ipcalc " + ipList[ip_index] + " | grep 'Network:'")).readlines()[0][:-1]
		network_number = re.split(" +", network_number)[1]

		if network_number in network_dict:
			inner_host_ip.append(ipList[ip_index])
			inner_host_network_number.append(network_number)
		else:
			is_inter_host_container = True 


	if len(inner_host_ip) == 0:
		os.system("docker run -dit --privileged -h " + hostname + " --net=none "  + " --name=" + container_name  + " -v /home/yupeng/quagga:/home/quagga -v /home/share:/home/share centos-quagga-bgp /bin/bash")
		os.system("sleep 1")
	else:

		os.system("docker run -dit --privileged -h " + hostname + " --net=" + network_dict[inner_host_network_number[0]] + " --name=" + container_name + " --ip=" + inner_host_ip[0].split("/")[0]  + " -v /home/yupeng/quagga:/home/quagga -v /home/share:/home/share centos-quagga-bgp /bin/bash")
		
		os.system("sleep 1")

		for ip_index in range(1, len(inner_host_ip)):
			os.system("docker network connect --ip " + inner_host_ip[ip_index].split("/")[0] + " " + network_dict[inner_host_network_number[ip_index]] + " " + container_name)
			
	
	print "Created container, Name: " + container_name + ", IP: ",

	for ip in ipList:
		print ip,

	print "\n"	

	plen = ipList[0].split("/")[1]	

	netmask = plen_to_netmask( int(plen) )
	os.system("docker exec " + container_name + " ifconfig lo:0 " + container_name + " netmask " + netmask + " up")
	
	# delete default gw of bgp router, gw is to physic machine
        min_host = os.popen("ipcalc " + ipList[1] + " | grep 'HostMin:'").readlines()[0][:-1]
        min_host = re.split(" +", min_host)[1]

	#debug
	os.system("docker exec " + container_name + " route del default gw " + min_host)

	# set mtu for container
	os.system("docker exec " + container_name + " bash -c \"ifconfig |awk -v RS=  '/'\$ODMU_IP'/{print \$1}' | xargs -I %  ip link set mtu 1462 dev  % \" ")

        # execute bot_sub.py python program in docker container
        os.system("docker exec " + container_name + " python /home/quagga/bot_sub.py &")

        # execute /home/quagga/run-bgp.py in docker container
	if is_inter_host_container == False:
        	os.system("docker exec " + container_name + " python /home/quagga/run-bgp.py /home/quagga/bgp-configure.txt")

        # execute /home/quagga/run-bgp.py in docker container
        os.system("docker exec " + container_name + " rm /var/run/quagga/ospfd.vty")



## generate containers END






