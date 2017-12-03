test $# -lt 1 && exit

cmd=$1
docker ps | tail -n +2 | awk '{print $NF}' | xargs -I {} bash -c "docker exec {} bash -c \"ps -ef | grep $cmd | grep -v bash | grep -v grep | awk '{print \\\$2}' | xargs -I % echo {} %\"" | while read a b; do echo "docker exec $a kill $b"; docker exec $a kill $b; done
