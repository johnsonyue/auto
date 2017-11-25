docker ps -a | grep centos-quagga:centos-quagga-bgp | awk '{print $NF}' | xargs -I {} bash -c "docker stop {} && docker rm {}"
docker network ls | grep -E "net_[0-9]+" | awk '{print $1}' | xargs -I {} bash -c "docker network rm {}"
