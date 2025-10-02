"""
CryptoAlpha AI Portfolio Manager - Main Trading Agent
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from .base_agent import BaseAgent
from utils.technical_indicators import TechnicalAnalyzer
from utils.risk_manager import RiskManager
from models.price_predictor import PricePredictor
from strategies.momentum_strategy import MomentumStrategy
from strategies.mean_reversion_strategy import MeanReversionStrategy

class CryptoAlphaAgent(BaseAgent):
    """
    Advanced AI trading agent for cryptocurrency markets
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("CryptoAlpha", config)
        
        # Initialize components
        self.technical_analyzer = TechnicalAnalyzer()
        self.risk_manager = RiskManager(config)
        self.price_predictor = PricePredictor()
        
        # Trading strategies
        self.strategies = {
            'momentum': MomentumStrategy(),
            'mean_reversion': MeanReversionStrategy()
        }
        
        # Agent state
        self.current_signals = {}
        self.last_analysis_time = None
        self.active_positions = {}
        
        self.logger.info("CryptoAlpha Agent initialized successfully")
    
    def analyze_market(self, market_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Comprehensive market analysis using multiple approaches
        """
        analysis = {
            'timestamp': datetime.now(),
            'signals': {},
            'predictions': {},
            'risk_assessment': {},
            'strategy_recommendations': {}
        }
        
        try:
            # Technical analysis
            technical_signals = self.technical_analyzer.analyze(market_data)
            analysis['signals'].update(technical_signals)
            
            # Price predictions
            predictions = self.price_predictor.predict(market_data)
            analysis['predictions'].update(predictions)
            
            # Risk assessment
            risk_metrics = self.risk_manager.assess_risk(market_data, self.active_positions)
            analysis['risk_assessment'] = risk_metrics
            
            # Strategy analysis
            for strategy_name, strategy in self.strategies.items():
                strategy_signals = strategy.analyze(market_data, technical_signals)
                analysis['strategy_recommendations'][strategy_name] = strategy_signals
            
            # Generate overall trading signal
            analysis['overall_signal'] = self._generate_overall_signal(analysis)
            
            self.current_signals = analysis
            self.last_analysis_time = datetime.now()
            
            self.logger.info(f"Market analysis completed: {analysis['overall_signal']}")
            
        except Exception as e:
            self.logger.error(f"Error in market analysis: {e}")
            analysis['error'] = str(e)
            
        return analysis
    
    def make_trading_decision(self, analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Make intelligent trading decision based on comprehensive analysis
        """
        if 'error' in analysis:
            self.logger.warning("Skipping trade decision due to analysis error")
            return None
        
        overall_signal = analysis.get('overall_signal', 'HOLD')
        risk_metrics = analysis.get('risk_assessment', {})
        
        # Check risk limits
        if not self.risk_manager.can_trade(risk_metrics):
            self.logger.info("Trade blocked by risk management")
            return None
        
        # Determine action based on signal strength
        trade_decision = None
        
        if overall_signal == 'STRONG_BUY':
            trade_decision = self._create_buy_decision(analysis, size='large')
        elif overall_signal == 'BUY':
            trade_decision = self._create_buy_decision(analysis, size='medium')
        elif overall_signal == 'STRONG_SELL':
            trade_decision = self._create_sell_decision(analysis, size='large')
        elif overall_signal == 'SELL':
            trade_decision = self._create_sell_decision(analysis, size='medium')
        
        if trade_decision:
            # Add risk management parameters
            trade_decision.update({
                'stop_loss': self._calculate_stop_loss(analysis),
                'take_profit': self._calculate_take_profit(analysis),
                'risk_score': risk_metrics.get('overall_risk', 0.5)
            })
            
            self.logger.info(f"Trading decision made: {trade_decision}")
        
        return trade_decision
    
    def execute_trade(self, trade_decision: Dict[str, Any]) -> bool:
        """
        Execute the trading decision
        """
        try:
            # This would integrate with Recall Network API
            # For now, we'll simulate the trade execution
            
            symbol = trade_decision['symbol']
            action = trade_decision['action']
            quantity = trade_decision['quantity']
            
            # Simulate trade execution
            trade_result = {
                'timestamp': datetime.now(),
                'symbol': symbol,
                'action': action,
                'quantity': quantity,
                'price': trade_decision.get('price', 0),
                'status': 'executed',
                'portfolio_changes': self._calculate_portfolio_changes(trade_decision)
            }
            
            # Update active positions
            self._update_active_positions(trade_decision)
            
            # Update portfolio
            self.update_portfolio(trade_result)
            
            self.logger.info(f"Trade executed successfully: {trade_result}")
            return True
            
        except Exception as e:
            self.logger.error(f"Trade execution failed: {e}")
            return False
    
    def _generate_overall_signal(self, analysis: Dict[str, Any]) -> str:
        """
        Generate overall trading signal from multiple indicators
        """
        signals = []
        weights = []
        
        # Technical signals
        technical_signals = analysis.get('signals', {})
        if 'rsi_signal' in technical_signals:
            signals.append(technical_signals['rsi_signal'])
            weights.append(0.3)
        
        if 'macd_signal' in technical_signals:
            signals.append(technical_signals['macd_signal'])
            weights.append(0.3)
        
        # Strategy signals
        strategy_recs = analysis.get('strategy_recommendations', {})
        for strategy_name, strategy_data in strategy_recs.items():
            if 'signal' in strategy_data:
                signals.append(strategy_data['signal'])
                weights.append(0.2)
        
        # Simple voting mechanism
        if not signals:
            return 'HOLD'
        
        # Weighted signal calculation
        signal_values = {'BUY': 1, 'SELL': -1, 'HOLD': 0}
        weighted_sum = sum(signal_values.get(signal, 0) * weight for signal, weight in zip(signals, weights))
        
        if weighted_sum > 0.5:
            return 'STRONG_BUY' if weighted_sum > 0.8 else 'BUY'
        elif weighted_sum < -0.5:
            return 'STRONG_SELL' if weighted_sum < -0.8 else 'SELL'
        else:
            return 'HOLD'
    
    def _create_buy_decision(self, analysis: Dict[str, Any], size: str = 'medium') -> Dict[str, Any]:
        """Create buy trading decision"""
        size_multipliers = {'small': 0.25, 'medium': 0.5, 'large': 0.75}
        base_quantity = self.config.get('max_position_size', 0.1) * size_multipliers.get(size, 0.5)
        
        return {
            'action': 'BUY',
            'symbol': 'BTC/USD',  # Would be determined from analysis
            'quantity': base_quantity,
            'reason': 'Strong buy signal from multiple indicators',
            'confidence': analysis.get('predictions', {}).get('confidence', 0.5)
        }
    
    def _create_sell_decision(self, analysis: Dict[str, Any], size: str = 'medium') -> Dict[str, Any]:
        """Create sell trading decision"""
        size_multipliers = {'small': 0.25, 'medium': 0.5, 'large': 0.75}
        
        return {
            'action': 'SELL',
            'symbol': 'BTC/USD',  # Would be determined from analysis
            'quantity': size_multipliers.get(size, 0.5),
            'reason': 'Strong sell signal from multiple indicators',
            'confidence': analysis.get('predictions', {}).get('confidence', 0.5)
        }
    
    def _calculate_stop_loss(self, analysis: Dict[str, Any]) -> float:
        """Calculate stop loss price"""
        current_price = analysis.get('predictions', {}).get('current_price', 100)
        return current_price * (1 - self.config.get('stop_loss_percentage', 0.05))
    
    def _calculate_take_profit(self, analysis: Dict[str, Any]) -> float:
        """Calculate take profit price"""
        current_price = analysis.get('predictions', {}).get('current_price', 100)
        return current_price * (1 + self.config.get('take_profit_percentage', 0.15))
    
    def _calculate_portfolio_changes(self, trade_decision: Dict[str, Any]) -> Dict[str, float]:
        """Calculate portfolio changes from trade"""
        # Simplified portfolio update logic
        return {trade_decision['symbol']: trade_decision['quantity']}
    
    def _update_active_positions(self, trade_decision: Dict[str, Any]) -> None:
        """Update active positions tracking"""
        symbol = trade_decision['symbol']
        action = trade_decision['action']
        quantity = trade_decision['quantity']
        
        if action == 'BUY':
            self.active_positions[symbol] = self.active_positions.get(symbol, 0) + quantity
        elif action == 'SELL':
            self.active_positions[symbol] = self.active_positions.get(symbol, 0) - quantity
