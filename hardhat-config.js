require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

// Ensure required environment variables are set
const PRIVATE_KEY = process.env.PRIVATE_KEY || "0x0000000000000000000000000000000000000000000000000000000000000000";
const ETHERSCAN_API_KEY = process.env.ETHERSCAN_API_KEY || "";
const BSCSCAN_API_KEY = process.env.BSCSCAN_API_KEY || "";
const POLYGONSCAN_API_KEY = process.env.POLYGONSCAN_API_KEY || "";

// RPC URLs
const ETHEREUM_RPC = process.env.ETHEREUM_RPC || "https://eth-mainnet.g.alchemy.com/v2/your-api-key";
const BSC_RPC = process.env.BSC_RPC || "https://bsc-dataseed.binance.org/";
const POLYGON_RPC = process.env.POLYGON_RPC || "https://polygon-rpc.com/";

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.19",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      }
    }
  },
  networks: {
    hardhat: {
      forking: {
        url: ETHEREUM_RPC,
        blockNumber: 18500000 // Pin to specific block for consistent testing
      }
    },
    localhost: {
      url: "http://127.0.0.1:8545"
    },
    ethereum: {
      url: ETHEREUM_RPC,
      accounts: [PRIVATE_KEY],
      chainId: 1
    },
    goerli: {
      url: "https://goerli.infura.io/v3/your-infura-key",
      accounts: [PRIVATE_KEY],
      chainId: 5
    },
    bsc: {
      url: BSC_RPC,
      accounts: [PRIVATE_KEY],
      chainId: 56
    },
    bscTestnet: {
      url: "https://data-seed-prebsc-1-s1.binance.org:8545",
      accounts: [PRIVATE_KEY],
      chainId: 97
    },
    polygon: {
      url: POLYGON_RPC,
      accounts: [PRIVATE_KEY],
      chainId: 137
    },
    mumbai: {
      url: "https://rpc-mumbai.maticvigil.com",
      accounts: [PRIVATE_KEY],
      chainId: 80001
    }
  },
  etherscan: {
    apiKey: {
      mainnet: ETHERSCAN_API_KEY,
      goerli: ETHERSCAN_API_KEY,
      bsc: BSCSCAN_API_KEY,
      bscTestnet: BSCSCAN_API_KEY,
      polygon: POLYGONSCAN_API_KEY,
      polygonMumbai: POLYGONSCAN_API_KEY
    }
  },
  paths: {
    sources: "./contracts",
    tests: "./tests",
    cache: "./cache",
    artifacts: "./artifacts"
  },
  mocha: {
    timeout: 40000
  }
};