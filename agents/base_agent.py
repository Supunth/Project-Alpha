"""
Base agent class for Recall Network trading agents
"""
from abc import ABC, abstractmethod
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd

class BaseAgent(ABC):
    """
    Abstract base class for all trading agents
    """
    
    def __init__(self, agent_name: str, config: Dict[str, Any]):
        self.agent_name = agent_name
        self.config = config
        self.logger = self._setup_logger()
        self.portfolio = {}
        self.trade_history = []
        self.performance_metrics = {}
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for the agent"""
        logger = logging.getLogger(self.agent_name)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    @abstractmethod
    def analyze_market(self, market_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze market data and return trading signals
        
        Args:
            market_data: DataFrame containing market data
            
        Returns:
            Dict containing trading signals and analysis
        """
        pass
    
    @abstractmethod
    def make_trading_decision(self, analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Make trading decision based on market analysis
        
        Args:
            analysis: Market analysis results
            
        Returns:
            Trading decision or None if no action needed
        """
        pass
    
    @abstractmethod
    def execute_trade(self, trade_decision: Dict[str, Any]) -> bool:
        """
        Execute a trading decision
        
        Args:
            trade_decision: Trading decision to execute
            
        Returns:
            True if trade executed successfully, False otherwise
        """
        pass
    
    def update_portfolio(self, trade_result: Dict[str, Any]) -> None:
        """Update portfolio after trade execution"""
        self.portfolio.update(trade_result.get('portfolio_changes', {}))
        self.trade_history.append({
            'timestamp': datetime.now(),
            'trade': trade_result,
            'portfolio_value': self.get_portfolio_value()
        })
    
    def get_portfolio_value(self) -> float:
        """Calculate current portfolio value"""
        # This would integrate with actual market prices
        return sum(self.portfolio.values())
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Calculate performance metrics"""
        if len(self.trade_history) < 2:
            return {}
            
        # Calculate basic metrics
        total_return = (self.get_portfolio_value() - self.config.get('initial_value', 10000)) / self.config.get('initial_value', 10000)
        
        self.performance_metrics = {
            'total_return': total_return,
            'total_trades': len(self.trade_history),
            'portfolio_value': self.get_portfolio_value()
        }
        
        return self.performance_metrics
    
    def log_performance(self) -> None:
        """Log current performance metrics"""
        metrics = self.get_performance_metrics()
        self.logger.info(f"Performance Metrics: {metrics}")
