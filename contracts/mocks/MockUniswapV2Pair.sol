// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MockUniswapV2Pair {
    address public token0;
    address public token1;
    uint112 public reserve0;
    uint112 public reserve1;
    uint32 public blockTimestampLast;

    constructor(address _token0, address _token1, uint112 _reserve0, uint112 _reserve1) {
        token0 = _token0;
        token1 = _token1;
        reserve0 = _reserve0;
        reserve1 = _reserve1;
        blockTimestampLast = uint32(block.timestamp);
    }

    function getReserves() external view returns (uint112, uint112, uint32) {
        return (reserve0, reserve1, blockTimestampLast);
    }
} 