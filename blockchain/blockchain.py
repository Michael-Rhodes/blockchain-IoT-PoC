from flask import Flask, jsonify
from time import time

# define blockchain class
class Blockchain:
	def __init__(self):
		self.nodes = set()
		self.chain = []
		self.lastBlock = None
		self.prepareMessages = []
		self.commitMessages = []
	
		# create genesis block
		block = self.add_block(self.create_block('1', prev_hash='0'))

	def add_block(self, block):
		self.chain.append(block)
		return True

	def create_block(self, newHash, prev_hash=None):
		if not prev_hash:
			prev_hash = self.block_hash(self.chain[-1])
		block = {
			'index': len(self.chain),
			'hash': newHash,
			'prev_hash': prev_hash,
			'timestamp': time(),
			'transaction':	{}
		}
		return block

	def block_hash(self, block):
		return block['hash']

	def add_node(self, address):
		self.nodes.add(address)
		return True

# create blockchain
blockchain = Blockchain()

# create flask API
app = Flask(__name__)

# create unique id for this node

@app.route('/nodes',methods=['GET'])
# returns list of nodes in the chain
def getNodes():
	return jsonify(list(blockchain.nodes)), 201

@app.route('/nodes/register',methods=['POST'])
# adds a new node to the chain
def registerNode():
	return

@app.route('/validateHash',methods=['POST'])
# This is where IoT devices verify the hash of the config file is correct
# If the hash is not currently in the blockchain, it forwards the request to
# all other nodes through '/chain/pre-prepare'
def validateHash():
	return

@app.route('/chain',methods=['GET'])
# returns the current chain
def getChain():
	response = {
		'message': 'Current chain',
		'chain': blockchain.chain
	}
	return jsonify(response), 200

@app.route('/chain/pre-prepare',methods=['POST'])
# receives the chain with the new block and forwards what it heard from all other
# nodes through '/chain/prepare'
def prePrepare():
	return

@app.route('/chain/prepare',methods=['POST'])
# once the node recieves a consistent message (> 2/3), it performs validation and
# sends the result to all other nodes
def prepare():
	return

@app.route('/chain/commit',methods=['POST'])
# updates the chain if > 2/3 of nodes say the new block is valid
def commit():
	return

@app.route('/debug')
def debug():
	response = {
		'nodes': list(blockchain.nodes),
		'chain': blockchain.chain,
		'lastblock': blockchain.lastBlock,
		'prepare': blockchain.prepareMessages,
		'commit': blockchain.commitMessages
	}
	return jsonify(response), 200

if __name__ == '__main__':
	app.run(host='0.0.0.0')
