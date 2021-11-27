from solcx import compile_standard, install_solc
import json, os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

# Compile Solidity
install_solc("0.6.0")

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
    solc_version="0.6.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)


# get bytecode
byte_code = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# connecting to ganache
# w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
# chain_id = 1337

# connecting to rinkeby
http_provider = os.getenv("HTTP_PROVIDER")
w3 = Web3(Web3.HTTPProvider(http_provider))
chain_id = 4

my_address = os.getenv("ADDRESS")
private_key = os.getenv("PRIVATE_KEY_ETH")

# create the contract
SimpleStorage = w3.eth.contract(abi=abi, bytecode=byte_code)

# get latest transaction
nonce = w3.eth.getTransactionCount(my_address)

print("Deploying Contract!")
# 1. Building a transaction
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
        "gasPrice": w3.eth.gas_price,
    }
)

# 2. Sign a transaction
signed_tx = w3.eth.account.sign_transaction(transaction, private_key=private_key)

# 3. Send a transaction
tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed Sucessfully!")

# Working with the contract
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)


# Initial value of FavNumber
print(simple_storage.functions.retrieve().call())  # Call

store_transaction = simple_storage.functions.store(15).buildTransaction(
    {
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce+1,
        "gasPrice": w3.eth.gas_price,
    }
)

signed_stored_tx = w3.eth.account.sign_transaction(store_transaction,private_key=private_key)
stored_tx_hash = w3.eth.send_raw_transaction(signed_stored_tx.rawTransaction)
stored_tx_receipt = w3.eth.wait_for_transaction_receipt(stored_tx_hash)

print(simple_storage.functions.retrieve().call())