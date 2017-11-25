#!/bin/bash

interfaces=`ifconfig |awk -v RS=  '/'$ODMU_IP'/{print $1}' | grep -v lo`
OLD_IFS="$IFS"
IFS=" "
interfaces=($interfaces)
IFS="$OLD_IFS"

for i in ${interfaces[@]}
do
        temp=`./get_ip $i`
        ip=`echo $temp | awk -F ' ' '{print $1}'`
        ipList[${#ipList[@]}]=${i}:${ip}
done


for  i in ${ipList[@]}
do 
	echo $i >> host-ip-address
done
