"""Performance monitoring for sniper bot."""
import json
import time
from typing import Dict, List
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class TradeRecord:
    timestamp: float
    token_address: str
    token_symbol: str
    buy_amount_bnb: float
    success: bool
    profit_loss: float = 0.0

class PerformanceMonitor:
    def __init__(self, data_file: str = "trade_history.json"):
        self.data_file = data_file
        self.trades: List[TradeRecord] = []
        self.load_data()
        
    def load_data(self):
        """Load trade data"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.trades = [TradeRecord(**trade) for trade in data.get('trades', [])]
        except FileNotFoundError:
            print("No existing data found")
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def save_data(self):
        """Save trade data"""
        try:
            data = {'trades': [asdict(trade) for trade in self.trades]}
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def record_trade(self, trade: TradeRecord):
        """Record new trade"""
        self.trades.append(trade)
        self.save_data()
        
    def print_performance_summary(self, days: int = 7):
        """Print performance summary"""
        cutoff_time = time.time() - (days * 24 * 3600)
        recent_trades = [t for t in self.trades if t.timestamp >= cutoff_time]
        
        if not recent_trades:
            print("No recent trades found")
            return
        
        total_trades = len(recent_trades)
        successful_trades = len([t for t in recent_trades if t.success])
        success_rate = (successful_trades / total_trades) * 100
        
        total_invested = sum(t.buy_amount_bnb for t in recent_trades)
        total_pnl = sum(t.profit_loss for t in recent_trades)
        
        print("=" * 50)
        print(f"PERFORMANCE SUMMARY ({days} days)")
        print("=" * 50)
        print(f"Total Trades: {total_trades}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Total Invested: {total_invested:.4f} BNB")
        print(f"Total P&L: {total_pnl:+.4f} BNB")
        if total_invested > 0:
            roi = (total_pnl / total_invested) * 100
            print(f"ROI: {roi:+.2f}%")
        print("=" * 50)

def main():
    monitor = PerformanceMonitor()
    monitor.print_performance_summary(7)

if __name__ == "__main__":
    main()
