"""
Market data fetching utilities for CryptoAlpha
"""
import pandas as pd
import yfinance as yf
import ccxt
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

class MarketDataFetcher:
    """
    Fetches market data from various sources
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.exchanges = {
            'binance': ccxt.binance(),
            'coinbase': ccxt.coinbasepro(),
        }
        
        # Cache for recent data
        self.data_cache = {}
        self.cache_duration = 60  # seconds
    
    async def fetch_latest_data(self, symbols: List[str], timeframe: str = '1m') -> Optional[pd.DataFrame]:
        """
        Fetch latest market data for given symbols
        """
        try:
            # Check cache first
            cache_key = f"{'-'.join(symbols)}_{timeframe}"
            if self._is_cache_valid(cache_key):
                return self.data_cache[cache_key]['data']
            
            # Fetch new data
            all_data = []
            
            for symbol in symbols:
                try:
                    # Try multiple exchanges
                    for exchange_name, exchange in self.exchanges.items():
                        try:
                            ohlcv = await self._fetch_ohlcv_async(exchange, symbol, timeframe, limit=100)
                            if ohlcv:
                                df = self._convert_to_dataframe(ohlcv, symbol)
                                df['exchange'] = exchange_name
                                all_data.append(df)
                                break  # Use first successful exchange
                        except Exception as e:
                            self.logger.warning(f"Failed to fetch {symbol} from {exchange_name}: {e}")
                            continue
                
                except Exception as e:
                    self.logger.error(f"Error fetching data for {symbol}: {e}")
                    continue
            
            if not all_data:
                return None
            
            # Combine all data
            combined_data = pd.concat(all_data, ignore_index=True)
            
            # Cache the data
            self.data_cache[cache_key] = {
                'data': combined_data,
                'timestamp': datetime.now()
            }
            
            return combined_data
            
        except Exception as e:
            self.logger.error(f"Error in fetch_latest_data: {e}")
            return None
    
    async def fetch_historical_data(self, symbols: List[str], start_date: str, end_date: str, timeframe: str = '1h') -> Optional[pd.DataFrame]:
        """
        Fetch historical market data
        """
        try:
            all_data = []
            
            for symbol in symbols:
                try:
                    # Use yfinance for historical data (more reliable)
                    ticker = yf.Ticker(self._convert_symbol_format(symbol))
                    hist = ticker.history(start=start_date, end=end_date, interval=timeframe)
                    
                    if not hist.empty:
                        hist.columns = [col.lower() for col in hist.columns]
                        hist['symbol'] = symbol
                        hist.reset_index(inplace=True)
                        all_data.append(hist)
                        
                except Exception as e:
                    self.logger.error(f"Error fetching historical data for {symbol}: {e}")
                    continue
            
            if not all_data:
                return None
            
            return pd.concat(all_data, ignore_index=True)
            
        except Exception as e:
            self.logger.error(f"Error in fetch_historical_data: {e}")
            return None
    
    async def fetch_real_time_price(self, symbol: str) -> Optional[float]:
        """
        Fetch real-time price for a symbol
        """
        try:
            for exchange_name, exchange in self.exchanges.items():
                try:
                    ticker = await self._fetch_ticker_async(exchange, symbol)
                    if ticker and 'last' in ticker:
                        return float(ticker['last'])
                except Exception as e:
                    self.logger.warning(f"Failed to fetch price from {exchange_name}: {e}")
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error fetching real-time price: {e}")
            return None
    
    def _convert_symbol_format(self, symbol: str) -> str:
        """
        Convert trading pair format for yfinance
        """
        # Convert BTC/USD to BTC-USD for yfinance
        return symbol.replace('/', '-')
    
    def _convert_to_dataframe(self, ohlcv: List, symbol: str) -> pd.DataFrame:
        """
        Convert OHLCV data to DataFrame
        """
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['symbol'] = symbol
        df.set_index('timestamp', inplace=True)
        return df
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """
        Check if cached data is still valid
        """
        if cache_key not in self.data_cache:
            return False
        
        cache_time = self.data_cache[cache_key]['timestamp']
        return (datetime.now() - cache_time).seconds < self.cache_duration
    
    async def _fetch_ohlcv_async(self, exchange, symbol: str, timeframe: str, limit: int = 100) -> Optional[List]:
        """
        Async wrapper for OHLCV fetching
        """
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None, 
                lambda: exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            )
        except Exception as e:
            self.logger.error(f"Error in _fetch_ohlcv_async: {e}")
            return None
    
    async def _fetch_ticker_async(self, exchange, symbol: str) -> Optional[Dict]:
        """
        Async wrapper for ticker fetching
        """
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None, 
                lambda: exchange.fetch_ticker(symbol)
            )
        except Exception as e:
            self.logger.error(f"Error in _fetch_ticker_async: {e}")
            return None
    
    def get_supported_symbols(self) -> List[str]:
        """
        Get list of supported trading symbols
        """
        return [
            'BTC/USD', 'ETH/USD', 'ADA/USD', 'SOL/USD', 
            'DOT/USD', 'LINK/USD', 'UNI/USD', 'AAVE/USD'
        ]
    
    def get_supported_timeframes(self) -> List[str]:
        """
        Get list of supported timeframes
        """
        return ['1m', '5m', '15m', '1h', '4h', '1d']
