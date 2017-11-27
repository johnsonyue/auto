import os
import sys
import re
from IPy import IP

if len(sys.argv) < 4:
	print "command paramter less than 3"
	print "eg, python " + sys.argv[0] + " node-list.ip_level  link-list.ip_level  output_file_name"
	exit()

fnode = open(sys.argv[1], 'r')
nodeLines = fnode.readlines()
flink = open(sys.argv[2], 'r')
linkLines = flink.readlines()

for i in range(len(nodeLines)):
        nodeLines[i] = nodeLines[i].strip()
	
for i in range(len(linkLines)):
	linkLines[i] = linkLines[i].strip()


fw = open(sys.argv[3], 'w')

for i in nodeLines:
	fw.writelines("######\n")


	temp_list = i.split("#")

	ip_list = temp_list[3].split("|")
	container_name = ip_list[0].split("/")[0]

	fw.writelines(container_name + "\n")
	
	
	## write zebra.conf	
	fw.writelines("#zebra.conf#\n")

	hostname = "-".join(container_name.split("."))

	fw.writelines("hostname " + hostname + "\n")
	fw.writelines("log file /var/log/quagga/quagga.log\n")

	eth_id = 0
	for ip in ip_list:

		# the first position of ip_list has been saved for container_name, not a ip with link
		if ip.split("/")[0] == container_name:
			continue

		fw.writelines("interface eth" + str(eth_id) + "\n") 
		fw.writelines(" ip address " + ip + "\n")
		fw.writelines(" ipv6 nd suppress-ra\n")
		eth_id += 1	

	fw.writelines("interface lo\n")
	fw.writelines("ip forwarding\n")
	fw.writelines("line vty\n")
	fw.writelines("####\n")
	## write zebra.conf ends

	## write bgpd.conf
	fw.writelines("#bgp.conf#\n")
	fw.writelines("hostname bgpd\n")
	fw.writelines("password zebra\n")
	fw.writelines("log file /var/log/quagga/quagga.log\n")
	fw.writelines("log stdout\n")

	asn = temp_list[4] 
	fw.writelines("router bgp " + asn + "\n")
	fw.writelines(" bgp router-id " + container_name.split("/")[0] + "\n")
	fw.writelines(" network " + temp_list[6] +  "\n")
	fw.writelines(" timers bgp 10 30\n")
	#fw.writelines(" timers connect 60\n")

	for linkLine in linkLines:
		temp_link_list = linkLine.split("#")
		ip_1 = temp_link_list[1]
		ip_2 = temp_link_list[3]

		## simply check
		if ip_1 == ip_list[0] or ip_2 == ip_list[0]:
			# ip_list[0] is lo:0 interface, should not appears in link.txt
			print "Warning: lo:0 should not appears in link.txt"
			continue
		if ip_1 == ip_2:
			print "One link should contain different ip addresses"
			continue		
		## check ends

		if ip_1 in ip_list:
			neighbor_ip = ip_2.split("/")[0]
			neighbor_asn = temp_link_list[2]
			fw.writelines(" neighbor " + neighbor_ip  + " remote-as " + neighbor_asn + " \n")	
		elif ip_2 in ip_list:
			neighbor_ip = ip_1.split("/")[0]
                        neighbor_asn = temp_link_list[0]
                        fw.writelines(" neighbor " + neighbor_ip  + " remote-as " + neighbor_asn + " \n")

	fw.writelines("line vty\n")
	fw.writelines("####\n")
	## write bgpd.conf ends


fnode.close()
flink.close()
fw.close()





