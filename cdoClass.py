import json
import datetime
import requests
from urllib.parse import urlparse
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class CDO(object):
	def __init__(self, token, proxy):
		self.token = "bearer " + token
		self.url_base = "https://www.defenseorchestrator.com/aegis/rest/v1/services"
		self.proxy = proxy
		self.connect = requests.session()
		self.connect.verify = False
		self.disable_warnings = True
		self.connect.headers.update({'Content-Type':'application/json'})
		self.connect.headers.update({'Authorization':self.token})

	def get_list(self, object_id, list_name):
		ip_list = []
		try:
			resp = self.connect.get('{0}/targets/objects/{1}'.format(self.url_base,object_id), proxies=self.proxy)
			if resp.status_code >= 200 and resp.status_code < 300:
				contents = resp.json()['contents']
				for item in contents:
					ip_list.append(item['sourceElement'])
			return resp.status_code, ip_list
		except Exception as e:
			return 0, e

	def update_list(self, object_id, list_name, ips):
		contents = []
		for ip in ips:
			piece = {
				"@type" : "NetworkContent",
				"sourceElement" : ip
			}
			contents.append(piece)
		payload = {
			"name": list_name,
			"@typeName": "LocalObject",
			"objectType": "NETWORK_GROUP",
			"contents": contents,
			"deviceType": "ASA"
		}
		#print(payload)
		try:
			resp = self.connect.put('{0}/targets/objects/{1}'.format(self.url_base, object_id), data=json.dumps(payload), proxies=self.proxy)
			return resp.status_code, resp.json()
		except Exception as e:
			return 0, e

	def get_uids(self):
		uids = []
		try:
			#end of url "fieldname:value" for specific devices    
			resp = self.connect.get('{0}/targets/devices?q=tagValues:INTERNET'.format(self.url_base), proxies=self.proxy)
			if resp.status_code >= 200 and resp.status_code < 300:
				for device in resp.json():
					uids.append(device['uid'])
				print(uids)
			return resp.status_code, uids
		except Exception as e:
			return 0, e

	def commit(self, uids):
		contents = []
		for uid in uids:
			piece = {
				"uid" : uid,
				"namespace" : "targets",
				"type" : "devices"
			}
			contents.append(piece)
		payload = {
			"action": "WRITE",
			"triggerState": "PENDING_ORCHESTRATION",
			"objectType": "NETWORK_GROUP",
			"objRefs": contents
		}
		#print(payload)
		try:
			resp = self.connect.post('{0}/state-machines/jobs'.format(self.url_base), data=json.dumps(payload), proxies=self.proxy)
			return resp.status_code, resp.json()
		except Exception as e:
			return 0, e
