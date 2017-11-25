import os
import sys

f = open(sys.argv[1], 'r')

confLines = f.readlines()

for i in range(len(confLines)):
        confLines[i] = confLines[i].strip()
f.close()


# get container hostname

hostname = (os.popen("hostname")).readlines()[0][:-1]

container_name = ".".join(hostname.split("-"))

# print "containerName: ", container_name


fw_zebra = open("/etc/quagga/zebra.conf", 'w')
fw_bgpd = open("/etc/quagga/bgpd.conf", 'w')

i = 1
while i < len(confLines):


        if str(confLines[i]) != str(container_name):

#               print confLines[i], container_name
                i += 1
                continue

        zebra_line = i + 2
        while confLines[zebra_line] != "####":
                #if confLines[zebra_line].split()[0] != "interface" and not is_interface:
                #       fw_zebra.writelines(confLines[zebra_line] + "\n")
                #       is_interface = True
                zebra_line += 1
        fw_zebra.writelines("hostname " + container_name.replace('.','-') +"\n")
        fw_zebra.writelines("log file /var/log/quagga/quagga.log\n")
        cmd="ip a | grep \"inet .*global eth.*$\" | awk '{print \"interface \"$NF\"\\nip address \"$2\"\\nipv6 nd suppress-ra\"}'"
        fw_zebra.writelines(os.popen(cmd).read())
        fw_zebra.writelines("interface lo\nip forwarding\nline vty\n")

        bgp_line = zebra_line + 2

        while confLines[bgp_line] != "####":

                fw_bgpd.writelines(confLines[bgp_line] + "\n")
                bgp_line += 1
        break
        i += 1

if i >= len(confLines):
        print "container_name not found"


fw_bgpd.close()
fw_zebra.close()
os.system("service zebra start")
os.system("service bgpd start")


