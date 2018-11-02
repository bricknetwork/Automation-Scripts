from netmiko import ConnectHandler
import paramiko
from paramiko.ssh_exception import BadHostKeyException, AuthenticationException, SSHException
from datetime import datetime
import dns.resolver
import getpass
import sys
import json

class firewall_connect(object):
	def __init__(self, host_addr, type, uname, pwd):
		self.connect = ConnectHandler(device_type=type, ip=host_addr, username=uname, password=pwd)
		self.password = pwd
	
	def block_ips(self, ip_list, object):
		#blank password for test firewall
		self.password = ""
		try:
			response1 = self.connect.send_command("enable")
			response2 = self.connect.send_command(self.password)
			response3 = self.connect.send_command("configure terminal")
			response4 = self.connect.send_command("object-group network {0}".format(object))
			for ip in ip_list:
				if "/" not in ip:
					blocked_status = self.connect.send_command("network-object host {0}".format(ip))
					print("Blocked ip: $s" %(ip))
				else:
					#subnet blocking, base ip and mask
					print("Blocked subnet: $s" %(ip))
		except Exception as e:
			print (e)