#!/usr/bin/env python
import ConfigParser
import os, re
import getopt
import sys
import ssh_to_host

def leak():
  # Read the configuration of leaking
  config = ConfigParser.ConfigParser()
  config.read('./leak.conf')
  leak_asn = int(config.get('leak', 'asn'))
  leaks = config.get('leak', 'leaks')
  leaklist = eval(leaks)

  config2 = ConfigParser.ConfigParser()
  config2.read('./changed.conf')
  last = config2.getint('changed', 'last')
  new = leak_asn
  
  # Copy bgpd.conf to a new one
  result = os.path.exists('./bgpd.old')
  if not result:
    os.system('cp ./bgp-configure.txt ./bgpd.old') 

  # Start to deploy leaks
  pattern = re.compile(r'.*?router bgp (\d*)')
  pattern2 = re.compile(r'.*?neighbor PROVIDER peer-group')
  pattern3 = re.compile(r'.*?neighbor (.*?) remote-as (\d*)')
  pattern4 = re.compile(r'.*?neighbor (.*?) peer-group')

  # A variable to show if the leaking as is matched in the bgpd.conf
  ifmatched = 0 

  # Current neighbor ASN's router-id
  neigh = '' 

  wlist = []

  with open('./bgpd.old', 'r') as rfile:
    lines = rfile.readlines()
    for line in lines:
      match = pattern.match(line)
      if match:
        asn = int(match.group(1))
        wlist.append(line)
        if asn == leak_asn:
          ifmatched = 1
        else:
          ifmatched = 0
      else:
        if ifmatched:
          match = pattern2.match(line)
          if match:
            addleakrule(wlist)
            wlist.append(line)
          else:
            match = pattern3.match(line)
            if match:
              neigh_id = match.group(1)
              neigh_asn = int(match.group(2))
              if neigh_asn in leaklist:
                neigh = neigh_id
              else:
                neigh = ''
              wlist.append(line)
            else:
              match = pattern4.match(line)
              if match:
                current_id = match.group(1)
                if current_id == neigh:
                  wlist.append(' neighbor %s peer-group LEAK\n' % neigh)
                else:
                  wlist.append(line)
              else:
                wlist.append(line)
        else:
          wlist.append(line)
  with open('./bgp-configure.txt', 'w') as wfile:
    wfile.write(''.join(wlist))

  reload_bgp(last)
  reload_bgp(new)

  config2.set('changed', 'last', new)
  config2.write(open('./changed.conf', 'w'))


def addleakrule(wlist):
  wlist.append(' neighbor LEAK     peer-group\n')
  wlist.append(' neighbor LEAK     route-map RM-CUSTOMER-IN  in\n')
  wlist.append(' neighbor LEAK     route-map RM-PROVIDER-OUT out\n')
  wlist.append(' neighbor LEAK     next-hop-self\n\n')


def recover():
  config = ConfigParser.ConfigParser()
  config.read('./changed.conf')
  last = config.getint('changed', 'last')

  if last > 0:
    result = os.path.exists('./bgpd.old')
    if result:
      os.system('cp ./bgpd.old ./bgp-configure.txt')
  
    reload_bgp(last)
    config.set('changed', 'last', 0)
    config.write(open('./changed.conf', 'w'))


def reload_bgp(asn):
  result = ssh_to_host.scp_command(asn)
  if result:
    ssh_to_host.ssh_command(asn, 'python run-bgp.py')


if __name__ == '__main__':
  opts, args = getopt.getopt(sys.argv[1:], "lr", ["leak", "recover"])
  for o, a in opts:
    if o in ('-l', '--leak'):
      leak()
    elif o in ('-r', '--recover'):
      recover()
    else:
      print 'Wrong command!'
      sys.exit(0)
