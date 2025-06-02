import os
import json

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)

def main():
    # Update LPLockChecker test
    create_file(
        "sniper-contracts/test/LPLockChecker.test.js",
        """const { expect } = require("chai");
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
"""
    )

    # Create mock contracts
    create_file(
        "sniper-contracts/contracts/mocks/MockToken.sol",
        """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MockToken is ERC20 {
    constructor() ERC20("Mock Token", "MOCK") {
        _mint(msg.sender, 1000000 * 10**decimals());
    }
}
"""
    )

    create_file(
        "sniper-contracts/contracts/mocks/MockFactory.sol",
        """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MockFactory {
    mapping(address => mapping(address => address)) public getPair;

    function createPair(address tokenA, address tokenB) external {
        getPair[tokenA][tokenB] = address(new MockPair());
    }
}

contract MockPair {
    // Simple mock pair implementation
}
"""
    )

    # Install OpenZeppelin contracts
    os.chdir("sniper-contracts")
    os.system("npm install @openzeppelin/contracts")
    os.chdir("..")

    print("✅ LPLockChecker test fixed with mock contracts")

if __name__ == "__main__":
    main()