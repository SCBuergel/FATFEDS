"""
based on https://web3py.readthedocs.io/en/latest/examples.html#example-code by by Mikko Ohtamaa

A stateful event scanner for Ethereum-based blockchains using web3.py.

With the stateful mechanism, you can do one batch scan or incremental scans,
where events are added wherever the scanner left off.
"""

from web3 import Web3

from EventScannerState import EventScannerState
from JSONifiedState import JSONifiedState
from utils import *
from EventScanner import EventScanner

if __name__ == "__main__":
    # Scans all indicated events of a contract.
    # The demo supports persistent state by using a JSON file.
    import sys
    import json
    from web3.providers.rpc import HTTPProvider

    # We use tqdm library to render a nice progress bar in the console
    # https://pypi.org/project/tqdm/
    from tqdm import tqdm

    def run():

        """
        if len(sys.argv) < 2:
            print("Usage: eventscanner.py http://your-node-url")
            sys.exit(1)
        api_url = sys.argv[1]
        """
        api_url = "https://rpc.gnosis.gateway.fm"

        provider = HTTPProvider(api_url)

        # Remove the default JSON-RPC retry middleware
        # as it correctly cannot handle eth_getLogs block range
        # throttle down.
        provider.middlewares.clear()

        w3 = Web3(provider)

        ADDRESS = "0xcFaD25b3570533867CA8C81E8fC4dD53242088bf"

        ABI = """
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
    """
        abi = json.loads(ABI)
        CONTRACT = w3.eth.contract(abi=abi)

        deployed_at_block = 30454954 
        # Restore/create our persistent state
        state = JSONifiedState()
        state.restore()

        # chain_id: int, w3: Web3, abi: Dict, state: EventScannerState, events: List, filters: Dict, max_chunk_scan_size: int=10000
        scanner = EventScanner(
                w3=w3,
                contract=CONTRACT,
                state=state,
                events=[CONTRACT.events.logNewVal],
                filters={"address": ADDRESS},
                # How many maximum blocks at the time we request from JSON-RPC
                # and we are unlikely to exceed the response size limit of the JSON-RPC server
                max_chunk_scan_size=10000
                )

        # Assume we might have scanned the blocks all the way to the last Ethereum block
        # that mined a few seconds before the previous scan run ended.
        # Because there might have been a minor Ethereum chain reorganisations
        # since the last scan ended, we need to discard
        # the last few blocks from the previous scan results.
        chain_reorg_safety_blocks = 10
        scanner.delete_potentially_forked_block_data(state.get_last_scanned_block() - chain_reorg_safety_blocks)

        # Scan from [last block scanned] - [latest ethereum block]
        # Note that our chain reorg safety blocks cannot go negative
        start_block = max(state.get_last_scanned_block() - chain_reorg_safety_blocks, deployed_at_block)
        end_block = scanner.get_suggested_scan_end_block()
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
            result, total_chunks_scanned = scanner.scan(start_block, end_block, progress_callback=_update_progress)

        state.save()
        duration = time.time() - start
        print(f"Scanned total {len(result)} Transfer events, in {duration} seconds, total {total_chunks_scanned} chunk scans performed")

    run()

