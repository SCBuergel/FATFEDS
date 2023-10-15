## Fast And Trustless Framework for Event Data Syncing (FATFEDS)

This is an MVP implementation of a Fast And Trustless Framework for Event Data Syncing (FATFEDS). Applications can rapidly sync data by downloading a compressed file of past event data. That data is trustless as it is compared to an an on-chain hash chain of all event data via a single on-chain data read of the tip of the hash chain.

The system comprises:
1. **HOPR Ledger**: A base contract that implements the on-chain hash chain.
2. **Indexee contract**: A contract that is derived from HOPR Ledger and which utilizes it's hash chain for event data.
3. **Indexer service**: A service that consumes legacy on-chain event data (which is slow) to establish a database of event data.
4. **Event data server**: The (compressed) database of indexed event data is served to clients.
5. **Event data verification client**: A client that pulls data from an event data server, calculates the tip of the hash chain of that data and compares it to the tip of the chain that's read from on-chain
