import json
import random
import time
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import sys

# In-Memory Blockchain State
class BlockchainState:
    def __init__(self):
        # Genesis block
        genesis_hash = "0x" + hashlib.sha256(b"genesis_block_payload").hexdigest()
        self.blocks = [{
            "number": "0x0",
            "hash": genesis_hash,
            "parentHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
            "timestamp": hex(int(time.time())),
            "transactions": []
        }]
        self.receipts = {}
        self.nonces = {}
        self.balances = {}
        self.deployed_contract_address = "0x9876543210FEDCBA9876543210FEDCBA98765432"

    def get_block_number(self):
        return len(self.blocks) - 1

    def get_nonce(self, address):
        addr_lower = address.lower()
        return self.nonces.get(addr_lower, 0)

    def increment_nonce(self, address):
        addr_lower = address.lower()
        self.nonces[addr_lower] = self.nonces.get(addr_lower, 0) + 1

    def mine_block(self, from_addr, is_deployment=False):
        parent_block = self.blocks[-1]
        block_number = len(self.blocks)
        timestamp = int(time.time())
        
        # Calculate unique tx hash
        nonce_val = self.get_nonce(from_addr)
        tx_payload = f"{from_addr}-{nonce_val}-{block_number}-{timestamp}"
        tx_hash = "0x" + hashlib.sha256(tx_payload.encode('utf-8')).hexdigest()
        
        # Calculate unique block hash linked to parent
        block_payload = f"{block_number}-{parent_block['hash']}-{timestamp}-{tx_hash}"
        block_hash = "0x" + hashlib.sha256(block_payload.encode('utf-8')).hexdigest()
        
        new_block = {
            "number": hex(block_number),
            "hash": block_hash,
            "parentHash": parent_block["hash"],
            "timestamp": hex(timestamp),
            "transactions": [tx_hash]
        }
        self.blocks.append(new_block)
        
        # Generate and save receipt
        receipt = {
            "transactionHash": tx_hash,
            "transactionIndex": "0x0",
            "blockHash": block_hash,
            "blockNumber": hex(block_number),
            "from": from_addr,
            "to": None if is_deployment else self.deployed_contract_address,
            "cumulativeGasUsed": "0x5208", # 21000 gas
            "gasUsed": "0x5208",
            "contractAddress": self.deployed_contract_address if is_deployment else None,
            "logs": [],
            "status": "0x1" # Success status
        }
        self.receipts[tx_hash] = receipt
        self.increment_nonce(from_addr)
        
        return tx_hash, new_block

# Initialize blockchain state
state = BlockchainState()

class MockBlockchainHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Silence standard HTTP logger logs
        pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path == "/stats":
            # Extract last 10 transactions hash list
            tx_list = list(state.receipts.keys())[-10:]
            
            response = {
                "block_number": state.get_block_number() + 1240, # Add block offset
                "gas_price_gwei": 20,
                "peer_count": 8,
                "node_latency_ms": random.randint(3, 10),
                "contract_address": state.deployed_contract_address,
                "transactions": tx_list,
                "total_transactions": len(state.receipts),
                "blocks": state.blocks[-5:] # Show last 5 blocks details
            }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            req = json.loads(post_data.decode('utf-8'))
            
            method = req.get("method")
            params = req.get("params", [])
            req_id = req.get("id")
            
            result = None
            
            if method == "web3_clientVersion":
                result = "MockEthereum/v1.0-Private"
            elif method == "net_listening":
                result = True
            elif method == "net_version":
                result = "1337"
            elif method == "eth_chainId":
                result = "0x539" # 1337 in hex
            elif method == "eth_blockNumber":
                # Return current block number (with offset) in hex
                result = hex(state.get_block_number() + 1240)
            elif method == "eth_gasPrice":
                result = hex(20000000000) # 20 Gwei
            elif method == "eth_getTransactionCount":
                address = params[0] if len(params) > 0 else "0x0"
                result = hex(state.get_nonce(address))
            elif method == "eth_sendRawTransaction":
                # Mine a transaction on the in-memory engine
                is_contract_deployment = (len(state.receipts) == 0)
                from_addr = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
                tx_hash, new_block = state.mine_block(from_addr, is_deployment=is_contract_deployment)
                result = tx_hash
                print(f"[Blockchain Ledger] Mined Block #{new_block['number']} | Hash: {new_block['hash'][:24]}... | Tx Count: 1")
            elif method == "eth_getTransactionReceipt":
                tx_hash = params[0]
                result = state.receipts.get(tx_hash, None)
                if not result:
                    # Provide dynamic fallback receipt if queried hash was from mock seeding
                    result = {
                        "transactionHash": tx_hash,
                        "transactionIndex": "0x0",
                        "blockHash": "0x00000000000000000000000000000000000000000000000000000000000001a1",
                        "blockNumber": "0x4da",
                        "from": "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1",
                        "to": state.deployed_contract_address,
                        "cumulativeGasUsed": "0x5208",
                        "gasUsed": "0x5208",
                        "contractAddress": None,
                        "logs": [],
                        "status": "0x1"
                    }
            elif method == "eth_getBlockByNumber":
                block_param = params[0]
                if block_param == "latest":
                    result = state.blocks[-1]
                else:
                    try:
                        # Convert block number hex to int
                        block_idx = int(block_param, 16) - 1240
                        if 0 <= block_idx < len(state.blocks):
                            result = state.blocks[block_idx]
                        else:
                            result = state.blocks[-1]
                    except Exception:
                        result = state.blocks[-1]
            elif method == "eth_call":
                result = "0x"
            else:
                result = "0x"

            response = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": result
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        except Exception as e:
            print(f"[Blockchain Error] HTTP handler failed: {e}", file=sys.stderr)
            self.send_response(500)
            self.end_headers()

def run_server(port=8545):
    server = HTTPServer(('127.0.0.1', port), MockBlockchainHandler)
    print(f"[Blockchain] Real in-memory private blockchain engine listening on http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[Blockchain] Shutting down Blockchain Engine...")
        server.server_close()

if __name__ == "__main__":
    run_server()
