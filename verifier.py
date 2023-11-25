import requests, json
from web3 import Web3
from eth_abi.packed import encode_packed
from hexbytes import HexBytes

abiFileName = "indexer/abi.json"
dbUrl = "http://127.0.0.1:8000/json/indexerStateDb.json"
contractAddress = "0xcFaD25b3570533867CA8C81E8fC4dD53242088bf"
eventFunctionSelector = HexBytes("0x233629de63670a91aaae19064df62ba6984319be8a24d54d6aaf8c2316cf4f50")
domainSeparator = HexBytes("0x8bb334260a8d6dcd89ec95fd0ae477bb7750afd6ee0cae37dcc08ced791725d0")

with open(abiFileName) as abiFile:
    abi = json.loads(abiFile.read())

db = requests.get(dbUrl).json()

fullInitialHash = Web3.solidity_keccak(["address"], [ contractAddress ]).hex()
currentHash = HexBytes(fullInitialHash[:-8])
print(f"initial hash: {currentHash.hex()}")

for blockNo in db["blocks"]:
    for txHash in db["blocks"][blockNo]:
        for logIndex in db["blocks"][blockNo][txHash]:

            # look up the event name in the ABI
            eventAbi = next(( obj for obj in abi if obj.get("name") == db["blocks"][blockNo][txHash][logIndex]["event"] and obj.get("type") == "event" ), None)
            types_list = [entry["type"] for entry in eventAbi["inputs"]]
            args = list(db["blocks"][blockNo][txHash][logIndex]['args'].values())
            assert len(types_list) == len(args), f"expected list of types from ABI and list of arguments to have same length, but they differ: {len(types_list)} vs {len(args)}"
            
            # add entries for event function selector in the beginning of the lists
            types_list.insert(0, "bytes32")
            args.insert(0, eventFunctionSelector)
            
            print(types_list)
            print(args)
            payload = encode_packed(types_list, args)
            print(f"payload: {payload.hex()}")

            innerHash = Web3.solidity_keccak(["bytes32"], [ payload ])
            print(f"inner hash: {innerHash.hex()}")

            print(f"previous hash: {currentHash.hex()}")

            innerVal = encode_packed(["bytes32", "uint32", "bytes28", "bytes32"], [domainSeparator, int(blockNo), currentHash, innerHash])
            print(f"{innerVal.hex()}")

            fullNewHash = Web3.solidity_keccak(["bytes32"], [ innerVal ]).hex()
            currentHash = HexBytes(fullNewHash[:-8])
            print(f"new hash: {currentHash.hex()}")
            

print(f"VERIFIED ROOT HASH: {currentHash.hex()} at block {blockNo}")
