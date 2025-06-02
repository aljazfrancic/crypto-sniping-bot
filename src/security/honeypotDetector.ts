import { Contract, providers } from 'ethers';
import { TokenScanner } from './tokenScanner';

const HONEYPOT_INDICATORS = [
  'blacklist',
  'whitelist',
  'maxTxAmount',
  'antiWhale'
];

export class HoneypotDetector {
  constructor(private provider: providers.Provider) {}

  async analyze(tokenAddress: string): Promise<{isHoneypot: boolean, riskScore: number}> {
    const scanner = new TokenScanner(tokenAddress, this.provider);
    const [contractAnalysis, taxAnalysis] = await Promise.all([
      scanner.checkSuspiciousFunctions(HONEYPOT_INDICATORS),
      scanner.calculateTradeTaxes()
    ]);
    
    return {
      isHoneypot: contractAnalysis.suspiciousCount > 2 || taxAnalysis.buyTax > 15,
      riskScore: contractAnalysis.suspiciousCount * 20 + taxAnalysis.buyTax
    };
  }
}
