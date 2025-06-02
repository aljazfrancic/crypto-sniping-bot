"""Risk management system for crypto sniping bot."""
import time
from decimal import Decimal
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"

@dataclass
class Position:
    token_address: str
    token_symbol: str
    entry_price: Decimal
    amount_bnb: Decimal
    timestamp: float
    stop_loss: Optional[Decimal] = None

class RiskManager:
    def __init__(self, config: Dict):
        self.max_daily_loss = Decimal(str(config.get('MAX_DAILY_LOSS_BNB', '0.1')))
        self.max_positions = config.get('MAX_POSITIONS', 5)
        self.stop_loss_percentage = config.get('STOP_LOSS_PERCENTAGE', 50)
        self.max_consecutive_losses = config.get('MAX_CONSECUTIVE_LOSSES', 5)
        
        self.daily_loss = Decimal('0')
        self.positions: Dict[str, Position] = {}
        self.consecutive_losses = 0
        self.circuit_breaker_active = False
        
    def should_allow_trade(self, amount: Decimal) -> Tuple[bool, str]:
        """Check if trade should be allowed"""
        
        if self.circuit_breaker_active:
            return False, "Circuit breaker active"
        
        if self.daily_loss >= self.max_daily_loss:
            return False, f"Daily loss limit reached: {self.daily_loss} BNB"
        
        if len(self.positions) >= self.max_positions:
            return False, f"Max positions reached: {len(self.positions)}"
        
        if self.consecutive_losses >= self.max_consecutive_losses:
            return False, f"Too many consecutive losses: {self.consecutive_losses}"
        
        return True, "Trade approved"
    
    def open_position(self, token_address: str, token_symbol: str, 
                     entry_price: Decimal, amount: Decimal) -> str:
        """Open new position"""
        
        stop_loss = entry_price * (1 - self.stop_loss_percentage / 100)
        
        position = Position(
            token_address=token_address,
            token_symbol=token_symbol,
            entry_price=entry_price,
            amount_bnb=amount,
            timestamp=time.time(),
            stop_loss=stop_loss
        )
        
        self.positions[token_address] = position
        print(f"Position opened: {token_symbol} | Stop: {stop_loss}")
        return token_address
    
    def close_position(self, token_address: str, exit_price: Decimal, 
                      reason: str = "Manual") -> Decimal:
        """Close position and calculate P&L"""
        
        if token_address not in self.positions:
            return Decimal('0')
        
        position = self.positions[token_address]
        price_change = (exit_price - position.entry_price) / position.entry_price
        pnl = position.amount_bnb * price_change
        
        if pnl < 0:
            self.daily_loss += abs(pnl)
            self.consecutive_losses += 1
            
            if self.consecutive_losses >= self.max_consecutive_losses:
                self.circuit_breaker_active = True
                print("CIRCUIT BREAKER ACTIVATED!")
        else:
            self.consecutive_losses = 0
        
        del self.positions[token_address]
        print(f"Position closed: {position.token_symbol} | P&L: {pnl:+.4f} BNB")
        return pnl
    
    def get_risk_report(self) -> str:
        """Generate risk report"""
        
        return f"""
RISK REPORT
Daily Loss: {self.daily_loss}/{self.max_daily_loss} BNB
Positions: {len(self.positions)}/{self.max_positions}
Consecutive Losses: {self.consecutive_losses}
Circuit Breaker: {'ACTIVE' if self.circuit_breaker_active else 'INACTIVE'}
"""

def main():
    config = {
        'MAX_DAILY_LOSS_BNB': '0.1',
        'MAX_POSITIONS': 5,
        'STOP_LOSS_PERCENTAGE': 50,
        'MAX_CONSECUTIVE_LOSSES': 3
    }
    
    risk_manager = RiskManager(config)
    print(risk_manager.get_risk_report())

if __name__ == "__main__":
    main()
