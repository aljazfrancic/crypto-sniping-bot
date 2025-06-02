const { expect } = require("chai");
const { ethers } = require("hardhat");
const { loadFixture } = require("@nomicfoundation/hardhat-network-helpers");

describe("Sniper Contract", function () {
    // Fixture for common test setup
    async function deployContractsFixture() {
        const [owner, user1, user2] = await ethers.getSigners();
        
        // Deploy mock WETH
        const MockWETH = await ethers.getContractFactory("MockWETH");
        const weth = await MockWETH.deploy();
        
        // Deploy mock token
        const MockERC20 = await ethers.getContractFactory("MockERC20");
        const token = await MockERC20.deploy("Test Token", "TEST", ethers.utils.parseEther("1000000"));
        
        // Deploy mock router
        const MockRouter = await ethers.getContractFactory("MockUniswapV2Router");
        const router = await MockRouter.deploy(weth.address);
        
        // Deploy sniper contract
        const Sniper = await ethers.getContractFactory("Sniper");
        const sniper = await Sniper.deploy(router.address);
        
        // Setup mock liquidity
        await token.transfer(router.address, ethers.utils.parseEther("10000"));
        await weth.deposit({ value: ethers.utils.parseEther("10") });
        await weth.transfer(router.address, ethers.utils.parseEther("10"));
        
        return { sniper, router, weth, token, owner, user1, user2 };
    }
    
    describe("Deployment", function () {
        it("Should set the correct router address", async function () {
            const { sniper, router } = await loadFixture(deployContractsFixture);
            expect(await sniper.router()).to.equal(router.address);
        });
        
        it("Should set the correct WETH address", async function () {
            const { sniper, weth } = await loadFixture(deployContractsFixture);
            expect(await sniper.WETH()).to.equal(weth.address);
        });
        
        it("Should set the correct owner", async function () {
            const { sniper, owner } = await loadFixture(deployContractsFixture);
            expect(await sniper.owner()).to.equal(owner.address);
        });
        
        it("Should set default slippage and deadline", async function () {
            const { sniper } = await loadFixture(deployContractsFixture);
            expect(await sniper.maxSlippage()).to.equal(500); // 5%
            expect(await sniper.deadline()).to.equal(300); // 5 minutes
        });
    });
    
    describe("Buy Token", function () {
        it("Should buy tokens successfully", async function () {
            const { sniper, token, owner } = await loadFixture(deployContractsFixture);
            
            const buyAmount = ethers.utils.parseEther("1");
            const minTokens = ethers.utils.parseEther("100");
            
            await expect(
                sniper.buyToken(token.address, minTokens, { value: buyAmount })
            ).to.emit(sniper, "TokenBought");
            
            const balance = await token.balanceOf(sniper.address);
            expect(balance).to.be.gt(0);
        });
        
        it("Should revert if no ETH sent", async function () {
            const { sniper, token } = await loadFixture(deployContractsFixture);
            
            await expect(
                sniper.buyToken(token.address, 0)
            ).to.be.revertedWith("No ETH sent");
        });
        
        it("Should revert if token is blacklisted", async function () {
            const { sniper, token } = await loadFixture(deployContractsFixture);
            
            await sniper.blacklistToken(token.address, true);
            
            await expect(
                sniper.buyToken(token.address, 0, { value: ethers.utils.parseEther("1") })
            ).to.be.revertedWith("Token is blacklisted");
        });
        
        it("Should only allow owner to buy", async function () {
            const { sniper, token, user1 } = await loadFixture(deployContractsFixture);
            
            await expect(
                sniper.connect(user1).buyToken(token.address, 0, { value: ethers.utils.parseEther("1") })
            ).to.be.revertedWith("Ownable: caller is not the owner");
        });
    });
    
    describe("Sell Token", function () {
        it("Should sell tokens successfully", async function () {
            const { sniper, token, owner } = await loadFixture(deployContractsFixture);
            
            // First buy some tokens
            await sniper.buyToken(token.address, 0, { value: ethers.utils.parseEther("1") });
            
            const tokenBalance = await token.balanceOf(sniper.address);
            expect(tokenBalance).to.be.gt(0);
            
            // Sell tokens
            await expect(
                sniper.sellToken(token.address, tokenBalance, 0)
            ).to.emit(sniper, "TokenSold");
            
            const ethBalance = await ethers.provider.getBalance(sniper.address);
            expect(ethBalance).to.be.gt(0);
        });
        
        it("Should revert if insufficient token balance", async function () {
            const { sniper, token } = await loadFixture(deployContractsFixture);
            
            await expect(
                sniper.sellToken(token.address, ethers.utils.parseEther("100"), 0)
            ).to.be.revertedWith("Insufficient token balance");
        });
    });
    
    describe("Configuration", function () {
        it("Should update slippage", async function () {
            const { sniper } = await loadFixture(deployContractsFixture);
            
            await sniper.updateSlippage(1000); // 10%
            expect(await sniper.maxSlippage()).to.equal(1000);
        });
        
        it("Should not allow slippage over 50%", async function () {
            const { sniper } = await loadFixture(deployContractsFixture);
            
            await expect(
                sniper.updateSlippage(5001)
            ).to.be.revertedWith("Slippage too high");
        });
        
        it("Should update deadline", async function () {
            const { sniper } = await loadFixture(deployContractsFixture);
            
            await sniper.updateDeadline(600); // 10 minutes
            expect(await sniper.deadline()).to.equal(600);
        });
        
        it("Should enforce deadline limits", async function () {
            const { sniper } = await loadFixture(deployContractsFixture);
            
            await expect(
                sniper.updateDeadline(30) // Too short
            ).to.be.revertedWith("Deadline too short");
            
            await expect(
                sniper.updateDeadline(7200) // Too long
            ).to.be.revertedWith("Deadline too long");
        });
    });
    
    describe("Blacklist", function () {
        it("Should blacklist and unblacklist tokens", async function () {
            const { sniper, token } = await loadFixture(deployContractsFixture);
            
            await sniper.blacklistToken(token.address, true);
            expect(await sniper.blacklistedTokens(token.address)).to.be.true;
            
            await sniper.blacklistToken(token.address, false);
            expect(await sniper.blacklistedTokens(token.address)).to.be.false;
        });
    });
    
    describe("Withdrawals", function () {
        it("Should withdraw ETH", async function () {
            const { sniper, owner } = await loadFixture(deployContractsFixture);
            
            // Send ETH to contract
            await owner.sendTransaction({
                to: sniper.address,
                value: ethers.utils.parseEther("1")
            });
            
            const initialBalance = await ethers.provider.getBalance(owner.address);
            
            await sniper.withdrawETH();
            
            const finalBalance = await ethers.provider.getBalance(owner.address);
            expect(finalBalance).to.be.gt(initialBalance);
        });
        
        it("Should withdraw tokens", async function () {
            const { sniper, token, owner } = await loadFixture(deployContractsFixture);
            
            // First buy some tokens
            await sniper.buyToken(token.address, 0, { value: ethers.utils.parseEther("1") });
            
            const contractBalance = await token.balanceOf(sniper.address);
            expect(contractBalance).to.be.gt(0);
            
            await sniper.withdrawToken(token.address, contractBalance);
            
            const ownerBalance = await token.balanceOf(owner.address);
            expect(ownerBalance).to.equal(contractBalance);
        });
        
        it("Should only allow owner to withdraw", async function () {
            const { sniper, user1 } = await loadFixture(deployContractsFixture);
            
            await expect(
                sniper.connect(user1).withdrawETH()
            ).to.be.revertedWith("Ownable: caller is not the owner");
        });
    });
    
    describe("Pair Info", function () {
        it("Should get pair info", async function () {
            const { sniper, token, router } = await loadFixture(deployContractsFixture);
            
            // Mock pair info
            const pairInfo = await sniper.getPairInfo(token.address);
            
            // In a real test, we would check actual values
            // For now, just check the structure
            expect(pairInfo.pair).to.be.properAddress;
            expect(pairInfo.tokenReserve).to.be.gte(0);
            expect(pairInfo.wethReserve).to.be.gte(0);
            expect(pairInfo.price).to.be.gte(0);
        });
    });
});

// Mock contracts for testing
// In a real project, these would be in separate files

// MockWETH.sol
/*
pragma solidity ^0.8.0;

contract MockWETH {
    mapping(address => uint256) public balanceOf;
    
    function deposit() public payable {
        balanceOf[msg.sender] += msg.value;
    }
    
    function transfer(address to, uint256 amount) public returns (bool) {
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;
        return true;
    }
}
*/

// MockERC20.sol
/*
pragma solidity ^0.8.0;

contract MockERC20 {
    string public name;
    string public symbol;
    uint8 public decimals = 18;
    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    
    constructor(string memory _name, string memory _symbol, uint256 _supply) {
        name = _name;
        symbol = _symbol;
        totalSupply = _supply;
        balanceOf[msg.sender] = _supply;
    }
    
    function transfer(address to, uint256 amount) public returns (bool) {
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;
        return true;
    }
    
    function approve(address spender, uint256 amount) public returns (bool) {
        allowance[msg.sender][spender] = amount;
        return true;
    }
    
    function transferFrom(address from, address to, uint256 amount) public returns (bool) {
        allowance[from][msg.sender] -= amount;
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        return true;
    }
}
*/

// MockUniswapV2Router.sol
/*
pragma solidity ^0.8.0;

contract MockUniswapV2Router {
    address public WETH;
    address public factory;
    
    constructor(address _weth) {
        WETH = _weth;
        factory = address(this); // Mock factory
    }
    
    function getAmountsOut(uint amountIn, address[] memory path) 
        public view returns (uint[] memory amounts) {
        amounts = new uint[](path.length);
        amounts[0] = amountIn;
        // Mock exchange rate: 1 ETH = 1000 tokens
        amounts[1] = amountIn * 1000;
    }
    
    function swapExactETHForTokens(
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external payable returns (uint[] memory amounts) {
        require(msg.value > 0, "No ETH sent");
        amounts = getAmountsOut(msg.value, path);
        
        // Mock token transfer
        MockERC20(path[1]).transfer(to, amounts[1]);
        
        return amounts;
    }
    
    function swapExactTokensForETH(
        uint amountIn,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external returns (uint[] memory amounts) {
        amounts = new uint[](2);
        amounts[0] = amountIn;
        amounts[1] = amountIn / 1000; // Mock rate
        
        // Mock token transfer
        MockERC20(path[0]).transferFrom(msg.sender, address(this), amountIn);
        payable(to).transfer(amounts[1]);
        
        return amounts;
    }
}
*/