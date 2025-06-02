const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("LPLockChecker", function () {
  let checker;
  let mockToken;
  let mockFactory;

  beforeEach(async function () {
    // Deploy mock token
    const MockToken = await ethers.getContractFactory("MockToken");
    mockToken = await MockToken.deploy();
    await mockToken.deployed();

    // Deploy mock factory
    const MockFactory = await ethers.getContractFactory("MockFactory");
    mockFactory = await MockFactory.deploy();
    await mockFactory.deployed();

    // Deploy LPLockChecker
    const LPLockChecker = await ethers.getContractFactory("LPLockChecker");
    checker = await LPLockChecker.deploy(mockFactory.address);
    await checker.deployed();
  });

  it("should return lock status for a pair", async function () {
    // Create a mock pair
    await mockFactory.createPair(mockToken.address, ethers.constants.AddressZero);
    
    // Check lock status
    const status = await checker.getLPLockStatus(mockToken.address);
    expect(status.isLocked).to.be.false;
    expect(status.lockReason).to.equal("");
  });
});
