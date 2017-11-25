#!/bin/bash
bandwidth=$1

ifconfig |awk -v RS=  '/'$ODMU_IP'/{print $1}' | grep -v lo | xargs -I %  wondershaper -c -a %
ifconfig |awk -v RS=  '/'$ODMU_IP'/{print $1}' | grep -v lo | xargs -I %  wondershaper -a  % -u $bandwidth -d $bandwidth
