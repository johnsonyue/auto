#!/usr/bin/env python

import pexpect
import os, re

def scp_command (asn):

  user = 'root'

  result = asn_to_container(asn)

  if result:
    host, container = result
  else:
    return None

  filename = './bgp-configure.txt'

  password = '1q2w3e4r'

  ssh_newkey = 'Are you sure you want to continue connecting'

  child = pexpect.spawn('scp %s %s@%s:/home/qcy/' % (filename, user, host))
  i = child.expect([pexpect.TIMEOUT, ssh_newkey, 'password: '])

  if i == 0:  # Timeout
    print 'ERROR!'
    print child.before, child.after
    return None

  if i == 1:
    child.sendline('yes')
    child.expect('password: ')
    i = child.expect([pexpect.TIMEOUT, 'password: '])
    if i == 0:  # Timeout
      print 'ERROR'
      print child.before, child.after
      return None

  child.sendline(password)
  child.expect(pexpect.EOF)
  return 'Success' 


def ssh_command (asn, command):

  user = 'root'

  result = asn_to_container(asn)

  if result:
    host, container = result
  else:
    return None

  password = '1q2w3e4r'

  ssh_newkey = 'Are you sure you want to continue connecting'

  child = pexpect.spawn('ssh %s@%s "docker exec %s %s"' % (user, host, container, command))
  i = child.expect([pexpect.TIMEOUT, ssh_newkey, 'password: '])

  if i == 0:  # Timeout
    print 'ERROR!'
    print child.before, child.after
    return None

  if i == 1:
    child.sendline('yes')
    child.expect('password: ')
    i = child.expect([pexpect.TIMEOUT, 'password: '])
    if i == 0:  # Timeout
      print 'ERROR'
      print child.before, child.after
      return None

  child.sendline(password)
  child.expect(pexpect.EOF)
  return 'Success' 


def asn_to_container(search):
  asn_list = {}
  pattern = re.compile(r'(.*?)#\d*?#BGP#(.*?)\|.*?#(\d*?)#.*?#.*?')
  with open('host-asinfo.ip_level', 'r') as rfile:
    lines = rfile.readlines()
    for line in lines:
      match = pattern.match(line)
      if match:
        host = match.group(1)
        ipaddr = match.group(2)
        container = ipaddr.split('/')[0]
        asn = int(match.group(3))
        asn_list[asn] = (host, container)
  if search in asn_list:
    return asn_list[search]
  return None


if __name__ == '__main__':
  child = scp_command(3049)
  child.expect(pexpect.EOF)
