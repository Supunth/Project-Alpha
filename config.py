"""
Configuration settings for CryptoAlpha AI Portfolio Manager
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Main configuration class"""
    
    # Recall Network API
    RECALL_API_KEY = os.getenv('RECALL_API_KEY', 'e98ce8c3103734d5_a7177b2cc584618f')
    RECALL_API_KEY_SANDBOX = '2e0fce1504934a8f_15b2d1eb5112799d'
    RECALL_BASE_URL = os.getenv('RECALL_BASE_URL', 'https://api.recall.network')
    
    # Environment Selection
    USE_PRODUCTION = os.getenv('USE_PRODUCTION', 'true').lower() == 'true'
    
    # Trading Configuration
    DEFAULT_TRADING_PAIRS = os.getenv('DEFAULT_TRADING_PAIRS', 'BTC/USD,ETH/USD,ADA/USD').split(',')
    INITIAL_PORTFOLIO_VALUE = float(os.getenv('INITIAL_PORTFOLIO_VALUE', '10000'))
    MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', '0.1'))
    RISK_TOLERANCE = float(os.getenv('RISK_TOLERANCE', '0.02'))
    
    # Model Configuration
    MODEL_UPDATE_FREQUENCY = int(os.getenv('MODEL_UPDATE_FREQUENCY', '3600'))
    ENABLE_LIVE_TRADING = os.getenv('ENABLE_LIVE_TRADING', 'false').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Competition Settings
    COMPETITION_ID = os.getenv('COMPETITION_ID', 'default')
    AGENT_NAME = os.getenv('AGENT_NAME', 'CryptoAlpha_v1.0')
    MAX_TRADES_PER_HOUR = int(os.getenv('MAX_TRADES_PER_HOUR', '10'))
    
    # Risk Management
    STOP_LOSS_PERCENTAGE = 0.05  # 5% stop loss
    TAKE_PROFIT_PERCENTAGE = 0.15  # 15% take profit
    MAX_DAILY_LOSS = 0.03  # 3% max daily loss
    
    # Technical Indicators
    RSI_PERIOD = 14
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    BB_PERIOD = 20
    BB_STD = 2

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    ENABLE_LIVE_TRADING = False
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    ENABLE_LIVE_TRADING = True
    LOG_LEVEL = 'INFO'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
