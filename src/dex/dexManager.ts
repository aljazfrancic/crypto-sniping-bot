import { PancakeSwap } from './pancakeSwap';
import { UniswapV3 } from './uniswapV3';
import { Provider } from '@ethersproject/providers';

export enum DexType {
  PANCAKE_SWAP = 'PANCAKE',
  UNISWAP_V3 = 'UNISWAP_V3'
}

export class DexManager {
  private handlers = {
    [DexType.PANCAKE_SWAP]: new PancakeSwap(),
    [DexType.UNISWAP_V3]: new UniswapV3()
  };

  getHandler(dexType: DexType) {
    return this.handlers[dexType];
  }

  async getLiquidityPool(dexType: DexType, tokenAddress: string) {
    return this.getHandler(dexType).getPool(tokenAddress);
  }
}
