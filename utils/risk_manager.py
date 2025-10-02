"""
Risk management module for CryptoAlpha trading agent
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class RiskManager:
    """
    Advanced risk management system
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_position_size = config.get('max_position_size', 0.1)
        self.risk_tolerance = config.get('risk_tolerance', 0.02)
        self.stop_loss_percentage = config.get('stop_loss_percentage', 0.05)
        self.max_daily_loss = config.get('max_daily_loss', 0.03)
        
        # Risk tracking
        self.daily_pnl = 0.0
        self.last_reset_date = datetime.now().date()
        self.position_history = []
        self.drawdown_history = []
    
    def assess_risk(self, market_data: pd.DataFrame, active_positions: Dict[str, float]) -> Dict[str, Any]:
        """
        Comprehensive risk assessment
        """
        risk_metrics = {
            'timestamp': datetime.now(),
            'market_risk': self._assess_market_risk(market_data),
            'position_risk': self._assess_position_risk(active_positions),
            'portfolio_risk': self._assess_portfolio_risk(active_positions),
            'liquidity_risk': self._assess_liquidity_risk(market_data),
            'overall_risk': 0.0,
            'risk_score': 0.0
        }
        
        # Calculate overall risk score
        risk_metrics['overall_risk'] = self._calculate_overall_risk(risk_metrics)
        risk_metrics['risk_score'] = min(risk_metrics['overall_risk'], 1.0)
        
        return risk_metrics
    
    def can_trade(self, risk_metrics: Dict[str, Any]) -> bool:
        """
        Determine if trading is allowed based on risk assessment
        """
        # Check daily loss limit
        if self.daily_pnl <= -self.max_daily_loss:
            return False
        
        # Check overall risk score
        if risk_metrics.get('risk_score', 0) > 0.8:
            return False
        
        # Check market volatility
        market_risk = risk_metrics.get('market_risk', {})
        if market_risk.get('volatility', 0) > 0.1:  # 10% volatility threshold
            return False
        
        return True
    
    def calculate_position_size(self, signal_strength: float, risk_metrics: Dict[str, Any]) -> float:
        """
        Calculate optimal position size based on risk
        """
        base_size = self.max_position_size
        
        # Adjust for signal strength
        size_multiplier = min(signal_strength, 1.0)
        
        # Adjust for risk score
        risk_adjustment = 1.0 - risk_metrics.get('risk_score', 0)
        
        # Final position size
        position_size = base_size * size_multiplier * risk_adjustment
        
        return max(0.01, min(position_size, self.max_position_size))
    
    def update_daily_pnl(self, trade_result: Dict[str, Any]) -> None:
        """
        Update daily P&L tracking
        """
        current_date = datetime.now().date()
        
        # Reset if new day
        if current_date != self.last_reset_date:
            self.daily_pnl = 0.0
            self.last_reset_date = current_date
        
        # Update P&L
        if 'pnl' in trade_result:
            self.daily_pnl += trade_result['pnl']
    
    def _assess_market_risk(self, market_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Assess market-wide risk factors
        """
        if market_data.empty:
            return {'volatility': 0, 'trend': 'neutral'}
        
        # Calculate volatility
        returns = market_data['close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)  # Annualized
        
        # Determine trend
        price_change = (market_data['close'].iloc[-1] - market_data['close'].iloc[0]) / market_data['close'].iloc[0]
        
        if price_change > 0.02:
            trend = 'bullish'
        elif price_change < -0.02:
            trend = 'bearish'
        else:
            trend = 'neutral'
        
        return {
            'volatility': volatility,
            'trend': trend,
            'price_change': price_change
        }
    
    def _assess_position_risk(self, active_positions: Dict[str, float]) -> Dict[str, Any]:
        """
        Assess risk from current positions
        """
        if not active_positions:
            return {'concentration_risk': 0, 'total_exposure': 0}
        
        # Calculate concentration risk
        total_exposure = sum(abs(pos) for pos in active_positions.values())
        max_position = max(abs(pos) for pos in active_positions.values()) if active_positions else 0
        concentration_risk = max_position / total_exposure if total_exposure > 0 else 0
        
        return {
            'concentration_risk': concentration_risk,
            'total_exposure': total_exposure,
            'position_count': len(active_positions)
        }
    
    def _assess_portfolio_risk(self, active_positions: Dict[str, float]) -> Dict[str, Any]:
        """
        Assess overall portfolio risk
        """
        # Calculate portfolio value and exposure
        portfolio_value = 10000  # This would come from actual portfolio
        total_exposure = sum(abs(pos) for pos in active_positions.values())
        exposure_ratio = total_exposure / portfolio_value if portfolio_value > 0 else 0
        
        # Check if exposure exceeds limits
        overexposed = exposure_ratio > self.max_position_size * 2
        
        return {
            'exposure_ratio': exposure_ratio,
            'overexposed': overexposed,
            'leverage_ratio': exposure_ratio
        }
    
    def _assess_liquidity_risk(self, market_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Assess liquidity risk
        """
        if 'volume' not in market_data.columns or market_data.empty:
            return {'liquidity_score': 1.0}
        
        # Calculate average volume
        avg_volume = market_data['volume'].mean()
        current_volume = market_data['volume'].iloc[-1]
        
        # Liquidity score based on volume
        liquidity_score = min(current_volume / avg_volume, 2.0) if avg_volume > 0 else 1.0
        
        return {
            'liquidity_score': liquidity_score,
            'volume_ratio': current_volume / avg_volume if avg_volume > 0 else 1.0
        }
    
    def _calculate_overall_risk(self, risk_metrics: Dict[str, Any]) -> float:
        """
        Calculate overall risk score
        """
        market_risk = risk_metrics.get('market_risk', {})
        position_risk = risk_metrics.get('position_risk', {})
        portfolio_risk = risk_metrics.get('portfolio_risk', {})
        liquidity_risk = risk_metrics.get('liquidity_risk', {})
        
        # Weighted risk calculation
        risk_components = [
            market_risk.get('volatility', 0) * 0.3,
            position_risk.get('concentration_risk', 0) * 0.25,
            portfolio_risk.get('exposure_ratio', 0) * 0.25,
            (2.0 - liquidity_risk.get('liquidity_score', 1.0)) * 0.2  # Inverted liquidity score
        ]
        
        return sum(risk_components)
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """
        Get current risk summary
        """
        return {
            'daily_pnl': self.daily_pnl,
            'max_daily_loss': self.max_daily_loss,
            'risk_tolerance': self.risk_tolerance,
            'position_count': len(self.position_history),
            'last_reset_date': self.last_reset_date
        }
