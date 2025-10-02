"""
Mean reversion trading strategy for CryptoAlpha
"""
import pandas as pd
import numpy as np
from typing import Dict, Any
import logging

class MeanReversionStrategy:
    """
    Mean reversion trading strategy
    """
    
    def __init__(self):
        self.name = "Mean Reversion Strategy"
        self.logger = logging.getLogger(__name__)
        
        # Strategy parameters
        self.lookback_period = 20
        self.z_score_threshold = 2.0  # 2 standard deviations
        self.bollinger_bands_period = 20
        self.bollinger_bands_std = 2
    
    def analyze(self, market_data: pd.DataFrame, technical_signals: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market data using mean reversion strategy
        """
        if market_data.empty or len(market_data) < self.lookback_period:
            return {'signal': 'HOLD', 'strength': 0, 'reason': 'Insufficient data'}
        
        try:
            # Calculate mean reversion indicators
            z_score = self._calculate_z_score(market_data)
            bollinger_position = self._calculate_bollinger_position(market_data)
            rsi_extreme = self._check_rsi_extreme(technical_signals)
            
            # Generate signal
            signal, strength = self._generate_signal(z_score, bollinger_position, rsi_extreme)
            
            return {
                'signal': signal,
                'strength': strength,
                'z_score': z_score,
                'bollinger_position': bollinger_position,
                'rsi_extreme': rsi_extreme,
                'reason': self._get_signal_reason(signal, z_score, bollinger_position)
            }
            
        except Exception as e:
            self.logger.error(f"Error in mean reversion strategy analysis: {e}")
            return {'signal': 'HOLD', 'strength': 0, 'reason': f'Analysis error: {e}'}
    
    def _calculate_z_score(self, data: pd.DataFrame) -> float:
        """
        Calculate Z-score for mean reversion
        """
        if len(data) < self.lookback_period:
            return 0
        
        recent_prices = data['close'].tail(self.lookback_period)
        current_price = recent_prices.iloc[-1]
        
        mean_price = recent_prices.mean()
        std_price = recent_prices.std()
        
        if std_price == 0:
            return 0
        
        z_score = (current_price - mean_price) / std_price
        return z_score
    
    def _calculate_bollinger_position(self, data: pd.DataFrame) -> float:
        """
        Calculate position within Bollinger Bands
        """
        if len(data) < self.bollinger_bands_period:
            return 0.5  # Neutral position
        
        recent_prices = data['close'].tail(self.bollinger_bands_period)
        current_price = recent_prices.iloc[-1]
        
        # Calculate Bollinger Bands
        sma = recent_prices.mean()
        std = recent_prices.std()
        
        upper_band = sma + (std * self.bollinger_bands_std)
        lower_band = sma - (std * self.bollinger_bands_std)
        
        # Calculate position (0 = lower band, 1 = upper band)
        if upper_band != lower_band:
            position = (current_price - lower_band) / (upper_band - lower_band)
        else:
            position = 0.5
        
        return position
    
    def _check_rsi_extreme(self, technical_signals: Dict[str, Any]) -> Dict[str, bool]:
        """
        Check for RSI extreme conditions
        """
        rsi = technical_signals.get('rsi', 50)
        
        return {
            'oversold': rsi < 30,
            'overbought': rsi > 70,
            'extreme_oversold': rsi < 20,
            'extreme_overbought': rsi > 80
        }
    
    def _generate_signal(self, z_score: float, bollinger_position: float, rsi_extreme: Dict[str, bool]) -> tuple:
        """
        Generate trading signal based on mean reversion analysis
        """
        # Strong mean reversion signals
        if z_score > self.z_score_threshold or bollinger_position > 0.8 or rsi_extreme['extreme_overbought']:
            return 'SELL', min(abs(z_score) * 25, 100)
        
        elif z_score < -self.z_score_threshold or bollinger_position < 0.2 or rsi_extreme['extreme_oversold']:
            return 'BUY', min(abs(z_score) * 25, 100)
        
        # Moderate mean reversion signals
        elif abs(z_score) > self.z_score_threshold / 2:
            if z_score > 0:
                return 'SELL', abs(z_score) * 15
            else:
                return 'BUY', abs(z_score) * 15
        
        # Bollinger Band extremes
        elif bollinger_position > 0.7:
            return 'SELL', (bollinger_position - 0.5) * 100
        elif bollinger_position < 0.3:
            return 'BUY', (0.5 - bollinger_position) * 100
        
        # RSI extremes
        elif rsi_extreme['overbought']:
            return 'SELL', 60
        elif rsi_extreme['oversold']:
            return 'BUY', 60
        
        # No clear mean reversion signal
        else:
            return 'HOLD', 0
    
    def _get_signal_reason(self, signal: str, z_score: float, bollinger_position: float) -> str:
        """
        Generate human-readable reason for the signal
        """
        if signal == 'BUY':
            if z_score < -self.z_score_threshold:
                return f"Strong oversold condition (Z-score: {z_score:.2f})"
            elif bollinger_position < 0.3:
                return f"Price near lower Bollinger Band (position: {bollinger_position:.2f})"
            else:
                return "Multiple oversold indicators detected"
        
        elif signal == 'SELL':
            if z_score > self.z_score_threshold:
                return f"Strong overbought condition (Z-score: {z_score:.2f})"
            elif bollinger_position > 0.7:
                return f"Price near upper Bollinger Band (position: {bollinger_position:.2f})"
            else:
                return "Multiple overbought indicators detected"
        
        else:
            return "Price within normal range, no mean reversion opportunity"
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """
        Get strategy information and parameters
        """
        return {
            'name': self.name,
            'lookback_period': self.lookback_period,
            'z_score_threshold': self.z_score_threshold,
            'bollinger_bands_period': self.bollinger_bands_period,
            'bollinger_bands_std': self.bollinger_bands_std,
            'description': 'Mean reversion strategy that identifies overbought/oversold conditions'
        }
