const hre = require("hardhat");

async function main() {
  console.log("Starting deployment...");

  // Get deployer account
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying contracts with account:", deployer.address);
  console.log("Account balance:", (await deployer.getBalance()).toString());

  // Get network info
  const network = await hre.ethers.provider.getNetwork();
  console.log("Network:", network.name, "Chain ID:", network.chainId);

  // Deploy Sniper contract
  console.log("\nDeploying Sniper contract...");
  const Sniper = await hre.ethers.getContractFactory("Sniper");
  const sniper = await Sniper.deploy(
    process.env.ROUTER_ADDRESS,
    process.env.FACTORY_ADDRESS,
    process.env.WETH_ADDRESS,
  );

  await sniper.waitForDeployment();
  const sniperAddress = await sniper.getAddress();
  console.log("✅ Sniper deployed to:", sniperAddress);

  // Verify initial configuration
  console.log("\nVerifying deployment...");
  console.log("Router:", await sniper.router());
  console.log("WETH:", await sniper.WETH());
  console.log("Owner:", await sniper.owner());
  console.log(
    "Max Slippage:",
    (await sniper.maxSlippage()).toString(),
    "(",
    (await sniper.maxSlippage()) / 100,
    "%)",
  );
  console.log("Deadline:", (await sniper.deadline()).toString(), "seconds");

  // Save deployment info
  const deploymentInfo = {
    network: network.name,
    chainId: network.chainId,
    sniperAddress: sniperAddress,
    deployer: deployer.address,
    timestamp: new Date().toISOString(),
  };

  console.log("\n📄 Deployment Info:");
  console.log(JSON.stringify(deploymentInfo, null, 2));

  // Write to file
  const fs = require("fs");
  const path = require("path");
  const deploymentsDir = path.join(__dirname, "../deployments");

  if (!fs.existsSync(deploymentsDir)) {
    fs.mkdirSync(deploymentsDir);
  }

  const deploymentFile = path.join(
    deploymentsDir,
    `deployment-${network.name}-${network.chainId}.json`,
  );

  fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));
  console.log(`\n💾 Deployment info saved to ${deploymentFile}`);

  // Verify on Etherscan/BSCScan if not local
  if (network.chainId !== 31337) {
    console.log("\n🔍 Waiting for block confirmations before verification...");
    await sniper.deployTransaction.wait(6);

    console.log("Verifying contract on explorer...");
    try {
      await hre.run("verify:verify", {
        address: sniperAddress,
        constructorArguments: [
          process.env.ROUTER_ADDRESS,
          process.env.FACTORY_ADDRESS,
          process.env.WETH_ADDRESS,
        ],
      });
      console.log("✅ Contract verified!");
    } catch (error) {
      console.log("❌ Verification failed:", error.message);
      console.log("You can verify manually with:");
      console.log(
        `npx hardhat verify --network ${network.name} ${sniperAddress} "${process.env.ROUTER_ADDRESS}" "${process.env.FACTORY_ADDRESS}" "${process.env.WETH_ADDRESS}"`,
      );
    }
  }

  console.log("\n🎉 Deployment complete!");
  console.log("\n⚠️  IMPORTANT: Add this to your .env file:");
  console.log(`SNIPER_CONTRACT=${sniperAddress}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
