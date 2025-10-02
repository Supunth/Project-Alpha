"""
Technical analysis indicators for cryptocurrency trading
"""
import pandas as pd
import numpy as np
import ta
from typing import Dict, Any

class TechnicalAnalyzer:
    """
    Technical analysis tools for market data
    """
    
    def __init__(self):
        self.indicators = {}
    
    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform comprehensive technical analysis
        """
        if data.empty:
            return {}
        
        signals = {}
        
        try:
            # Calculate basic indicators
            signals.update(self._calculate_rsi(data))
            signals.update(self._calculate_macd(data))
            signals.update(self._calculate_bollinger_bands(data))
            signals.update(self._calculate_moving_averages(data))
            signals.update(self._calculate_volume_indicators(data))
            
            # Generate trading signals
            signals.update(self._generate_signals(signals))
            
        except Exception as e:
            print(f"Error in technical analysis: {e}")
            
        return signals
    
    def _calculate_rsi(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate RSI indicator"""
        if len(data) < 14:
            return {}
        
        rsi = ta.momentum.RSIIndicator(data['close'], window=14).rsi()
        current_rsi = rsi.iloc[-1]
        
        return {
            'rsi': current_rsi,
            'rsi_signal': self._rsi_signal(current_rsi)
        }
    
    def _calculate_macd(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate MACD indicator"""
        if len(data) < 26:
            return {}
        
        macd_indicator = ta.trend.MACD(data['close'])
        macd_line = macd_indicator.macd()
        signal_line = macd_indicator.macd_signal()
        histogram = macd_indicator.macd_diff()
        
        current_macd = macd_line.iloc[-1]
        current_signal = signal_line.iloc[-1]
        current_hist = histogram.iloc[-1]
        
        return {
            'macd': current_macd,
            'macd_signal': current_signal,
            'macd_histogram': current_hist,
            'macd_signal': self._macd_signal(current_macd, current_signal, current_hist)
        }
    
    def _calculate_bollinger_bands(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate Bollinger Bands"""
        if len(data) < 20:
            return {}
        
        bb = ta.volatility.BollingerBands(data['close'], window=20, window_dev=2)
        bb_upper = bb.bollinger_hband()
        bb_lower = bb.bollinger_lband()
        bb_middle = bb.bollinger_mavg()
        
        current_price = data['close'].iloc[-1]
        current_upper = bb_upper.iloc[-1]
        current_lower = bb_lower.iloc[-1]
        current_middle = bb_middle.iloc[-1]
        
        return {
            'bb_upper': current_upper,
            'bb_lower': current_lower,
            'bb_middle': current_middle,
            'bb_position': (current_price - current_lower) / (current_upper - current_lower),
            'bb_signal': self._bb_signal(current_price, current_upper, current_lower)
        }
    
    def _calculate_moving_averages(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate moving averages"""
        if len(data) < 50:
            return {}
        
        sma_20 = ta.trend.SMAIndicator(data['close'], window=20).sma_indicator()
        sma_50 = ta.trend.SMAIndicator(data['close'], window=50).sma_indicator()
        
        current_price = data['close'].iloc[-1]
        current_sma_20 = sma_20.iloc[-1]
        current_sma_50 = sma_50.iloc[-1]
        
        return {
            'sma_20': current_sma_20,
            'sma_50': current_sma_50,
            'ma_signal': self._ma_signal(current_price, current_sma_20, current_sma_50)
        }
    
    def _calculate_volume_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate volume-based indicators"""
        if 'volume' not in data.columns or len(data) < 20:
            return {}
        
        # Volume moving average
        volume_ma = data['volume'].rolling(window=20).mean()
        current_volume = data['volume'].iloc[-1]
        current_volume_ma = volume_ma.iloc[-1]
        
        # Volume ratio
        volume_ratio = current_volume / current_volume_ma if current_volume_ma > 0 else 1
        
        return {
            'volume_ratio': volume_ratio,
            'volume_signal': self._volume_signal(volume_ratio)
        }
    
    def _generate_signals(self, indicators: Dict[str, Any]) -> Dict[str, str]:
        """Generate overall trading signals from indicators"""
        signals = []
        
        # Collect all signals
        for key, value in indicators.items():
            if key.endswith('_signal') and isinstance(value, str):
                signals.append(value)
        
        # Simple voting mechanism
        buy_signals = signals.count('BUY')
        sell_signals = signals.count('SELL')
        
        if buy_signals > sell_signals:
            overall_signal = 'BUY'
        elif sell_signals > buy_signals:
            overall_signal = 'SELL'
        else:
            overall_signal = 'HOLD'
        
        return {
            'overall_signal': overall_signal,
            'signal_strength': abs(buy_signals - sell_signals) / len(signals) if signals else 0
        }
    
    def _rsi_signal(self, rsi: float) -> str:
        """Generate RSI-based signal"""
        if rsi > 70:
            return 'SELL'  # Overbought
        elif rsi < 30:
            return 'BUY'   # Oversold
        else:
            return 'HOLD'
    
    def _macd_signal(self, macd: float, signal: float, histogram: float) -> str:
        """Generate MACD-based signal"""
        if macd > signal and histogram > 0:
            return 'BUY'
        elif macd < signal and histogram < 0:
            return 'SELL'
        else:
            return 'HOLD'
    
    def _bb_signal(self, price: float, upper: float, lower: float) -> str:
        """Generate Bollinger Bands signal"""
        if price >= upper:
            return 'SELL'  # Price at upper band
        elif price <= lower:
            return 'BUY'   # Price at lower band
        else:
            return 'HOLD'
    
    def _ma_signal(self, price: float, sma_20: float, sma_50: float) -> str:
        """Generate moving average signal"""
        if price > sma_20 > sma_50:
            return 'BUY'   # Bullish alignment
        elif price < sma_20 < sma_50:
            return 'SELL'  # Bearish alignment
        else:
            return 'HOLD'
    
    def _volume_signal(self, volume_ratio: float) -> str:
        """Generate volume-based signal"""
        if volume_ratio > 1.5:
            return 'BUY'   # High volume
        elif volume_ratio < 0.5:
            return 'SELL'  # Low volume
        else:
            return 'HOLD'
