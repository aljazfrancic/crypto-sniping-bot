// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IPancakePair {
    function balanceOf(address owner) external view returns (uint256);
    function totalSupply() external view returns (uint256);
}

interface IPancakeFactory {
    function getPair(address tokenA, address tokenB) external view returns (address pair);
}

contract LPLockChecker {
    // Testnet addresses
    address constant PANCAKE_FACTORY = 0x6725F303b657a9451d8BA641348b6761A6CC7a17; // PancakeSwap V2 Factory Testnet
    address constant WBNB = 0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd; // Testnet WBNB
    
    // These locker addresses might not exist on testnet, but we'll keep the structure
    address constant PINK_LOCK = 0x407993575c91ce7643a4d4cCACc9A98c36eE1BBE;
    address constant UNICRYPT = 0xC765bddB93b0D1c1A88282BA0fa6B2d00E3e0c83;
    address constant TEAM_FINANCE = 0xE2fE530C047f2d85298b07D9333C05737f1435fB;
    
    struct LPStatus {
        address pair;
        uint256 totalSupply;
        uint256 lockedAmount;
        uint256 lockedPercentage;
        bool isSecure;
    }
    
    function checkLPLock(address token) external view returns (LPStatus memory status) {
        address pair = IPancakeFactory(PANCAKE_FACTORY).getPair(token, WBNB);
        if (pair == address(0)) {
            return status; // No pair exists
        }
        
        status.pair = pair;
        status.totalSupply = IPancakePair(pair).totalSupply();
        
        if (status.totalSupply == 0) {
            return status;
        }
        
        // Check known lockers
        uint256 pinkLockBalance = IPancakePair(pair).balanceOf(PINK_LOCK);
        uint256 unicryptBalance = IPancakePair(pair).balanceOf(UNICRYPT);
        uint256 teamFinanceBalance = IPancakePair(pair).balanceOf(TEAM_FINANCE);
        
        status.lockedAmount = pinkLockBalance + unicryptBalance + teamFinanceBalance;
        status.lockedPercentage = (status.lockedAmount * 100) / status.totalSupply;
        
        // Consider secure if >80% locked
        status.isSecure = status.lockedPercentage >= 80;
        
        return status;
    }
}