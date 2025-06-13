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
        await weth.waitForDeployment();
        const wethAddress = await weth.getAddress();
        
        // Deploy mock token
        const MockERC20 = await ethers.getContractFactory("MockERC20");
        const token = await MockERC20.deploy("Test Token", "TEST", ethers.parseEther("1000000"));
        await token.waitForDeployment();
        const tokenAddress = await token.getAddress();
        
        // Deploy mock pair
        const MockPair = await ethers.getContractFactory("MockUniswapV2Pair");
        const reserve0 = ethers.parseEther("10000");
        const reserve1 = ethers.parseEther("10");
        const pair = await MockPair.deploy(tokenAddress, wethAddress, reserve0, reserve1);
        await pair.waitForDeployment();
        const pairAddress = await pair.getAddress();

        // Deploy mock factory
        const MockFactory = await ethers.getContractFactory("MockUniswapV2Factory");
        const factory = await MockFactory.deploy(pairAddress);
        await factory.waitForDeployment();
        const factoryAddress = await factory.getAddress();

        // Deploy mock router
        const MockRouter = await ethers.getContractFactory("MockUniswapV2Router");
        const router = await MockRouter.deploy(wethAddress);
        await router.waitForDeployment();
        const routerAddress = await router.getAddress();
        await router.setFactory(factoryAddress);
        
        // Deploy sniper contract
        const Sniper = await ethers.getContractFactory("Sniper");
        const sniper = await Sniper.deploy(routerAddress);
        await sniper.waitForDeployment();
        const sniperAddress = await sniper.getAddress();
        
        // Setup mock liquidity
        await token.transfer(routerAddress, reserve0);
        await weth.deposit({ value: reserve1 });
        await weth.transfer(routerAddress, reserve1);
        
        return { 
            sniper, 
            router, 
            weth, 
            token, 
            owner, 
            user1, 
            user2, 
            pair, 
            factory,
            sniperAddress,
            routerAddress,
            wethAddress,
            tokenAddress,
            pairAddress,
            factoryAddress
        };
    }
    
    describe("Deployment", function () {
        it("Should set the correct WETH address", async function () {
            const { sniper, wethAddress } = await loadFixture(deployContractsFixture);
            expect(await sniper.WETH()).to.equal(wethAddress);
        });
        it("Should set the correct owner", async function () {
            const { sniper, owner } = await loadFixture(deployContractsFixture);
            expect(await sniper.owner()).to.equal(await owner.getAddress());
        });
        it("Should set default slippage and deadline", async function () {
            const { sniper } = await loadFixture(deployContractsFixture);
            expect(await sniper.maxSlippage()).to.equal(500); // 5%
            expect(await sniper.deadline()).to.equal(300); // 5 minutes
        });
    });
    describe("Buy Token", function () {
        it("Should buy tokens successfully", async function () {
            const { sniper, token, tokenAddress } = await loadFixture(deployContractsFixture);
            const buyAmount = ethers.parseEther("1");
            const minTokens = ethers.parseEther("100");
            await expect(
                sniper.buyToken(tokenAddress, minTokens, { value: buyAmount })
            ).to.emit(sniper, "TokenBought");
            const balance = await token.balanceOf(await sniper.getAddress());
            expect(balance).to.be.gt(0);
        });
        it("Should revert if no ETH sent", async function () {
            const { sniper, tokenAddress } = await loadFixture(deployContractsFixture);
            await expect(
                sniper.buyToken(tokenAddress, 0)
            ).to.be.revertedWith("No ETH sent");
        });
        it("Should revert if token is blacklisted", async function () {
            const { sniper, tokenAddress } = await loadFixture(deployContractsFixture);
            await sniper.blacklistToken(tokenAddress, true);
            await expect(
                sniper.buyToken(tokenAddress, 0, { value: ethers.parseEther("1") })
            ).to.be.revertedWith("Token is blacklisted");
        });
        it("Should only allow owner to buy", async function () {
            const { sniper, tokenAddress, user1 } = await loadFixture(deployContractsFixture);
            await expect(
                sniper.connect(user1).buyToken(tokenAddress, 0, { value: ethers.parseEther("1") })
            ).to.be.revertedWith("Ownable: caller is not the owner");
        });
    });
    describe("Sell Token", function () {
        it("Should sell tokens successfully", async function () {
            const { sniper, token, tokenAddress } = await loadFixture(deployContractsFixture);
            await sniper.buyToken(tokenAddress, 0, { value: ethers.parseEther("1") });
            const tokenBalance = await token.balanceOf(await sniper.getAddress());
            expect(tokenBalance).to.be.gt(0);
            await expect(
                sniper.sellToken(tokenAddress, tokenBalance)
            ).to.emit(sniper, "TokenSold");
            const ethBalance = await ethers.provider.getBalance(await sniper.getAddress());
            expect(ethBalance).to.be.gte(0);
        });
        it("Should revert if insufficient token balance", async function () {
            const { sniper, tokenAddress } = await loadFixture(deployContractsFixture);
            await expect(
                sniper.sellToken(tokenAddress, ethers.parseEther("100"))
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
            const { sniper, tokenAddress } = await loadFixture(deployContractsFixture);
            await sniper.blacklistToken(tokenAddress, true);
            expect(await sniper.blacklistedTokens(tokenAddress)).to.be.true;
            await sniper.blacklistToken(tokenAddress, false);
            expect(await sniper.blacklistedTokens(tokenAddress)).to.be.false;
        });
    });
    describe("Withdrawals", function () {
        it("Should withdraw ETH", async function () {
            const { sniper, owner } = await loadFixture(deployContractsFixture);
            // Send ETH to contract
            await owner.sendTransaction({
                to: await sniper.getAddress(),
                value: ethers.parseEther("1")
            });
            const prevBalance = await ethers.provider.getBalance(await owner.getAddress());
            const tx = await sniper.withdrawETH();
            const receipt = await tx.wait();
            // Check that owner's balance increased by at least 1 ETH minus gas
            const newBalance = await ethers.provider.getBalance(await owner.getAddress());
            expect(newBalance).to.be.gt(prevBalance); // Can't check exact due to gas
        });
        it("Should withdraw tokens", async function () {
            const { sniper, token, tokenAddress, owner } = await loadFixture(deployContractsFixture);
            await sniper.buyToken(tokenAddress, 0, { value: ethers.parseEther("1") });
            const contractBalance = await token.balanceOf(await sniper.getAddress());
            expect(contractBalance).to.be.gt(0);
            const prevOwnerBalance = await token.balanceOf(await owner.getAddress());
            await sniper.withdrawToken(tokenAddress, contractBalance);
            const ownerBalance = await token.balanceOf(await owner.getAddress());
            expect(ownerBalance - prevOwnerBalance).to.equal(contractBalance);
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
            const { sniper, tokenAddress, pairAddress } = await loadFixture(deployContractsFixture);
            const [pairAddr, tokenReserve, wethReserve, price] = await sniper.getPairInfo(tokenAddress);
            expect(pairAddr).to.equal(pairAddress);
            expect(tokenReserve).to.be.gt(0);
            expect(wethReserve).to.be.gt(0);
            expect(price).to.be.gt(0);
        });
    });
});