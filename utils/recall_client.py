"""
Recall Network API client for CryptoAlpha
"""
import asyncio
import aiohttp
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

class RecallNetworkClient:
    """
    Client for interacting with Recall Network API
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.recall.network"
        self.session = None
        self.logger = logging.getLogger(__name__)
        
    async def connect(self):
        """
        Initialize connection to Recall Network
        """
        try:
            self.session = aiohttp.ClientSession(
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
            )
            self.logger.info("Connected to Recall Network API")
        except Exception as e:
            self.logger.error(f"Failed to connect to Recall Network: {e}")
    
    async def disconnect(self):
        """
        Close connection to Recall Network
        """
        if self.session:
            await self.session.close()
            self.logger.info("Disconnected from Recall Network API")
    
    async def execute_trade(self, trade_decision: Dict[str, Any]) -> bool:
        """
        Execute a trade through Recall Network
        """
        try:
            if not self.session:
                await self.connect()
            
            # Prepare trade payload
            trade_payload = {
                'symbol': trade_decision['symbol'],
                'action': trade_decision['action'],
                'quantity': trade_decision['quantity'],
                'timestamp': datetime.now().isoformat(),
                'metadata': {
                    'agent_name': 'CryptoAlpha',
                    'confidence': trade_decision.get('confidence', 0.5),
                    'reason': trade_decision.get('reason', ''),
                    'stop_loss': trade_decision.get('stop_loss'),
                    'take_profit': trade_decision.get('take_profit')
                }
            }
            
            # Submit trade to Recall Network
            async with self.session.post(
                f"{self.base_url}/trades",
                json=trade_payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self.logger.info(f"Trade submitted successfully: {result}")
                    return True
                else:
                    error_text = await response.text()
                    self.logger.error(f"Trade submission failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error executing trade: {e}")
            return False
    
    async def get_competition_status(self, competition_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current competition status
        """
        try:
            if not self.session:
                await self.connect()
            
            async with self.session.get(
                f"{self.base_url}/competitions/{competition_id}/status"
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    self.logger.error(f"Failed to get competition status: {response.status}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error getting competition status: {e}")
            return None
    
    async def get_leaderboard(self, competition_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current leaderboard
        """
        try:
            if not self.session:
                await self.connect()
            
            async with self.session.get(
                f"{self.base_url}/competitions/{competition_id}/leaderboard"
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    self.logger.error(f"Failed to get leaderboard: {response.status}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error getting leaderboard: {e}")
            return None
    
    async def get_portfolio_value(self) -> Optional[float]:
        """
        Get current portfolio value from Recall Network
        """
        try:
            if not self.session:
                await self.connect()
            
            async with self.session.get(
                f"{self.base_url}/portfolio/value"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('value', 0.0)
                else:
                    self.logger.error(f"Failed to get portfolio value: {response.status}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error getting portfolio value: {e}")
            return None
    
    async def get_market_data(self, symbols: list) -> Optional[Dict[str, Any]]:
        """
        Get market data from Recall Network
        """
        try:
            if not self.session:
                await self.connect()
            
            params = {'symbols': ','.join(symbols)}
            
            async with self.session.get(
                f"{self.base_url}/market/data",
                params=params
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    self.logger.error(f"Failed to get market data: {response.status}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error getting market data: {e}")
            return None
    
    async def submit_performance_report(self, metrics: Dict[str, Any]) -> bool:
        """
        Submit performance report to Recall Network
        """
        try:
            if not self.session:
                await self.connect()
            
            report_payload = {
                'timestamp': datetime.now().isoformat(),
                'agent_name': 'CryptoAlpha',
                'metrics': metrics
            }
            
            async with self.session.post(
                f"{self.base_url}/reports/performance",
                json=report_payload
            ) as response:
                if response.status == 200:
                    self.logger.info("Performance report submitted successfully")
                    return True
                else:
                    error_text = await response.text()
                    self.logger.error(f"Performance report submission failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error submitting performance report: {e}")
            return False
