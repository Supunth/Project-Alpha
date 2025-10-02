"""
Tests for CryptoAlpha trading agent
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.crypto_alpha_agent import CryptoAlphaAgent
from config import config

class TestCryptoAlphaAgent:
    """Test cases for CryptoAlpha agent"""
    
    @pytest.fixture
    def sample_config(self):
        """Sample configuration for testing"""
        return {
            'max_position_size': 0.1,
            'risk_tolerance': 0.02,
            'stop_loss_percentage': 0.05,
            'take_profit_percentage': 0.15,
            'initial_value': 10000
        }
    
    @pytest.fixture
    def sample_market_data(self):
        """Sample market data for testing"""
        dates = pd.date_range(start='2023-01-01', periods=100, freq='1H')
        
        # Generate realistic price data
        np.random.seed(42)
        base_price = 100
        returns = np.random.normal(0, 0.02, 100)
        prices = [base_price]
        
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        data = pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'close': prices,
            'volume': np.random.randint(1000, 10000, 100)
        })
        
        data.set_index('timestamp', inplace=True)
        return data
    
    @pytest.fixture
    def agent(self, sample_config):
        """Create agent instance for testing"""
        return CryptoAlphaAgent(sample_config)
    
    def test_agent_initialization(self, agent):
        """Test agent initialization"""
        assert agent.agent_name == "CryptoAlpha"
        assert agent.config['max_position_size'] == 0.1
        assert agent.portfolio == {}
        assert agent.trade_history == []
    
    def test_market_analysis(self, agent, sample_market_data):
        """Test market analysis functionality"""
        analysis = agent.analyze_market(sample_market_data)
        
        assert isinstance(analysis, dict)
        assert 'timestamp' in analysis
        assert 'signals' in analysis
        assert 'predictions' in analysis
        assert 'risk_assessment' in analysis
        assert 'overall_signal' in analysis
    
    def test_trading_decision(self, agent, sample_market_data):
        """Test trading decision making"""
        analysis = agent.analyze_market(sample_market_data)
        trade_decision = agent.make_trading_decision(analysis)
        
        if trade_decision:
            assert 'action' in trade_decision
            assert 'symbol' in trade_decision
            assert 'quantity' in trade_decision
            assert trade_decision['action'] in ['BUY', 'SELL']
    
    def test_portfolio_management(self, agent):
        """Test portfolio management"""
        initial_value = agent.get_portfolio_value()
        
        # Simulate trade result
        trade_result = {
            'portfolio_changes': {'BTC/USD': 0.1},
            'pnl': 100
        }
        
        agent.update_portfolio(trade_result)
        
        # Check portfolio was updated
        assert 'BTC/USD' in agent.portfolio
        
        # Check performance metrics
        metrics = agent.get_performance_metrics()
        assert 'total_trades' in metrics
        assert 'portfolio_value' in metrics
    
    def test_risk_management_integration(self, agent, sample_market_data):
        """Test risk management integration"""
        analysis = agent.analyze_market(sample_market_data)
        
        # Check risk assessment is included
        assert 'risk_assessment' in analysis
        risk_metrics = analysis['risk_assessment']
        assert 'overall_risk' in risk_metrics
        assert 'risk_score' in risk_metrics
    
    def test_signal_generation(self, agent, sample_market_data):
        """Test signal generation logic"""
        analysis = agent.analyze_market(sample_market_data)
        
        # Test overall signal generation
        overall_signal = analysis.get('overall_signal')
        assert overall_signal in ['BUY', 'SELL', 'HOLD', 'STRONG_BUY', 'STRONG_SELL']
        
        # Test strategy recommendations
        strategy_recs = analysis.get('strategy_recommendations', {})
        assert isinstance(strategy_recs, dict)
    
    def test_error_handling(self, agent):
        """Test error handling with invalid data"""
        # Test with empty data
        empty_data = pd.DataFrame()
        analysis = agent.analyze_market(empty_data)
        
        # Should handle gracefully
        assert isinstance(analysis, dict)
        
        # Test with insufficient data
        insufficient_data = pd.DataFrame({
            'close': [100, 101],
            'volume': [1000, 1100]
        })
        
        analysis = agent.analyze_market(insufficient_data)
        assert isinstance(analysis, dict)

if __name__ == "__main__":
    pytest.main([__file__])
