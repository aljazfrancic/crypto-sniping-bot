const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying with:", deployer.address);

  const factory = process.env.PANCAKE_FACTORY || "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73";
  const wbnb = process.env.WBNB || "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c";

  const LPLockChecker = await hre.ethers.getContractFactory("LPLockChecker");
  const checker = await LPLockChecker.deploy(factory, wbnb);
  await checker.waitForDeployment();

  console.log("LPLockChecker deployed to:", await checker.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});