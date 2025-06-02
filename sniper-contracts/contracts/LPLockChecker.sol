// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IPancakePair {
    function balanceOf(address owner) external view returns (uint256);
    function totalSupply() external view returns (uint256);
}

interface IPancakeFactory {
    function getPair(address tokenA, address tokenB) external view returns (address pair);
}

/// @title LP Lock Checker
/// @notice Checks how much liquidity is locked in known lockers for a given token/WBNB pair.
contract LPLockChecker {
    // known lockers on BSC
    address public constant PINK_LOCK = 0x407993575c91ce7643a4d4cCACc9A98c36eE1BBE;
    address public constant UNICRYPT   = 0xC765bddB93b0D1c1A88282BA0fa6B2d00E3e0c83;
    address public constant TEAM_FINANCE = 0xE2fE530C047f2d85298b07D9333C05737f1435fB;

    address public immutable factory;
    address public immutable wbnb;

    constructor(address _factory, address _wbnb) {
        factory = _factory;
        wbnb = _wbnb;
    }

    struct LPStatus {
        address pair;
        uint256 totalSupply;
        uint256 lockedAmount;
        uint256 lockedPercentage;
        bool isSecure;
    }

    function checkLPLock(address token) external view returns (LPStatus memory status) {
        address pair = IPancakeFactory(factory).getPair(token, wbnb);
        if (pair == address(0)) {
            return status; // default zeros
        }

        status.pair = pair;
        // safe staticcall to avoid revert if pair isn't a contract
        (bool okTS, bytes memory tsData) = pair.staticcall(abi.encodeWithSelector(IPancakePair.totalSupply.selector));
        if (!okTS || tsData.length < 32) return status;
        status.totalSupply = abi.decode(tsData, (uint256));

        if (status.totalSupply == 0) {
            return status;
        }

        uint256 locked;
        address[3] memory lockers = [PINK_LOCK, UNICRYPT, TEAM_FINANCE];
        for (uint8 i=0;i<3;i++){
            (bool ok, bytes memory data) = pair.staticcall(abi.encodeWithSelector(IPancakePair.balanceOf.selector, lockers[i]));
            if (ok && data.length >= 32) {
                locked += abi.decode(data, (uint256));
            }
        }

        status.lockedAmount = locked;
        status.lockedPercentage = (locked * 100) / status.totalSupply;
        status.isSecure = status.lockedPercentage >= 80;
        return status;
    }
}