// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MockFactory {
    mapping(address => mapping(address => address)) public getPair;

    function createPair(address tokenA, address tokenB) external {
        getPair[tokenA][tokenB] = address(new MockPair());
    }
}

contract MockPair {
    // Simple mock pair implementation
}
