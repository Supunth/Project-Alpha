"""
Breakout trading strategy for CryptoAlpha
"""
import pandas as pd
import numpy as np
from typing import Dict, Any
import logging

class BreakoutStrategy:
    """
    Breakout trading strategy
    """
    
    def __init__(self):
        self.name = "Breakout Strategy"
        self.logger = logging.getLogger(__name__)
        
        # Strategy parameters
        self.lookback_period = 20
        self.breakout_threshold = 0.02  # 2% breakout threshold
        self.volume_confirmation_threshold = 1.5  # 1.5x average volume
        self.resistance_levels = []
        self.support_levels = []
    
    def analyze(self, market_data: pd.DataFrame, technical_signals: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market data using breakout strategy
        """
        if market_data.empty or len(market_data) < self.lookback_period:
            return {'signal': 'HOLD', 'strength': 0, 'reason': 'Insufficient data'}
        
        try:
            # Identify support and resistance levels
            self._identify_levels(market_data)
            
            # Check for breakouts
            breakout_info = self._check_breakouts(market_data)
            
            # Volume confirmation
            volume_confirmation = self._check_volume_confirmation(market_data)
            
            # Generate signal
            signal, strength = self._generate_signal(breakout_info, volume_confirmation)
            
            return {
                'signal': signal,
                'strength': strength,
                'breakout_info': breakout_info,
                'volume_confirmation': volume_confirmation,
                'support_levels': self.support_levels[-5:],  # Last 5 levels
                'resistance_levels': self.resistance_levels[-5:],  # Last 5 levels
                'reason': self._get_signal_reason(signal, breakout_info)
            }
            
        except Exception as e:
            self.logger.error(f"Error in breakout strategy analysis: {e}")
            return {'signal': 'HOLD', 'strength': 0, 'reason': f'Analysis error: {e}'}
    
    def _identify_levels(self, data: pd.DataFrame) -> None:
        """
        Identify support and resistance levels
        """
        if len(data) < self.lookback_period:
            return
        
        # Find local highs and lows
        highs = data['high'].rolling(window=5, center=True).max()
        lows = data['low'].rolling(window=5, center=True).min()
        
        # Identify resistance levels (local highs)
        for i in range(2, len(highs) - 2):
            if (highs.iloc[i] == data['high'].iloc[i] and 
                highs.iloc[i] > highs.iloc[i-1] and 
                highs.iloc[i] > highs.iloc[i+1]):
                
                level = highs.iloc[i]
                if level not in self.resistance_levels:
                    self.resistance_levels.append(level)
        
        # Identify support levels (local lows)
        for i in range(2, len(lows) - 2):
            if (lows.iloc[i] == data['low'].iloc[i] and 
                lows.iloc[i] < lows.iloc[i-1] and 
                lows.iloc[i] < lows.iloc[i+1]):
                
                level = lows.iloc[i]
                if level not in self.support_levels:
                    self.support_levels.append(level)
        
        # Keep only recent levels
        self.resistance_levels = self.resistance_levels[-10:]
        self.support_levels = self.support_levels[-10:]
    
    def _check_breakouts(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Check for breakout conditions
        """
        current_price = data['close'].iloc[-1]
        current_high = data['high'].iloc[-1]
        current_low = data['low'].iloc[-1]
        
        breakout_info = {
            'resistance_breakout': False,
            'support_breakout': False,
            'breakout_strength': 0,
            'nearest_resistance': None,
            'nearest_support': None
        }
        
        # Check resistance breakouts
        for resistance in self.resistance_levels:
            if current_high > resistance * (1 + self.breakout_threshold):
                breakout_info['resistance_breakout'] = True
                breakout_info['breakout_strength'] = (current_high - resistance) / resistance
                break
        
        # Check support breakouts (downward)
        for support in self.support_levels:
            if current_low < support * (1 - self.breakout_threshold):
                breakout_info['support_breakout'] = True
                breakout_info['breakout_strength'] = (support - current_low) / support
                break
        
        # Find nearest levels
        if self.resistance_levels:
            breakout_info['nearest_resistance'] = min(self.resistance_levels, 
                                                    key=lambda x: abs(x - current_price))
        
        if self.support_levels:
            breakout_info['nearest_support'] = min(self.support_levels, 
                                                 key=lambda x: abs(x - current_price))
        
        return breakout_info
    
    def _check_volume_confirmation(self, data: pd.DataFrame) -> bool:
        """
        Check if volume confirms the breakout
        """
        if 'volume' not in data.columns:
            return True  # Assume confirmation if no volume data
        
        current_volume = data['volume'].iloc[-1]
        avg_volume = data['volume'].rolling(window=self.lookback_period).mean().iloc[-1]
        
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        return volume_ratio >= self.volume_confirmation_threshold
    
    def _generate_signal(self, breakout_info: Dict[str, Any], volume_confirmation: bool) -> tuple:
        """
        Generate trading signal based on breakout analysis
        """
        # Strong resistance breakout with volume confirmation
        if (breakout_info['resistance_breakout'] and 
            volume_confirmation and 
            breakout_info['breakout_strength'] > self.breakout_threshold):
            return 'BUY', min(breakout_info['breakout_strength'] * 100, 100)
        
        # Strong support breakout with volume confirmation
        elif (breakout_info['support_breakout'] and 
              volume_confirmation and 
              breakout_info['breakout_strength'] > self.breakout_threshold):
            return 'SELL', min(breakout_info['breakout_strength'] * 100, 100)
        
        # Moderate breakouts
        elif breakout_info['resistance_breakout'] and breakout_info['breakout_strength'] > 0.01:
            return 'BUY', breakout_info['breakout_strength'] * 50
        elif breakout_info['support_breakout'] and breakout_info['breakout_strength'] > 0.01:
            return 'SELL', breakout_info['breakout_strength'] * 50
        
        # No clear breakout
        else:
            return 'HOLD', 0
    
    def _get_signal_reason(self, signal: str, breakout_info: Dict[str, Any]) -> str:
        """
        Generate human-readable reason for the signal
        """
        if signal == 'BUY':
            strength = breakout_info['breakout_strength']
            return f"Resistance breakout detected (strength: {strength:.2%})"
        elif signal == 'SELL':
            strength = breakout_info['breakout_strength']
            return f"Support breakout detected (strength: {strength:.2%})"
        else:
            return "No significant breakouts detected"
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """
        Get strategy information and parameters
        """
        return {
            'name': self.name,
            'lookback_period': self.lookback_period,
            'breakout_threshold': self.breakout_threshold,
            'volume_confirmation_threshold': self.volume_confirmation_threshold,
            'description': 'Breakout strategy that identifies and trades price breakouts from support/resistance levels'
        }
