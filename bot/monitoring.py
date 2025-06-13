import logging
import time
from datetime import datetime
from pathlib import Path
import json
from typing import Dict, Any, Optional
import os

class BotMonitor:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Set up logging
        self.logger = logging.getLogger("sniper_bot")
        self.logger.setLevel(logging.INFO)
        
        # File handler
        log_file = self.log_dir / f"sniper_bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Metrics
        self.metrics: Dict[str, Any] = {
            "start_time": time.time(),
            "trades": {
                "total": 0,
                "successful": 0,
                "failed": 0
            },
            "positions": {
                "active": 0,
                "closed": 0,
                "total_profit": 0.0
            },
            "errors": {
                "total": 0,
                "by_type": {}
            }
        }
        
        # Backup directory
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
    
    def log_trade(self, trade_type: str, token_address: str, amount: float, 
                  price: float, status: str, tx_hash: Optional[str] = None):
        """Log a trade event"""
        trade_info = {
            "timestamp": datetime.now().isoformat(),
            "type": trade_type,
            "token": token_address,
            "amount": amount,
            "price": price,
            "status": status,
            "tx_hash": tx_hash
        }
        
        self.logger.info(f"Trade: {json.dumps(trade_info)}")
        
        # Update metrics
        self.metrics["trades"]["total"] += 1
        if status == "success":
            self.metrics["trades"]["successful"] += 1
        else:
            self.metrics["trades"]["failed"] += 1
    
    def log_error(self, error_type: str, message: str, details: Optional[Dict] = None):
        """Log an error event"""
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "message": message,
            "details": details
        }
        
        self.logger.error(f"Error: {json.dumps(error_info)}")
        
        # Update metrics
        self.metrics["errors"]["total"] += 1
        self.metrics["errors"]["by_type"][error_type] = \
            self.metrics["errors"]["by_type"].get(error_type, 0) + 1
    
    def update_position(self, token_address: str, status: str, profit: float = 0.0):
        """Update position metrics"""
        if status == "active":
            self.metrics["positions"]["active"] += 1
        elif status == "closed":
            self.metrics["positions"]["active"] -= 1
            self.metrics["positions"]["closed"] += 1
            self.metrics["positions"]["total_profit"] += profit
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self.metrics
    
    def save_metrics(self):
        """Save metrics to file"""
        metrics_file = self.log_dir / f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    def create_backup(self):
        """Create a backup of important files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(exist_ok=True)
        
        # Backup .env file
        if os.path.exists('.env'):
            with open('.env', 'r') as src, open(backup_path / '.env', 'w') as dst:
                dst.write(src.read())
        
        # Backup latest metrics
        self.save_metrics()
        metrics_files = list(self.log_dir.glob('metrics_*.json'))
        if metrics_files:
            latest_metrics = max(metrics_files, key=lambda x: x.stat().st_mtime)
            with open(latest_metrics, 'r') as src, open(backup_path / 'metrics.json', 'w') as dst:
                dst.write(src.read())
        
        # Backup latest log
        log_files = list(self.log_dir.glob('sniper_bot_*.log'))
        if log_files:
            latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
            with open(latest_log, 'r') as src, open(backup_path / 'sniper_bot.log', 'w') as dst:
                dst.write(src.read())
        
        self.logger.info(f"Backup created at {backup_path}")
        return backup_path
    
    def restore_from_backup(self, backup_path: str):
        """Restore from a backup"""
        backup_path = Path(backup_path)
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found at {backup_path}")
        
        # Restore .env
        if (backup_path / '.env').exists():
            with open(backup_path / '.env', 'r') as src, open('.env', 'w') as dst:
                dst.write(src.read())
        
        # Restore metrics
        if (backup_path / 'metrics.json').exists():
            with open(backup_path / 'metrics.json', 'r') as f:
                self.metrics = json.load(f)
        
        self.logger.info(f"Restored from backup at {backup_path}") 