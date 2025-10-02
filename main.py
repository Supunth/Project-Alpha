"""
CryptoAlpha AI Portfolio Manager - Main Entry Point
"""
import asyncio
import logging
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
from agents.crypto_alpha_agent import CryptoAlphaAgent
from utils.data_fetcher import MarketDataFetcher
from utils.recall_client import RecallNetworkClient

class CryptoAlphaRunner:
    """
    Main runner for the CryptoAlpha trading agent
    """
    
    def __init__(self):
        self.config = config['development']()
        self.agent = CryptoAlphaAgent(self.config.__dict__)
        self.data_fetcher = MarketDataFetcher()
        self.recall_client = RecallNetworkClient(self.config.RECALL_API_KEY)
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, self.config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    async def run_competition(self):
        """
        Run the agent in a Recall Network competition
        """
        self.logger.info("Starting CryptoAlpha in Recall Network competition...")
        
        try:
            # Initialize competition connection
            await self.recall_client.connect()
            
            # Main trading loop
            while True:
                try:
                    # Fetch market data
                    market_data = await self.data_fetcher.fetch_latest_data(
                        symbols=self.config.DEFAULT_TRADING_PAIRS
                    )
                    
                    if market_data is not None and not market_data.empty:
                        # Analyze market
                        analysis = self.agent.analyze_market(market_data)
                        
                        # Make trading decision
                        trade_decision = self.agent.make_trading_decision(analysis)
                        
                        if trade_decision:
                            # Execute trade through Recall Network
                            success = await self.recall_client.execute_trade(trade_decision)
                            
                            if success:
                                self.agent.execute_trade(trade_decision)
                                self.logger.info("Trade executed successfully")
                            else:
                                self.logger.warning("Trade execution failed")
                        
                        # Log performance
                        self.agent.log_performance()
                    
                    # Wait before next iteration
                    await asyncio.sleep(60)  # 1 minute intervals
                    
                except KeyboardInterrupt:
                    self.logger.info("Stopping agent...")
                    break
                except Exception as e:
                    self.logger.error(f"Error in main loop: {e}")
                    await asyncio.sleep(30)  # Wait before retry
                    
        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
        finally:
            await self.recall_client.disconnect()
    
    async def run_backtest(self, start_date: str, end_date: str):
        """
        Run backtest with historical data
        """
        self.logger.info(f"Running backtest from {start_date} to {end_date}")
        
        # Fetch historical data
        historical_data = await self.data_fetcher.fetch_historical_data(
            symbols=self.config.DEFAULT_TRADING_PAIRS,
            start_date=start_date,
            end_date=end_date
        )
        
        if historical_data is None or historical_data.empty:
            self.logger.error("No historical data available")
            return
        
        # Process data day by day
        for date, day_data in historical_data.groupby(historical_data.index.date):
            analysis = self.agent.analyze_market(day_data)
            trade_decision = self.agent.make_trading_decision(analysis)
            
            if trade_decision:
                self.agent.execute_trade(trade_decision)
                self.logger.info(f"Backtest trade on {date}: {trade_decision['action']}")
        
        # Final performance report
        metrics = self.agent.get_performance_metrics()
        self.logger.info(f"Backtest completed. Final metrics: {metrics}")

def main():
    """Main entry point"""
    runner = CryptoAlphaRunner()
    
    if len(sys.argv) > 1 and sys.argv[1] == 'backtest':
        # Run backtest
        start_date = sys.argv[2] if len(sys.argv) > 2 else '2023-01-01'
        end_date = sys.argv[3] if len(sys.argv) > 3 else '2023-12-31'
        
        asyncio.run(runner.run_backtest(start_date, end_date))
    else:
        # Run live competition
        asyncio.run(runner.run_competition())

if __name__ == "__main__":
    main()
