// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract MockUniswapV2Router {
    address public immutable WETH;
    address public factoryAddress;
    
    constructor(address _WETH) {
        WETH = _WETH;
    }
    
    function setFactory(address _factory) external {
        factoryAddress = _factory;
    }
    
    function factory() external view returns (address) {
        return factoryAddress;
    }
    
    function swapExactETHForTokens(
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external payable returns (uint[] memory amounts) {
        require(path[0] == WETH, "Invalid path");
        require(deadline >= block.timestamp, "Deadline expired");
        
        // Mock a simple 1:1 swap
        uint256 amountOut = msg.value;
        IERC20(path[1]).transfer(to, amountOut);
        
        amounts = new uint256[](2);
        amounts[0] = msg.value;
        amounts[1] = amountOut;
    }
    
    function swapExactTokensForETH(
        uint amountIn,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external returns (uint[] memory amounts) {
        require(path[1] == WETH, "Invalid path");
        require(deadline >= block.timestamp, "Deadline expired");
        
        // Mock a simple 1:1 swap
        IERC20(path[0]).transferFrom(msg.sender, address(this), amountIn);
        payable(to).transfer(amountIn);
        
        amounts = new uint256[](2);
        amounts[0] = amountIn;
        amounts[1] = amountIn;
    }
    
    function getAmountsOut(uint amountIn, address[] calldata path)
        external pure returns (uint[] memory amounts) {
        amounts = new uint256[](2);
        amounts[0] = amountIn;
        amounts[1] = amountIn; // Mock 1:1 price
    }
} 