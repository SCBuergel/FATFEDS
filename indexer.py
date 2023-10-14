import json
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://rpc.gnosischain.com", request_kwargs={'timeout': 60}))

with open('indexee-abi.json') as abi_file:
    abi_string = abi_file.read()

abi = json.loads(abi_string)

indexee_address = "0xcFaD25b3570533867CA8C81E8fC4dD53242088bf"

event_abi = '''{
        "anonymous": false,
        "inputs": [
            {
                "indexed": true,
                "internalType": "address",
                "name": "setter",
                "type": "address"
                },
            {
                "indexed": false,
                "internalType": "uint256",
                "name": "newVal",
                "type": "uint256"
                }
            ],
        "name": "logNewVal",
        "type": "event"
        }'''

event = json.loads(event_abi)

Indexee = w3.eth.contract(abi = abi)

ind = Indexee(address = indexee_address)

v = ind.functions.val().call()
print(v)

