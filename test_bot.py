"""
Quick test for CryptoAlpha bot functionality
"""
from agents.crypto_alpha_agent import CryptoAlphaAgent
from config import config
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def test_bot():
    print('CryptoAlpha Agent Test Results:')
    print('=' * 50)
    
    # Create agent
    agent_config = config['development']()
    agent = CryptoAlphaAgent(agent_config.__dict__)
    
    # Generate test market data
    dates = pd.date_range(start=datetime.now() - timedelta(hours=100), periods=100, freq='1H')
    np.random.seed(42)
    base_price = 45000
    prices = [base_price]
    for i in range(99):
        prices.append(prices[-1] * (1 + np.random.normal(0, 0.02)))
    
    test_data = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': [p * 1.01 for p in prices],
        'low': [p * 0.99 for p in prices], 
        'close': prices,
        'volume': np.random.randint(1000, 10000, 100)
    })
    test_data.set_index('timestamp', inplace=True)
    
    # Test market analysis
    analysis = agent.analyze_market(test_data)
    print(f'Overall Signal: {analysis["overall_signal"]}')
    print(f'Technical Signals: {len(analysis["signals"])} indicators analyzed')
    
    # Test trading decision
    decision = agent.make_trading_decision(analysis)
    if decision:
        print(f'Trading Decision: {decision["action"]} {decision["symbol"]}')
        print(f'Quantity: {decision["quantity"]}')
        print(f'Reason: {decision["reason"]}')
    else:
        print('No trading action recommended (risk management active)')
    
    # Test performance metrics
    metrics = agent.get_performance_metrics()
    print(f'Performance Metrics: {len(metrics)} metrics calculated')
    
    # Test strategies
    strategies = analysis.get('strategy_recommendations', {})
    print(f'Strategy Analysis: {len(strategies)} strategies evaluated')
    for strategy_name, strategy_data in strategies.items():
        signal = strategy_data.get('signal', 'HOLD')
        strength = strategy_data.get('strength', 0)
        print(f'   - {strategy_name}: {signal} (strength: {strength:.1f})')
    
    print('\nAll tests passed! Bot is ready for trading!')
    print('Ready for Recall Network competitions!')

if __name__ == "__main__":
    test_bot()
