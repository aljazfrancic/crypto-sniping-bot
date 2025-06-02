// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

interface IRouter {
    function swapExactETHForTokensSupportingFeeOnTransferTokens(
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external payable;
}

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

    function snipeToken(
        address router,
        address[] calldata path,
        uint amountOutMin,
        uint deadline
    ) external payable onlyOwner {
        IRouter(router).swapExactETHForTokensSupportingFeeOnTransferTokens{value: msg.value}(
            amountOutMin,
            path,
            address(this),
            deadline
        );
    }

    function quickSell(
        address router,
        address[] calldata path,
        uint amountIn,
        uint amountOutMin,
        uint deadline
    ) external onlyOwner {
        IERC20(path[0]).approve(router, amountIn);
        IRouter(router).swapExactETHForTokensSupportingFeeOnTransferTokens(
            amountOutMin,
            path,
            owner,
            deadline
        );
    }

    function rescueTokens(address token) external onlyOwner {
        IERC20(token).transfer(owner, IERC20(token).balanceOf(address(this)));
    }
}