# 🚀 CryptoAlpha Quick Start Guide

Get your AI trading agent up and running in minutes!

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- Recall Network API key (optional for testing)

## ⚡ Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Backtest (No API Key Required)
```bash
python run_backtest.py
```

### 3. Test the Agent
```bash
python -m pytest tests/test_agent.py -v
```

## 🔧 Configuration

### Environment Variables (Optional)
Create a `.env` file in the project root:
```env
RECALL_API_KEY=your_api_key_here
ENABLE_LIVE_TRADING=false
LOG_LEVEL=INFO
```

### Basic Configuration
Edit `config.py` to customize:
- Trading pairs
- Risk parameters
- Model settings

## 🎯 Running the Agent

### Live Trading (Requires Recall Network API)
```bash
python main.py
```

### Backtest Mode
```bash
python main.py backtest 2023-01-01 2023-12-31
```

### Custom Backtest Scenarios
```bash
python run_backtest.py
```

## 📊 Understanding the Output

### Backtest Results
- **Total Return**: Overall profit/loss percentage
- **Sharpe Ratio**: Risk-adjusted returns
- **Max Drawdown**: Largest peak-to-trough decline
- **Win Rate**: Percentage of profitable trades

### Trading Signals
- **BUY**: Strong buy signal
- **SELL**: Strong sell signal
- **HOLD**: No clear signal

## 🛠️ Customization

### Adding New Strategies
1. Create a new file in `strategies/`
2. Implement the strategy class
3. Add to `agents/crypto_alpha_agent.py`

### Modifying Risk Management
Edit `utils/risk_manager.py` to adjust:
- Position sizing
- Stop losses
- Risk limits

### Adding Technical Indicators
Extend `utils/technical_indicators.py` with new indicators.

## 🧪 Testing

### Run All Tests
```bash
python -m pytest
```

### Run Specific Tests
```bash
python -m pytest tests/test_agent.py::TestCryptoAlphaAgent::test_market_analysis
```

## 📈 Performance Optimization

### For Better Performance:
1. Increase `MODEL_UPDATE_FREQUENCY` for less frequent model retraining
2. Adjust `MAX_TRADES_PER_HOUR` to limit trade frequency
3. Modify technical indicator periods in `config.py`

### For More Aggressive Trading:
1. Increase `MAX_POSITION_SIZE`
2. Lower `RISK_TOLERANCE`
3. Adjust signal thresholds in strategies

## 🔍 Troubleshooting

### Common Issues:

**Import Errors**: Make sure all dependencies are installed
```bash
pip install -r requirements.txt
```

**API Connection Issues**: Check your Recall Network API key and network connection

**Insufficient Data**: Ensure you have enough historical data for analysis (minimum 50 data points)

### Getting Help:
- Check the logs for detailed error messages
- Review the configuration in `config.py`
- Test with backtest mode first

## 🏆 Competition Ready

Your agent is now ready for Recall Network competitions! Key features:

- ✅ **Transparent Performance**: All trades are logged and verifiable
- ✅ **Risk Management**: Built-in position sizing and risk controls
- ✅ **Multiple Strategies**: Momentum, mean reversion, and breakout strategies
- ✅ **Real-time Analysis**: Live market data processing
- ✅ **Backtesting**: Test strategies before live trading

## 🎉 Next Steps

1. **Test thoroughly** with backtests
2. **Customize** strategies for your trading style
3. **Monitor performance** and adjust parameters
4. **Join competitions** on Recall Network
5. **Share results** and learn from the community

Happy trading! 🚀
