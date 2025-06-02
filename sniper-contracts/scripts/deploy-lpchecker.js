const hre = require("hardhat");
async function main() {
  const Checker = await hre.ethers.getContractFactory("LPLockChecker");
  const checker = await Checker.deploy();
  await checker.waitForDeployment();
  console.log("LPLockChecker deployed to:", await checker.getAddress());
}
main().catch((e)=>{console.error(e); process.exitCode=1;});