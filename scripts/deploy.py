import json
import os
from web3 import Web3
from solcx import compile_standard, install_solc

def deploy_contract():
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
        
    chain_id = 1337
    my_address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
    private_key = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"
    
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
    raw_tx = getattr(signed_txn, "raw_transaction", getattr(signed_txn, "rawTransaction", None))
    tx_hash = w3.eth.send_raw_transaction(raw_tx)
    
    print(f"Transaction hash: {tx_hash.hex()}")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    contract_address = tx_receipt.get("contractAddress") if hasattr(tx_receipt, "get") else getattr(tx_receipt, "contractAddress", None)
    if not contract_address:
         contract_address = getattr(tx_receipt, "contract_address", None)
         
    print(f"Contract deployed to address: {contract_address}")
    
    env_lines = []
    if os.path.exists(".env"):
        with open(".env", "r") as env_file:
            env_lines = env_file.readlines()
    
    env_lines = [line for line in env_lines if not line.startswith("CONTRACT_ADDRESS=") and not line.startswith("WEB3_PROVIDER_URI=") and not line.startswith("PRIVATE_KEY=")]
    
    env_lines.append(f"CONTRACT_ADDRESS={contract_address}\n")
    env_lines.append("WEB3_PROVIDER_URI=http://127.0.0.1:8545\n")
    env_lines.append(f"PRIVATE_KEY={private_key}\n")
    
    with open(".env", "w") as env_file:
        env_file.writelines(env_lines)
    print("Successfully saved configuration to .env file.")

if __name__ == "__main__":
    deploy_contract()
