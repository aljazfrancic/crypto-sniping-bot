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
    address constant PANCAKE_FACTORY = 0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73;
    address constant WBNB = 0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c;

    // known lockers on BSC
    address constant PINK_LOCK   = 0x407993575c91ce7643a4d4cCACc9A98c36eE1BBE;
    address constant UNICRYPT    = 0xC765bddB93b0D1c1A88282BA0fa6B2d00E3e0c83;
    address constant TEAM_FINANCE= 0xE2fE530C047f2d85298b07D9333C05737f1435fB;

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
            return status;
        }

        status.pair = pair;
        status.totalSupply = IPancakePair(pair).totalSupply();

        if (status.totalSupply == 0) {
            return status;
        }

        uint256 locked =
            IPancakePair(pair).balanceOf(PINK_LOCK) +
            IPancakePair(pair).balanceOf(UNICRYPT) +
            IPancakePair(pair).balanceOf(TEAM_FINANCE);

        status.lockedAmount = locked;
        status.lockedPercentage = (locked * 100) / status.totalSupply;
        status.isSecure = status.lockedPercentage >= 80;
        return status;
    }
}