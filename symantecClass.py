import json
import datetime
import requests
from urllib.parse import urlparse
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class connector(object):
	def __init__(self, url_base, proxy):
		self.token = "Bearer "
		self.domainId = ""
		self.proxy = proxy
		self.url_base = url_base
		self.connect = requests.session()
		self.connect.verify = False
		self.disable_warnings = True

	def authorize(self, uname, pwd):
		self.connect.headers.update({'Content-Type':'application/json'})
		payload = {
			"username" : uname,
			"password" : pwd
		}
		try:
			resp = self.connect.post('{0}/identity/authenticate'.format(self.url_base), data=json.dumps(payload), proxies=self.proxy)
			if resp.status_code >= 200 and resp.status_code < 300:
				self.token = self.token + resp.json()['token']
				self.domainId = resp.json()['domainid']
			return resp.status_code, self.domainId
		except Exception as e:
			return 0, e	

	def get_list(self, list_name):
		self.connect.headers.update({'Content-Type':'application/json'})
		self.connect.headers.update({'Authorization':self.token})
		try:
			resp = self.connect.get('{0}/policy-objects/fingerprints'.format(self.url_base), params={'name':list_name}, proxies=self.proxy)
			return resp.status_code, resp.json()
		except Exception as e:
			return 0, e

	def update_list(self, list_id, list_name, hash_type, description, list):
		self.connect.headers.update({'Content-Type':'application/json'})
		self.connect.headers.update({'Authorization':self.token})
		payload = {
			'name': list_name, 
			'hashType': hash_type, 
			'description': description, 
			'data': list, 
			'domainId': self.domainId
		}
		try:
			resp = self.connect.post('{0}/policy-objects/fingerprints/{1}'.format(self.url_base, list_id), data=json.dumps(payload), proxies=self.proxy)
			return resp.status_code, ""
		except Exception as e:
			return 0, e
		