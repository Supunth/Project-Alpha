"""
Sample data generator for testing and development
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List

def generate_sample_crypto_data(
    symbol: str = "BTC/USD",
    days: int = 30,
    timeframe: str = "1H"
) -> pd.DataFrame:
    """
    Generate sample cryptocurrency market data for testing
    """
    # Calculate number of periods based on timeframe
    periods_per_day = {
        "1m": 1440,   # 1 minute
        "5m": 288,    # 5 minutes
        "15m": 96,    # 15 minutes
        "1H": 24,     # 1 hour
        "4H": 6,      # 4 hours
        "1d": 1       # 1 day
    }
    
    periods = periods_per_day.get(timeframe, 24) * days
    
    # Generate timestamps
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    timestamps = pd.date_range(start=start_time, end=end_time, periods=periods)
    
    # Generate realistic price data using geometric Brownian motion
    np.random.seed(42)  # For reproducible results
    
    # Initial price (around current BTC price)
    initial_price = 45000
    
    # Parameters for GBM
    drift = 0.0001  # Slight upward drift
    volatility = 0.02  # 2% volatility per period
    
    # Generate price series
    dt = 1 / periods_per_day.get(timeframe, 24)
    random_shocks = np.random.normal(0, 1, periods)
    
    log_returns = (drift - 0.5 * volatility**2) * dt + volatility * np.sqrt(dt) * random_shocks
    prices = initial_price * np.exp(np.cumsum(log_returns))
    
    # Generate OHLC data
    data = []
    for i, (timestamp, close_price) in enumerate(zip(timestamps, prices)):
        # Generate realistic OHLC from close price
        volatility_factor = 0.005  # 0.5% intraday volatility
        
        high = close_price * (1 + abs(np.random.normal(0, volatility_factor)))
        low = close_price * (1 - abs(np.random.normal(0, volatility_factor)))
        open_price = prices[i-1] if i > 0 else close_price
        
        # Generate volume (higher volume during price movements)
        base_volume = 1000
        volume_multiplier = 1 + abs(log_returns[i]) * 10
        volume = int(base_volume * volume_multiplier * np.random.uniform(0.5, 2.0))
        
        data.append({
            'timestamp': timestamp,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close_price,
            'volume': volume,
            'symbol': symbol
        })
    
    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    
    return df

def generate_multiple_symbols_data(symbols: List[str], days: int = 7) -> Dict[str, pd.DataFrame]:
    """
    Generate sample data for multiple cryptocurrency symbols
    """
    data_dict = {}
    
    for symbol in symbols:
        # Use different seeds for each symbol to create unique price patterns
        np.random.seed(hash(symbol) % 1000)
        data_dict[symbol] = generate_sample_crypto_data(symbol, days)
    
    return data_dict

def create_backtest_scenario() -> Dict[str, pd.DataFrame]:
    """
    Create a backtest scenario with known price movements
    """
    # Create a scenario with clear trends and reversals
    periods = 100
    timestamps = pd.date_range(start='2023-01-01', periods=periods, freq='1H')
    
    # Create a scenario: uptrend -> reversal -> downtrend -> recovery
    prices = []
    base_price = 40000
    
    # Phase 1: Strong uptrend (periods 0-30)
    for i in range(30):
        price = base_price * (1 + i * 0.005)  # 0.5% increase per period
        prices.append(price)
    
    # Phase 2: Reversal (periods 31-50)
    peak_price = prices[-1]
    for i in range(20):
        price = peak_price * (1 - i * 0.003)  # 0.3% decrease per period
        prices.append(price)
    
    # Phase 3: Downtrend (periods 51-80)
    for i in range(30):
        price = prices[-1] * (1 - 0.002)  # 0.2% decrease per period
        prices.append(price)
    
    # Phase 4: Recovery (periods 81-99)
    for i in range(19):
        price = prices[-1] * (1 + 0.004)  # 0.4% increase per period
        prices.append(price)
    
    # Generate OHLC data
    data = []
    for i, (timestamp, close_price) in enumerate(zip(timestamps, prices)):
        volatility = 0.003  # 0.3% intraday volatility
        
        high = close_price * (1 + abs(np.random.normal(0, volatility)))
        low = close_price * (1 - abs(np.random.normal(0, volatility)))
        open_price = prices[i-1] if i > 0 else close_price
        
        # Higher volume during trend changes
        if i in [30, 50, 80]:  # Trend change points
            volume = 5000
        else:
            volume = 2000
        
        data.append({
            'timestamp': timestamp,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close_price,
            'volume': volume,
            'symbol': 'BTC/USD'
        })
    
    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    
    return {'BTC/USD': df}

if __name__ == "__main__":
    # Generate sample data for testing
    print("Generating sample data...")
    
    # Single symbol data
    btc_data = generate_sample_crypto_data("BTC/USD", days=7)
    print(f"Generated BTC data: {len(btc_data)} periods")
    print(btc_data.head())
    
    # Multiple symbols data
    symbols = ["BTC/USD", "ETH/USD", "ADA/USD"]
    multi_data = generate_multiple_symbols_data(symbols, days=3)
    print(f"\nGenerated data for {len(multi_data)} symbols")
    
    # Backtest scenario
    scenario_data = create_backtest_scenario()
    print(f"\nGenerated backtest scenario: {len(scenario_data['BTC/USD'])} periods")
    
    print("\nSample data generation complete!")
