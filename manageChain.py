# Author: Michael Rhodes
# File: manageChain.py
#
# Description: registers nodes on all nodes in the chain, then acts as the IoT
# 	device and tries to validate several valid and invalid hashes
# 

import urllib3
import json
from urllib.parse import urlencode
from time import sleep
import hashlib


#### this variable is used to represent configuration files from a server
dummyConfigServer = ['1','2','3','4','5']
dummyFileIndex = 0

#### CHANGE LOCAL IP TO YOUR LOCAL IP ADDRESS ####
localIP = '192.168.70.138'
hosts = [
	'http://'+localIP+':5001',
	'http://'+localIP+':5002',
	'http://'+localIP+':5003',
	'http://'+localIP+':5004'
	]

# simulates the downloading and hashing of a file
def getConfigHash():
	global dummyFileIndex
	global dummyConfigServer
	m = hashlib.sha256()
	m.update(dummyConfigServer[dummyFileIndex].encode())
	dummyFileIndex += 1
	return m.hexdigest()


http = urllib3.PoolManager()

# register nodes - for each node, don't add itself the list
for host in hosts:
	data = { "nodes": [x for x in hosts if x != host] }
	data= json.dumps(data).encode('utf-8')
	res = http.request('POST', host+'/nodes/register', body=data, headers={'Content-Type': 'application/json'})


# validate current config (this will add a new block to the chain)
configHash = getConfigHash()
data = { "hash": configHash }
data= json.dumps(data).encode('utf-8')
res = http.request('POST', hosts[0]+'/validateHash', body=data, headers={'Content-Type': 'application/json'})
print ('Trying to validate current config hash:',configHash)
print ('    ',res.data)


# validate new config (this will add a new block to the chain)
configHash = getConfigHash()
data = { "hash": configHash }
data= json.dumps(data).encode('utf-8')
res = http.request('POST', hosts[0]+'/validateHash', body=data, headers={'Content-Type': 'application/json'})
print ('\nTrying to validate new config hash:',configHash)
print ('    ',res.data)


# validate same config (no new block will be added)
dummyFileIndex=1
configHash = getConfigHash()
data = { "hash": configHash }
data= json.dumps(data).encode('utf-8')
res = http.request('POST', hosts[0]+'/validateHash', body=data, headers={'Content-Type': 'application/json'})
print ('\nTrying to validate same config hash:',configHash)
print ('    ',res.data)


# try to validate an invalid hash
sleep(5)
data = { "hash": "2" }
getConfigHash()		# keeps dummyFileIndex in sync with the blockchain
data= json.dumps(data).encode('utf-8')
res = http.request('POST', hosts[0]+'/validateHash', body=data, headers={'Content-Type': 'application/json'})
print ("\nTrying to validate an invalid hash ('2'):")
print ('    ',res.data)


