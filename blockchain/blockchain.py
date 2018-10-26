# Author: Michael Rhodes
# File: blockchain.py
#
# Description: a blockchain using the PBFT consensus algorithm to validate
#	configuration hashes


from flask import Flask, jsonify, request
from time import time
from socket import gethostname
import json
import urllib3
import hashlib

#### this variable is used to represent configuration files from a server
dummyConfigServer = ['1','2','3','4','5']

# define blockchain class
class Blockchain:
	def __init__(self):
		self.nodes = set()
		self.chain = []
		self.lastBlock = None
		self.prepareMessages = []
		self.commitMessages = []
		self.nodeid = gethostname()

		# create genesis block
		block = self.add_block(self.create_block('1', prev_hash='0'))

	def add_block(self, block):
		self.chain.append(block)
		self.lastBlock = block
		return True

	def create_block(self, newHash, prev_hash=None):
		if not prev_hash:
			prev_hash = self.block_hash(self.chain[-1])
		block = {
			'index': len(self.chain),
			'hash': newHash,
			'prev_hash': prev_hash,
			'timestamp': time()
		}
		return block

	def block_hash(self, block):
		return block['hash']

	def add_node(self, address):
		self.nodes.add(address)
		return True

	# stage in PBFT - once >2/3 of messages are the same, validate then share result 
	def prepare(self, block):
		self.prepareMessages.append(block)
		if (len(self.prepareMessages) >= len(self.nodes)):
			for b in self.prepareMessages:
				count = 0
				for b1 in self.prepareMessages:
					if (b == b1):
						count += 1
				if (count > ((len(self.nodes) * 2) / 3)):
					self.validate(b)
					return
			self.validate(None)
		return 

	# verify block contains an accurate hash (both previous and new)
	def validate(self, block):
		chain = self.chain.copy()
		if (block and block['prev_hash'] == self.lastBlock['hash']):
			if (self.isValidHash(block['hash'])):
				chain.append(block)
			else: #remove from prepare messages so it doesn't impact future validation
				self.prepareMessages = [x for x in self.prepareMessages if x != block]
		self.commit(chain)
		data = {'chain': chain}
		self.sendToNodes('/chain/commit', data)
		return 

	
	# represents a function that downloads the current config and verifies the hash
	@staticmethod
	def isValidHash(m):
		global dummyConfigServer
		for config in dummyConfigServer:
			if m == hashlib.sha256(config.encode()).hexdigest():
				return True
		return False


	# final stage in PBFT - stores the chain that appears the most (>2/3)
	def commit(self, chain):
		self.commitMessages.append(chain)
		count = 0
		for bchain in self.commitMessages:
			if (len(chain) != len(bchain)):
				continue
			for d1, d2 in zip(bchain, chain):
				for key, value in d1.items():
					if value != d2[key]:
						# ignore timestamps in genesis block
						if key == 'timestamp' and len(chain) <= 2:
							continue
						count -= 1
						break
			count += 1
		if (count > (((len(self.nodes)+1)*2)/3)):
			self.chain = chain
			self.lastBlock = self.chain[-1]
			self.prepareMessages.clear()
			self.commitMessages.clear()
		return

	# communicates the data between nodes at given endpoint
	def sendToNodes(self, loc, data):
		data = json.dumps(data).encode('utf-8')
		http = urllib3.PoolManager()
		for node in blockchain.nodes:
			res = http.request(
				'POST',
				node+loc,
				body=data,
				headers={'Content-Type': 'application/json'}
			)




# create blockchain
blockchain = Blockchain()

# create flask API
app = Flask(__name__)


@app.route('/nodes',methods=['GET'])
# returns list of nodes in the chain
def getNodes():
	return jsonify(list(blockchain.nodes)), 201


@app.route('/nodes/register',methods=['POST'])
# adds a new node to the chain
def registerNodes():
	nodes = request.get_json().get('nodes')
	if nodes is None:
		return "Error: invalid list of nodes", 400
	for node in nodes:
		blockchain.add_node(node)
	response = {
		'message': "Success",
		'Nodes_Added': len(nodes)
	}
	return jsonify(response), 200



@app.route('/validateHash',methods=['POST'])
# This is where IoT devices verify the hash of the config file is correct
# If the hash is not currently in the blockchain, it forwards the request to
# all other nodes through '/chain/pre-prepare'
def validateHash():
	digest = request.get_json().get('hash')
	if digest is None:
		return "Error: no hash provided", 400

	if (blockchain.block_hash(blockchain.lastBlock) == digest):
		return "Success: Current hash is valid", 200

	else:
		# forward new block to other nodes for validation
		chainLen = len(blockchain.chain)
		newBlock = blockchain.create_block(digest)
		data = {
			'nodeID': blockchain.nodeid,
			'block': newBlock
		}
		blockchain.sendToNodes('/chain/pre-prepare', data)
		if (len(blockchain.chain) > chainLen):
			return "Success: Hash is valid. New block was added to the chain."
		return "Failure: Hash is invalid. Please try again.", 200
 


@app.route('/chain',methods=['GET'])
# returns the current chain
def getChain():
	response = {
		'message': 'Current chain',
		'chain': blockchain.chain
	}
	return jsonify(response), 200



@app.route('/chain/pre-prepare',methods=['POST'])
# receives the chain with the new block and forwards what it heard to all other
# nodes through '/chain/prepare'
def prePrepare():
	data = request.get_json()
	blockchain.prepare(data.get('block'))
	blockchain.sendToNodes('/chain/prepare', data)
	return "Success: forwarded message", 200




@app.route('/chain/prepare',methods=['POST'])
# once the node recieves a consistent message (> 2/3), it performs validation and
# sends the result to all other nodes
def getPrepareMessages():
	blockchain.prepare(request.get_json().get('block'))
	return "Success: 1", 200



@app.route('/chain/commit',methods=['POST'])
# updates the chain if > 2/3 of nodes say the new block is valid
def getCommitMessages():
	blockchain.commit(request.get_json().get('chain'))
	return "Success: 1", 200


@app.route('/debug')
def debug():
	response = {
		'nodes': list(blockchain.nodes),
		'chain': blockchain.chain,
		'lastblock': blockchain.lastBlock,
		'prepare': blockchain.prepareMessages,
		'commit': blockchain.commitMessages,
		'uid': blockchain.nodeid
#		'readytovalidate': blockchain.readyToValidate
	}
	return jsonify(response), 200



if __name__ == '__main__':
	app.run(host='0.0.0.0')
