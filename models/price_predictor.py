"""
Price prediction model for cryptocurrency trading
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from typing import Dict, Any, Optional, Tuple
import logging

class PricePredictor:
    """
    Machine learning model for price prediction
    """
    
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.logger = logging.getLogger(__name__)
    
    def predict(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Predict future price movements
        """
        if data.empty or len(data) < 50:
            return {'error': 'Insufficient data for prediction'}
        
        try:
            # Prepare features
            features = self._prepare_features(data)
            
            if not self.is_trained:
                self._train_model(data, features)
            
            # Make prediction
            prediction = self._make_prediction(features)
            
            return {
                'predicted_price': prediction,
                'confidence': self._calculate_confidence(features),
                'current_price': data['close'].iloc[-1],
                'price_change': prediction - data['close'].iloc[-1],
                'price_change_percent': (prediction - data['close'].iloc[-1]) / data['close'].iloc[-1] * 100
            }
            
        except Exception as e:
            self.logger.error(f"Error in price prediction: {e}")
            return {'error': str(e)}
    
    def _prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """
        Prepare features for the model
        """
        features = []
        
        # Price features
        features.append(data['close'].iloc[-1])  # Current price
        features.append(data['high'].iloc[-1])   # Current high
        features.append(data['low'].iloc[-1])    # Current low
        features.append(data['volume'].iloc[-1] if 'volume' in data.columns else 0)  # Current volume
        
        # Technical indicators
        features.extend(self._calculate_technical_features(data))
        
        # Price momentum
        features.extend(self._calculate_momentum_features(data))
        
        # Volatility features
        features.extend(self._calculate_volatility_features(data))
        
        return np.array(features).reshape(1, -1)
    
    def _calculate_technical_features(self, data: pd.DataFrame) -> list:
        """
        Calculate technical indicator features
        """
        features = []
        
        # Moving averages
        if len(data) >= 20:
            sma_20 = data['close'].rolling(window=20).mean().iloc[-1]
            features.append(sma_20)
        else:
            features.append(data['close'].iloc[-1])
        
        if len(data) >= 50:
            sma_50 = data['close'].rolling(window=50).mean().iloc[-1]
            features.append(sma_50)
        else:
            features.append(data['close'].iloc[-1])
        
        # RSI
        if len(data) >= 14:
            delta = data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs.iloc[-1]))
            features.append(rsi)
        else:
            features.append(50)  # Neutral RSI
        
        return features
    
    def _calculate_momentum_features(self, data: pd.DataFrame) -> list:
        """
        Calculate momentum features
        """
        features = []
        
        # Price changes over different periods
        periods = [1, 5, 10, 20]
        for period in periods:
            if len(data) > period:
                price_change = (data['close'].iloc[-1] - data['close'].iloc[-period-1]) / data['close'].iloc[-period-1]
                features.append(price_change)
            else:
                features.append(0)
        
        return features
    
    def _calculate_volatility_features(self, data: pd.DataFrame) -> list:
        """
        Calculate volatility features
        """
        features = []
        
        # Rolling volatility
        periods = [5, 10, 20]
        for period in periods:
            if len(data) > period:
                returns = data['close'].pct_change().rolling(window=period).std().iloc[-1]
                features.append(returns if not np.isnan(returns) else 0)
            else:
                features.append(0)
        
        return features
    
    def _train_model(self, data: pd.DataFrame, current_features: np.ndarray) -> None:
        """
        Train the prediction model
        """
        try:
            # Prepare training data
            X, y = self._prepare_training_data(data)
            
            if len(X) < 10:  # Need minimum data for training
                self.logger.warning("Insufficient data for training, using default prediction")
                return
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model.fit(X_scaled, y)
            self.is_trained = True
            
            self.logger.info("Price prediction model trained successfully")
            
        except Exception as e:
            self.logger.error(f"Error training model: {e}")
    
    def _prepare_training_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare training data from historical data
        """
        X, y = [], []
        
        # Use sliding window approach
        window_size = 50
        for i in range(window_size, len(data) - 1):
            # Features for this window
            window_data = data.iloc[i-window_size:i+1]
            features = self._prepare_features(window_data)
            X.append(features.flatten())
            
            # Target: next period's price
            target_price = data['close'].iloc[i+1]
            y.append(target_price)
        
        return np.array(X), np.array(y)
    
    def _make_prediction(self, features: np.ndarray) -> float:
        """
        Make price prediction
        """
        try:
            if self.is_trained:
                features_scaled = self.scaler.transform(features)
                prediction = self.model.predict(features_scaled)[0]
                return float(prediction)
            else:
                # Simple prediction based on current price and momentum
                current_price = features[0, 0]
                momentum = features[0, 4] if features.shape[1] > 4 else 0
                return current_price * (1 + momentum * 0.1)
                
        except Exception as e:
            self.logger.error(f"Error making prediction: {e}")
            return features[0, 0]  # Return current price as fallback
    
    def _calculate_confidence(self, features: np.ndarray) -> float:
        """
        Calculate prediction confidence
        """
        try:
            if self.is_trained:
                features_scaled = self.scaler.transform(features)
                # Use feature importance and variance for confidence
                feature_importance = self.model.feature_importances_
                confidence = np.mean(feature_importance) * 100
                return min(confidence, 100)
            else:
                # Lower confidence for untrained model
                return 30.0
                
        except Exception as e:
            self.logger.error(f"Error calculating confidence: {e}")
            return 20.0
