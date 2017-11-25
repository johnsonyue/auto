import sys

# f1: asinfo.txt
# asn#as name#announced prefix
f1 = open(sys.argv[1], 'r')
f1_lines = f1.readlines()

# f2: asrela.txt
# as_1#as_2#bandwidth#relation
f2 = open(sys.argv[2], 'r')
f2_lines = f2.readlines()

fwNode = open(sys.argv[1] + ".ip_level", 'w')
fwLink = open(sys.argv[2] + ".ip_level", 'w')


as_list = []

# as_dict: asn -> annouced network prefix
as_dict = {}

# as_name_dict: asn -> as name
as_name_dict = {}
for i in range(len(f1_lines)):
	f1_lines[i] = f1_lines[i].strip()
	temp = f1_lines[i].split("#")

	as_list.append(temp[0])
	as_dict[temp[0]] = temp[-1]

	as_name_dict[temp[0]] = temp[1]


# netwokr_dict: asn -> available newwork segmention /29
# each used, delete first segmention in the dict-value-list.
network_dict = {}
for i in as_list:
	temp_list = ["10", "18", "26", "34", "42", "50", "58", "66", "74", "82", "90", "98", "106", "114","122", \
			 "130", "138", "146", "154", "162", "170", "178", "186", "194", "202", "210", "218", "226", "234", "242", "250"]
	network_dict[i] = temp_list

# prefix_dict: asn -> first three number of annouced prefix, eg, 10.0.0.
prefix_dict = {}
for i in as_list:
	network = as_dict[i].split("/")[0]
	netLen = as_dict[i].split("/")[1]
	if int(netLen) > 24:
		print "netLen > 24"
		exit()

	temp_list = network.split(".")
	
	prefix_dict[i]  = temp_list[0] + "." + temp_list[1] + "." +  temp_list[2] + "."
	
# node_dict: asn -> lines of node.txt of the asn
node_dict = {}
for asn in as_list:
	node_dict[asn] = "BGP#" + prefix_dict[asn] + "2/29|"


for asn in as_list:
	i = 0
	while i < len(f2_lines):
		
		f2_lines[i] = f2_lines[i].strip()
		temp = f2_lines[i].split("#")

		as_1 = temp[0]
		as_2 = temp[1]

		bandwidth = temp[2]
		relation = temp[3]

		if as_1 == asn:
			gen_network = prefix_dict[asn] + (network_dict[asn])[0] + "/29"
			gen_network_2 = prefix_dict[asn] + str( int( (network_dict[asn])[0] ) + 1 ) + "/29"
			fwLink.writelines(as_1 + "#" + gen_network + "#" + as_2 + "#" +  gen_network_2 + "#" + bandwidth + "#" + relation + "\n")
			(network_dict[asn]).remove((network_dict[asn])[0])

			f2_lines.remove(f2_lines[i])

			if as_1 not in as_list or as_2 not in as_list:
				print "error"
				exit()
	
			node_dict[as_1] += (gen_network + "|")
			node_dict[as_2] += (gen_network_2 + "|")
			
			continue		

		i += 1

for i in node_dict:
	# current ->  node_dict[i] = "BGP#ip_1|ip_2|"
	fwNode.writelines(node_dict[i][:-1] + "#" + i + "#" + as_name_dict[i] + "#" + as_dict[i] + "\n")


f1.close()
f2.close()
fwNode.close()
fwLink.close()

