# 1.10.11.150#6#6050#ASN-6050#6.50.0.0/16

import sys
import socket
import struct

# FUNCTION SECTION
############################
 
def ip_str2int(ip):
	packedIP = socket.inet_aton(ip)
	return struct.unpack("!L", packedIP)[0]
def ip_int2str(i):
	return socket.inet_ntoa(struct.pack('!L',i))

#example "202.118.224.0/24", 10, 29
def get_prefixes(prefix, number, length):

	ipaddr_str, ipaddr_len = prefix.split('/')
	ipaddr = ip_str2int(ipaddr_str)
	max_ipaddr = ipaddr + 2**(32-int(ipaddr_len)) - 1

	ipaddr_list = []

	for i in range(int(number)):
		new_prefix = ipaddr+2**(32-int(length))*i
		if new_prefix > max_ipaddr:
			print "reach the max IP addr in "+str(prefix)
			break
		ipaddr_list.append(ip_int2str(new_prefix)+"/"+str(length))

	return ipaddr_list

def get_next_prefix(prefix, number, length): 
 
	ipaddr_str, ipaddr_len = prefix.split('/')
	ipaddr = ip_str2int(ipaddr_str)
	max_ipaddr = ipaddr + 2**(32-int(ipaddr_len)) - 1

	new_prefix = ipaddr+2**(32-int(length))*int(number)
	if new_prefix > max_ipaddr:
		print "reach the max IP addr in "+str(prefix)
		return ""
	return ip_int2str(new_prefix)+"/"+str(length)

# FUNCTION ENDS
##############################





# READFILES SECTION
#############################

if len(sys.argv) < 6:
        print "command paramters is less than 5"
        print "eg, python " + sys.argv[0] + " hostip-hostid.txt  hostid-as.txt  node-list  link-list output_dir"
        exit()

# hsotip-hostid.txt
# 10.10.11.141#1
f_hostip = open(sys.argv[1], 'r')

# hostid-as.txt
# 1#1001
# 1#1002
f_hostid = open(sys.argv[2], 'r')

# node-list
# 1002#ASN-1002#1.2.0.0/16
f1 = open(sys.argv[3], 'r')

# link-list
# 1002#1005#50M#P2C
f2 = open(sys.argv[4], 'r')

ip_id_lines = f_hostip.readlines()
for i in range(len(ip_id_lines)):
	ip_id_lines[i] = ip_id_lines[i].strip()

id_as_lines = f_hostid.readlines()
for i in range(len(id_as_lines)):
	id_as_lines[i] = id_as_lines[i].strip()

asinfo_lines = f1.readlines()
for i in range(len(asinfo_lines)):
	asinfo_lines[i] = asinfo_lines[i].strip()

asrela_lines = f2.readlines()
for i in range(len(asrela_lines)):
	asrela_lines[i] = asrela_lines[i].strip()


f_hostip.close()
f_hostid.close()
f1.close()
f2.close()

output_dir = sys.argv[5]
if output_dir[-1] != "/":
	output_dir = output_dir + "/"

# READFILES ENDS
###############################



# SECTION: get "hostip - hostid - asn" information
###############################

# id_ip_dict:  host-id -> host-ip
id_ip_dict = {}
for i in range(len(ip_id_lines)):
        temp_list = ip_id_lines[i].split("#")

        id_ip_dict[temp_list[1]] = temp_list[0]

# as_id_dict: as number -> host-id
as_id_dict = {}
for i in range(len(id_as_lines)):
        temp_list = id_as_lines[i].split("#")

        as_id_dict[temp_list[1]] = temp_list[0]

# as_dict:  asinfo line in node-list file -> as_number
as_dict = {}
for i in range(len(asinfo_lines)):
        temp_list = asinfo_lines[i].split("#")

        as_dict[asinfo_lines[i]] = temp_list[0]

#for i in asinfo_lines:

#        asn = as_dict[i]
#        host_id = as_id_dict[asn]
#        host_ip = id_ip_dict[host_id]

# SECION ENDS
################################



# SECTION: arrange ip address for as, arrange ip-level link between as neighbor
################################

## basic information

# asn#as name#announced prefix
asinfo_lines = asinfo_lines

# as_1#as_2#bandwidth#relation
asrela_lines = asrela_lines

# asn_host_dict: asn -> host-ip
# asn_prefix_dict: asn -> annunced prefix
asn_host_dict = {}
asn_prefix_dict = {}
asn_list = []
for i in range(len(asinfo_lines)):
	asn = asinfo_lines[i].split("#")[0]
	asn_list.append(asn)

	asn_host_dict[asn] = id_ip_dict[as_id_dict[asn]]
	asn_prefix_dict[asn] = asinfo_lines[i].split("#")[2]	

## basic information ends


## put each ip-pair in link-list lines to list value src_link_list
src_link_list = []
for i in range(len(asrela_lines)):
        asrela_lines[i] = asrela_lines[i].strip()
	temp_list = asrela_lines[i].split("#")
	as_1 = temp_list[0]
	as_2 = temp_list[1]

	temp_link = []
	temp_link.append(as_1)
	temp_link.append(as_2)

	src_link_list.append(temp_link)



link_list = []
for i in range(len(src_link_list)):
	link_list.append(src_link_list[i])

## put ends


## put inter-host-as-link into \inter_as_link lisk according to \asn_host_dict information
## remove inter-host-as-link from \link_list
inter_as_link = []

i = 0
while i < len(link_list):
	asn_1 = link_list[i][0]
        asn_2 = link_list[i][1]

	if asn_host_dict[asn_1] != asn_host_dict[asn_2]:
                inter_as_link.append(link_list[i])
                link_list.remove(link_list[i])
                continue

	i += 1

## put and remove ends


## put asns into subnet_dict
# subnet_dict: asn -> asn_list
# asns in one subnet_dict[first-asn] will be arranged a ip address which is in the first-asn's annouced prefix
subnet_dict = {}

while len(link_list) > 0:
	asn_1 = link_list[0][0]
	asn_2 = link_list[0][1]
	
	subnet_dict[asn_1] = []
	subnet_dict[asn_1].append(asn_1)
	subnet_dict[asn_1].append(asn_2)

	link_list.remove(link_list[0])

	j = 0
	while j < len(link_list):
		
		if link_list[j][0] == asn_1 or link_list[j][1] == asn_1:
			if link_list[j][0] not in subnet_dict[asn_1]:
				subnet_dict[asn_1].append(link_list[j][0])
			
			if link_list[j][1] not in subnet_dict[asn_1]:
				subnet_dict[asn_1].append(link_list[j][1])	

			link_list.remove(link_list[j])
			continue
		j += 1

	j = 0
	while j < len(link_list):
		if link_list[j][0] in subnet_dict[asn_1] and link_list[j][1] in subnet_dict[asn_1]: 
			link_list.remove(link_list[j])
			continue
		j += 1


## put ends


import math

## fill two dictionary as_ipaddr_dict and link_ipaddr_dict

# as_ipaddr_dict: asn -> asn's ipaddress list
as_ipaddr_dict = {}

# link_ipaddr_dict: link_list[i] -> link's two ipaddress
link_ipaddr_dict = {}

# add lo:0 ip address for every as
net_used_count = {}
for i in asn_list:
	as_ipaddr_dict[i] = []
	
	subnet_prefix = get_next_prefix(asn_prefix_dict[i], 0, 30)
	available_ipaddr = get_prefixes(subnet_prefix, 3, 32)
	available_ipaddr.remove(available_ipaddr[0])
        available_ipaddr.remove(available_ipaddr[0])

	as_ipaddr_dict[i].append(available_ipaddr[0].split("/")[0] + "/30")
	available_ipaddr.remove(available_ipaddr[0])
	net_used_count[i] = 1

# add inter host link ip address

for i in inter_as_link:

	inter_as_link_str = i[0] + "#" + i[1]

	asn_1 = i[0]
	asn_2 = i[1]

	new_network_order = net_used_count[asn_1]
	net_used_count[asn_1] += 1
	
	subnet_prefix = get_next_prefix(asn_prefix_dict[asn_1], new_network_order, 29)
	available_ipaddr = get_prefixes(subnet_prefix, 5, 32)
        available_ipaddr.remove(available_ipaddr[0])
        available_ipaddr.remove(available_ipaddr[0])

	as_ipaddr_dict[asn_1].append(available_ipaddr[0].split("/")[0] + "/29")
	link_ipaddr_dict[inter_as_link_str] = available_ipaddr[0].split("/")[0] + "/29#"
	available_ipaddr.remove(available_ipaddr[0])

	as_ipaddr_dict[asn_2].append(available_ipaddr[0].split("/")[0] + "/29")
	link_ipaddr_dict[inter_as_link_str] += available_ipaddr[0].split("/")[0] + "/29"
        available_ipaddr.remove(available_ipaddr[0])


# add inner link ip address
for i in subnet_dict:
	count = len(subnet_dict[i])
	count += 3

	net_len = 32 - int(math.ceil(math.log(count, 2)))

	if net_len < 29:
		temp_net_used_count = int (math.ceil( float(net_used_count[i]) / ( 2 **(29 - net_len) ) ) )
	elif net_len == 29:
		temp_net_used_count = net_used_count[i]
	else:
		print "ERROR: dict: " + i + ", " +  subnet_dict[i] + " has too little AS."
		exit()	
	
	subnet_prefix = get_next_prefix(asn_prefix_dict[i], temp_net_used_count, net_len)
	available_ipaddr = get_prefixes(subnet_prefix, count, 32)
	available_ipaddr.remove(available_ipaddr[0])
	available_ipaddr.remove(available_ipaddr[0])

	for j in subnet_dict[i]:
		as_ipaddr_dict[j].append(available_ipaddr[0].split("/")[0] + "/" + str(net_len))
		available_ipaddr.remove(available_ipaddr[0])

	for j in src_link_list:

		link_str = j[0] + "#" + j[1]

		if j[0] in subnet_dict[i] and j[1] in subnet_dict[i]:
			link_ipaddr_dict[link_str] = as_ipaddr_dict[j[0]][-1] + "#" + as_ipaddr_dict[j[1]][-1]


## test
#for i in asn_list:
#	print as_ipaddr_dict[i]


#for i in src_link_list:

#	temp_str = i[0] + "#" + i[1]

#	print link_ipaddr_dict[temp_str]

## test ends

fwNode = open(sys.argv[3] + ".ip_level", 'w')
fwLink = open(sys.argv[4] + ".ip_level", 'w')
fwInterLink = open(output_dir + "interlink.txt", 'w')

for i in asinfo_lines:
	temp_list = i.split("#")

	asn = as_dict[i]
        host_id = as_id_dict[asn]
        host_ip = id_ip_dict[host_id]

	as_ip_list = ""
	for j in as_ipaddr_dict[asn]:
		as_ip_list += j + "|"
	as_ip_list = as_ip_list[:-1]

	as_name = temp_list[1]
	prefix = temp_list[2] 

	fwNode.writelines(host_ip + "#" +\
			host_id + "#" +\
			"BGP" + "#" +\
			as_ip_list + "#" +\
			asn + "#" +\
			as_name + "#" +\
			prefix + "\n" \
	)

for i in asrela_lines:
	temp_list = i.split("#")
	
	bandwidth = temp_list[2]
	relation = temp_list[3]

	asn_1 = temp_list[0]
	asn_2 = temp_list[1]

	index = asn_1 + "#" + asn_2

	ip_pair_str = link_ipaddr_dict[index]

	ip_1 = ip_pair_str.split("#")[0]
	ip_2 = ip_pair_str.split("#")[1]

	fwLink.writelines(asn_1 + "#" +\
			ip_1 + "#" +\
			asn_2 + "#" +\
			ip_2 + "#" +\
			bandwidth + "#" +\
			relation + "\n" \
	)	


for i in asrela_lines:
#        asn = as_dict[i]
#        host_id = as_id_dict[asn]
#        host_ip = id_ip_dict[host_id]

        temp_list = i.split("#")

        bandwidth = temp_list[2]
        relation = temp_list[3]

        asn_1 = temp_list[0]
        asn_2 = temp_list[1]

	if id_ip_dict[as_id_dict[asn_1]] == id_ip_dict[as_id_dict[asn_2]]:
		continue

        index = asn_1 + "#" + asn_2

        ip_pair_str = link_ipaddr_dict[index]

	container_name_1 = as_ipaddr_dict[asn_1][0].split('/')[0]
	container_name_2 = as_ipaddr_dict[asn_2][0].split('/')[0]

        ip_1 = ip_pair_str.split("#")[0]
        ip_2 = ip_pair_str.split("#")[1]
	
	id_1 = as_id_dict[asn_1]
	id_2 = as_id_dict[asn_2]

        fwInterLink.writelines(id_1 + "#" +\
                        asn_1 + "#" +\
                        container_name_1 + "#" +\
                        ip_1 + "#" +\
                        id_2 + "#" +\
                        asn_2 + "#" +\
                        container_name_2 + "#" +\
                        ip_2 + "#" +\
                        bandwidth + "#" +\
                        relation + "\n" \
        )
		
fwNode.close()
fwLink.close()
fwInterLink.close()

