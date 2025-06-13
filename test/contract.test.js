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
        
        // Deploy mock pair
        const MockPair = await ethers.getContractFactory("MockUniswapV2Pair");
        const reserve0 = ethers.utils.parseEther("10000");
        const reserve1 = ethers.utils.parseEther("10");
        const pair = await MockPair.deploy(token.address, weth.address, reserve0, reserve1);

        // Deploy mock factory
        const MockFactory = await ethers.getContractFactory("MockUniswapV2Factory");
        const factory = await MockFactory.deploy(pair.address);

        // Deploy mock router
        const MockRouter = await ethers.getContractFactory("MockUniswapV2Router");
        const router = await MockRouter.deploy(weth.address);
        await router.setFactory(factory.address);
        
        // Deploy sniper contract
        const Sniper = await ethers.getContractFactory("Sniper");
        const sniper = await Sniper.deploy(router.address);
        
        // Setup mock liquidity
        await token.transfer(router.address, reserve0);
        await weth.deposit({ value: reserve1 });
        await weth.transfer(router.address, reserve1);
        
        return { sniper, router, weth, token, owner, user1, user2, pair, factory };
    }
    
    describe("Deployment", function () {
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
            const { sniper, token } = await loadFixture(deployContractsFixture);
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
            const { sniper, token } = await loadFixture(deployContractsFixture);
            await sniper.buyToken(token.address, 0, { value: ethers.utils.parseEther("1") });
            const tokenBalance = await token.balanceOf(sniper.address);
            expect(tokenBalance).to.be.gt(0);
            await expect(
                sniper.sellToken(token.address, tokenBalance)
            ).to.emit(sniper, "TokenSold");
            const ethBalance = await ethers.provider.getBalance(sniper.address);
            expect(ethBalance).to.be.gte(0);
        });
        it("Should revert if insufficient token balance", async function () {
            const { sniper, token } = await loadFixture(deployContractsFixture);
            await expect(
                sniper.sellToken(token.address, ethers.utils.parseEther("100"))
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
            const prevBalance = await ethers.provider.getBalance(owner.address);
            const tx = await sniper.withdrawETH();
            const receipt = await tx.wait();
            // Check that owner's balance increased by at least 1 ETH minus gas
            const newBalance = await ethers.provider.getBalance(owner.address);
            expect(newBalance).to.be.gt(prevBalance); // Can't check exact due to gas
        });
        it("Should withdraw tokens", async function () {
            const { sniper, token, owner } = await loadFixture(deployContractsFixture);
            await sniper.buyToken(token.address, 0, { value: ethers.utils.parseEther("1") });
            const contractBalance = await token.balanceOf(sniper.address);
            expect(contractBalance).to.be.gt(0);
            const prevOwnerBalance = await token.balanceOf(owner.address);
            await sniper.withdrawToken(token.address, contractBalance);
            const ownerBalance = await token.balanceOf(owner.address);
            expect(ownerBalance.sub(prevOwnerBalance)).to.equal(contractBalance);
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
            const { sniper, token, pair } = await loadFixture(deployContractsFixture);
            const [pairAddr, tokenReserve, wethReserve, price] = await sniper.getPairInfo(token.address);
            expect(pairAddr).to.equal(pair.address);
            expect(tokenReserve).to.be.gt(0);
            expect(wethReserve).to.be.gt(0);
            expect(price).to.be.gt(0);
        });
    });
});