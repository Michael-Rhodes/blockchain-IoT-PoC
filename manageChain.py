import urllib3
import json
from urllib.parse import urlencode

localIP = '192.168.70.138'
hosts = [
	'http://'+localIP+':5001',
	'http://'+localIP+':5002',
	'http://'+localIP+':5003',
	'http://'+localIP+':5004'
	]
http = urllib3.PoolManager()

# register nodes
for host in hosts:
	data = { "nodes": [x for x in hosts if x != host] }
	data= json.dumps(data).encode('utf-8')
	res = http.request('POST', host+'/nodes/register', body=data, headers={'Content-Type': 'application/json'})

# validate current config
data = { "hash": "1" }
data= json.dumps(data).encode('utf-8')
res = http.request('POST', hosts[0]+'/validateHash', body=data, headers={'Content-Type': 'application/json'})
print (res.data)

# validate if new config is legit
data = { "hash": "2" }
data= json.dumps(data).encode('utf-8')
res = http.request('POST', hosts[0]+'/validateHash', body=data, headers={'Content-Type': 'application/json'})
print (res.data)
