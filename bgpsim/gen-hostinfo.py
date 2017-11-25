import sys

if len(sys.argv) < 4:
	print "command paramters is less than 3"
	print "eg, python " + sys.argv[0] + " hostip-hostid.txt  hostid-as.txt  asinfo.txt.ip_level"
	exit()

f1 = open(sys.argv[1], 'r')
f2 = open(sys.argv[2], 'r')
f3 = open(sys.argv[3], 'r')
fw = open(sys.argv[4], 'w')

ip_id_lines = f1.readlines()
id_as_lines = f2.readlines()
asinfo_lines = f3.readlines()

# id_ip_dict:  host-id -> host-ip
id_ip_dict = {}
for i in range(len(ip_id_lines)):
	ip_id_lines[i] = ip_id_lines[i].strip()
	temp_list = ip_id_lines[i].split("#")
	
	
	id_ip_dict[temp_list[1]] = temp_list[0]

# as_id_dict: as number -> host-id
as_id_dict = {}
for i in range(len(id_as_lines)):
	id_as_lines[i] = id_as_lines[i].strip()
	temp_list = id_as_lines[i].split("#")
        

	as_id_dict[temp_list[1]] = temp_list[0]

# as_dict:  asinfo line in asinfo.txt.ip_level file -> as_number
as_dict = {}
for i in range(len(asinfo_lines)):
        print asinfo_lines[i]

	asinfo_lines[i] = asinfo_lines[i].strip()
        temp_list = asinfo_lines[i].split("#")
        

	as_dict[asinfo_lines[i]] = temp_list[2]


for i in asinfo_lines:

	asn = as_dict[i]
	host_id = as_id_dict[asn]
	host_ip = id_ip_dict[host_id]

	fw.write(host_ip + "#" + host_id + "#" + i + "\n")


fw.close()
f1.close()
f2.close()
f3.close()
