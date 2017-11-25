import sys


f = open(sys.argv[1], 'r')
asinfoLines = f.readlines()

for i in range(len(asinfoLines)):
        asinfoLines[i] = asinfoLines[i].strip()

# interface_hostip_dict:  interface appears in host-asinfo.txt.ip_level -> host_ip
interface_hostip_dict = {}
interface_info = {}
for i in range(len(asinfoLines)):
        temp_list = asinfoLines[i].split("#")
        hostip_in_node_file = temp_list[0]

	host_id = temp_list[1]
	asn = temp_list[4]


        temp_ip_list = temp_list[3].split("|")

	container_name = temp_ip_list[0].split("/")[0]

        for j in temp_ip_list:
                interface_hostip_dict[j] = hostip_in_node_file
                interface_info[j] = host_id + "#" + asn + "#" + container_name + "#" + j

f.close()


f = open(sys.argv[2], 'r')
linkLines = f.readlines()
for i in range(len(linkLines)):
        linkLines[i] = linkLines[i].strip()
	
	temp_list = linkLines[i].split("#")

	interface_1 = temp_list[1]
        interface_2 = temp_list[3]

	if interface_hostip_dict[interface_1] != interface_hostip_dict[interface_2]:
		print interface_info[interface_1] + "#" + interface_info[interface_2]
f.close()


