"""
Historical data downloader
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
import time

logger = logging.getLogger(__name__)

class DataDownloader:
    """
    Download historical price data for training.
    """
    
    def __init__(self):
        """Initialize data downloader."""
        self.pairs = ['XAUUSD', 'BTCUSD']
        self.timeframe = 'M15'  # 15-minute candles
        logger.info("Data Downloader initialized")
    
    def download_historical_data(self, pair: str, years: int = 25,
                                 timeframe: str = 'M15') -> Optional[pd.DataFrame]:
        """
        Download historical data for a pair.
        
        Args:
            pair: Trading pair
            years: Number of years of historical data
            timeframe: Timeframe (M15, H1, etc.)
        
        Returns:
            DataFrame with OHLCV data or None
        """
        try:
            logger.info(f"Downloading {years} years of {pair} data ({timeframe})...")
            
            # This is a placeholder implementation
            # In production, you would use:
            # 1. MetaTrader5 Python library
            # 2. External API (Alpha Vantage, Twelve Data, etc.)
            # 3. Broker's API
            
            # Generate synthetic data for demonstration
            end_date = datetime.now()
            start_date = end_date - timedelta(days=years*365)
            
            # Calculate number of candles
            if timeframe == 'M15':
                minutes_per_candle = 15
            elif timeframe == 'H1':
                minutes_per_candle = 60
            elif timeframe == 'D1':
                minutes_per_candle = 1440
            else:
                minutes_per_candle = 15
            
            total_minutes = (end_date - start_date).total_seconds() / 60
            num_candles = int(total_minutes / minutes_per_candle)
            
            logger.info(f"Generating {num_candles} candles...")
            
            # Generate timestamps
            timestamps = pd.date_range(start=start_date, end=end_date, 
                                      periods=num_candles)
            
            # Generate price data (random walk)
            np.random.seed(42)
            
            if pair == 'XAUUSD':
                base_price = 1800
                volatility = 20
            elif pair == 'BTCUSD':
                base_price = 30000
                volatility = 1000
            else:
                base_price = 1.0
                volatility = 0.01
            
            # Random walk
            returns = np.random.normal(0, volatility, num_candles)
            prices = base_price + np.cumsum(returns)
            
            # Generate OHLC from prices
            data = []
            for i, (ts, price) in enumerate(zip(timestamps, prices)):
                # Add some intra-candle variation
                high = price + abs(np.random.normal(0, volatility/4))
                low = price - abs(np.random.normal(0, volatility/4))
                open_price = price + np.random.normal(0, volatility/8)
                close = price
                volume = abs(np.random.normal(1000, 200))
                
                data.append({
                    'timestamp': ts,
                    'open': open_price,
                    'high': max(high, open_price, close),
                    'low': min(low, open_price, close),
                    'close': close,
                    'volume': volume
                })
            
            df = pd.DataFrame(data)
            
            logger.info(f"✅ Downloaded {len(df)} candles for {pair}")
            
            return df
        
        except Exception as e:
            logger.error(f"Error downloading data for {pair}: {e}")
            return None
    
    def download_all_pairs(self, years: int = 25) -> Dict[str, pd.DataFrame]:
        """
        Download data for all configured pairs.
        
        Args:
            years: Number of years of data
        
        Returns:
            Dictionary of pair -> DataFrame
        """
        try:
            data = {}
            
            for pair in self.pairs:
                df = self.download_historical_data(pair, years)
                if df is not None:
                    data[pair] = df
                time.sleep(1)  # Rate limiting
            
            logger.info(f"✅ Downloaded data for {len(data)} pairs")
            
            return data
        
        except Exception as e:
            logger.error(f"Error downloading all pairs: {e}")
            return {}
    
    def save_to_csv(self, df: pd.DataFrame, filename: str):
        """
        Save DataFrame to CSV.
        
        Args:
            df: DataFrame
            filename: Output filename
        """
        try:
            df.to_csv(filename, index=False)
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
