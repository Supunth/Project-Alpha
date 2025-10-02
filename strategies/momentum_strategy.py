"""
Momentum trading strategy for CryptoAlpha
"""
import pandas as pd
import numpy as np
from typing import Dict, Any
import logging

class MomentumStrategy:
    """
    Momentum-based trading strategy
    """
    
    def __init__(self):
        self.name = "Momentum Strategy"
        self.logger = logging.getLogger(__name__)
        
        # Strategy parameters
        self.lookback_period = 20
        self.momentum_threshold = 0.02  # 2% momentum threshold
        self.volume_threshold = 1.5     # 1.5x average volume
    
    def analyze(self, market_data: pd.DataFrame, technical_signals: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market data using momentum strategy
        """
        if market_data.empty or len(market_data) < self.lookback_period:
            return {'signal': 'HOLD', 'strength': 0, 'reason': 'Insufficient data'}
        
        try:
            # Calculate momentum indicators
            momentum_score = self._calculate_momentum_score(market_data)
            volume_confirmation = self._check_volume_confirmation(market_data)
            trend_strength = self._calculate_trend_strength(market_data)
            
            # Generate signal
            signal, strength = self._generate_signal(
                momentum_score, volume_confirmation, trend_strength
            )
            
            return {
                'signal': signal,
                'strength': strength,
                'momentum_score': momentum_score,
                'volume_confirmation': volume_confirmation,
                'trend_strength': trend_strength,
                'reason': self._get_signal_reason(signal, momentum_score, trend_strength)
            }
            
        except Exception as e:
            self.logger.error(f"Error in momentum strategy analysis: {e}")
            return {'signal': 'HOLD', 'strength': 0, 'reason': f'Analysis error: {e}'}
    
    def _calculate_momentum_score(self, data: pd.DataFrame) -> float:
        """
        Calculate overall momentum score
        """
        current_price = data['close'].iloc[-1]
        
        # Price momentum over different periods
        momentum_scores = []
        
        periods = [5, 10, self.lookback_period]
        for period in periods:
            if len(data) >= period:
                past_price = data['close'].iloc[-period-1]
                momentum = (current_price - past_price) / past_price
                momentum_scores.append(momentum)
        
        # Weighted average momentum (more recent periods have higher weight)
        weights = [0.5, 0.3, 0.2]
        weighted_momentum = sum(score * weight for score, weight in zip(momentum_scores, weights))
        
        return weighted_momentum
    
    def _check_volume_confirmation(self, data: pd.DataFrame) -> bool:
        """
        Check if volume confirms momentum
        """
        if 'volume' not in data.columns:
            return True  # Assume confirmation if no volume data
        
        current_volume = data['volume'].iloc[-1]
        avg_volume = data['volume'].rolling(window=self.lookback_period).mean().iloc[-1]
        
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        return volume_ratio >= self.volume_threshold
    
    def _calculate_trend_strength(self, data: pd.DataFrame) -> float:
        """
        Calculate trend strength using linear regression
        """
        if len(data) < self.lookback_period:
            return 0
        
        # Use recent data for trend calculation
        recent_data = data['close'].tail(self.lookback_period)
        
        # Simple linear regression slope
        x = np.arange(len(recent_data))
        y = recent_data.values
        
        # Calculate slope
        n = len(x)
        slope = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x**2) - np.sum(x)**2)
        
        # Normalize slope to percentage
        trend_strength = slope / recent_data.iloc[0] * 100
        
        return trend_strength
    
    def _generate_signal(self, momentum_score: float, volume_confirmation: bool, trend_strength: float) -> tuple:
        """
        Generate trading signal based on momentum analysis
        """
        # Strong momentum with volume confirmation
        if momentum_score > self.momentum_threshold and volume_confirmation and trend_strength > 1:
            return 'BUY', min(abs(momentum_score) * 100, 100)
        
        # Strong negative momentum with volume confirmation
        elif momentum_score < -self.momentum_threshold and volume_confirmation and trend_strength < -1:
            return 'SELL', min(abs(momentum_score) * 100, 100)
        
        # Moderate momentum
        elif abs(momentum_score) > self.momentum_threshold / 2:
            if momentum_score > 0:
                return 'BUY', abs(momentum_score) * 50
            else:
                return 'SELL', abs(momentum_score) * 50
        
        # No clear momentum
        else:
            return 'HOLD', 0
    
    def _get_signal_reason(self, signal: str, momentum_score: float, trend_strength: float) -> str:
        """
        Generate human-readable reason for the signal
        """
        if signal == 'BUY':
            return f"Strong upward momentum ({momentum_score:.2%}) with positive trend ({trend_strength:.2f}%)"
        elif signal == 'SELL':
            return f"Strong downward momentum ({momentum_score:.2%}) with negative trend ({trend_strength:.2f}%)"
        else:
            return "Insufficient momentum or conflicting signals"
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """
        Get strategy information and parameters
        """
        return {
            'name': self.name,
            'lookback_period': self.lookback_period,
            'momentum_threshold': self.momentum_threshold,
            'volume_threshold': self.volume_threshold,
            'description': 'Momentum-based strategy that identifies and follows price trends'
        }
