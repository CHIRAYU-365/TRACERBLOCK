import json
from web3 import Web3
from solcx import compile_standard, install_solc

def deploy_contract():
    # Install solc if not installed
    print("Installing solc...")
    install_solc('0.8.0')
    
    with open("contracts/SupplyChain.sol", "r") as file:
        supply_chain_file = file.read()
        
    print("Compiling contract...")
    compiled_sol = compile_standard(
        {
            "language": "Solidity",
            "sources": {"SupplyChain.sol": {"content": supply_chain_file}},
            "settings": {
                "outputSelection": {
                    "*": {
                        "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                    }
                }
            },
        },
        solc_version="0.8.0",
    )
    
    with open("contracts/compiled_code.json", "w") as file:
        json.dump(compiled_sol, file)
        
    bytecode = compiled_sol["contracts"]["SupplyChain.sol"]["SupplyChain"]["evm"]["bytecode"]["object"]
    abi = compiled_sol["contracts"]["SupplyChain.sol"]["SupplyChain"]["abi"]
    
    print("Connecting to Web3 provider...")
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    if not w3.is_connected():
        print("Failed to connect to web3 provider.")
        return
        
    chain_id = 1337 # Ganache default chain ID, modify as needed
    my_address = "YOUR_ADDRESS_HERE"
    private_key = "YOUR_PRIVATE_KEY_HERE"
    
    print("Deploying contract...")
    SupplyChain = w3.eth.contract(abi=abi, bytecode=bytecode)
    nonce = w3.eth.get_transaction_count(my_address)
    
    transaction = SupplyChain.constructor().build_transaction({
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
        "gasPrice": w3.eth.gas_price
    })
    
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    
    print(f"Transaction hash: {tx_hash.hex()}")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Contract deployed to address: {tx_receipt.contractAddress}")

if __name__ == "__main__":
    deploy_contract()
