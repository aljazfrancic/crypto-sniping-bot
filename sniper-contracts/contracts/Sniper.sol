// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@uniswap/v2-periphery/contracts/interfaces/IUniswapV2Router02.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/// @title Minimalistic sniping contract for new liquidity pairs
/// @author ChatGPT
/// @notice Use at your own risk. This contract is for educational purposes.
contract Sniper {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    receive() external payable {}

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    /// @notice Buy tokens with native currency as soon as pair is created
    /// @param router Address of the DEX router (e.g., PancakeSwap)
    /// @param path Swap path [WETH, NewToken]
    /// @param amountOutMin Minimum amount of tokens to receive (slippage control)
    /// @param deadline Unix timestamp after which the tx is invalid
    function snipeToken(
        address router,
        address[] calldata path,
        uint256 amountOutMin,
        uint256 deadline
    ) external payable onlyOwner {
        IUniswapV2Router02 dex = IUniswapV2Router02(router);
        dex.swapExactETHForTokensSupportingFeeOnTransferTokens{value: msg.value}(
            amountOutMin,
            path,
            address(this),
            deadline
        );
    }

    /// @notice Sell tokens back to native currency
    function quickSell(
        address router,
        address[] calldata path,
        uint256 amountIn,
        uint256 amountOutMin,
        uint256 deadline
    ) external onlyOwner {
        IERC20(path[0]).approve(router, amountIn);
        IUniswapV2Router02 dex = IUniswapV2Router02(router);
        dex.swapExactTokensForETHSupportingFeeOnTransferTokens(
            amountIn,
            amountOutMin,
            path,
            owner,
            deadline
        );
    }

    /// @notice Emergency withdraw any ERC20
    function rescueTokens(address token) external onlyOwner {
        IERC20(token).transfer(owner, IERC20(token).balanceOf(address(this)));
    }
}