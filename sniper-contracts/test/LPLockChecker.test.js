const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("LPLockChecker", function () {
  let checker;
  it("deploys and returns empty status on non-existent pair", async function () {
    const LPLockChecker = await ethers.getContractFactory("LPLockChecker");
    checker = await LPLockChecker.deploy();
    await checker.waitForDeployment();

    const fakeToken = "0x0000000000000000000000000000000000000001";
    const status = await checker.checkLPLock(fakeToken);
    expect(status.pair).to.equal(ethers.ZeroAddress);
    expect(status.totalSupply).to.equal(0n);
    expect(status.isSecure).to.equal(false);
  });
});