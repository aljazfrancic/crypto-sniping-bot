"""
Analytics and Performance Tracking Module
Provides comprehensive trading analytics and performance metrics
"""

import logging
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import statistics
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class TradeRecord:
    """Data class for individual trade records."""
    
    id: Optional[int] = None
    timestamp: datetime = None
    token_address: str = ""
    token_symbol: str = ""
    pair_address: str = ""
    action: str = ""  # 'buy' or 'sell'
    amount_eth: float = 0.0
    amount_tokens: int = 0
    price_eth: float = 0.0
    gas_used: int = 0
    gas_price: int = 0
    transaction_hash: str = ""
    status: str = ""  # 'pending', 'confirmed', 'failed'
    profit_loss: float = 0.0
    profit_loss_percentage: float = 0.0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class PerformanceMetrics:
    """Data class for performance metrics."""
    
    total_trades: int = 0
    successful_trades: int = 0
    failed_trades: int = 0
    total_volume_eth: float = 0.0
    total_profit_loss: float = 0.0
    win_rate: float = 0.0
    average_profit: float = 0.0
    average_loss: float = 0.0
    best_trade: float = 0.0
    worst_trade: float = 0.0
    total_gas_fees: float = 0.0
    honeypots_detected: int = 0
    pairs_analyzed: int = 0


class TradingAnalytics:
    """Comprehensive trading analytics and performance tracking."""
    
    def __init__(self, db_path: str = "sniper_analytics.db"):
        """Initialize analytics with database storage.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.trades: List[TradeRecord] = []
        self._init_database()
        self._load_trades()
    
    def _init_database(self):
        """Initialize SQLite database for persistent storage."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create trades table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS trades (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        token_address TEXT NOT NULL,
                        token_symbol TEXT,
                        pair_address TEXT,
                        action TEXT NOT NULL,
                        amount_eth REAL,
                        amount_tokens INTEGER,
                        price_eth REAL,
                        gas_used INTEGER,
                        gas_price INTEGER,
                        transaction_hash TEXT UNIQUE,
                        status TEXT,
                        profit_loss REAL DEFAULT 0.0,
                        profit_loss_percentage REAL DEFAULT 0.0
                    )
                ''')
                
                # Create performance metrics table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS daily_metrics (
                        date TEXT PRIMARY KEY,
                        total_trades INTEGER DEFAULT 0,
                        successful_trades INTEGER DEFAULT 0,
                        failed_trades INTEGER DEFAULT 0,
                        total_volume_eth REAL DEFAULT 0.0,
                        total_profit_loss REAL DEFAULT 0.0,
                        total_gas_fees REAL DEFAULT 0.0,
                        honeypots_detected INTEGER DEFAULT 0,
                        pairs_analyzed INTEGER DEFAULT 0
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON trades(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_token_address ON trades(token_address)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON trades(status)')
                
                conn.commit()
                logger.info("Analytics database initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize analytics database: {e}")
            raise
    
    def _load_trades(self):
        """Load existing trades from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM trades ORDER BY timestamp DESC LIMIT 1000
                ''')
                
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                for row in rows:
                    trade_data = dict(zip(columns, row))
                    trade_data['timestamp'] = datetime.fromisoformat(trade_data['timestamp'])
                    trade = TradeRecord(**trade_data)
                    self.trades.append(trade)
                
                logger.info(f"Loaded {len(self.trades)} trade records from database")
                
        except Exception as e:
            logger.error(f"Failed to load trades from database: {e}")
    
    def record_trade(self, trade: TradeRecord) -> bool:
        """Record a new trade in the database and memory.
        
        Args:
            trade: Trade record to store
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                trade_dict = asdict(trade)
                trade_dict['timestamp'] = trade.timestamp.isoformat()
                del trade_dict['id']  # Let database auto-increment
                
                columns = ', '.join(trade_dict.keys())
                placeholders = ', '.join(['?' for _ in trade_dict])
                
                cursor.execute(f'''
                    INSERT OR REPLACE INTO trades ({columns})
                    VALUES ({placeholders})
                ''', list(trade_dict.values()))
                
                trade.id = cursor.lastrowid
                conn.commit()
                
                # Add to memory
                self.trades.insert(0, trade)  # Insert at beginning for recent first
                
                # Keep only last 1000 trades in memory
                if len(self.trades) > 1000:
                    self.trades = self.trades[:1000]
                
                logger.debug(f"Recorded trade: {trade.action} {trade.token_symbol}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to record trade: {e}")
            return False
    
    def update_trade_status(self, transaction_hash: str, status: str, **kwargs) -> bool:
        """Update trade status and additional fields.
        
        Args:
            transaction_hash: Transaction hash to identify trade
            status: New status
            **kwargs: Additional fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build update query
                update_fields = ['status = ?']
                values = [status]
                
                for key, value in kwargs.items():
                    if key in ['profit_loss', 'profit_loss_percentage', 'gas_used', 'gas_price']:
                        update_fields.append(f'{key} = ?')
                        values.append(value)
                
                values.append(transaction_hash)
                
                cursor.execute(f'''
                    UPDATE trades 
                    SET {', '.join(update_fields)}
                    WHERE transaction_hash = ?
                ''', values)
                
                conn.commit()
                
                # Update in memory
                for trade in self.trades:
                    if trade.transaction_hash == transaction_hash:
                        trade.status = status
                        for key, value in kwargs.items():
                            if hasattr(trade, key):
                                setattr(trade, key, value)
                        break
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to update trade status: {e}")
            return False
    
    def calculate_performance_metrics(self, days: int = 30) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics.
        
        Args:
            days: Number of days to analyze (0 for all time)
            
        Returns:
            Performance metrics
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days) if days > 0 else datetime.min
            relevant_trades = [
                trade for trade in self.trades 
                if trade.timestamp >= cutoff_date and trade.status == 'confirmed'
            ]
            
            if not relevant_trades:
                return PerformanceMetrics()
            
            # Basic counts
            total_trades = len(relevant_trades)
            successful_trades = len([t for t in relevant_trades if t.profit_loss > 0])
            failed_trades = len([t for t in relevant_trades if t.profit_loss < 0])
            
            # Volume and P&L
            total_volume = sum(t.amount_eth for t in relevant_trades if t.action == 'buy')
            total_pnl = sum(t.profit_loss for t in relevant_trades)
            
            # Gas fees
            total_gas_fees = sum(
                (t.gas_used * t.gas_price) / 10**18 
                for t in relevant_trades 
                if t.gas_used and t.gas_price
            )
            
            # Win rate
            win_rate = (successful_trades / total_trades * 100) if total_trades > 0 else 0
            
            # Average profits/losses
            profits = [t.profit_loss for t in relevant_trades if t.profit_loss > 0]
            losses = [t.profit_loss for t in relevant_trades if t.profit_loss < 0]
            
            avg_profit = statistics.mean(profits) if profits else 0
            avg_loss = statistics.mean(losses) if losses else 0
            
            # Best and worst trades
            all_pnl = [t.profit_loss for t in relevant_trades]
            best_trade = max(all_pnl) if all_pnl else 0
            worst_trade = min(all_pnl) if all_pnl else 0
            
            return PerformanceMetrics(
                total_trades=total_trades,
                successful_trades=successful_trades,
                failed_trades=failed_trades,
                total_volume_eth=total_volume,
                total_profit_loss=total_pnl,
                win_rate=win_rate,
                average_profit=avg_profit,
                average_loss=avg_loss,
                best_trade=best_trade,
                worst_trade=worst_trade,
                total_gas_fees=total_gas_fees
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate performance metrics: {e}")
            return PerformanceMetrics()
    
    def get_token_performance(self, days: int = 30) -> Dict[str, Dict[str, Any]]:
        """Get performance breakdown by token.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with token performance data
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days) if days > 0 else datetime.min
            relevant_trades = [
                trade for trade in self.trades 
                if trade.timestamp >= cutoff_date and trade.status == 'confirmed'
            ]
            
            token_stats = defaultdict(lambda: {
                'trades': 0,
                'volume': 0.0,
                'profit_loss': 0.0,
                'wins': 0,
                'losses': 0,
                'symbol': 'UNKNOWN'
            })
            
            for trade in relevant_trades:
                token = trade.token_address
                stats = token_stats[token]
                
                stats['trades'] += 1
                stats['symbol'] = trade.token_symbol or 'UNKNOWN'
                
                if trade.action == 'buy':
                    stats['volume'] += trade.amount_eth
                
                stats['profit_loss'] += trade.profit_loss
                
                if trade.profit_loss > 0:
                    stats['wins'] += 1
                elif trade.profit_loss < 0:
                    stats['losses'] += 1
            
            # Calculate win rates
            for stats in token_stats.values():
                total = stats['wins'] + stats['losses']
                stats['win_rate'] = (stats['wins'] / total * 100) if total > 0 else 0
            
            return dict(token_stats)
            
        except Exception as e:
            logger.error(f"Failed to get token performance: {e}")
            return {}
    
    def get_daily_summary(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get daily trading summary.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of daily summaries
        """
        try:
            summaries = []
            
            for i in range(days):
                date = datetime.now().date() - timedelta(days=i)
                start_date = datetime.combine(date, datetime.min.time())
                end_date = datetime.combine(date, datetime.max.time())
                
                day_trades = [
                    trade for trade in self.trades
                    if start_date <= trade.timestamp <= end_date
                    and trade.status == 'confirmed'
                ]
                
                summary = {
                    'date': date.isoformat(),
                    'trades': len(day_trades),
                    'volume': sum(t.amount_eth for t in day_trades if t.action == 'buy'),
                    'profit_loss': sum(t.profit_loss for t in day_trades),
                    'wins': len([t for t in day_trades if t.profit_loss > 0]),
                    'losses': len([t for t in day_trades if t.profit_loss < 0])
                }
                
                summaries.append(summary)
            
            return summaries
            
        except Exception as e:
            logger.error(f"Failed to get daily summary: {e}")
            return []
    
    def detect_patterns(self) -> Dict[str, Any]:
        """Detect trading patterns and provide insights.
        
        Returns:
            Dictionary with pattern analysis
        """
        try:
            if len(self.trades) < 10:
                return {"message": "Insufficient data for pattern analysis"}
            
            confirmed_trades = [t for t in self.trades if t.status == 'confirmed']
            
            patterns = {}
            
            # Time-based patterns
            hour_performance = defaultdict(list)
            for trade in confirmed_trades:
                hour = trade.timestamp.hour
                hour_performance[hour].append(trade.profit_loss)
            
            best_hours = []
            for hour, pnl_list in hour_performance.items():
                if len(pnl_list) >= 3:  # At least 3 trades
                    avg_pnl = statistics.mean(pnl_list)
                    best_hours.append((hour, avg_pnl, len(pnl_list)))
            
            best_hours.sort(key=lambda x: x[1], reverse=True)
            patterns['best_trading_hours'] = best_hours[:3]
            
            # Token success patterns
            token_success = {}
            for trade in confirmed_trades:
                token = trade.token_symbol or trade.token_address[:8]
                if token not in token_success:
                    token_success[token] = {'wins': 0, 'total': 0}
                
                token_success[token]['total'] += 1
                if trade.profit_loss > 0:
                    token_success[token]['wins'] += 1
            
            # Find tokens with high success rate (min 3 trades)
            successful_tokens = []
            for token, stats in token_success.items():
                if stats['total'] >= 3:
                    win_rate = stats['wins'] / stats['total']
                    successful_tokens.append((token, win_rate, stats['total']))
            
            successful_tokens.sort(key=lambda x: x[1], reverse=True)
            patterns['most_successful_tokens'] = successful_tokens[:5]
            
            # Gas efficiency analysis
            gas_trades = [t for t in confirmed_trades if t.gas_used and t.gas_price]
            if gas_trades:
                avg_gas_fee = statistics.mean(
                    (t.gas_used * t.gas_price) / 10**18 for t in gas_trades
                )
                patterns['average_gas_fee_eth'] = avg_gas_fee
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to detect patterns: {e}")
            return {"error": str(e)}
    
    def export_data(self, format: str = 'json', days: int = 30) -> str:
        """Export trading data in specified format.
        
        Args:
            format: Export format ('json' or 'csv')
            days: Number of days to export
            
        Returns:
            Exported data as string
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days) if days > 0 else datetime.min
            export_trades = [
                trade for trade in self.trades 
                if trade.timestamp >= cutoff_date
            ]
            
            if format.lower() == 'json':
                export_data = []
                for trade in export_trades:
                    trade_dict = asdict(trade)
                    trade_dict['timestamp'] = trade.timestamp.isoformat()
                    export_data.append(trade_dict)
                
                return json.dumps(export_data, indent=2)
                
            elif format.lower() == 'csv':
                import csv
                import io
                
                output = io.StringIO()
                if export_trades:
                    fieldnames = asdict(export_trades[0]).keys()
                    writer = csv.DictWriter(output, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for trade in export_trades:
                        trade_dict = asdict(trade)
                        trade_dict['timestamp'] = trade.timestamp.isoformat()
                        writer.writerow(trade_dict)
                
                return output.getvalue()
            
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Failed to export data: {e}")
            return ""
    
    def get_risk_metrics(self) -> Dict[str, float]:
        """Calculate risk metrics for the trading strategy.
        
        Returns:
            Dictionary with risk metrics
        """
        try:
            confirmed_trades = [t for t in self.trades if t.status == 'confirmed']
            
            if len(confirmed_trades) < 10:
                return {"message": "Insufficient data for risk analysis"}
            
            pnl_values = [t.profit_loss for t in confirmed_trades]
            pnl_percentages = [t.profit_loss_percentage for t in confirmed_trades if t.profit_loss_percentage]
            
            metrics = {}
            
            # Sharpe ratio (simplified - assuming risk-free rate of 0)
            if pnl_values:
                avg_return = statistics.mean(pnl_values)
                std_dev = statistics.stdev(pnl_values) if len(pnl_values) > 1 else 0
                metrics['sharpe_ratio'] = avg_return / std_dev if std_dev > 0 else 0
            
            # Maximum drawdown
            if pnl_values:
                cumulative_pnl = []
                running_total = 0
                for pnl in pnl_values:
                    running_total += pnl
                    cumulative_pnl.append(running_total)
                
                peak = cumulative_pnl[0]
                max_drawdown = 0
                
                for value in cumulative_pnl:
                    if value > peak:
                        peak = value
                    drawdown = peak - value
                    if drawdown > max_drawdown:
                        max_drawdown = drawdown
                
                metrics['max_drawdown'] = max_drawdown
            
            # Volatility
            if pnl_percentages:
                metrics['volatility'] = statistics.stdev(pnl_percentages)
            
            # Value at Risk (VaR) - 95th percentile
            if len(pnl_values) >= 20:
                sorted_pnl = sorted(pnl_values)
                var_index = int(len(sorted_pnl) * 0.05)
                metrics['var_95'] = sorted_pnl[var_index]
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate risk metrics: {e}")
            return {"error": str(e)}
    
    def generate_report(self, days: int = 30) -> str:
        """Generate a comprehensive performance report.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Formatted report as string
        """
        try:
            metrics = self.calculate_performance_metrics(days)
            token_perf = self.get_token_performance(days)
            patterns = self.detect_patterns()
            risk_metrics = self.get_risk_metrics()
            
            report = []
            report.append("=" * 60)
            report.append(f"CRYPTO SNIPER BOT - PERFORMANCE REPORT")
            report.append(f"Analysis Period: Last {days} days" if days > 0 else "All Time")
            report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append("=" * 60)
            
            # Performance Summary
            report.append("\n📊 PERFORMANCE SUMMARY")
            report.append("-" * 30)
            report.append(f"Total Trades: {metrics.total_trades}")
            report.append(f"Win Rate: {metrics.win_rate:.1f}%")
            report.append(f"Total P&L: {metrics.total_profit_loss:.4f} ETH")
            report.append(f"Total Volume: {metrics.total_volume_eth:.4f} ETH")
            report.append(f"Average Profit: {metrics.average_profit:.4f} ETH")
            report.append(f"Average Loss: {metrics.average_loss:.4f} ETH")
            report.append(f"Best Trade: {metrics.best_trade:.4f} ETH")
            report.append(f"Worst Trade: {metrics.worst_trade:.4f} ETH")
            report.append(f"Total Gas Fees: {metrics.total_gas_fees:.4f} ETH")
            
            # Risk Metrics
            if isinstance(risk_metrics, dict) and 'error' not in risk_metrics:
                report.append("\n⚠️  RISK METRICS")
                report.append("-" * 20)
                for key, value in risk_metrics.items():
                    if isinstance(value, float):
                        report.append(f"{key.replace('_', ' ').title()}: {value:.4f}")
            
            # Top Performing Tokens
            if token_perf:
                report.append("\n🏆 TOP PERFORMING TOKENS")
                report.append("-" * 30)
                sorted_tokens = sorted(
                    token_perf.items(), 
                    key=lambda x: x[1]['profit_loss'], 
                    reverse=True
                )
                
                for i, (token, stats) in enumerate(sorted_tokens[:5], 1):
                    symbol = stats['symbol']
                    pnl = stats['profit_loss']
                    win_rate = stats['win_rate']
                    trades = stats['trades']
                    report.append(f"{i}. {symbol}: {pnl:.4f} ETH ({win_rate:.1f}% win rate, {trades} trades)")
            
            report.append("\n" + "=" * 60)
            
            return "\n".join(report)
            
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            return f"Error generating report: {e}" 