const hre = require("hardhat");

async function main() {
    console.log("Starting deployment...");
    
    // Get deployer account
    const [deployer] = await ethers.getSigners();
    console.log("Deploying contracts with account:", deployer.address);
    console.log("Account balance:", (await deployer.getBalance()).toString());
    
    // Get network info
    const network = await ethers.provider.getNetwork();
    console.log("Network:", network.name, "Chain ID:", network.chainId);
    
    // Router addresses for different networks
    const routerAddresses = {
        1: "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",      // Ethereum Mainnet - Uniswap V2
        5: "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",      // Goerli - Uniswap V2
        56: "0x10ED43C718714eb63d5aA57B78B54704E256024E",     // BSC Mainnet - PancakeSwap
        97: "0xD99D1c33F9fC3444f8101754aBC46c52416550D1",     // BSC Testnet - PancakeSwap
        137: "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff",    // Polygon - QuickSwap
        80001: "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff",  // Mumbai - QuickSwap
        31337: "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"   // Hardhat Fork
    };
    
    const routerAddress = routerAddresses[network.chainId];
    if (!routerAddress) {
        throw new Error(`No router address configured for chain ID ${network.chainId}`);
    }
    
    console.log("Using router address:", routerAddress);
    
    // Deploy Sniper contract
    console.log("\nDeploying Sniper contract...");
    const Sniper = await ethers.getContractFactory("Sniper");
    const sniper = await Sniper.deploy(routerAddress);
    
    await sniper.deployed();
    console.log("✅ Sniper deployed to:", sniper.address);
    
    // Verify initial configuration
    console.log("\nVerifying deployment...");
    console.log("Router:", await sniper.router());
    console.log("WETH:", await sniper.WETH());
    console.log("Owner:", await sniper.owner());
    console.log("Max Slippage:", (await sniper.maxSlippage()).toString(), "(", (await sniper.maxSlippage()) / 100, "%)");
    console.log("Deadline:", (await sniper.deadline()).toString(), "seconds");
    
    // Save deployment info
    const deploymentInfo = {
        network: network.name,
        chainId: network.chainId,
        deployer: deployer.address,
        sniper: sniper.address,
        router: routerAddress,
        deployedAt: new Date().toISOString(),
        blockNumber: await ethers.provider.getBlockNumber()
    };
    
    console.log("\n📄 Deployment Info:");
    console.log(JSON.stringify(deploymentInfo, null, 2));
    
    // Write to file
    const fs = require("fs");
    const deploymentPath = `./deployments/${network.chainId}-deployment.json`;
    
    // Create deployments directory if it doesn't exist
    if (!fs.existsSync("./deployments")) {
        fs.mkdirSync("./deployments");
    }
    
    fs.writeFileSync(deploymentPath, JSON.stringify(deploymentInfo, null, 2));
    console.log(`\n💾 Deployment info saved to ${deploymentPath}`);
    
    // Verify on Etherscan/BSCScan if not local
    if (network.chainId !== 31337) {
        console.log("\n🔍 Waiting for block confirmations before verification...");
        await sniper.deployTransaction.wait(5);
        
        console.log("Verifying contract on explorer...");
        try {
            await hre.run("verify:verify", {
                address: sniper.address,
                constructorArguments: [routerAddress],
            });
            console.log("✅ Contract verified!");
        } catch (error) {
            console.log("❌ Verification failed:", error.message);
            console.log("You can verify manually with:");
            console.log(`npx hardhat verify --network ${network.name} ${sniper.address} "${routerAddress}"`);
        }
    }
    
    console.log("\n🎉 Deployment complete!");
    console.log("\n⚠️  IMPORTANT: Add this to your .env file:");
    console.log(`SNIPER_CONTRACT=${sniper.address}`);
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });