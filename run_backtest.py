"""
Backtest runner for CryptoAlpha AI Portfolio Manager
"""
import asyncio
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
import matplotlib.pyplot as plt

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.crypto_alpha_agent import CryptoAlphaAgent
from config import config
from data.sample_data import create_backtest_scenario, generate_sample_crypto_data

class BacktestRunner:
    """
    Runs backtests for the CryptoAlpha agent
    """
    
    def __init__(self):
        self.config = config['development']()
        self.agent = CryptoAlphaAgent(self.config.__dict__)
        self.results = []
        
    def run_scenario_backtest(self, scenario_name: str = "trend_reversal"):
        """
        Run backtest with predefined scenario
        """
        print(f"Running backtest: {scenario_name}")
        
        if scenario_name == "trend_reversal":
            market_data = create_backtest_scenario()['BTC/USD']
        else:
            # Generate random data
            market_data = generate_sample_crypto_data("BTC/USD", days=30)
        
        return self._run_backtest(market_data, scenario_name)
    
    def run_historical_backtest(self, days: int = 30):
        """
        Run backtest with generated historical data
        """
        print(f"Running historical backtest for {days} days")
        
        market_data = generate_sample_crypto_data("BTC/USD", days=days)
        return self._run_backtest(market_data, "historical")
    
    def _run_backtest(self, market_data: pd.DataFrame, test_name: str):
        """
        Execute the backtest
        """
        print(f"Backtesting with {len(market_data)} data points")
        
        # Initialize tracking
        portfolio_values = []
        trade_history = []
        initial_value = self.config.INITIAL_PORTFOLIO_VALUE
        
        # Process data in chunks (simulating real-time trading)
        chunk_size = 24  # Process 24 hours at a time
        
        for i in range(0, len(market_data), chunk_size):
            chunk = market_data.iloc[i:i+chunk_size]
            
            if len(chunk) < 10:  # Need minimum data for analysis
                continue
            
            # Analyze market
            analysis = self.agent.analyze_market(chunk)
            
            # Make trading decision
            trade_decision = self.agent.make_trading_decision(analysis)
            
            if trade_decision:
                # Simulate trade execution
                success = self._simulate_trade_execution(trade_decision, chunk.iloc[-1])
                
                if success:
                    trade_history.append({
                        'timestamp': chunk.index[-1],
                        'decision': trade_decision,
                        'analysis': analysis
                    })
            
            # Track portfolio value
            current_value = self._calculate_portfolio_value(chunk.iloc[-1])
            portfolio_values.append({
                'timestamp': chunk.index[-1],
                'value': current_value,
                'price': chunk.iloc[-1]['close']
            })
        
        # Calculate performance metrics
        metrics = self._calculate_performance_metrics(portfolio_values, trade_history)
        
        # Store results
        result = {
            'test_name': test_name,
            'initial_value': initial_value,
            'final_value': portfolio_values[-1]['value'] if portfolio_values else initial_value,
            'portfolio_values': portfolio_values,
            'trade_history': trade_history,
            'metrics': metrics
        }
        
        self.results.append(result)
        
        # Print results
        self._print_results(result)
        
        return result
    
    def _simulate_trade_execution(self, trade_decision: dict, market_data: pd.Series) -> bool:
        """
        Simulate trade execution
        """
        try:
            # Update agent's portfolio (simplified)
            symbol = trade_decision['symbol']
            action = trade_decision['action']
            quantity = trade_decision['quantity']
            price = market_data['close']
            
            # Simulate position update
            if action == 'BUY':
                current_position = self.agent.portfolio.get(symbol, 0)
                self.agent.portfolio[symbol] = current_position + quantity
            elif action == 'SELL':
                current_position = self.agent.portfolio.get(symbol, 0)
                self.agent.portfolio[symbol] = max(0, current_position - quantity)
            
            # Add to trade history
            self.agent.trade_history.append({
                'timestamp': market_data.name,
                'action': action,
                'symbol': symbol,
                'quantity': quantity,
                'price': price,
                'portfolio_changes': self.agent.portfolio.copy()
            })
            
            return True
            
        except Exception as e:
            print(f"Trade execution failed: {e}")
            return False
    
    def _calculate_portfolio_value(self, market_data: pd.Series) -> float:
        """
        Calculate current portfolio value
        """
        cash_value = 10000  # Base cash value
        position_value = 0
        
        # Calculate position values
        for symbol, quantity in self.agent.portfolio.items():
            if symbol == 'BTC/USD':
                position_value += quantity * market_data['close']
        
        return cash_value + position_value
    
    def _calculate_performance_metrics(self, portfolio_values: list, trade_history: list) -> dict:
        """
        Calculate performance metrics
        """
        if not portfolio_values:
            return {}
        
        initial_value = portfolio_values[0]['value']
        final_value = portfolio_values[-1]['value']
        
        # Calculate returns
        total_return = (final_value - initial_value) / initial_value
        
        # Calculate daily returns
        daily_returns = []
        for i in range(1, len(portfolio_values)):
            prev_value = portfolio_values[i-1]['value']
            curr_value = portfolio_values[i]['value']
            daily_return = (curr_value - prev_value) / prev_value
            daily_returns.append(daily_return)
        
        # Calculate Sharpe ratio (simplified)
        if daily_returns:
            avg_return = sum(daily_returns) / len(daily_returns)
            volatility = (sum((r - avg_return)**2 for r in daily_returns) / len(daily_returns))**0.5
            sharpe_ratio = avg_return / volatility if volatility > 0 else 0
        else:
            sharpe_ratio = 0
        
        # Calculate maximum drawdown
        peak = initial_value
        max_drawdown = 0
        for pv in portfolio_values:
            if pv['value'] > peak:
                peak = pv['value']
            drawdown = (peak - pv['value']) / peak
            max_drawdown = max(max_drawdown, drawdown)
        
        return {
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown * 100,
            'total_trades': len(trade_history),
            'win_rate': self._calculate_win_rate(trade_history),
            'final_value': final_value
        }
    
    def _calculate_win_rate(self, trade_history: list) -> float:
        """
        Calculate win rate (simplified)
        """
        if not trade_history:
            return 0
        
        # Simple win rate calculation based on profitable trades
        # This is a simplified version - in reality, you'd track P&L per trade
        return 0.6  # Placeholder - would need actual P&L tracking
    
    def _print_results(self, result: dict):
        """
        Print backtest results
        """
        print(f"\n{'='*50}")
        print(f"BACKTEST RESULTS: {result['test_name'].upper()}")
        print(f"{'='*50}")
        
        metrics = result['metrics']
        print(f"Initial Value:    ${result['initial_value']:,.2f}")
        print(f"Final Value:      ${metrics['final_value']:,.2f}")
        print(f"Total Return:     {metrics['total_return_pct']:.2f}%")
        print(f"Sharpe Ratio:     {metrics['sharpe_ratio']:.3f}")
        print(f"Max Drawdown:     {metrics['max_drawdown_pct']:.2f}%")
        print(f"Total Trades:     {metrics['total_trades']}")
        print(f"Win Rate:         {metrics['win_rate']:.1%}")
        
        print(f"\nTrade Summary:")
        for trade in result['trade_history'][-5:]:  # Show last 5 trades
            print(f"  {trade['timestamp'].strftime('%Y-%m-%d %H:%M')}: {trade['action']} {trade['symbol']}")
    
    def plot_results(self, result: dict):
        """
        Plot backtest results
        """
        if not result['portfolio_values']:
            print("No data to plot")
            return
        
        # Create plots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Portfolio value over time
        timestamps = [pv['timestamp'] for pv in result['portfolio_values']]
        values = [pv['value'] for pv in result['portfolio_values']]
        prices = [pv['price'] for pv in result['portfolio_values']]
        
        ax1.plot(timestamps, values, label='Portfolio Value', linewidth=2)
        ax1.set_title(f'Portfolio Performance - {result["test_name"]}')
        ax1.set_ylabel('Portfolio Value ($)')
        ax1.legend()
        ax1.grid(True)
        
        # Price chart with trade markers
        ax2.plot(timestamps, prices, label='BTC Price', alpha=0.7)
        
        # Mark trades
        for trade in result['trade_history']:
            trade_time = trade['timestamp']
            trade_price = trade['decision']['symbol']  # This would need actual price
            action = trade['decision']['action']
            
            color = 'green' if action == 'BUY' else 'red'
            marker = '^' if action == 'BUY' else 'v'
            ax2.scatter(trade_time, trade_price, color=color, marker=marker, s=100, alpha=0.8)
        
        ax2.set_title('BTC Price with Trade Signals')
        ax2.set_ylabel('Price ($)')
        ax2.set_xlabel('Time')
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        plt.show()

def main():
    """
    Main function to run backtests
    """
    runner = BacktestRunner()
    
    # Run different backtest scenarios
    scenarios = [
        ("trend_reversal", "Trend Reversal Scenario"),
        ("historical", "30-Day Historical Data"),
    ]
    
    for scenario, description in scenarios:
        print(f"\n{description}")
        print("-" * 40)
        
        if scenario == "trend_reversal":
            result = runner.run_scenario_backtest("trend_reversal")
        else:
            result = runner.run_historical_backtest(30)
        
        # Optionally plot results
        # runner.plot_results(result)
    
    print(f"\nCompleted {len(runner.results)} backtests")

if __name__ == "__main__":
    main()
