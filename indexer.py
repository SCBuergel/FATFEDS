import json
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://rpc.gnosischain.com", request_kwargs={'timeout': 60}))

with open('indexee-abi.json') as abi_file:
    abi = abi_file.read()

indexee_address = "0x74Eb4619cBC29F5dd4a6Af16b868eFBf9552B34d"

Indexee = w3.eth.contract(abi = abi)

ind = Indexee(address = indexee_address)

v = ind.functions.val().call()
print(v)

