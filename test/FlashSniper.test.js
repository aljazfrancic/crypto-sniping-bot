const FlashSniper = artifacts.require("FlashSniper");

contract("FlashSniper", (accounts) => {
  let instance;
  const owner = accounts[0];
  
  beforeEach(async () => {
    instance = await FlashSniper.new("0xD99D1c33F9fC3444f8101754aBC46c52416550D1", { from: owner });
  });

  it("should set correct owner", async () => {
    const executor = await instance.executor();
    assert.equal(executor, owner, "Owner not set correctly");
  });

  it("should reject non-owner snipes", async () => {
    try {
      await instance.snipe("0x0000000000000000000000000000000000000000", 1000, { from: accounts[1] });
      assert.fail("Should have thrown error");
    } catch (error) {
      assert.include(error.message, "Not executor", "Failed to reject non-owner");
    }
  });
});