#!/usr/bin/env python
import os, re
import ConfigParser

def form(old):

  # Read the configuration 
  config = ConfigParser.ConfigParser()
  config.read('conf/path.conf')
  bgpsimple = config.get('relationship', 'bgpsimple')
  bgpconf = config.get('relationship', 'bgpconf')
  reladir = config.get('relationship', 'relationship')

  if not old:
    reladir = reladir + '.new'

  # Form as relationship
  asrela = {}
  with open(reladir, 'r') as rfile:
    lines = rfile.readlines()
    for line in lines:
      content = line.strip()
      sep = content.split('#')
      as1 = int(sep[0])
      as2 = int(sep[1])
      rela = sep[3]
      if (as1, as2) not in asrela:
        asrela[(as1, as2)] = rela
      if (as2, as1) not in asrela:
        if rela == 'P2C':
          asrela[(as2, as1)] = 'C2P'
        elif rela == 'C2P':
          asrela[(as2, as1)] = 'P2C'
        else:
          asrela[(as2, as1)] = rela

  # Patterns for finding BGP config
  pattern1 = re.compile(r'#bgp.conf#')
  pattern2 = re.compile(r'.*?router bgp (\d+)')
  pattern3 = re.compile(r'.*?bgp router-id (.+)')
  pattern4 = re.compile(r'.*?neighbor (.*?) remote-as (\d+)')
  pattern5 = re.compile(r'.*?line vty')
  pattern6 = re.compile(r'.*?####')


  # Create a list and a whole string for writing to the new bgp config
  wlist = []
  wholestr = ''

  # An variable to show if the next follow lines are bgp config
  ifbgp = 0

  # An variable to show if the config of current container has been wrote to the file
  ifwrote = 0

  # An variable to show if the rule of peer-group has been added to the wlist
  ifadded = 0

  with open(bgpsimple, 'r') as rfile:
    lines = rfile.readlines()
    for index, item in enumerate(lines):
      match = pattern1.match(item)
      if match:
        ifwrote = 0
        ifadded = 0
        ifbgp = 1
        if index + 1 < len(lines):
          container = lines[index+1].strip()
          wlist.append(item)
      else:
        if ifbgp:
          match = pattern2.match(item)
          if match:
            asn = int(match.group(1))
            wlist.append(item)
          else:
            match = pattern3.match(item)
            if match:
              routerid = match.group(1)
              wlist.append(item)
            else:
              match = pattern4.match(item)
              if match:
                if ifadded == 0:
                  addpeergroups(wlist, asn)
                  ifadded = 1
                neigh = match.groups()
                neigh_id = neigh[0] 
                neigh_asn = int(neigh[1])
                wlist.append(item)
                if (asn, neigh_asn) in asrela:
                  if asrela[(asn, neigh_asn)] == 'P2C':
                    wlist.append(" neighbor %s peer-group CUSTOMER\n" % neigh_id)
                  elif asrela[(asn, neigh_asn)] == 'C2P':
                    wlist.append(" neighbor %s peer-group PROVIDER\n" % neigh_id)
                  else:
                    wlist.append(" neighbor %s peer-group PEER\n" % neigh_id)
                else:
                  wlist.append(" neighbor %s peer-group CUSTOMER\n" % neigh_id)
              else:
                match = pattern5.match(item)
                if match:
                  addroutemaps(wlist, asn)
                  wlist.append(item)
                else:
                  match = pattern6.match(item)
                  if match:
                    wlist.append(item)
                    wholestr += ''.join(wlist)
                    ifwrote = 1
                    wlist = []
                    ifbgp = 0
                  else:
                    wlist.append(item)
        else:
          wlist.append(item)

    if ifwrote == 0:         
      wholestr += ''.join(wlist)

  with open(bgpconf, 'w') as wfile:
    wfile.write(wholestr)


def addpeergroups(wlist, asn):
  # Add peer groups
  wlist.append(' neighbor PROVIDER peer-group\n')
  wlist.append(' neighbor PROVIDER route-map RM-PROVIDER-IN  in\n')
  wlist.append(' neighbor PROVIDER route-map RM-PROVIDER-OUT out\n')
  wlist.append(' neighbor PROVIDER next-hop-self\n\n')
  wlist.append(' neighbor PEER     peer-group\n')
  wlist.append(' neighbor PEER     route-map RM-PEER-IN      in\n')
  wlist.append(' neighbor PEER     route-map RM-PROVIDER-OUT out\n')
  wlist.append(' neighbor PEER     next-hop-self\n\n')
  wlist.append(' neighbor CUSTOMER peer-group\n')
  wlist.append(' neighbor CUSTOMER route-map RM-CUSTOMER-IN  in\n')
  wlist.append(' neighbor CUSTOMER next-hop-self\n\n')
  
def addroutemaps(wlist, asn):
  # Add route maps
  wlist.append(' route-map RM-PROVIDER-IN permit 10\n')
  wlist.append(' set community %d:3080 additive\n' % asn)
  wlist.append(' set local-preference 80\n')
  wlist.append(' route-map RM-PROVIDER-IN permit 20\n\n')
  wlist.append(' route-map RM-PEER-IN permit 10\n')
  wlist.append(' set community %d:3090 additive\n' % asn)
  wlist.append(' set local-preference 90\n')
  wlist.append(' route-map RM-PEER-IN permit 20\n\n')
  wlist.append(' route-map RM-PROVIDER-OUT deny 10\n')
  wlist.append(' match community providers\n')
  wlist.append(' route-map RM-PROVIDER-OUT permit 20\n\n')
  wlist.append(' route-map RM-CUSTOMER-IN permit 10\n')
  wlist.append(' set community %d:3100\n' % asn)
  wlist.append(' set local-preference 100\n')
  wlist.append(' route-map RM-CUSTOMER-IN permit 20\n\n')


  wlist.append(' ip community-list standard providers permit %d:3080\n' % asn)
  wlist.append(' ip community-list standard providers permit %d:3090\n' % asn)
  wlist.append(' ip community-list standard providers deny\n\n')


if __name__ == '__main__':
  form(1)
