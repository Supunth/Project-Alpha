"""
Configuration template for CryptoAlpha AI Portfolio Manager
Copy this to config_local.py and update with your API keys
"""

# Recall Network API Configuration
RECALL_API_KEY_PRODUCTION = "e98ce8c3103734d5_a7177b2cc584618f"
RECALL_API_KEY_SANDBOX = "2e0fce1504934a8f_15b2d1eb5112799d"
RECALL_BASE_URL = "https://api.recall.network"

# Environment Selection
USE_PRODUCTION = True  # Set to False for sandbox testing

# Get the appropriate API key
RECALL_API_KEY = RECALL_API_KEY_PRODUCTION if USE_PRODUCTION else RECALL_API_KEY_SANDBOX

# Trading Configuration
DEFAULT_TRADING_PAIRS = ['BTC/USD', 'ETH/USD', 'ADA/USD']
INITIAL_PORTFOLIO_VALUE = 10000
MAX_POSITION_SIZE = 0.1
RISK_TOLERANCE = 0.02

# Model Configuration
MODEL_UPDATE_FREQUENCY = 3600  # seconds
ENABLE_LIVE_TRADING = True
LOG_LEVEL = 'INFO'

# Competition Settings
COMPETITION_ID = 'default'
AGENT_NAME = 'CryptoAlpha_v1.0'
MAX_TRADES_PER_HOUR = 10

# Risk Management
STOP_LOSS_PERCENTAGE = 0.05  # 5% stop loss
TAKE_PROFIT_PERCENTAGE = 0.15  # 15% take profit
MAX_DAILY_LOSS = 0.03  # 3% max daily loss

print(f"Using {'PRODUCTION' if USE_PRODUCTION else 'SANDBOX'} API key")
print(f"Agent Name: {AGENT_NAME}")
print(f"Trading Pairs: {DEFAULT_TRADING_PAIRS}")
