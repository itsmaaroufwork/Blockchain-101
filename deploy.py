from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

print("Installing...")
install_solc("0.8.0")

# Compile our Slidity

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.8.0",
)
with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]
# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# for connecting to rinkeby

w3 = Web3(
    Web3.HTTPProvider("https://rinkeby.infura.io/v3/33620f40de464a2a8c6000d5fe9be12e")
)
chain_id = 4
my_address = "0xb3B365aB97FfBaEC03a85faA0F4af8562A190e9C"
private_key = os.getenv("PRIVATE_KEY")

# create the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# Get the latestest transaction
nonce = w3.eth.getTransactionCount(my_address)

# 1. Build a transaction
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce,
    }
)
# 2. Sing a transaction
singed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
# 3. Send a transaction
# Send this signed transaction
print("Deploying Contract...")
tx_hash = w3.eth.send_raw_transaction(singed_txn.rawTransaction)

# Wait for Block Confirmations
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed!")
# Working with the contract, you always need
# Contract Address
# Contract ABI
Simple_Storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
# Calling a View Function with Web3.py
# Call VS Transact
# Call -> Simulate making the call and getting a return vlue "Calls don't make a state change"
# Transact -> Actually make a state change

# Initial value of favorite number
print(Simple_Storage.functions.retrieve().call())

# 1. Build a transaction
print("Updating Contract...")
store_transaction = Simple_Storage.functions.store(5).buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce + 1,
    }
)
# 2. Sing a transaction
singed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)
# 3. Send a transaction
send_store_tx = w3.eth.send_raw_transaction(singed_store_txn.rawTransaction)
# Wait for Block Confirmations
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print("Updated!")
print("Done :D")
