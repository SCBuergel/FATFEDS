// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Test, console2} from "forge-std/Test.sol";
import {Indexee} from "../src/Indexee.sol";

contract IndexeeTest is Test {
    Indexee public indexee;

    function setUp() public {
        indexee = new Indexee();
        indexee.setNewVal(1);
    }

    function test_SetNewVal(uint256 x) public {
        indexee.setNewVal(x);
        assertEq(indexee.val(), x);
    }
}
