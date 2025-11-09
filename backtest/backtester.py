"""
Backtesting Framework
Simulate trading strategy on historical data
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns


class Backtester:
    """
    Backtest trading strategy on historical data
    - Simulates trades based on signals
    - Calculates performance metrics
    - Generates equity curve
    """
    
    def __init__(self, initial_capital: float = 100, leverage: int = 5, 
                 commission: float = 0.0006, slippage: float = 0.0001):
        """
        Initialize backtester
        
        Args:
            initial_capital: Starting capital
            leverage: Leverage multiplier
            commission: Trading commission (0.06% = 0.0006)
            slippage: Price slippage (0.01% = 0.0001)
        """
        self.logger = logging.getLogger(__name__)
        
        self.initial_capital = initial_capital
        self.leverage = leverage
        self.commission = commission
        self.slippage = slippage
        
        # Results tracking
        self.trades = []
        self.equity_curve = []
        self.current_capital = initial_capital
        self.current_position = None
        
        self.logger.info(f"Backtester initialized: Capital=${initial_capital}, Leverage={leverage}x")
    
    def reset(self):
        """Reset backtester state"""
        self.trades = []
        self.equity_curve = []
        self.current_capital = self.initial_capital
        self.current_position = None
        self.logger.info("Backtester reset")
    
    def calculate_position_size(self, price: float, side: str, 
                               stop_loss: float, risk_percent: float = 2) -> float:
        """
        Calculate position size based on risk
        
        Args:
            price: Entry price
            side: 'long' or 'short'
            stop_loss: Stop loss price
            risk_percent: Risk per trade (%)
            
        Returns:
            Position size
        """
        risk_amount = self.current_capital * (risk_percent / 100)
        
        if side == 'long':
            price_risk = price - stop_loss
        else:
            price_risk = stop_loss - price
        
        if price_risk <= 0:
            return 0
        
        position_size = risk_amount / price_risk
        max_position_value = self.current_capital * self.leverage
        position_value = position_size * price
        
        if position_value > max_position_value:
            position_size = max_position_value / price
        
        return position_size
    
    def open_position(self, timestamp, price: float, side: str, 
                     stop_loss: float, take_profit: float, 
                     signal_data: Optional[Dict] = None) -> bool:
        """
        Open a position
        
        Args:
            timestamp: Entry timestamp
            price: Entry price
            side: 'long' or 'short'
            stop_loss: Stop loss price
            take_profit: Take profit price
            signal_data: Additional signal information
            
        Returns:
            True if position opened
        """
        if self.current_position is not None:
            self.logger.debug("Position already open, skipping")
            return False
        
        # Apply slippage
        actual_price = price * (1 + self.slippage) if side == 'long' else price * (1 - self.slippage)
        
        # Calculate position size
        position_size = self.calculate_position_size(actual_price, side, stop_loss)
        
        if position_size <= 0:
            self.logger.warning("Invalid position size")
            return False
        
        position_value = position_size * actual_price
        commission_cost = position_value * self.commission
        
        self.current_position = {
            'entry_timestamp': timestamp,
            'entry_price': actual_price,
            'side': side,
            'size': position_size,
            'value': position_value,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'commission': commission_cost,
            'signal_data': signal_data or {}
        }
        
        self.current_capital -= commission_cost
        
        self.logger.debug(f"Position opened: {side.upper()} {position_size:.4f} @ {actual_price:.2f}")
        return True
    
    def close_position(self, timestamp, price: float, reason: str = 'signal') -> Optional[Dict]:
        """
        Close current position
        
        Args:
            timestamp: Exit timestamp
            price: Exit price
            reason: Close reason ('signal', 'stop_loss', 'take_profit')
            
        Returns:
            Trade dict or None
        """
        if self.current_position is None:
            return None
        
        side = self.current_position['side']
        entry_price = self.current_position['entry_price']
        position_size = self.current_position['size']
        
        # Apply slippage
        actual_price = price * (1 - self.slippage) if side == 'long' else price * (1 + self.slippage)
        
        # Calculate PnL
        if side == 'long':
            pnl = (actual_price - entry_price) * position_size
        else:  # short
            pnl = (entry_price - actual_price) * position_size
        
        # Deduct exit commission
        exit_commission = position_size * actual_price * self.commission
        pnl -= exit_commission
        pnl -= self.current_position['commission']  # Entry commission
        
        # Update capital
        self.current_capital += pnl
        
        # Duration
        duration = timestamp - self.current_position['entry_timestamp']
        
        # Create trade record
        trade = {
            'entry_timestamp': self.current_position['entry_timestamp'],
            'exit_timestamp': timestamp,
            'duration': duration,
            'side': side,
            'entry_price': entry_price,
            'exit_price': actual_price,
            'size': position_size,
            'pnl': pnl,
            'pnl_percent': (pnl / self.current_capital) * 100,
            'return_percent': ((actual_price - entry_price) / entry_price * 100) if side == 'long' else ((entry_price - actual_price) / entry_price * 100),
            'close_reason': reason,
            'signal_data': self.current_position.get('signal_data', {})
        }
        
        self.trades.append(trade)
        self.current_position = None
        
        self.logger.debug(f"Position closed: {reason.upper()} PnL=${pnl:.2f}")
        return trade
    
    def check_stop_loss_take_profit(self, timestamp, high: float, low: float) -> Optional[Dict]:
        """
        Check if stop loss or take profit hit
        
        Args:
            timestamp: Current timestamp
            high: High price of bar
            low: Low price of bar
            
        Returns:
            Trade dict if closed, None otherwise
        """
        if self.current_position is None:
            return None
        
        side = self.current_position['side']
        stop_loss = self.current_position['stop_loss']
        take_profit = self.current_position['take_profit']
        
        if side == 'long':
            # Check stop loss first (more conservative)
            if low <= stop_loss:
                return self.close_position(timestamp, stop_loss, 'stop_loss')
            # Check take profit
            elif high >= take_profit:
                return self.close_position(timestamp, take_profit, 'take_profit')
        
        else:  # short
            # Check stop loss first
            if high >= stop_loss:
                return self.close_position(timestamp, stop_loss, 'stop_loss')
            # Check take profit
            elif low <= take_profit:
                return self.close_position(timestamp, take_profit, 'take_profit')
        
        return None
    
    def run_backtest(self, data: pd.DataFrame, signals: pd.Series, 
                    stop_loss_pct: float = 2.0, take_profit_pct: float = 4.0) -> Dict:
        """
        Run backtest on historical data
        
        Args:
            data: DataFrame with OHLCV data
            signals: Series with trading signals (1=buy, 0=sell/hold, 2=buy for ternary)
            stop_loss_pct: Stop loss percentage
            take_profit_pct: Take profit percentage
            
        Returns:
            Backtest results dict
        """
        self.reset()
        
        self.logger.info("Running backtest...")
        self.logger.info(f"Data: {len(data)} bars, Signals: {len(signals)} signals")
        
        # Ensure data and signals are aligned
        data = data.loc[signals.index]
        
        for idx, row in data.iterrows():
            timestamp = idx
            close = row['close']
            high = row['high']
            low = row['low']
            signal = signals.loc[idx]
            
            # Record equity
            self.equity_curve.append({
                'timestamp': timestamp,
                'equity': self.current_capital
            })
            
            # Check if position should be closed by SL/TP
            if self.current_position:
                trade = self.check_stop_loss_take_profit(timestamp, high, low)
            
            # Process signals
            if self.current_position is None:
                # Open new position based on signal
                if signal == 1:  # Buy signal
                    sl = close * (1 - stop_loss_pct / 100)
                    tp = close * (1 + take_profit_pct / 100)
                    self.open_position(timestamp, close, 'long', sl, tp)
                
                elif signal == 0:  # Sell signal (short)
                    sl = close * (1 + stop_loss_pct / 100)
                    tp = close * (1 - take_profit_pct / 100)
                    self.open_position(timestamp, close, 'short', sl, tp)
                
                elif signal == 2:  # Buy signal (ternary classification)
                    sl = close * (1 - stop_loss_pct / 100)
                    tp = close * (1 + take_profit_pct / 100)
                    self.open_position(timestamp, close, 'long', sl, tp)
            
            else:
                # Close position if opposite signal
                current_side = self.current_position['side']
                if (current_side == 'long' and signal == 0) or \
                   (current_side == 'short' and signal == 1):
                    self.close_position(timestamp, close, 'signal')
        
        # Close any remaining position
        if self.current_position:
            self.close_position(data.index[-1], data['close'].iloc[-1], 'end_of_data')
        
        # Calculate metrics
        results = self.calculate_metrics()
        
        self.logger.info("Backtest complete")
        self.logger.info(f"Total trades: {results['total_trades']}")
        self.logger.info(f"Win rate: {results['win_rate']:.2%}")
        self.logger.info(f"Final capital: ${results['final_capital']:.2f}")
        self.logger.info(f"Total return: {results['total_return']:.2%}")
        
        return results
    
    def calculate_metrics(self) -> Dict:
        """
        Calculate performance metrics
        
        Returns:
            Dict with metrics
        """
        if not self.trades:
            return {
                'total_trades': 0,
                'final_capital': self.current_capital,
                'total_return': 0,
                'win_rate': 0
            }
        
        trades_df = pd.DataFrame(self.trades)
        
        # Basic metrics
        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['pnl'] > 0])
        losing_trades = len(trades_df[trades_df['pnl'] < 0])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # PnL metrics
        total_pnl = trades_df['pnl'].sum()
        avg_pnl = trades_df['pnl'].mean()
        avg_win = trades_df[trades_df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
        avg_loss = trades_df[trades_df['pnl'] < 0]['pnl'].mean() if losing_trades > 0 else 0
        
        # Return metrics
        total_return = ((self.current_capital - self.initial_capital) / self.initial_capital) * 100
        
        # Profit factor
        gross_profit = trades_df[trades_df['pnl'] > 0]['pnl'].sum() if winning_trades > 0 else 0
        gross_loss = abs(trades_df[trades_df['pnl'] < 0]['pnl'].sum()) if losing_trades > 0 else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else np.inf
        
        # Drawdown
        equity_df = pd.DataFrame(self.equity_curve)
        equity_df['peak'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['peak']) / equity_df['peak'] * 100
        max_drawdown = equity_df['drawdown'].min()
        
        # Sharpe ratio (assuming daily data)
        returns = trades_df['return_percent'].values
        sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if len(returns) > 1 else 0
        
        # Average duration
        avg_duration = trades_df['duration'].mean()
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_pnl': avg_pnl,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'best_trade': trades_df['pnl'].max(),
            'worst_trade': trades_df['pnl'].min(),
            'profit_factor': profit_factor,
            'initial_capital': self.initial_capital,
            'final_capital': self.current_capital,
            'total_return': total_return,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'avg_duration': avg_duration,
            'trades_df': trades_df,
            'equity_df': equity_df
        }
    
    def plot_results(self, results: Dict, save_path: Optional[str] = None):
        """
        Plot backtest results
        
        Args:
            results: Results dict from calculate_metrics
            save_path: Path to save plot (optional)
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Equity curve
        equity_df = results['equity_df']
        axes[0, 0].plot(equity_df['timestamp'], equity_df['equity'], label='Equity')
        axes[0, 0].plot(equity_df['timestamp'], equity_df['peak'], 'r--', alpha=0.5, label='Peak')
        axes[0, 0].set_title('Equity Curve')
        axes[0, 0].set_xlabel('Time')
        axes[0, 0].set_ylabel('Capital ($)')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Drawdown
        axes[0, 1].fill_between(equity_df['timestamp'], equity_df['drawdown'], 0, color='red', alpha=0.3)
        axes[0, 1].set_title('Drawdown')
        axes[0, 1].set_xlabel('Time')
        axes[0, 1].set_ylabel('Drawdown (%)')
        axes[0, 1].grid(True, alpha=0.3)
        
        # PnL distribution
        trades_df = results['trades_df']
        axes[1, 0].hist(trades_df['pnl'], bins=30, alpha=0.7, edgecolor='black')
        axes[1, 0].axvline(x=0, color='red', linestyle='--', linewidth=2)
        axes[1, 0].set_title('PnL Distribution')
        axes[1, 0].set_xlabel('PnL ($)')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Win rate by trade
        trades_df['trade_num'] = range(1, len(trades_df) + 1)
        trades_df['win'] = (trades_df['pnl'] > 0).astype(int)
        axes[1, 1].scatter(trades_df['trade_num'], trades_df['pnl'], 
                          c=trades_df['win'], cmap='RdYlGn', alpha=0.6)
        axes[1, 1].axhline(y=0, color='black', linestyle='-', linewidth=1)
        axes[1, 1].set_title('Trade PnL Over Time')
        axes[1, 1].set_xlabel('Trade Number')
        axes[1, 1].set_ylabel('PnL ($)')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Plot saved to {save_path}")
        
        plt.show()
    
    def print_summary(self, results: Dict):
        """
        Print backtest summary
        
        Args:
            results: Results dict
        """
        print("\n" + "=" * 60)
        print("BACKTEST SUMMARY")
        print("=" * 60)
        print(f"Initial Capital: ${results['initial_capital']:.2f}")
        print(f"Final Capital: ${results['final_capital']:.2f}")
        print(f"Total Return: {results['total_return']:.2f}%")
        print(f"Total PnL: ${results['total_pnl']:.2f}")
        print("\n" + "-" * 60)
        print(f"Total Trades: {results['total_trades']}")
        print(f"Winning Trades: {results['winning_trades']}")
        print(f"Losing Trades: {results['losing_trades']}")
        print(f"Win Rate: {results['win_rate']:.2%}")
        print("\n" + "-" * 60)
        print(f"Average PnL: ${results['avg_pnl']:.2f}")
        print(f"Average Win: ${results['avg_win']:.2f}")
        print(f"Average Loss: ${results['avg_loss']:.2f}")
        print(f"Best Trade: ${results['best_trade']:.2f}")
        print(f"Worst Trade: ${results['worst_trade']:.2f}")
        print(f"Profit Factor: {results['profit_factor']:.2f}")
        print("\n" + "-" * 60)
        print(f"Max Drawdown: {results['max_drawdown']:.2f}%")
        print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        print(f"Avg Duration: {results['avg_duration']}")
        print("=" * 60)


if __name__ == "__main__":
    # Test backtester
    logging.basicConfig(level=logging.INFO)
    
    from utils.data_collector import DataCollector
    from utils.feature_engineering import FeatureEngineer
    from model.ai_model import TradingModel
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Collect data
    collector = DataCollector(
        api_key=os.getenv('BITGET_API_KEY', ''),
        api_secret=os.getenv('BITGET_API_SECRET', ''),
        password=os.getenv('BITGET_PASSWORD', ''),
        testnet=True
    )
    
    df = collector.fetch_ohlcv('SOL/USDT:USDT', '5m', 2000)
    
    # Extract features
    engineer = FeatureEngineer()
    df = engineer.extract_all_features(df)
    
    # Generate signals (dummy for testing - use actual model in production)
    signals = pd.Series(np.random.choice([0, 1], size=len(df)), index=df.index)
    
    # Run backtest
    backtester = Backtester(initial_capital=100, leverage=5)
    results = backtester.run_backtest(df, signals, stop_loss_pct=2.0, take_profit_pct=4.0)
    
    # Print summary
    backtester.print_summary(results)
    
    # Plot results
    backtester.plot_results(results, save_path='backtest/backtest_results.png')
