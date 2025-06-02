// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract FlashSniper {
    address public immutable executor;
    IUniswapV2Router02 public immutable uniswapRouter;
    
    constructor(address _router) {
        executor = msg.sender;
        uniswapRouter = IUniswapV2Router02(_router);
    }
    
    function snipe(address token, uint256 ethAmount) external payable {
        require(msg.sender == executor, "Not executor");
        require(!isRugToken(token), "Rug token detected");
        
        address[] memory path = new address[](2);
        path[0] = uniswapRouter.WETH();
        path[1] = token;
        
        uniswapRouter.swapExactETHForTokensSupportingFeeOnTransferTokens{value: ethAmount}(
            0,
            path,
            address(this),
            block.timestamp + 300
        );
    }
    
    function isRugToken(address token) private returns (bool) {
        try IUniswapV2Pair(token).getReserves() returns (uint112, uint112, uint32) {
            return false;
        } catch {
            return true;
        }
    }
}