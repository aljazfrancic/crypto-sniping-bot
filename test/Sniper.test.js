const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("Sniper Contract", function () {
  it("deploys and sets owner", async function () {
    const [deployer] = await ethers.getSigners();

    const Sniper = await ethers.getContractFactory("Sniper");
    const sniper = await Sniper.deploy();
    await sniper.waitForDeployment();

    expect(await sniper.owner()).to.equal(deployer.address);
  });
});
