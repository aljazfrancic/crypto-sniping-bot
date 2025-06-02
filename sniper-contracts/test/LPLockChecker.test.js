const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("LPLockChecker", function () {
  let checker;

  before(async function () {
    // deploy mock factory returning zero address
    const MockFactory = await ethers.getContractFactory("MockFactory");
    const factory = await MockFactory.deploy();
    await factory.waitForDeployment();

    // use arbitrary WBNB address for local tests
    const wbnb = "0xBB4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c";

    const LPLockChecker = await ethers.getContractFactory("LPLockChecker");
    checker = await LPLockChecker.deploy(factory.target, wbnb);
    await checker.waitForDeployment();
  });

  it("deploys and returns empty status on non-existent pair", async function () {
    const fakeToken = "0x0000000000000000000000000000000000000001";
    const status = await checker.checkLPLock(fakeToken);

    expect(status.pair).to.equal("0x0000000000000000000000000000000000000000");
    expect(status.totalSupply).to.equal(0);
    expect(status.isSecure).to.equal(false);
  });
});