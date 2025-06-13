// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

interface IUniswapV2Router02 {
    function factory() external pure returns (address);
    function WETH() external pure returns (address);
    
    function swapExactETHForTokens(
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external payable returns (uint[] memory amounts);
    
    function swapExactTokensForETH(
        uint amountIn,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external returns (uint[] memory amounts);
    
    function getAmountsOut(uint amountIn, address[] calldata path)
        external view returns (uint[] memory amounts);
}

interface IUniswapV2Pair {
    function getReserves() external view returns (uint112 reserve0, uint112 reserve1, uint32 blockTimestampLast);
    function token0() external view returns (address);
    function token1() external view returns (address);
}

contract Sniper is Ownable, ReentrancyGuard {
    IUniswapV2Router02 public immutable router;
    address public immutable WETH;
    
    uint256 public maxSlippage = 500; // 5% in basis points
    uint256 public deadline = 300; // 5 minutes
    
    mapping(address => bool) public blacklistedTokens;
    mapping(address => uint256) public tokenBalances;
    
    event TokenBought(address indexed token, uint256 amountIn, uint256 amountOut, uint256 timestamp);
    event TokenSold(address indexed token, uint256 amountIn, uint256 amountOut, uint256 timestamp);
    event SlippageUpdated(uint256 newSlippage);
    event DeadlineUpdated(uint256 newDeadline);
    event TokenBlacklisted(address indexed token, bool blacklisted);
    
    constructor(address _router) {
        require(_router != address(0), "Invalid router address");
        router = IUniswapV2Router02(_router);
        WETH = router.WETH();
    }
    
    function buyToken(
        address token,
        uint256 minAmountOut
    ) external payable onlyOwner nonReentrant {
        require(msg.value > 0, "No ETH sent");
        require(!blacklistedTokens[token], "Token is blacklisted");
        require(token != address(0), "Invalid token address");
        
        address[] memory path = new address[](2);
        path[0] = WETH;
        path[1] = token;
        
        // Calculate minimum output considering slippage
        uint256[] memory amountsOut = router.getAmountsOut(msg.value, path);
        uint256 amountOutMin = minAmountOut > 0 ? minAmountOut : (amountsOut[1] * (10000 - maxSlippage)) / 10000;
        
        uint256 balanceBefore = IERC20(token).balanceOf(address(this));
        
        uint256[] memory amounts = router.swapExactETHForTokens{value: msg.value}(
            amountOutMin,
            path,
            address(this),
            block.timestamp + deadline
        );
        
        uint256 balanceAfter = IERC20(token).balanceOf(address(this));
        uint256 actualReceived = balanceAfter - balanceBefore;
        
        tokenBalances[token] += actualReceived;
        
        emit TokenBought(token, msg.value, amounts[1], block.timestamp);
    }
    
    function sellToken(address token, uint256 amount) external onlyOwner {
        require(amount > 0, "Amount must be greater than 0");
        require(IERC20(token).balanceOf(address(this)) >= amount, "Insufficient token balance");

        IERC20(token).approve(address(router), amount);

        address[] memory path = new address[](2);
        path[0] = token;
        path[1] = WETH;

        router.swapExactTokensForETH(
            amount,
            0, // Accept any amount of ETH
            path,
            address(this),
            block.timestamp + deadline
        );
    }
    
    function updateSlippage(uint256 _maxSlippage) external onlyOwner {
        require(_maxSlippage <= 5000, "Slippage too high"); // Max 50%
        maxSlippage = _maxSlippage;
        emit SlippageUpdated(_maxSlippage);
    }
    
    function updateDeadline(uint256 _deadline) external onlyOwner {
        require(_deadline >= 60, "Deadline too short"); // Min 1 minute
        require(_deadline <= 3600, "Deadline too long"); // Max 1 hour
        deadline = _deadline;
        emit DeadlineUpdated(_deadline);
    }
    
    function blacklistToken(address token, bool blacklist) external onlyOwner {
        blacklistedTokens[token] = blacklist;
        emit TokenBlacklisted(token, blacklist);
    }
    
    function getTokenBalance(address token) external view returns (uint256) {
        return IERC20(token).balanceOf(address(this));
    }
    
    function getPairInfo(address token) external view returns (
        address pair,
        uint256 tokenReserve,
        uint256 wethReserve,
        uint256 price
    ) {
        address factory = router.factory();
        pair = IUniswapV2Factory(factory).getPair(token, WETH);
        
        if (pair != address(0)) {
            (uint112 reserve0, uint112 reserve1,) = IUniswapV2Pair(pair).getReserves();
            address token0 = IUniswapV2Pair(pair).token0();
            
            if (token0 == token) {
                tokenReserve = reserve0;
                wethReserve = reserve1;
            } else {
                tokenReserve = reserve1;
                wethReserve = reserve0;
            }
            
            if (tokenReserve > 0) {
                price = (wethReserve * 1e18) / tokenReserve;
            }
        }
    }
    
    function withdrawETH() external onlyOwner {
        uint256 balance = address(this).balance;
        require(balance > 0, "No ETH to withdraw");
        payable(owner()).transfer(balance);
    }
    
    function withdrawToken(address token, uint256 amount) external onlyOwner {
        uint256 balance = IERC20(token).balanceOf(address(this));
        require(balance >= amount, "Insufficient token balance");
        
        if (amount == 0) {
            amount = balance;
        }
        
        IERC20(token).transfer(owner(), amount);
        
        if (amount <= tokenBalances[token]) {
            tokenBalances[token] -= amount;
        } else {
            tokenBalances[token] = 0;
        }
    }
    
    function emergencyWithdrawAll() external onlyOwner {
        // Withdraw ETH
        if (address(this).balance > 0) {
            payable(owner()).transfer(address(this).balance);
        }
    }
    
    receive() external payable {}
}

interface IUniswapV2Factory {
    function getPair(address tokenA, address tokenB) external view returns (address pair);
}