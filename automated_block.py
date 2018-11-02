from openDNSClass import openDNS
from cdoClass import CDO
from symantecClass import connector
from firewallClass import firewall_connect
import sys
import getpass

#For symantec (use service account)
print("Login for Symantec14...")
user = input("Enter username: ")
pwd = getpass.getpass('Enter password: ')

print("Login for SSH...")
user2 = input("Enter username: ")
pwd2 = getpass.getpass('Enter password: ')

lrID = 'a3982506-20ef-9559-c12b-bfd0fbf2c139'
lrversion = '7.2.7'

proxy = {"http" : "http://qproxy.qdx.com:9090"}

new_hashes = []
new_urls = []
new_ips = []
firewalls = []

try:
	#Paths to <C:\ProgramData\Optic Link\var\tmp> txt files 
	new_hashes = open("new_hashes.txt").read().splitlines()
	new_urls = open("new_urls.txt").read().splitlines()
	new_ips = open("new_ips.txt").read().splitlines()
	#Path to locally saved list of firewalls to push IPs to block
	firewalls = open("firewall_list.txt").read().splitlines()
	print(firewalls)
	print("Successful import")
except:
	print("Couldn't retrieve lists to block")
	sys.exit()
	
def get_difference(currentlist,oldlist):
	update = list(set(currentlist) - set(oldlist))
	#print(update)
	if len(update) > 0:
		#if len(update) == 1 and len(oldlist) == 1:
		new_list = list(update + oldlist)
		#May or may not need special handling for different sizes, results surprisingly vary every test :/
		'''elif len(oldlist) == 1:
			new_list = list(set(update) + oldlist)
		elif len(update) == 1:
			print("WHAT")
			new_list = list(update + set(oldlist))
			print("THE")
		else:
			new_list = list(set(update) + set(oldlist))'''
		return new_list
	else:	
		return []

def umbrella():
	#change token for service account
	openDNSkey = "535abfce-698c-4bd4-b483-35a1ea89173c"
	umbrella = openDNS(key=openDNSkey, lrdeploymentID=lrID, lrvernum=lrversion, proxy=proxy)
	code1, response = umbrella.getDomains()
	blockedurls = []
	if int(code1) == 200:
		for domain in response['data']:
			blockedurls.append(domain['name'])
		update = get_difference(new_urls,blockedurls)
		if len(update) > 0: 
			code2, result = umbrella.blockURL(update)
			if code2 >= 200 and code2 < 300:
				print ("blocked successfully")
			else:
				print ("ERROR: %s details: %s" %(code2, result))
		else:
			print("Nothing new to block")
	else:
		print("ERROR: Couldn't connect to retrieve any info - %s details:\n%s" %(code1, response))

def cisco_def_orch():
	#change token for service account, splitup into concated string, can also just write it out longway in singe line
	cdo_token = ("eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2ZXIiOiIwIiwic3Vic2NyaXB0aW9ucyI6bnVsbCwidXNlcl9uYW1l"
		"IjoiZ3JlZ29yeS54LmNvb2tAcXVlc3RkaWFnbm9zdGljcy5jb20iLCJzY29wZSI6WyJ0cnVzdCIsIjIzMWY0YjQ1LTFkNTAtNGUyNy1h"
		"OWM4LWM3YTY3YWQ0M2Y4MSIsInJlYWQiLCJ3cml0ZSJdLCJpc3MiOiJpdGQiLCJpZCI6IjFlNzY4ODljLTc0NzEtNGE5Yy1hZmMwLTJi"
		"NTlhYzQxMDJiZCIsInNwaWQiOm51bGwsInN1YmplY3RUeXBlIjoidXNlciIsImF1dGhvcml0aWVzIjpbIlJPTEVfVVNFUiJdLCJqdGki"
		"OiI1YThhNDM5Ny0wNWNkLTQ4MzItYjAzYi03OGNjZTU2ZmJhZDUiLCJwYXJlbnRJZCI6IjIzMWY0YjQ1LTFkNTAtNGUyNy1hOWM4LWM3"
		"YTY3YWQ0M2Y4MSIsImNsaWVudF9pZCI6ImFwaS1jbGllbnQifQ.woiZzTmw_Xfsa0kqNENJH0VcKMoa1aRIivrJL4Jhy4pKDsegXthZr"
		"cZYc-t0_BcYOADlBBgDF-CbroerdflFuRVXO70vRkHaFP4FFL8WfCqti4k0lEEp-YOHztTJRXmAgOm9l7U12x5BLCEs5QPLclG9_fsoU"
		"qlWl-KCKnJ9qEE5Ve_kTQQFcwwDnnZOiO2b7zadQgRvp787N7oaITImbRQvkMCg2sMALWjh7k3AJ_Sk7SASsCWpf96Ibj_g9V9mdhqg0"
		"DPIM3-BQKmO7GF6GmIZCYcHJNMiaRROihwcdafJ-34YXHN5yYv4fWgosAB78lv2sPS1FGj7eOPZQjQNig")
	cdo_uid = "7c37d7ff-351c-45b7-bb78-f3ecf669c000"
	cdo_list_name = "automated-ip-block"
	
	blocked_ips = []
	connection = CDO(token=cdo_token,proxy=proxy)
	code1, blocked_ips = connection.get_list(cdo_uid, cdo_list_name)

	if int(code1) == 200:
		update = get_difference(new_ips, blocked_ips)
		if len(update) > 0: 
			code2=200#, result = connection.update_list(cdo_uid, cdo_list_name, update)
			if int(code2) == 200:
				print ("Successful update")
				#Commit process commented off, not yet tested
				'''code3, uids = connection.get_uids()
				if int(code3) == 200:
					code4, response = connection.commit()
					if int(code4) == 200
						print ("Successful commit")
					else:
						print ("ERROR: %s Failed commit: %s" %(code4, response))
				else:
					print ("ERROR: %s Failed to get uids: %s" %(code3, uids))'''
			else:
				print ("ERROR: %s details: %s" %(code2, result))
		else:
			print("Nothing new to block")
	else:
		print("ERROR: Couldn't connect to retrieve any info - %s details:\n%s" %(code1, blocked_ips))
		
def symantec():
	#"ATP Blacklisted files" used for testing, real policy list is "Kovter_Ransomware_MD5_List"
	symantec_platforms = [
		("https://qdcws3286:8446", "ATP Blacklisted files")
	]
	existing_list = []
	for semp, list_name in symantec_platforms:
		symantec = connector("{0}/sepm/api/v1".format(semp), proxy=proxy)
		result, resp = symantec.authorize(user,pwd)
		if int(result) >= 200 and int(result) < 300:
			code, existing_list = symantec.get_list(list_name)
			if int(code) >= 200 and int(code) < 300:
				new_hashes_upper = [hash.upper() for hash in new_hashes]
				update = get_difference(new_hashes_upper, existing_list['data'])
				if len(update) > 0:
					list_id = existing_list['id']
					list_name = existing_list['name']
					hash_type = existing_list['hashType']
					description = existing_list['description']
					status, response2 = symantec.update_list(list_id, list_name, hash_type, description, update)
					if int(status) >= 200 and int(status) < 300:
						print("Success")
					else:
						print ("ERROR: %s details: %s" %(status, response2))	
				else:
					print("Nothing new to block")
			else:
				print ("ERROR: %s details: %s" %(code, existing_list))
		else:
			print ("ERROR: %s cannot authorize: %s" %(result, resp))

def firewall_push():
	object_name = "test_block"
	print("1")
	print(firewalls)
	for firewall in firewalls:
		print("2")
		types = ['cisco_ios', 'cisco_xe', 'cisco_asa', 'cisco_nxos', 'cisco_xr']
		try:
			connection = firewall_connect(firewall, types[2], user2, pwd2)
			connection.block_ips(new_ips, object_name)
			#print("success")
		except Exception as e:
			print (e)

def main():
	try:
		print("\nSymantec:")
		#symantec()
	except Exception as e:
		print("Symmantec error:\n%s" %(e))
	'''try:
		print("\nCDO:")
		cisco_def_orch()
	except Exception as e:
		print("CDO error:\n%s" %(e))'''
	try:
		print("\nUmbrella:")
		#umbrella()
	except Exception as e:
		print("Umbrella error:\n%s" %(e))
	try:
		print("\nFirewall push:")
		firewall_push()
	except Exception as e:
		print("Firewall push error:\n%s" %(e))

if __name__ == '__main__':
	main()