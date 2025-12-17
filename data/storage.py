"""
Data storage for saving and loading processed data
"""

import logging
import json
import os
import numpy as np
import pandas as pd
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DataStorage:
    """
    Storage manager for processed data and models.
    """
    
    def __init__(self, data_dir: str = 'data'):
        """
        Initialize data storage.
        
        Args:
            data_dir: Directory for data files
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        logger.info(f"Data Storage initialized: {data_dir}")
    
    def save_dataframe(self, df: pd.DataFrame, filename: str):
        """
        Save DataFrame to JSON.
        
        Args:
            df: DataFrame to save
            filename: Output filename
        """
        try:
            filepath = os.path.join(self.data_dir, filename)
            df.to_json(filepath, orient='records', date_format='iso')
            logger.info(f"DataFrame saved: {filepath} ({len(df)} rows)")
        except Exception as e:
            logger.error(f"Error saving DataFrame: {e}")
    
    def load_dataframe(self, filename: str) -> pd.DataFrame:
        """
        Load DataFrame from JSON.
        
        Args:
            filename: Input filename
        
        Returns:
            DataFrame or None
        """
        try:
            filepath = os.path.join(self.data_dir, filename)
            df = pd.read_json(filepath, orient='records')
            logger.info(f"DataFrame loaded: {filepath} ({len(df)} rows)")
            return df
        except Exception as e:
            logger.error(f"Error loading DataFrame: {e}")
            return None
    
    def save_array(self, array: np.ndarray, filename: str):
        """
        Save numpy array.
        
        Args:
            array: Array to save
            filename: Output filename
        """
        try:
            filepath = os.path.join(self.data_dir, filename)
            np.save(filepath, array)
            logger.info(f"Array saved: {filepath} {array.shape}")
        except Exception as e:
            logger.error(f"Error saving array: {e}")
    
    def load_array(self, filename: str) -> np.ndarray:
        """
        Load numpy array.
        
        Args:
            filename: Input filename
        
        Returns:
            Array or None
        """
        try:
            filepath = os.path.join(self.data_dir, filename)
            array = np.load(filepath)
            logger.info(f"Array loaded: {filepath} {array.shape}")
            return array
        except Exception as e:
            logger.error(f"Error loading array: {e}")
            return None
    
    def save_metadata(self, metadata: Dict[str, Any], filename: str = 'metadata.json'):
        """
        Save metadata to JSON.
        
        Args:
            metadata: Metadata dictionary
            filename: Output filename
        """
        try:
            filepath = os.path.join(self.data_dir, filename)
            with open(filepath, 'w') as f:
                json.dump(metadata, f, indent=2)
            logger.info(f"Metadata saved: {filepath}")
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
    
    def load_metadata(self, filename: str = 'metadata.json') -> Dict[str, Any]:
        """
        Load metadata from JSON.
        
        Args:
            filename: Input filename
        
        Returns:
            Metadata dictionary or None
        """
        try:
            filepath = os.path.join(self.data_dir, filename)
            with open(filepath, 'r') as f:
                metadata = json.load(f)
            logger.info(f"Metadata loaded: {filepath}")
            return metadata
        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
            return None
