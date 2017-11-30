host_file=conf/node-list.ip_level
ip=$(grep $1 $host_file | cut -d'#' -f1 | head -n 1)
pass=hitnis1q2w3e4r
script="$2"
echo "$2" >.run-ssh

expect -c "set timeout -1
spawn bash -c \"cat .run-ssh | ssh -o 'StrictHostKeyChecking no' root@$ip 'bash -s'\"
expect -re \".*password.*\" {send \"$pass\r\"}
expect eof"

rm .run-ssh
#10.10.11.111#2#BGP#1.5.0.2/29|1.2.0.19/29#1005#ASN-1005#1.5.0.0/16
