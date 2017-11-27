#!/bin/bash

shared="shared"
web_dir="web"

conf="conf"

hostipfile="$conf/hostip-hostid.txt"
hostidfile="$conf/hostid-as.txt"
asinfo="$conf/node-list"
aslink="$conf/link-list"
hostinfofile="$conf/host-asinfo.ip_level"
aslinkfile="$conf/link-list.ip_level"
bgpsimplefile="$conf/bgp-simple.txt"
bgpconffile="$conf/bgp-configure.txt"
hostinfo="$conf/host-asinfo.ip_level"
interlinkfile="$conf/interlink.txt"

#python gen-bgp.py $asinfo $aslink 
python gen-ip-level.py $hostipfile $hostidfile $asinfo $aslink $conf
# output file: $asInfo.ip_level $asLink.ip_level

python gen-bgp-conf.py $asinfo.ip_level $aslink.ip_level $bgpsimplefile
# output file: bgp-configure.txt

python relation.py
cp $bgpconffile $shared
# Add relationships to BGP config

# to An Yuhao
cp $asinfo.ip_level $web_dir/conf
cp $aslink.ip_level $web_dir/conf

