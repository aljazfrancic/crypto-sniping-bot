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
        // Deploy mock factory
    const MockFactory = await ethers.getContractFactory("MockFactory");
    mockFactory = await MockFactory.deploy();
        // Deploy LPLockChecker
    const LPLockChecker = await ethers.getContractFactory("LPLockChecker");
    checker = await LPLockChecker.deploy(mockFactory.target);
      });

  it("should return lock status for a pair", async function () {
    // Create a mock pair
    await mockFactory.createPair(mockToken.target, ethers.constants.AddressZero);
    
    // Check lock status
    const status = await checker.getLPLockStatus(mockToken.target);
    expect(status.isLocked).to.be.false;
    expect(status.lockReason).to.equal("");
  });
});
