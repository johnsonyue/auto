test $# -lt 1 && exit

cmd=$1
docker ps | tail -n +2 | awk '{print $NF}' | xargs -I {} bash -c "docker exec {} bash -c \"ps -ef | grep $cmd | grep -v bash | grep -v grep | awk '{print \\\$2}' | xargs -I % echo {} %\"" | while read a b; do echo "docker exec $a kill $b"; docker exec $a kill $b; done

#docker ps | tail -n +2 | awk '{print $NF}' | xargs -I {} bash -c "d=\$(docker exec \$1 ip route | grep default); echo \$1 \$d" -- {} | grep default | cut -d' ' -f1 | xargs -I {} bash -c "echo \"docker exec {} ip route del default\"; docker exec {} ip route del default"

#docker ps -a | awk '{print $NF}' | while read l; do echo $l; docker exec $l bash -c "eval \"ip route del 10.11.118.67/32 \$(ip route | grep \"^2.43.0.0/\" | cut -d' ' -f2,3,4,5)\""; done
