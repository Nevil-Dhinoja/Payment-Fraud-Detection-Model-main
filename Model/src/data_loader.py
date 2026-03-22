"""
Data Loader Module
Author: Manan Monani
====================

This module handles loading data from various sources including:
- Local CSV files
- Kaggle datasets (automatic download)
- Database connections (extensible)

Includes data validation and basic statistics reporting.
"""

import os
import sys
import zipfile
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

import numpy as np
import pandas as pd
from loguru import logger

from src.config import Config


class DataLoader:
    """
    Data loader class for fraud detection dataset.
    
    Supports loading from local files or downloading from Kaggle.
    Provides data validation and basic statistics.
    
    Attributes:
        config: Configuration object
        data: Loaded DataFrame
        
    Usage:
        loader = DataLoader()
        df = loader.load_data()
        stats = loader.get_statistics()
    """
    
    # Kaggle dataset information
    KAGGLE_DATASET = "mlg-ulb/creditcardfraud"
    KAGGLE_FILENAME = "creditcard.csv"
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize DataLoader.
        
        Args:
            config: Configuration object. If None, loads default config.
        """
        self.config = config or Config()
        self.data: Optional[pd.DataFrame] = None
        self._raw_data_path = self.config.get_absolute_path(self.config.data.raw_data_path)
        
        logger.info(f"DataLoader initialized. Data path: {self._raw_data_path}")
    
    def download_from_kaggle(self, force: bool = False) -> bool:
        """
        Download the Credit Card Fraud dataset from Kaggle.
        
        Requires Kaggle API credentials to be set up:
        1. Create a Kaggle account
        2. Go to Account -> Create New API Token
        3. Place kaggle.json in ~/.kaggle/ (Linux/Mac) or %USERPROFILE%/.kaggle/ (Windows)
        
        Args:
            force: If True, download even if file exists
            
        Returns:
            True if download successful, False otherwise
        """
        if self._raw_data_path.exists() and not force:
            logger.info(f"Dataset already exists at {self._raw_data_path}")
            return True
        
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
            
            logger.info("Initializing Kaggle API...")
            api = KaggleApi()
            api.authenticate()
            
            # Create directory if it doesn't exist
            self._raw_data_path.parent.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Downloading dataset {self.KAGGLE_DATASET}...")
            api.dataset_download_files(
                self.KAGGLE_DATASET,
                path=str(self._raw_data_path.parent),
                unzip=True
            )
            
            logger.success(f"Dataset downloaded successfully to {self._raw_data_path}")
            return True
            
        except ImportError:
            logger.error("Kaggle package not installed. Run: pip install kaggle")
            return False
        except Exception as e:
            logger.error(f"Error downloading dataset: {e}")
            logger.info("Please download manually from: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud")
            return False
    
    def load_data(self, download_if_missing: bool = True) -> pd.DataFrame:
        """
        Load the fraud detection dataset.
        
        Args:
            download_if_missing: If True, attempt to download from Kaggle if file not found
            
        Returns:
            Loaded DataFrame
            
        Raises:
            FileNotFoundError: If data file not found and download fails
        """
        # Check if file exists
        if not self._raw_data_path.exists():
            logger.warning(f"Data file not found at {self._raw_data_path}")
            
            if download_if_missing:
                logger.info("Attempting to download from Kaggle...")
                if not self.download_from_kaggle():
                    raise FileNotFoundError(
                        f"Data file not found at {self._raw_data_path} and download failed. "
                        f"Please download manually from https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud"
                    )
            else:
                raise FileNotFoundError(f"Data file not found at {self._raw_data_path}")
        
        # Load the data
        logger.info(f"Loading data from {self._raw_data_path}...")
        
        try:
            self.data = pd.read_csv(self._raw_data_path)
            logger.success(f"Data loaded successfully. Shape: {self.data.shape}")
            
            # Basic validation
            self._validate_data()
            
            return self.data
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def _validate_data(self) -> None:
        """Validate the loaded data."""
        if self.data is None:
            raise ValueError("No data loaded")
        
        required_columns = ['Time', 'Amount', 'Class']
        missing_columns = [col for col in required_columns if col not in self.data.columns]
        
        if missing_columns:
            logger.warning(f"Missing expected columns: {missing_columns}")
        
        # Check for V1-V28 columns (PCA components)
        pca_columns = [f'V{i}' for i in range(1, 29)]
        present_pca = [col for col in pca_columns if col in self.data.columns]
        logger.info(f"PCA columns found: {len(present_pca)}/28")
        
        # Check for null values
        null_counts = self.data.isnull().sum()
        if null_counts.any():
            logger.warning(f"Null values found:\n{null_counts[null_counts > 0]}")
        else:
            logger.info("No null values found")
        
        # Check class distribution
        if 'Class' in self.data.columns:
            class_dist = self.data['Class'].value_counts()
            fraud_ratio = class_dist.get(1, 0) / len(self.data) * 100
            logger.info(f"Class distribution - Legitimate: {class_dist.get(0, 0):,}, Fraud: {class_dist.get(1, 0):,} ({fraud_ratio:.2f}%)")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the dataset.
        
        Returns:
            Dictionary containing various statistics
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        stats = {
            'shape': self.data.shape,
            'columns': list(self.data.columns),
            'dtypes': self.data.dtypes.to_dict(),
            'memory_usage_mb': self.data.memory_usage(deep=True).sum() / 1024 / 1024,
            'null_counts': self.data.isnull().sum().to_dict(),
            'numeric_stats': self.data.describe().to_dict(),
        }
        
        # Class-specific statistics
        if 'Class' in self.data.columns:
            stats['class_distribution'] = self.data['Class'].value_counts().to_dict()
            stats['fraud_percentage'] = self.data['Class'].mean() * 100
        
        # Amount statistics
        if 'Amount' in self.data.columns:
            stats['amount_stats'] = {
                'mean': self.data['Amount'].mean(),
                'median': self.data['Amount'].median(),
                'std': self.data['Amount'].std(),
                'min': self.data['Amount'].min(),
                'max': self.data['Amount'].max(),
            }
            
            # Amount by class
            if 'Class' in self.data.columns:
                stats['amount_by_class'] = self.data.groupby('Class')['Amount'].describe().to_dict()
        
        # Time statistics
        if 'Time' in self.data.columns:
            stats['time_stats'] = {
                'min': self.data['Time'].min(),
                'max': self.data['Time'].max(),
                'range_hours': (self.data['Time'].max() - self.data['Time'].min()) / 3600,
            }
        
        return stats
    
    def print_summary(self) -> None:
        """Print a formatted summary of the dataset."""
        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        stats = self.get_statistics()
        
        print("\n" + "="*60)
        print("📊 DATASET SUMMARY")
        print("="*60)
        print(f"\n📁 Shape: {stats['shape'][0]:,} rows × {stats['shape'][1]} columns")
        print(f"💾 Memory Usage: {stats['memory_usage_mb']:.2f} MB")
        
        if 'class_distribution' in stats:
            print(f"\n🎯 Class Distribution:")
            print(f"   - Legitimate (0): {stats['class_distribution'].get(0, 0):,}")
            print(f"   - Fraudulent (1): {stats['class_distribution'].get(1, 0):,}")
            print(f"   - Fraud Rate: {stats['fraud_percentage']:.4f}%")
        
        if 'amount_stats' in stats:
            print(f"\n💰 Transaction Amount:")
            print(f"   - Mean: ${stats['amount_stats']['mean']:.2f}")
            print(f"   - Median: ${stats['amount_stats']['median']:.2f}")
            print(f"   - Range: ${stats['amount_stats']['min']:.2f} - ${stats['amount_stats']['max']:.2f}")
        
        if 'time_stats' in stats:
            print(f"\n⏰ Time Range: {stats['time_stats']['range_hours']:.1f} hours")
        
        print("\n" + "="*60 + "\n")
    
    def get_feature_target_split(self, target_column: Optional[str] = None) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Split data into features and target.
        
        Args:
            target_column: Name of target column. If None, uses config value.
            
        Returns:
            Tuple of (features DataFrame, target Series)
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        target_col = target_column or self.config.features.target_column
        
        if target_col not in self.data.columns:
            raise ValueError(f"Target column '{target_col}' not found in data")
        
        X = self.data.drop(columns=[target_col])
        y = self.data[target_col]
        
        logger.info(f"Features shape: {X.shape}, Target shape: {y.shape}")
        
        return X, y
    
    def save_processed_data(self, data: pd.DataFrame, filename: str) -> Path:
        """
        Save processed data to the processed data directory.
        
        Args:
            data: DataFrame to save
            filename: Name of the file to save
            
        Returns:
            Path to saved file
        """
        processed_path = self.config.get_absolute_path(self.config.data.processed_data_path)
        processed_path.mkdir(parents=True, exist_ok=True)
        
        save_path = processed_path / filename
        data.to_csv(save_path, index=False)
        
        logger.info(f"Processed data saved to {save_path}")
        
        return save_path


class SyntheticDataGenerator:
    """
    Generate synthetic fraud detection data for testing purposes.
    
    Creates realistic-looking transaction data with configurable fraud rates.
    Useful when real data is not available or for testing pipelines.
    """
    
    def __init__(self, n_samples: int = 100000, fraud_ratio: float = 0.017, random_state: int = 42):
        """
        Initialize synthetic data generator.
        
        Args:
            n_samples: Number of samples to generate
            fraud_ratio: Ratio of fraudulent transactions (default 1.7% like real dataset)
            random_state: Random seed for reproducibility
        """
        self.n_samples = n_samples
        self.fraud_ratio = fraud_ratio
        self.random_state = random_state
        np.random.seed(random_state)
    
    def generate(self) -> pd.DataFrame:
        """
        Generate synthetic fraud detection dataset.
        
        Returns:
            DataFrame with synthetic transaction data
        """
        logger.info(f"Generating synthetic dataset with {self.n_samples:,} samples...")
        
        n_fraud = int(self.n_samples * self.fraud_ratio)
        n_legitimate = self.n_samples - n_fraud
        
        # Generate Time feature (seconds from first transaction)
        time = np.concatenate([
            np.random.uniform(0, 172800, n_legitimate),  # 48 hours
            np.random.uniform(0, 172800, n_fraud)
        ])
        
        # Generate PCA components V1-V28
        # Legitimate transactions: centered around 0
        v_legitimate = np.random.normal(0, 1, (n_legitimate, 28))
        # Fraudulent transactions: slightly different distribution
        v_fraud = np.random.normal(0.5, 1.5, (n_fraud, 28))
        v_features = np.vstack([v_legitimate, v_fraud])
        
        # Generate Amount feature
        amount_legitimate = np.random.exponential(100, n_legitimate)
        amount_fraud = np.random.exponential(500, n_fraud)  # Fraud tends to have higher amounts
        amount = np.concatenate([amount_legitimate, amount_fraud])
        
        # Generate labels
        labels = np.concatenate([np.zeros(n_legitimate), np.ones(n_fraud)])
        
        # Create DataFrame
        columns = ['Time'] + [f'V{i}' for i in range(1, 29)] + ['Amount', 'Class']
        data = np.column_stack([time, v_features, amount, labels])
        df = pd.DataFrame(data, columns=columns)
        
        # Shuffle the data
        df = df.sample(frac=1, random_state=self.random_state).reset_index(drop=True)
        
        # Convert Class to int
        df['Class'] = df['Class'].astype(int)
        
        logger.success(f"Synthetic dataset generated. Shape: {df.shape}")
        logger.info(f"Fraud ratio: {df['Class'].mean()*100:.2f}%")
        
        return df


if __name__ == "__main__":
    # Test data loader
    config = Config()
    loader = DataLoader(config)
    
    try:
        df = loader.load_data(download_if_missing=True)
        loader.print_summary()
    except FileNotFoundError as e:
        logger.warning(str(e))
        logger.info("Generating synthetic data for testing...")
        
        generator = SyntheticDataGenerator(n_samples=100000)
        df = generator.generate()
        
        # Save synthetic data
        raw_path = config.get_absolute_path(config.data.raw_data_path)
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(raw_path, index=False)
        logger.success(f"Synthetic data saved to {raw_path}")
