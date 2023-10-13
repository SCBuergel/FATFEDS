// SPDX-License-Identifier: GPL-3.0-or-later
pragma solidity 0.8.19;

import { HoprLedger } from "./Ledger.sol";

uint256 constant INDEX_SNAPSHOT_INTERVAL = 24 * 60 * 60;

contract Indexee is HoprLedger(INDEX_SNAPSHOT_INTERVAL) {
    uint256 public val;

    event logNewVal(address indexed setter, uint256 newVal);

    function setNewVal(uint256 newVal) external {
        val = newVal;
        emit logNewVal(msg.sender, newVal);
        indexEvent(abi.encodePacked(logNewVal.selector, msg.sender, newVal));
    }
}