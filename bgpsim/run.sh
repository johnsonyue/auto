#!/bin/bash

conf="conf"
host_shared_path="/home/yupeng/quagga"
shared="shared"
web_dir="web"

asinfo="$conf/node-list"
aslink="$conf/link-list"
hostinfofile="$conf/host-asinfo.ip_level"
aslinkfile="$conf/link-list.ip_level"
bgpsimplefile="$conf/bgp-simple.txt"
bgpconffile="$conf/bgp-configure.txt"
hostinfo="$conf/host-asinfo.ip_level"
interlinkfile="$conf/interlink.txt"


apt-get install -y -o Acquire::ForceIPv4=true python-pip ipcalc nfs-common
pip install IPy

echo ">> create"

mkdir -p $host_shared_path
cp $shared/* $host_shared_path

# put get-host-ip-address.sh and get_ip in current directory
python gen-container.py $hostinfo $aslinkfile $bgpconffile

rm -f host-ip-address 

cd $web_dir && nohup python tor3.py >http.log 2>&1 &
