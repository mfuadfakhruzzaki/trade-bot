"""
Trade Executor Module
Handles order execution on Bitget Futures
"""

import ccxt
import logging
import time
from typing import Dict, Optional, List
from datetime import datetime
import uuid


class TradeExecutor:
    """
    Executes trades on Bitget Futures
    - Market orders
    - Limit orders
    - Stop loss and take profit orders
    - Error handling and retry logic
    - Rate limiting
    """
    
    def __init__(self, api_key: str, api_secret: str, password: str, 
                 testnet: bool = True, dry_run: bool = False):
        """
        Initialize trade executor
        
        Args:
            api_key: Bitget API key
            api_secret: Bitget API secret
            password: Bitget API password
            testnet: Use testnet or mainnet
            dry_run: If True, simulate orders without executing
        """
        self.logger = logging.getLogger(__name__)
        self.dry_run = dry_run
        self.exchange = None
        
        if dry_run:
            self.logger.warning("DRY RUN MODE - Orders will be simulated")
        else:
            try:
                self.exchange = ccxt.bitget({
                    'apiKey': api_key,
                    'secret': api_secret,
                    'password': password,
                    'enableRateLimit': True,
                    'options': {
                        'defaultType': 'swap',  # futures
                    }
                })
                
                if testnet:
                    self.exchange.set_sandbox_mode(True)
                    self.logger.info("Trade Executor initialized (TESTNET)")
                else:
                    self.logger.warning("Trade Executor initialized (MAINNET - REAL MONEY)")
                
                # Test connection
                self.exchange.load_markets()
                
            except Exception as e:
                self.logger.error(f"Failed to initialize exchange: {e}")
                raise
        
        # Order tracking
        self.orders = []
        self.max_retries = 3
        self.retry_delay = 1  # seconds
    
    def set_leverage(self, symbol: str, leverage: int, margin_mode: str = 'cross'):
        """
        Set leverage for symbol
        
        Args:
            symbol: Trading pair
            leverage: Leverage value (1-125)
            margin_mode: 'cross' or 'isolated'
        """
        try:
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would set leverage: {symbol} = {leverage}x ({margin_mode})")
                return True
            
            self.exchange.set_leverage(leverage, symbol)
            self.logger.info(f"Leverage set: {symbol} = {leverage}x ({margin_mode})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting leverage: {e}")
            return False
    
    def create_market_order(self, symbol: str, side: str, amount: float, 
                           params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Create market order (immediate execution)
        
        Args:
            symbol: Trading pair (e.g., 'SOL/USDT:USDT')
            side: 'buy' or 'sell'
            amount: Position size
            params: Additional parameters
            
        Returns:
            Order dict or None if failed
        """
        try:
            if self.dry_run:
                order_id = f"DRY_{uuid.uuid4().hex[:8]}"
                order = {
                    'id': order_id,
                    'symbol': symbol,
                    'type': 'market',
                    'side': side,
                    'amount': amount,
                    'price': None,
                    'status': 'closed',
                    'filled': amount,
                    'remaining': 0,
                    'timestamp': int(time.time() * 1000),
                    'datetime': datetime.now().isoformat(),
                    'info': {'dry_run': True}
                }
                self.logger.info(f"[DRY RUN] Market order: {side.upper()} {amount} {symbol}")
                self.orders.append(order)
                return order
            
            # Execute real order with retries
            for attempt in range(self.max_retries):
                try:
                    order = self.exchange.create_order(
                        symbol=symbol,
                        type='market',
                        side=side,
                        amount=amount,
                        params=params or {}
                    )
                    
                    self.logger.info(f"Market order executed: {side.upper()} {amount} {symbol}")
                    self.logger.debug(f"Order details: {order}")
                    self.orders.append(order)
                    return order
                    
                except Exception as e:
                    self.logger.warning(f"Order attempt {attempt + 1} failed: {e}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                    else:
                        raise
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error creating market order: {e}")
            return None
    
    def create_limit_order(self, symbol: str, side: str, amount: float, 
                          price: float, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Create limit order
        
        Args:
            symbol: Trading pair
            side: 'buy' or 'sell'
            amount: Position size
            price: Limit price
            params: Additional parameters
            
        Returns:
            Order dict or None if failed
        """
        try:
            if self.dry_run:
                order_id = f"DRY_{uuid.uuid4().hex[:8]}"
                order = {
                    'id': order_id,
                    'symbol': symbol,
                    'type': 'limit',
                    'side': side,
                    'amount': amount,
                    'price': price,
                    'status': 'open',
                    'filled': 0,
                    'remaining': amount,
                    'timestamp': int(time.time() * 1000),
                    'datetime': datetime.now().isoformat(),
                    'info': {'dry_run': True}
                }
                self.logger.info(f"[DRY RUN] Limit order: {side.upper()} {amount} {symbol} @ {price}")
                self.orders.append(order)
                return order
            
            order = self.exchange.create_order(
                symbol=symbol,
                type='limit',
                side=side,
                amount=amount,
                price=price,
                params=params or {}
            )
            
            self.logger.info(f"Limit order created: {side.upper()} {amount} {symbol} @ {price}")
            self.orders.append(order)
            return order
            
        except Exception as e:
            self.logger.error(f"Error creating limit order: {e}")
            return None
    
    def create_stop_loss_order(self, symbol: str, side: str, amount: float, 
                              stop_price: float, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Create stop loss order
        
        Args:
            symbol: Trading pair
            side: 'buy' or 'sell'
            amount: Position size
            stop_price: Stop loss trigger price
            params: Additional parameters
            
        Returns:
            Order dict or None if failed
        """
        try:
            if self.dry_run:
                order_id = f"DRY_{uuid.uuid4().hex[:8]}"
                order = {
                    'id': order_id,
                    'symbol': symbol,
                    'type': 'stop_market',
                    'side': side,
                    'amount': amount,
                    'stopPrice': stop_price,
                    'status': 'open',
                    'timestamp': int(time.time() * 1000),
                    'datetime': datetime.now().isoformat(),
                    'info': {'dry_run': True}
                }
                self.logger.info(f"[DRY RUN] Stop loss: {side.upper()} {amount} {symbol} @ {stop_price}")
                self.orders.append(order)
                return order
            
            # Bitget-specific parameters for stop loss
            params = params or {}
            params.update({
                'stopPrice': stop_price,
                'triggerType': 'market_price'
            })
            
            order = self.exchange.create_order(
                symbol=symbol,
                type='stop_market',
                side=side,
                amount=amount,
                params=params
            )
            
            self.logger.info(f"Stop loss order created: {side.upper()} {amount} {symbol} @ {stop_price}")
            self.orders.append(order)
            return order
            
        except Exception as e:
            self.logger.error(f"Error creating stop loss order: {e}")
            return None
    
    def create_take_profit_order(self, symbol: str, side: str, amount: float, 
                                take_profit_price: float, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Create take profit order
        
        Args:
            symbol: Trading pair
            side: 'buy' or 'sell'
            amount: Position size
            take_profit_price: Take profit trigger price
            params: Additional parameters
            
        Returns:
            Order dict or None if failed
        """
        try:
            if self.dry_run:
                order_id = f"DRY_{uuid.uuid4().hex[:8]}"
                order = {
                    'id': order_id,
                    'symbol': symbol,
                    'type': 'take_profit_market',
                    'side': side,
                    'amount': amount,
                    'stopPrice': take_profit_price,
                    'status': 'open',
                    'timestamp': int(time.time() * 1000),
                    'datetime': datetime.now().isoformat(),
                    'info': {'dry_run': True}
                }
                self.logger.info(f"[DRY RUN] Take profit: {side.upper()} {amount} {symbol} @ {take_profit_price}")
                self.orders.append(order)
                return order
            
            # Bitget-specific parameters for take profit
            params = params or {}
            params.update({
                'stopPrice': take_profit_price,
                'triggerType': 'market_price'
            })
            
            order = self.exchange.create_order(
                symbol=symbol,
                type='take_profit_market',
                side=side,
                amount=amount,
                params=params
            )
            
            self.logger.info(f"Take profit order created: {side.upper()} {amount} {symbol} @ {take_profit_price}")
            self.orders.append(order)
            return order
            
        except Exception as e:
            self.logger.error(f"Error creating take profit order: {e}")
            return None
    
    def open_position_with_sl_tp(self, symbol: str, side: str, amount: float, 
                                 stop_loss: float, take_profit: float) -> Dict:
        """
        Open position with stop loss and take profit
        
        Args:
            symbol: Trading pair
            side: 'long' or 'short'
            amount: Position size
            stop_loss: Stop loss price
            take_profit: Take profit price
            
        Returns:
            Dict with order information
        """
        try:
            # Determine order sides
            entry_side = 'buy' if side == 'long' else 'sell'
            exit_side = 'sell' if side == 'long' else 'buy'
            
            # 1. Open position (market order)
            entry_order = self.create_market_order(symbol, entry_side, amount)
            if not entry_order:
                return {'success': False, 'error': 'Failed to create entry order'}
            
            # Small delay to ensure order is processed
            time.sleep(0.5)
            
            # 2. Set stop loss
            sl_order = self.create_stop_loss_order(symbol, exit_side, amount, stop_loss)
            
            # 3. Set take profit
            tp_order = self.create_take_profit_order(symbol, exit_side, amount, take_profit)
            
            result = {
                'success': True,
                'entry_order': entry_order,
                'stop_loss_order': sl_order,
                'take_profit_order': tp_order,
                'symbol': symbol,
                'side': side,
                'amount': amount,
                'entry_price': entry_order.get('average') or entry_order.get('price'),
                'stop_loss': stop_loss,
                'take_profit': take_profit
            }
            
            self.logger.info(f"Position opened: {side.upper()} {amount} {symbol}")
            self.logger.info(f"Entry: {result['entry_price']}, SL: {stop_loss}, TP: {take_profit}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error opening position with SL/TP: {e}")
            return {'success': False, 'error': str(e)}
    
    def close_position(self, symbol: str, side: str, amount: Optional[float] = None) -> Optional[Dict]:
        """
        Close position (market order)
        
        Args:
            symbol: Trading pair
            side: 'long' or 'short' (the side to close)
            amount: Amount to close (None = close all)
            
        Returns:
            Order dict or None if failed
        """
        try:
            # Get current position if amount not specified
            if amount is None:
                positions = self.get_positions(symbol)
                if positions:
                    amount = abs(float(positions[0].get('contracts', 0)))
                else:
                    self.logger.warning(f"No open position found for {symbol}")
                    return None
            
            # Determine close side (opposite of position side)
            close_side = 'sell' if side == 'long' else 'buy'
            
            # Close position
            order = self.create_market_order(symbol, close_side, amount, 
                                            params={'reduceOnly': True})
            
            if order:
                self.logger.info(f"Position closed: {side.upper()} {amount} {symbol}")
            
            return order
            
        except Exception as e:
            self.logger.error(f"Error closing position: {e}")
            return None
    
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """
        Cancel open order
        
        Args:
            order_id: Order ID
            symbol: Trading pair
            
        Returns:
            True if successful
        """
        try:
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would cancel order: {order_id}")
                return True
            
            self.exchange.cancel_order(order_id, symbol)
            self.logger.info(f"Order cancelled: {order_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error cancelling order: {e}")
            return False
    
    def get_order_status(self, order_id: str, symbol: str) -> Optional[Dict]:
        """
        Get order status
        
        Args:
            order_id: Order ID
            symbol: Trading pair
            
        Returns:
            Order dict or None
        """
        try:
            if self.dry_run:
                # Find in local orders
                for order in self.orders:
                    if order['id'] == order_id:
                        return order
                return None
            
            order = self.exchange.fetch_order(order_id, symbol)
            return order
            
        except Exception as e:
            self.logger.error(f"Error fetching order status: {e}")
            return None
    
    def get_positions(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Get open positions
        
        Args:
            symbol: Specific symbol or None for all
            
        Returns:
            List of position dicts
        """
        try:
            if self.dry_run:
                self.logger.debug("[DRY RUN] No real positions in dry run mode")
                return []
            
            positions = self.exchange.fetch_positions([symbol] if symbol else None)
            
            # Filter open positions
            open_positions = [
                pos for pos in positions 
                if float(pos.get('contracts', 0)) != 0
            ]
            
            return open_positions
            
        except Exception as e:
            self.logger.error(f"Error fetching positions: {e}")
            return []
    
    def get_balance(self) -> Dict:
        """
        Get account balance
        
        Returns:
            Balance dict
        """
        try:
            if self.dry_run:
                return {
                    'USDT': {
                        'free': 1000.0,
                        'used': 0.0,
                        'total': 1000.0
                    }
                }
            
            balance = self.exchange.fetch_balance()
            return balance
            
        except Exception as e:
            self.logger.error(f"Error fetching balance: {e}")
            return {}


if __name__ == "__main__":
    # Test trade executor
    logging.basicConfig(level=logging.INFO)
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    # Use dry run for testing
    executor = TradeExecutor(
        api_key=os.getenv('BITGET_API_KEY', ''),
        api_secret=os.getenv('BITGET_API_SECRET', ''),
        password=os.getenv('BITGET_PASSWORD', ''),
        testnet=True,
        dry_run=True  # Safe testing
    )
    
    symbol = 'SOL/USDT:USDT'
    
    # Set leverage
    executor.set_leverage(symbol, 5)
    
    # Test opening position with SL/TP
    result = executor.open_position_with_sl_tp(
        symbol=symbol,
        side='long',
        amount=0.1,
        stop_loss=95.0,
        take_profit=105.0
    )
    
    print("\nPosition opened:")
    print(result)
    
    # Test closing position
    # close_result = executor.close_position(symbol, 'long', 0.1)
    # print("\nPosition closed:")
    # print(close_result)
