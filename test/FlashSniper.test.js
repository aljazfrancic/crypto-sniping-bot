const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("FlashSniper", function () {
  let flashSniper;
  let owner;

  beforeEach(async function () {
    [owner] = await ethers.getSigners();
    const FlashSniper = await ethers.getContractFactory("FlashSniper");
    flashSniper = await FlashSniper.deploy();
    await flashSniper.deployed();
  });

  it("should deploy correctly", async function () {
    expect(await flashSniper.owner()).to.equal(owner.address);
  });
});
