import os
from web3 import Web3

RPC_URL = os.environ.get("WEB3_PROVIDER_URI", "http://127.0.0.1:8545")
CONTRACT_ADDRESS = os.environ.get("CONTRACT_ADDRESS", "0x0000000000000000000000000000000000000000")
PRIVATE_KEY = os.environ.get("PRIVATE_KEY", "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef")

ABI = [
    {
        "inputs": [
            {"internalType": "uint256", "name": "productId", "type": "uint256"},
            {"internalType": "string", "name": "status", "type": "string"},
            {"internalType": "string", "name": "location", "type": "string"},
            {"internalType": "uint256", "name": "temperature", "type": "uint256"}
        ],
        "name": "logEvent",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "productId", "type": "uint256"},
            {"internalType": "string", "name": "initialStatus", "type": "string"},
            {"internalType": "string", "name": "location", "type": "string"}
        ],
        "name": "registerProduct",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

def get_web3():
    return Web3(Web3.HTTPProvider(RPC_URL))

def log_event_to_blockchain(product_id: int, status: str, location: str, temperature: int = 20) -> str:
    w3 = get_web3()
    if not w3.is_connected():
        print("Web3 is not connected to RPC, returning dummy hash.")
        return "0x_dummy_hash_not_connected"
        
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)
    account = w3.eth.account.from_key(PRIVATE_KEY)
    
    if CONTRACT_ADDRESS == "0x0000000000000000000000000000000000000000":
        return "0x_dummy_hash_contract_not_deployed"

    try:
        tx = contract.functions.logEvent(product_id, status, location, temperature).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 2000000,
            'gasPrice': w3.eth.gas_price
        })
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return w3.to_hex(tx_hash)
    except Exception as e:
        print(f"Failed to log to blockchain: {e}")
        return "0x_error_hash"

def register_product_on_blockchain(product_id: int, status: str, location: str) -> str:
    w3 = get_web3()
    if not w3.is_connected():
        return "0x_dummy_hash"
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)
    account = w3.eth.account.from_key(PRIVATE_KEY)
    
    if CONTRACT_ADDRESS == "0x0000000000000000000000000000000000000000":
        return "0x_dummy_hash_contract_not_deployed"

    try:
        tx = contract.functions.registerProduct(product_id, status, location).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 2000000,
            'gasPrice': w3.eth.gas_price
        })
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return w3.to_hex(tx_hash)
    except Exception as e:
        print(f"Failed to register on blockchain: {e}")
        return "0x_error_hash"
