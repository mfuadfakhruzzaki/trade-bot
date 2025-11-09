"""
Data Collector Module
Fetches real-time and historical data from Bitget Futures API
"""

import ccxt
import pandas as pd
import logging
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import time


class DataCollector:
    """
    Handles data collection from Bitget exchange
    - OHLCV data (candlestick)
    - Orderbook data
    - Funding rate
    - Open interest
    """
    
    def __init__(self, api_key: str, api_secret: str, password: str, testnet: bool = True):
        """
        Initialize Bitget exchange connection
        
        Args:
            api_key: Bitget API key
            api_secret: Bitget API secret
            password: Bitget API password
            testnet: Use testnet or mainnet
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize Bitget exchange
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
                self.logger.info("Using Bitget TESTNET")
            else:
                self.logger.info("Using Bitget MAINNET")
                
            # Test connection
            self.exchange.load_markets()
            self.logger.info("Successfully connected to Bitget")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Bitget: {e}")
            raise
    
    def fetch_ohlcv(self, symbol: str, timeframe: str = '5m', limit: int = 100) -> pd.DataFrame:
        """
        Fetch OHLCV (candlestick) data
        
        Args:
            symbol: Trading pair (e.g., 'SOL/USDT:USDT')
            timeframe: Timeframe (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Number of candles to fetch
            
        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        try:
            self.logger.debug(f"Fetching OHLCV for {symbol} {timeframe} (limit: {limit})")
            
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            self.logger.debug(f"Fetched {len(df)} candles")
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching OHLCV: {e}")
            raise
    
    def fetch_orderbook(self, symbol: str, limit: int = 20) -> Dict:
        """
        Fetch orderbook (bids and asks)
        
        Args:
            symbol: Trading pair
            limit: Depth of orderbook
            
        Returns:
            Dict with 'bids' and 'asks' lists
        """
        try:
            self.logger.debug(f"Fetching orderbook for {symbol}")
            
            orderbook = self.exchange.fetch_order_book(symbol, limit=limit)
            
            return {
                'bids': orderbook['bids'],  # [[price, amount], ...]
                'asks': orderbook['asks'],
                'timestamp': orderbook['timestamp'],
                'datetime': orderbook['datetime']
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching orderbook: {e}")
            raise
    
    def fetch_funding_rate(self, symbol: str) -> Dict:
        """
        Fetch current funding rate for futures
        
        Args:
            symbol: Trading pair
            
        Returns:
            Dict with funding rate info
        """
        try:
            self.logger.debug(f"Fetching funding rate for {symbol}")
            
            funding = self.exchange.fetch_funding_rate(symbol)
            
            return {
                'funding_rate': funding['fundingRate'],
                'funding_timestamp': funding['fundingTimestamp'],
                'next_funding_time': funding.get('fundingDatetime', None)
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching funding rate: {e}")
            return {'funding_rate': 0, 'funding_timestamp': None, 'next_funding_time': None}
    
    def fetch_open_interest(self, symbol: str) -> Optional[float]:
        """
        Fetch open interest for futures
        
        Args:
            symbol: Trading pair
            
        Returns:
            Open interest value or None
        """
        try:
            self.logger.debug(f"Fetching open interest for {symbol}")
            
            # Note: Not all exchanges support this via ccxt
            # May need custom implementation
            ticker = self.exchange.fetch_ticker(symbol)
            open_interest = ticker.get('info', {}).get('openInterest', None)
            
            if open_interest:
                return float(open_interest)
            return None
            
        except Exception as e:
            self.logger.error(f"Error fetching open interest: {e}")
            return None
    
    def fetch_ticker(self, symbol: str) -> Dict:
        """
        Fetch current ticker (price, volume, etc.)
        
        Args:
            symbol: Trading pair
            
        Returns:
            Ticker data dict
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                'last': ticker['last'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'volume': ticker['baseVolume'],
                'timestamp': ticker['timestamp']
            }
        except Exception as e:
            self.logger.error(f"Error fetching ticker: {e}")
            raise
    
    def fetch_historical_data(self, symbol: str, timeframe: str = '5m', 
                             days: int = 30) -> pd.DataFrame:
        """
        Fetch historical data for multiple days (for training)
        
        Args:
            symbol: Trading pair
            timeframe: Timeframe
            days: Number of days to fetch
            
        Returns:
            DataFrame with historical OHLCV data
        """
        try:
            self.logger.info(f"Fetching {days} days of historical data for {symbol}")
            
            # Calculate how many candles we need
            timeframe_map = {
                '1m': 1, '5m': 5, '15m': 15, '30m': 30,
                '1h': 60, '4h': 240, '1d': 1440
            }
            minutes_per_candle = timeframe_map.get(timeframe, 5)
            candles_per_day = (24 * 60) // minutes_per_candle
            total_candles = candles_per_day * days
            
            # Fetch in chunks (exchange limits per request)
            chunk_size = 1000
            all_data = []
            
            since = self.exchange.parse8601(
                (datetime.utcnow() - timedelta(days=days)).isoformat()
            )
            
            while len(all_data) < total_candles:
                ohlcv = self.exchange.fetch_ohlcv(
                    symbol, timeframe, since=since, limit=chunk_size
                )
                
                if not ohlcv:
                    break
                
                all_data.extend(ohlcv)
                since = ohlcv[-1][0] + 1  # Next timestamp
                
                self.logger.debug(f"Fetched {len(all_data)} / {total_candles} candles")
                time.sleep(self.exchange.rateLimit / 1000)  # Respect rate limit
                
                if len(ohlcv) < chunk_size:
                    break  # No more data
            
            df = pd.DataFrame(all_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            df = df[~df.index.duplicated(keep='first')]  # Remove duplicates
            
            self.logger.info(f"Successfully fetched {len(df)} candles")
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching historical data: {e}")
            raise
    
    def get_market_info(self, symbol: str) -> Dict:
        """
        Get market information (limits, precision, etc.)
        
        Args:
            symbol: Trading pair
            
        Returns:
            Market info dict
        """
        try:
            market = self.exchange.market(symbol)
            return {
                'min_amount': market['limits']['amount']['min'],
                'max_amount': market['limits']['amount']['max'],
                'min_cost': market['limits']['cost']['min'],
                'price_precision': market['precision']['price'],
                'amount_precision': market['precision']['amount'],
                'contract_size': market.get('contractSize', 1)
            }
        except Exception as e:
            self.logger.error(f"Error fetching market info: {e}")
            raise
    
    def get_balance(self) -> Dict:
        """
        Get account balance
        
        Returns:
            Balance dict
        """
        try:
            balance = self.exchange.fetch_balance()
            return {
                'total': balance['total'],
                'free': balance['free'],
                'used': balance['used']
            }
        except Exception as e:
            self.logger.error(f"Error fetching balance: {e}")
            raise
    
    def get_positions(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Get open positions
        
        Args:
            symbol: Specific symbol or None for all
            
        Returns:
            List of position dicts
        """
        try:
            positions = self.exchange.fetch_positions([symbol] if symbol else None)
            
            # Filter out positions with 0 contracts
            open_positions = [
                pos for pos in positions 
                if float(pos.get('contracts', 0)) > 0
            ]
            
            return open_positions
            
        except Exception as e:
            self.logger.error(f"Error fetching positions: {e}")
            raise


if __name__ == "__main__":
    # Test the data collector
    logging.basicConfig(level=logging.DEBUG)
    
    # Load from .env for testing
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    collector = DataCollector(
        api_key=os.getenv('BITGET_API_KEY', ''),
        api_secret=os.getenv('BITGET_API_SECRET', ''),
        password=os.getenv('BITGET_PASSWORD', ''),
        testnet=True
    )
    
    # Test fetching OHLCV
    df = collector.fetch_ohlcv('SOL/USDT:USDT', '5m', 100)
    print("\nOHLCV Data:")
    print(df.tail())
    
    # Test orderbook
    orderbook = collector.fetch_orderbook('SOL/USDT:USDT')
    print("\nOrderbook:")
    print(f"Best bid: {orderbook['bids'][0]}")
    print(f"Best ask: {orderbook['asks'][0]}")
    
    # Test funding rate
    funding = collector.fetch_funding_rate('SOL/USDT:USDT')
    print(f"\nFunding rate: {funding}")
