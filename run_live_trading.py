"""
Live Trading Runner for CryptoAlpha AI Portfolio Manager
"""
import asyncio
import logging
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
from agents.crypto_alpha_agent import CryptoAlphaAgent
from utils.data_fetcher import MarketDataFetcher
from utils.recall_client import RecallNetworkClient

class LiveTradingRunner:
    """
    Runner for live trading with Recall Network
    """
    
    def __init__(self, use_sandbox=False):
        self.config = config['development']()
        
        # Override API key based on environment
        if use_sandbox:
            self.config.RECALL_API_KEY = self.config.RECALL_API_KEY_SANDBOX
            print("🔧 Using SANDBOX API key for testing")
        else:
            print("🚀 Using PRODUCTION API key for live trading")
        
        self.agent = CryptoAlphaAgent(self.config.__dict__)
        self.data_fetcher = MarketDataFetcher()
        self.recall_client = RecallNetworkClient(self.config.RECALL_API_KEY)
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, self.config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    async def run(self):
        """
        Run live trading
        """
        self.logger.info("🚀 Starting CryptoAlpha Live Trading...")
        self.logger.info(f"Agent: {self.config.AGENT_NAME}")
        self.logger.info(f"Trading Pairs: {self.config.DEFAULT_TRADING_PAIRS}")
        self.logger.info(f"Max Position Size: {self.config.MAX_POSITION_SIZE}")
        
        try:
            # Initialize connection
            await self.recall_client.connect()
            self.logger.info("✅ Connected to Recall Network")
            
            # Get initial portfolio value
            portfolio_value = await self.recall_client.get_portfolio_value()
            self.logger.info(f"💰 Initial Portfolio Value: ${portfolio_value:,.2f}")
            
            # Main trading loop
            iteration = 0
            while True:
                try:
                    iteration += 1
                    self.logger.info(f"\n📊 Trading Iteration #{iteration}")
                    
                    # Fetch market data
                    market_data = await self.data_fetcher.fetch_latest_data(
                        symbols=self.config.DEFAULT_TRADING_PAIRS
                    )
                    
                    if market_data is not None and not market_data.empty:
                        self.logger.info(f"📈 Market data received: {len(market_data)} data points")
                        
                        # Analyze market
                        analysis = self.agent.analyze_market(market_data)
                        overall_signal = analysis.get('overall_signal', 'HOLD')
                        self.logger.info(f"🎯 Overall Signal: {overall_signal}")
                        
                        # Make trading decision
                        trade_decision = self.agent.make_trading_decision(analysis)
                        
                        if trade_decision:
                            self.logger.info(f"💡 Trading Decision: {trade_decision['action']} {trade_decision['symbol']}")
                            
                            # Execute trade through Recall Network
                            success = await self.recall_client.execute_trade(trade_decision)
                            
                            if success:
                                self.agent.execute_trade(trade_decision)
                                self.logger.info("✅ Trade executed successfully")
                                
                                # Update portfolio value
                                new_portfolio_value = await self.recall_client.get_portfolio_value()
                                self.logger.info(f"💰 Updated Portfolio Value: ${new_portfolio_value:,.2f}")
                            else:
                                self.logger.warning("❌ Trade execution failed")
                        else:
                            self.logger.info("⏸️ No trading action taken")
                        
                        # Log performance
                        self.agent.log_performance()
                    
                    else:
                        self.logger.warning("⚠️ No market data available")
                    
                    # Wait before next iteration
                    self.logger.info(f"⏰ Waiting {self.config.MODEL_UPDATE_FREQUENCY} seconds...")
                    await asyncio.sleep(self.config.MODEL_UPDATE_FREQUENCY)
                    
                except KeyboardInterrupt:
                    self.logger.info("🛑 Stopping agent (Keyboard Interrupt)...")
                    break
                except Exception as e:
                    self.logger.error(f"❌ Error in trading loop: {e}")
                    await asyncio.sleep(30)  # Wait before retry
                    
        except Exception as e:
            self.logger.error(f"💥 Fatal error: {e}")
        finally:
            await self.recall_client.disconnect()
            self.logger.info("👋 Disconnected from Recall Network")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run CryptoAlpha Live Trading')
    parser.add_argument('--sandbox', action='store_true', 
                       help='Use sandbox API key for testing')
    parser.add_argument('--production', action='store_true',
                       help='Use production API key for live trading')
    
    args = parser.parse_args()
    
    # Determine environment
    use_sandbox = args.sandbox or (not args.production and not args.sandbox)
    
    if use_sandbox:
        print("🧪 SANDBOX MODE - Safe for testing")
    else:
        print("⚠️  PRODUCTION MODE - Real money trading!")
        confirm = input("Are you sure you want to trade with real money? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Cancelled. Use --sandbox for testing.")
            return
    
    # Run the trading bot
    runner = LiveTradingRunner(use_sandbox=use_sandbox)
    asyncio.run(runner.run())

if __name__ == "__main__":
    main()
