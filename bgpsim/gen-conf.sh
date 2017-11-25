#!/bin/bash

shared="shared"
web_dir="web"

conf="conf"

asinfo="$conf/node-list"
aslink="$conf/link-list"
hostinfofile="$conf/host-asinfo.ip_level"
aslinkfile="$conf/link-list.ip_level"
bgpsimplefile="$conf/bgp-simple.txt"
bgpconffile="$conf/bgp-configure.txt"
hostinfo="$conf/host-asinfo.ip_level"
interlinkfile="$conf/interlink.txt"

python gen-bgp.py $asinfo $aslink 
# output file: $asInfo.ip_level $asLink.ip_level

python gen-bgp-conf.py $asinfo.ip_level $aslink.ip_level $bgpsimplefile
# output file: bgp-configure.txt

python relation.py
cp $bgpconffile $shared
# Add relationships to BGP config

python gen-hostinfo.py ${conf}/hostip-hostid.txt ${conf}/hostid-as.txt $asinfo.ip_level $hostinfo
# output file: host-asinfo.ip_level

# to An Yuhao
cp $hostinfo $web_dir/conf
cp $aslink.ip_level $web_dir/conf

# generate interlink for openvswitch
python gen-interlink.py $hostinfo ${aslink}.ip_level > $interlinkfile

