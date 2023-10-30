"""
based on https://web3py.readthedocs.io/en/latest/examples.html#example-code by by Mikko Ohtamaa

A stateful event scanner for Ethereum-based blockchains using web3.py.

With the stateful mechanism, you can do one batch scan or incremental scans,
where events are added wherever the scanner left off.
"""

# We use tqdm library to render a nice progress bar in the console
# https://pypi.org/project/tqdm/
from tqdm import tqdm
import sys
import json
from web3.providers.rpc import HTTPProvider
from web3 import Web3
from flask import Flask, send_from_directory

from EventScannerState import EventScannerState
from JSONifiedState import JSONifiedState
from utils import *
from EventScanner import EventScanner


class indexer:
    def __init__(
            self,
            dbFolder,
            dbFileName,
            rpcProviderUrl,
            contractAddress,
            contractAbi,
            contractDeploymentBlock,
            eventNameListToIndex,
            maxChunkSize=10000,
            chainReorgSafetyBlocks=10,
            serveDb=True,
            dbServerPort=8000,
            indexerDbFileName="indexDb.json"
            ):
        
        self.dbFolder = dbFolder
        self.dbFileName = dbFileName
        self.rpcProviderUrl = rpcProviderUrl
        self.contractAddress = contractAddress
        self.contractAbi = contractAbi
        self.contractDeploymentBlock = contractDeploymentBlock
        self.eventNameListToIndex = eventNameListToIndex
        self.maxChunkSize = maxChunkSize
        self.chainReorgSafetyBlocks = chainReorgSafetyBlocks
        self.serveDb = serveDb
        self.dbServerPort = dbServerPort
        
        provider = HTTPProvider(self.rpcProviderUrl)

        # Remove the default JSON-RPC retry middleware
        # as it correctly cannot handle eth_getLogs block range
        # throttle down.
        provider.middlewares.clear()

        w3 = Web3(provider)

        abi = json.loads(self.contractAbi)
        CONTRACT = w3.eth.contract(abi=abi)

        # Restore/create our persistent state
        self.state = JSONifiedState(indexerDbFileName)
        self.state.restore()

        events = [CONTRACT.events[a] for a in self.eventNameListToIndex]
        # chain_id: int, w3: Web3, abi: Dict, state: EventScannerState, events: List, filters: Dict, max_chunk_scan_size: int=10000
        self.scanner = EventScanner(
                w3=w3,
                contract=CONTRACT,
                state=self.state,
                events=events,
                filters={"address": contractAddress},
                # How many maximum blocks at the time we request from JSON-RPC
                # and we are unlikely to exceed the response size limit of the JSON-RPC server
                max_chunk_scan_size=self.maxChunkSize
                )


    def scan(self):
        self.scanner.delete_potentially_forked_block_data(self.state.get_last_scanned_block() - self.chainReorgSafetyBlocks)

        # Scan from [last block scanned] - [latest ethereum block]
        # Note that our chain reorg safety blocks cannot go negative
        start_block = max(self.state.get_last_scanned_block() - self.chainReorgSafetyBlocks, self.contractDeploymentBlock)
        end_block = self.scanner.get_suggested_scan_end_block()
        blocks_to_scan = end_block - start_block

        print(f"Scanning events from blocks {start_block} - {end_block}")

        # Render a progress bar in the console
        start = time.time()
        with tqdm(total=blocks_to_scan) as progress_bar:
            def _update_progress(start, end, current, current_block_timestamp, chunk_size, events_count):
                if current_block_timestamp:
                    formatted_time = current_block_timestamp.strftime("%d-%m-%Y")
                else:
                    formatted_time = "no block time available"
                progress_bar.set_description(f"Current block: {current} ({formatted_time}), blocks in a scan batch: {chunk_size}, events processed in a batch {events_count}")
                progress_bar.update(chunk_size)

            # Run the scan
            result, total_chunks_scanned = self.scanner.scan(start_block, end_block, progress_callback=_update_progress)

        self.state.save()
        duration = time.time() - start
        print(f"Scanned total {len(result)} Transfer events, in {duration} seconds, total {total_chunks_scanned} chunk scans performed")


def run():
    ind = indexer(
            dbFolder="dbFolder",
            dbFileName="indexerStateDb.json",
            rpcProviderUrl="https://rpc.gnosis.gateway.fm",
            contractAddress="0xcFaD25b3570533867CA8C81E8fC4dD53242088bf",
            contractAbi="""
                [
                    {
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
                    }
                ]
            """,
            eventNameListToIndex=["logNewVal"],
            contractDeploymentBlock=30454954,
            maxChunkSize=10000,
            serveDb=True,
            dbServerPort=8000
            )
    ind.scan()

run()

app = Flask(__name__)
@app.route("/json/<filename>")
def serve_json(filename):
    return send_from_directory("./state_db/", filename, as_attachment=False, mimetype="application/json")
app.run(port = 8000)
