import requests, json
# import sha3 # pip install pysha3
from web3 import Web3
from eth_abi.packed import encode_packed
from hexbytes import HexBytes

dbUrl = "http://127.0.0.1:8000/json/indexerStateDb.json"

dbFile = requests.get(dbUrl).json()

# print(json.dumps(dbFile, indent=2))

# h = sha256.keccak_256()
# h.update(123)

contractAddress = "0xcFaD25b3570533867CA8C81E8fC4dD53242088bf"
initialHash = Web3.solidity_keccak(["address"], [ contractAddress ])
print(f"initial hash: {initialHash.hex()}")

eventFunctionSelector = HexBytes("0x233629de63670a91aaae19064df62ba6984319be8a24d54d6aaf8c2316cf4f50")
param1 = "0x4327D722daD3BE8F8Fb14443c1c3d4A2c5067922"
param2 = 5
payload = encode_packed(["bytes32", "address", "uint256"], [ eventFunctionSelector, param1, param2 ])
print(f"payload: {payload.hex()}")

innerHash = Web3.solidity_keccak(["bytes32"], [ payload ])
print(f"inner hash: {innerHash.hex()}")

domainSeparator = HexBytes("0x8bb334260a8d6dcd89ec95fd0ae477bb7750afd6ee0cae37dcc08ced791725d0")
blockNumber = 30455184
previousHash = initialHash.hex()
cutHash = HexBytes(previousHash[:-8])
print(f"{previousHash}")
print(f"{cutHash.hex()}")

innerVal =  encode_packed(["bytes32", "uint32", "bytes28", "bytes32"], [domainSeparator, blockNumber, cutHash, innerHash])

print(f"{innerVal.hex()}")

newHash = Web3.solidity_keccak(["bytes32"], [ innerVal ])

print(f"new hash: {newHash.hex()}")
