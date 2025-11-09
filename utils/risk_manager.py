"""
Risk Management Module
Handles position sizing, leverage, stop loss, take profit, and risk controls
"""

import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd


class RiskManager:
    """
    Manages trading risk and position sizing
    - Position size calculation
    - Leverage management
    - Stop loss and take profit
    - Daily loss limits
    - Cooldown periods
    """
    
    def __init__(self, config: Dict):
        """
        Initialize risk manager
        
        Args:
            config: Risk management configuration
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Risk parameters
        self.initial_capital = config.get('initial_capital', 100)
        self.current_capital = self.initial_capital
        self.leverage = config.get('leverage', 5)
        self.risk_per_trade = config.get('risk_per_trade', 2)  # percentage
        self.max_loss_per_day = config.get('max_loss_per_day', 10)  # percentage
        self.max_open_positions = config.get('max_open_positions', 3)
        self.stop_loss_percent = config.get('stop_loss_percent', 2.0)
        self.take_profit_percent = config.get('take_profit_percent', 4.0)
        self.trailing_stop = config.get('trailing_stop', False)
        self.trailing_stop_percent = config.get('trailing_stop_percent', 1.5)
        self.cooldown_period = config.get('cooldown_period', 600)  # seconds
        
        # Tracking
        self.daily_pnl = 0
        self.daily_loss = 0
        self.trades_today = 0
        self.last_loss_time = None
        self.open_positions = []
        self.daily_reset_time = datetime.now().date()
        
        self.logger.info("Risk Manager initialized")
        self.logger.info(f"Capital: ${self.initial_capital}, Leverage: {self.leverage}x")
        self.logger.info(f"Risk per trade: {self.risk_per_trade}%, Max daily loss: {self.max_loss_per_day}%")
    
    def update_capital(self, new_capital: float):
        """Update current capital"""
        self.current_capital = new_capital
        self.logger.info(f"Capital updated: ${self.current_capital:.2f}")
    
    def reset_daily_tracking(self):
        """Reset daily tracking metrics"""
        today = datetime.now().date()
        if today > self.daily_reset_time:
            self.logger.info(f"Resetting daily tracking. Previous day PnL: ${self.daily_pnl:.2f}")
            self.daily_pnl = 0
            self.daily_loss = 0
            self.trades_today = 0
            self.daily_reset_time = today
    
    def calculate_position_size(self, entry_price: float, stop_loss_price: float,
                               side: str = 'long') -> Tuple[float, float]:
        """
        Calculate position size based on risk per trade
        
        Args:
            entry_price: Entry price
            stop_loss_price: Stop loss price
            side: 'long' or 'short'
            
        Returns:
            (position_size, position_value) tuple
        """
        try:
            # Calculate risk amount in dollars
            risk_amount = self.current_capital * (self.risk_per_trade / 100)
            
            # Calculate price risk per unit
            if side == 'long':
                price_risk = entry_price - stop_loss_price
            else:  # short
                price_risk = stop_loss_price - entry_price
            
            if price_risk <= 0:
                self.logger.error(f"Invalid stop loss: entry={entry_price}, sl={stop_loss_price}")
                return 0, 0
            
            # Position size = risk amount / price risk
            position_size = risk_amount / price_risk
            
            # Apply leverage
            position_value = position_size * entry_price
            max_position_value = self.current_capital * self.leverage
            
            if position_value > max_position_value:
                position_value = max_position_value
                position_size = position_value / entry_price
            
            self.logger.debug(f"Position size: {position_size:.4f} units, Value: ${position_value:.2f}")
            return position_size, position_value
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {e}")
            return 0, 0
    
    def calculate_fixed_position_size(self, entry_price: float) -> Tuple[float, float]:
        """
        Calculate fixed position size based on available capital and leverage
        
        Args:
            entry_price: Entry price
            
        Returns:
            (position_size, position_value) tuple
        """
        try:
            # Use a fixed percentage of capital per trade
            position_value = (self.current_capital * self.leverage) / self.max_open_positions
            position_size = position_value / entry_price
            
            self.logger.debug(f"Fixed position size: {position_size:.4f} units, Value: ${position_value:.2f}")
            return position_size, position_value
            
        except Exception as e:
            self.logger.error(f"Error calculating fixed position size: {e}")
            return 0, 0
    
    def calculate_stop_loss(self, entry_price: float, side: str = 'long') -> float:
        """
        Calculate stop loss price
        
        Args:
            entry_price: Entry price
            side: 'long' or 'short'
            
        Returns:
            Stop loss price
        """
        if side == 'long':
            sl_price = entry_price * (1 - self.stop_loss_percent / 100)
        else:  # short
            sl_price = entry_price * (1 + self.stop_loss_percent / 100)
        
        self.logger.debug(f"Stop loss calculated: {sl_price:.4f} ({self.stop_loss_percent}%)")
        return sl_price
    
    def calculate_take_profit(self, entry_price: float, side: str = 'long') -> float:
        """
        Calculate take profit price
        
        Args:
            entry_price: Entry price
            side: 'long' or 'short'
            
        Returns:
            Take profit price
        """
        if side == 'long':
            tp_price = entry_price * (1 + self.take_profit_percent / 100)
        else:  # short
            tp_price = entry_price * (1 - self.take_profit_percent / 100)
        
        self.logger.debug(f"Take profit calculated: {tp_price:.4f} ({self.take_profit_percent}%)")
        return tp_price
    
    def can_open_position(self) -> Tuple[bool, str]:
        """
        Check if new position can be opened
        
        Returns:
            (can_open, reason) tuple
        """
        # Reset daily tracking if new day
        self.reset_daily_tracking()
        
        # Check max open positions
        if len(self.open_positions) >= self.max_open_positions:
            return False, f"Max open positions reached ({self.max_open_positions})"
        
        # Check daily loss limit
        daily_loss_percent = (self.daily_loss / self.initial_capital) * 100
        if daily_loss_percent >= self.max_loss_per_day:
            return False, f"Daily loss limit reached ({daily_loss_percent:.2f}%)"
        
        # Check cooldown period after loss
        if self.last_loss_time:
            time_since_loss = (datetime.now() - self.last_loss_time).total_seconds()
            if time_since_loss < self.cooldown_period:
                remaining = self.cooldown_period - time_since_loss
                return False, f"Cooldown period active ({remaining:.0f}s remaining)"
        
        # Check if enough capital
        if self.current_capital <= self.initial_capital * 0.5:
            return False, "Insufficient capital (50% drawdown reached)"
        
        return True, "OK"
    
    def validate_trade(self, signal: Dict, current_price: float) -> Tuple[bool, str]:
        """
        Validate if trade should be executed
        
        Args:
            signal: Trading signal dict
            current_price: Current market price
            
        Returns:
            (is_valid, reason) tuple
        """
        # Check if can open position
        can_open, reason = self.can_open_position()
        if not can_open:
            return False, reason
        
        # Check signal confidence
        confidence_threshold = self.config.get('confidence_threshold', 0.6)
        if signal['confidence'] < confidence_threshold:
            return False, f"Low confidence ({signal['confidence']:.2f} < {confidence_threshold})"
        
        # Only allow BUY or SELL signals
        if signal['signal'] not in ['BUY', 'SELL']:
            return False, f"Invalid signal: {signal['signal']}"
        
        return True, "Valid"
    
    def add_position(self, position: Dict):
        """
        Add new position to tracking
        
        Args:
            position: Position dict with details
        """
        self.open_positions.append(position)
        self.trades_today += 1
        self.logger.info(f"Position added: {position['side']} {position['size']:.4f} @ {position['entry_price']:.4f}")
    
    def remove_position(self, position_id: str):
        """
        Remove closed position from tracking
        
        Args:
            position_id: Position ID
        """
        self.open_positions = [p for p in self.open_positions if p.get('id') != position_id]
        self.logger.info(f"Position removed: {position_id}")
    
    def update_position_pnl(self, position_id: str, pnl: float, is_closed: bool = False):
        """
        Update position PnL
        
        Args:
            position_id: Position ID
            pnl: Profit/Loss amount
            is_closed: Whether position is closed
        """
        self.daily_pnl += pnl
        
        if pnl < 0:
            self.daily_loss += abs(pnl)
            self.last_loss_time = datetime.now()
        
        if is_closed:
            self.remove_position(position_id)
        
        self.logger.info(f"PnL updated: ${pnl:.2f}, Daily PnL: ${self.daily_pnl:.2f}")
    
    def get_risk_metrics(self) -> Dict:
        """
        Get current risk metrics
        
        Returns:
            Dict with risk metrics
        """
        return {
            'current_capital': self.current_capital,
            'initial_capital': self.initial_capital,
            'daily_pnl': self.daily_pnl,
            'daily_loss': self.daily_loss,
            'daily_loss_percent': (self.daily_loss / self.initial_capital) * 100,
            'trades_today': self.trades_today,
            'open_positions': len(self.open_positions),
            'max_open_positions': self.max_open_positions,
            'leverage': self.leverage,
            'can_trade': self.can_open_position()[0]
        }
    
    def check_trailing_stop(self, position: Dict, current_price: float) -> Optional[float]:
        """
        Check and update trailing stop
        
        Args:
            position: Position dict
            current_price: Current market price
            
        Returns:
            New stop loss price or None
        """
        if not self.trailing_stop:
            return None
        
        try:
            side = position['side']
            entry_price = position['entry_price']
            current_sl = position.get('stop_loss')
            
            if side == 'long':
                # Update SL if price moved up
                profit_percent = ((current_price - entry_price) / entry_price) * 100
                if profit_percent > self.trailing_stop_percent:
                    new_sl = current_price * (1 - self.trailing_stop_percent / 100)
                    if new_sl > current_sl:
                        self.logger.info(f"Trailing stop updated: {current_sl:.4f} -> {new_sl:.4f}")
                        return new_sl
            
            else:  # short
                profit_percent = ((entry_price - current_price) / entry_price) * 100
                if profit_percent > self.trailing_stop_percent:
                    new_sl = current_price * (1 + self.trailing_stop_percent / 100)
                    if new_sl < current_sl:
                        self.logger.info(f"Trailing stop updated: {current_sl:.4f} -> {new_sl:.4f}")
                        return new_sl
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error checking trailing stop: {e}")
            return None


if __name__ == "__main__":
    # Test risk manager
    logging.basicConfig(level=logging.DEBUG)
    
    config = {
        'initial_capital': 100,
        'leverage': 5,
        'risk_per_trade': 2,
        'max_loss_per_day': 10,
        'max_open_positions': 3,
        'stop_loss_percent': 2.0,
        'take_profit_percent': 4.0,
        'trailing_stop': True,
        'trailing_stop_percent': 1.5,
        'cooldown_period': 600,
        'confidence_threshold': 0.6
    }
    
    rm = RiskManager(config)
    
    # Test position sizing
    entry_price = 100.0
    sl_price = rm.calculate_stop_loss(entry_price, 'long')
    tp_price = rm.calculate_take_profit(entry_price, 'long')
    
    print(f"\nEntry: ${entry_price}")
    print(f"Stop Loss: ${sl_price:.2f}")
    print(f"Take Profit: ${tp_price:.2f}")
    
    position_size, position_value = rm.calculate_position_size(entry_price, sl_price, 'long')
    print(f"\nPosition Size: {position_size:.4f} units")
    print(f"Position Value: ${position_value:.2f}")
    
    # Test validation
    signal = {'signal': 'BUY', 'confidence': 0.75}
    is_valid, reason = rm.validate_trade(signal, entry_price)
    print(f"\nTrade Valid: {is_valid}, Reason: {reason}")
    
    # Test metrics
    print("\nRisk Metrics:")
    print(rm.get_risk_metrics())
