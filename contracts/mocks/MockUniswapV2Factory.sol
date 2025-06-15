// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MockUniswapV2Factory {
    address public pair;
    constructor(address _pair) {
        pair = _pair;
    }
    function getPair(address, address) external view returns (address) {
        return pair;
    }
} 