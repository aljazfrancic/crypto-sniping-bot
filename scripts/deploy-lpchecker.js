const hre = require("hardhat");

async function main() {
  console.log("Deploying LPLockChecker...");
  
  const LPLockChecker = await hre.ethers.getContractFactory("LPLockChecker");
  const checker = await LPLockChecker.deploy();
  
  await checker.waitForDeployment();
  
  console.log("LPLockChecker deployed to:", await checker.getAddress());
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });