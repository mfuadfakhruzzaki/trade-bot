"""
Web Dashboard for Trading Bot Monitoring
Real-time monitoring with Flask
"""

from flask import Flask, render_template, jsonify
import logging
import os
import json
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List

app = Flask(__name__)
logger = logging.getLogger(__name__)


class DashboardData:
    """Manages data for dashboard display"""
    
    def __init__(self, data_file: str = 'monitoring/dashboard_data.json'):
        self.data_file = data_file
        self.ensure_data_file()
    
    def ensure_data_file(self):
        """Create data file if not exists"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            self.save_data({
                'bot_status': 'stopped',
                'capital': 100,
                'pnl': 0,
                'trades': [],
                'equity_history': [],
                'positions': [],
                'last_signal': None,
                'risk_metrics': {}
            })
    
    def load_data(self) -> Dict:
        """Load dashboard data from file"""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return {}
    
    def save_data(self, data: Dict):
        """Save dashboard data to file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    def update_bot_status(self, status: str):
        """Update bot status"""
        data = self.load_data()
        data['bot_status'] = status
        data['last_update'] = datetime.now().isoformat()
        self.save_data(data)
    
    def update_capital(self, capital: float, pnl: float):
        """Update capital and PnL"""
        data = self.load_data()
        data['capital'] = capital
        data['pnl'] = pnl
        data['pnl_percent'] = (pnl / (capital - pnl)) * 100 if capital > pnl else 0
        self.save_data(data)
    
    def add_trade(self, trade: Dict):
        """Add trade to history"""
        data = self.load_data()
        if 'trades' not in data:
            data['trades'] = []
        data['trades'].append(trade)
        # Keep only last 100 trades
        data['trades'] = data['trades'][-100:]
        self.save_data(data)
    
    def update_equity(self, equity: float):
        """Update equity curve"""
        data = self.load_data()
        if 'equity_history' not in data:
            data['equity_history'] = []
        
        data['equity_history'].append({
            'timestamp': datetime.now().isoformat(),
            'equity': equity
        })
        
        # Keep only last 1000 points
        data['equity_history'] = data['equity_history'][-1000:]
        self.save_data(data)
    
    def update_positions(self, positions: List[Dict]):
        """Update open positions"""
        data = self.load_data()
        data['positions'] = positions
        self.save_data(data)
    
    def update_signal(self, signal: Dict):
        """Update last signal"""
        data = self.load_data()
        data['last_signal'] = signal
        data['last_signal']['timestamp'] = datetime.now().isoformat()
        self.save_data(data)
    
    def update_risk_metrics(self, metrics: Dict):
        """Update risk metrics"""
        data = self.load_data()
        data['risk_metrics'] = metrics
        self.save_data(data)
    
    def get_statistics(self) -> Dict:
        """Calculate trading statistics"""
        data = self.load_data()
        trades = data.get('trades', [])
        
        if not trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'avg_pnl': 0,
                'best_trade': 0,
                'worst_trade': 0,
                'profit_factor': 0
            }
        
        trades_df = pd.DataFrame(trades)
        
        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['pnl'] > 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        avg_pnl = trades_df['pnl'].mean()
        best_trade = trades_df['pnl'].max()
        worst_trade = trades_df['pnl'].min()
        
        gross_profit = trades_df[trades_df['pnl'] > 0]['pnl'].sum() if winning_trades > 0 else 0
        gross_loss = abs(trades_df[trades_df['pnl'] < 0]['pnl'].sum()) if (total_trades - winning_trades) > 0 else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': total_trades - winning_trades,
            'win_rate': win_rate,
            'avg_pnl': avg_pnl,
            'best_trade': best_trade,
            'worst_trade': worst_trade,
            'profit_factor': profit_factor
        }


# Initialize dashboard data manager
dashboard = DashboardData()


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')


@app.route('/api/status')
def get_status():
    """Get current bot status"""
    data = dashboard.load_data()
    stats = dashboard.get_statistics()
    
    return jsonify({
        'bot_status': data.get('bot_status', 'unknown'),
        'capital': data.get('capital', 0),
        'pnl': data.get('pnl', 0),
        'pnl_percent': data.get('pnl_percent', 0),
        'positions': len(data.get('positions', [])),
        'last_update': data.get('last_update', 'N/A'),
        'statistics': stats
    })


@app.route('/api/trades')
def get_trades():
    """Get trade history"""
    data = dashboard.load_data()
    trades = data.get('trades', [])
    
    # Return last 50 trades
    return jsonify(trades[-50:])


@app.route('/api/equity')
def get_equity():
    """Get equity curve data"""
    data = dashboard.load_data()
    equity_history = data.get('equity_history', [])
    
    # Return last 500 points
    return jsonify(equity_history[-500:])


@app.route('/api/positions')
def get_positions():
    """Get open positions"""
    data = dashboard.load_data()
    positions = data.get('positions', [])
    
    return jsonify(positions)


@app.route('/api/signal')
def get_signal():
    """Get last trading signal"""
    data = dashboard.load_data()
    signal = data.get('last_signal', {})
    
    return jsonify(signal)


@app.route('/api/risk')
def get_risk_metrics():
    """Get risk metrics"""
    data = dashboard.load_data()
    risk_metrics = data.get('risk_metrics', {})
    
    return jsonify(risk_metrics)


def run_dashboard(host='0.0.0.0', port=5000, debug=False):
    """Run the dashboard server"""
    logger.info(f"Starting dashboard on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run_dashboard(debug=True)
