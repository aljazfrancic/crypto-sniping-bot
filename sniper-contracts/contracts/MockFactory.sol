// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract MockFactory {
    function getPair(address, address) external pure returns (address) {
        return address(0);
    }
}