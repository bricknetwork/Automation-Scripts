import json
import datetime
import requests
from urllib.parse import urlparse

class openDNS(object):
	def __init__(self, key, lrdeploymentID, lrvernum, proxy):
		self.lrID = lrdeploymentID
		self.lrversion = lrvernum
		self.proxy = proxy
		self.key = key
		self.url_base = "https://s-platform.api.opendns.com/1.0"
		self.connect = requests.session()

	def blockURL(self, urls):
		self.connect.headers.update({'Content-Type':'application/json'})
		now = datetime.datetime.now()
		UtcTime = now.strftime('%Y-%m-%dT%H:%M:%S.0Z')
		payload = []
		for url in urls:
			domain = '{uri.netloc}'.format(uri=urlparse(url))
			if len(domain) == 0:
				domain = url
			piece = {
				"alertTime": UtcTime,
				"deviceId": self.lrID,
				"deviceVersion": self.lrversion,
				"dstDomain": domain,
				"dstUrl": url,
				"eventTime": UtcTime,
				"protocolVersion": "1.0a",
				"providerName": "LogRhythm"
			}
			payload.append(piece)
		try:
			resp = self.connect.post('{0}/events?customerKey={1}'.format(self.url_base,self.key), data=json.dumps(payload), proxies=self.proxy)
			return resp.status_code, resp.json()
		except Exception as e:
			return 0, e

	def getDomains(self):
		self.connect.headers.update({'ACCEPT':'application/json'})
		try:
			resp = self.connect.get('{0}/domains?customerKey={1}'.format(self.url_base,self.key), proxies=self.proxy)
			return resp.status_code, resp.json()
		except Exception as e:
			return 0, e