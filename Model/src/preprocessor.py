"""
Data Preprocessor Module
Author: Manan Monani
========================

This module handles all data preprocessing tasks including:
- Missing value imputation
- Feature scaling (Standard, MinMax, Robust)
- Train/validation/test split
- Class imbalance handling (SMOTE, ADASYN, etc.)

Provides sklearn-compatible transformers for pipeline integration.
"""

import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from loguru import logger
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.impute import SimpleImputer
from imblearn.over_sampling import SMOTE, ADASYN, RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler
from imblearn.combine import SMOTEENN, SMOTETomek
import joblib

from src.config import Config


class Preprocessor:
    """
    Data preprocessing pipeline for fraud detection.
    
    Handles:
    - Missing value imputation
    - Feature scaling
    - Data splitting
    - Class imbalance handling
    
    Attributes:
        config: Configuration object
        scaler: Fitted scaler object
        imputer: Fitted imputer object
        
    Usage:
        preprocessor = Preprocessor()
        X_train, X_test, y_train, y_test = preprocessor.fit_transform(X, y)
    """
    
    SCALERS = {
        'standard': StandardScaler,
        'minmax': MinMaxScaler,
        'robust': RobustScaler,
    }
    
    SAMPLERS = {
        'smote': SMOTE,
        'adasyn': ADASYN,
        'random_oversample': RandomOverSampler,
        'random_undersample': RandomUnderSampler,
        'smoteenn': SMOTEENN,
        'smotetomek': SMOTETomek,
    }
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize Preprocessor.
        
        Args:
            config: Configuration object. If None, loads default config.
        """
        self.config = config or Config()
        
        # Initialize transformers
        self.scaler = None
        self.imputer = None
        self.sampler = None
        
        # Feature information
        self.feature_names: List[str] = []
        self.numeric_features: List[str] = []
        self.categorical_features: List[str] = []
        
        # Fitted flag
        self._is_fitted = False
        
        logger.info("Preprocessor initialized")
    
    def _init_scaler(self) -> None:
        """Initialize the scaler based on configuration."""
        scaling_method = self.config.features.scaling_method.lower()
        
        if scaling_method not in self.SCALERS:
            logger.warning(f"Unknown scaling method '{scaling_method}'. Using 'robust'.")
            scaling_method = 'robust'
        
        self.scaler = self.SCALERS[scaling_method]()
        logger.info(f"Initialized {scaling_method} scaler")
    
    def _init_imputer(self) -> None:
        """Initialize the imputer."""
        self.imputer = SimpleImputer(strategy='median')
        logger.info("Initialized median imputer")
    
    def _init_sampler(self) -> None:
        """Initialize the resampler based on configuration."""
        method = self.config.imbalance.method.lower()
        
        if method == 'none':
            self.sampler = None
            logger.info("No resampling will be applied")
            return
        
        if method not in self.SAMPLERS:
            logger.warning(f"Unknown sampling method '{method}'. Using 'smote'.")
            method = 'smote'
        
        sampling_strategy = self.config.imbalance.sampling_strategy
        random_state = self.config.data.random_state
        
        if method in ['smote', 'adasyn', 'random_oversample']:
            self.sampler = self.SAMPLERS[method](
                sampling_strategy=sampling_strategy,
                random_state=random_state
            )
        elif method == 'random_undersample':
            self.sampler = self.SAMPLERS[method](
                sampling_strategy=sampling_strategy,
                random_state=random_state
            )
        elif method in ['smoteenn', 'smotetomek']:
            self.sampler = self.SAMPLERS[method](
                random_state=random_state
            )
        
        logger.info(f"Initialized {method} sampler with strategy={sampling_strategy}")
    
    def analyze_features(self, X: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Analyze and categorize features.
        
        Args:
            X: Feature DataFrame
            
        Returns:
            Dictionary with feature categories
        """
        self.feature_names = list(X.columns)
        
        # Identify numeric features
        self.numeric_features = X.select_dtypes(include=[np.number]).columns.tolist()
        
        # Identify categorical features
        self.categorical_features = X.select_dtypes(include=['object', 'category']).columns.tolist()
        
        feature_info = {
            'all': self.feature_names,
            'numeric': self.numeric_features,
            'categorical': self.categorical_features,
            'n_features': len(self.feature_names),
        }
        
        logger.info(f"Feature analysis: {len(self.numeric_features)} numeric, {len(self.categorical_features)} categorical")
        
        return feature_info
    
    def handle_missing_values(self, X: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """
        Handle missing values in the data.
        
        Args:
            X: Feature DataFrame
            fit: If True, fit the imputer. If False, use already fitted imputer.
            
        Returns:
            DataFrame with imputed values
        """
        missing_count = X.isnull().sum().sum()
        
        if missing_count == 0:
            logger.info("No missing values found")
            return X
        
        logger.info(f"Found {missing_count} missing values. Imputing...")
        
        if fit:
            self._init_imputer()
            X_imputed = pd.DataFrame(
                self.imputer.fit_transform(X),
                columns=X.columns,
                index=X.index
            )
        else:
            if self.imputer is None:
                raise ValueError("Imputer not fitted. Call with fit=True first.")
            X_imputed = pd.DataFrame(
                self.imputer.transform(X),
                columns=X.columns,
                index=X.index
            )
        
        logger.success("Missing values imputed successfully")
        return X_imputed
    
    def scale_features(self, X: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """
        Scale numeric features.
        
        Args:
            X: Feature DataFrame
            fit: If True, fit the scaler. If False, use already fitted scaler.
            
        Returns:
            DataFrame with scaled features
        """
        if not self.numeric_features:
            self.analyze_features(X)
        
        logger.info(f"Scaling {len(self.numeric_features)} numeric features...")
        
        X_scaled = X.copy()
        
        if fit:
            self._init_scaler()
            X_scaled[self.numeric_features] = self.scaler.fit_transform(X[self.numeric_features])
        else:
            if self.scaler is None:
                raise ValueError("Scaler not fitted. Call with fit=True first.")
            X_scaled[self.numeric_features] = self.scaler.transform(X[self.numeric_features])
        
        logger.success("Features scaled successfully")
        return X_scaled
    
    def split_data(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        test_size: Optional[float] = None,
        validation_size: Optional[float] = None,
        stratify: bool = True
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, Optional[pd.DataFrame], Optional[pd.Series]]:
        """
        Split data into train/validation/test sets.
        
        Args:
            X: Feature DataFrame
            y: Target Series
            test_size: Size of test set (fraction)
            validation_size: Size of validation set (fraction of remaining data after test split)
            stratify: If True, use stratified splitting
            
        Returns:
            Tuple of (X_train, X_test, y_train, y_test, X_val, y_val)
            X_val and y_val are None if validation_size is None or 0
        """
        test_size = test_size or self.config.data.test_size
        validation_size = validation_size or self.config.data.validation_size
        random_state = self.config.data.random_state
        
        stratify_col = y if stratify else None
        
        logger.info(f"Splitting data: test_size={test_size}, validation_size={validation_size}")
        
        # First split: train+val / test
        X_train_val, X_test, y_train_val, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=random_state,
            stratify=stratify_col
        )
        
        X_val, y_val = None, None
        
        # Second split: train / val (if validation_size > 0)
        if validation_size and validation_size > 0:
            # Adjust validation size relative to train_val
            val_size_adjusted = validation_size / (1 - test_size)
            stratify_train = y_train_val if stratify else None
            
            X_train, X_val, y_train, y_val = train_test_split(
                X_train_val, y_train_val,
                test_size=val_size_adjusted,
                random_state=random_state,
                stratify=stratify_train
            )
        else:
            X_train, y_train = X_train_val, y_train_val
        
        # Log split information
        logger.info(f"Train set: {len(X_train):,} samples")
        if X_val is not None:
            logger.info(f"Validation set: {len(X_val):,} samples")
        logger.info(f"Test set: {len(X_test):,} samples")
        
        return X_train, X_test, y_train, y_test, X_val, y_val
    
    def resample(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.Series, np.ndarray],
        fit: bool = True
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Handle class imbalance through resampling.
        
        Args:
            X: Feature data
            y: Target data
            fit: If True, fit the sampler
            
        Returns:
            Tuple of (X_resampled, y_resampled)
        """
        if fit:
            self._init_sampler()
        
        if self.sampler is None:
            logger.info("No resampling applied")
            return np.array(X), np.array(y)
        
        # Log original distribution
        unique, counts = np.unique(y, return_counts=True)
        logger.info(f"Original distribution: {dict(zip(unique, counts))}")
        
        # Resample
        logger.info(f"Applying {type(self.sampler).__name__}...")
        X_resampled, y_resampled = self.sampler.fit_resample(X, y)
        
        # Log new distribution
        unique, counts = np.unique(y_resampled, return_counts=True)
        logger.info(f"Resampled distribution: {dict(zip(unique, counts))}")
        
        return X_resampled, y_resampled
    
    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> 'Preprocessor':
        """
        Fit all preprocessors on the data.
        
        Args:
            X: Feature DataFrame
            y: Target Series (optional)
            
        Returns:
            Self
        """
        logger.info("Fitting preprocessor...")
        
        # Analyze features
        self.analyze_features(X)
        
        # Handle missing values
        X = self.handle_missing_values(X, fit=True)
        
        # Scale features
        self.scale_features(X, fit=True)
        
        self._is_fitted = True
        logger.success("Preprocessor fitted successfully")
        
        return self
    
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transform data using fitted preprocessors.
        
        Args:
            X: Feature DataFrame
            
        Returns:
            Transformed DataFrame
        """
        if not self._is_fitted:
            raise ValueError("Preprocessor not fitted. Call fit() first.")
        
        # Handle missing values
        X = self.handle_missing_values(X, fit=False)
        
        # Scale features
        X = self.scale_features(X, fit=False)
        
        return X
    
    def fit_transform(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        apply_resampling: bool = True
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Complete preprocessing pipeline: fit, transform, split, and resample.
        
        Args:
            X: Feature DataFrame
            y: Target Series
            apply_resampling: If True, apply resampling to training data
            
        Returns:
            Tuple of (X_train, X_test, y_train, y_test, X_val, y_val)
        """
        logger.info("Starting preprocessing pipeline...")
        
        # Fit on full data
        self.fit(X)
        
        # Transform
        X_transformed = self.transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test, X_val, y_val = self.split_data(X_transformed, y)
        
        # Apply resampling to training data only
        if apply_resampling:
            X_train, y_train = self.resample(X_train, y_train)
        
        # Convert to numpy arrays
        X_train = np.array(X_train)
        X_test = np.array(X_test)
        y_train = np.array(y_train)
        y_test = np.array(y_test)
        
        if X_val is not None:
            X_val = np.array(X_val)
            y_val = np.array(y_val)
        
        logger.success("Preprocessing pipeline completed")
        
        return X_train, X_test, y_train, y_test, X_val, y_val
    
    def save(self, path: Union[str, Path]) -> None:
        """
        Save preprocessor to disk.
        
        Args:
            path: Path to save the preprocessor
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        save_dict = {
            'scaler': self.scaler,
            'imputer': self.imputer,
            'feature_names': self.feature_names,
            'numeric_features': self.numeric_features,
            'categorical_features': self.categorical_features,
            'is_fitted': self._is_fitted,
        }
        
        joblib.dump(save_dict, path)
        logger.info(f"Preprocessor saved to {path}")
    
    def load(self, path: Union[str, Path]) -> 'Preprocessor':
        """
        Load preprocessor from disk.
        
        Args:
            path: Path to load the preprocessor from
            
        Returns:
            Self
        """
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"Preprocessor file not found: {path}")
        
        save_dict = joblib.load(path)
        
        self.scaler = save_dict['scaler']
        self.imputer = save_dict['imputer']
        self.feature_names = save_dict['feature_names']
        self.numeric_features = save_dict['numeric_features']
        self.categorical_features = save_dict['categorical_features']
        self._is_fitted = save_dict['is_fitted']
        
        logger.info(f"Preprocessor loaded from {path}")
        
        return self
    
    def get_cv_splits(self, X: np.ndarray, y: np.ndarray, n_splits: Optional[int] = None) -> StratifiedKFold:
        """
        Get cross-validation splits.
        
        Args:
            X: Feature array
            y: Target array
            n_splits: Number of folds
            
        Returns:
            StratifiedKFold object
        """
        n_splits = n_splits or self.config.training.cv_n_folds
        
        cv = StratifiedKFold(
            n_splits=n_splits,
            shuffle=True,
            random_state=self.config.data.random_state
        )
        
        return cv


if __name__ == "__main__":
    # Test preprocessor
    from src.data_loader import DataLoader, SyntheticDataGenerator
    
    config = Config()
    
    # Generate synthetic data for testing
    generator = SyntheticDataGenerator(n_samples=10000)
    df = generator.generate()
    
    # Prepare features and target
    X = df.drop(columns=['Class'])
    y = df['Class']
    
    # Initialize preprocessor
    preprocessor = Preprocessor(config)
    
    # Run preprocessing pipeline
    X_train, X_test, y_train, y_test, X_val, y_val = preprocessor.fit_transform(X, y)
    
    print(f"\nPreprocessing Results:")
    print(f"X_train shape: {X_train.shape}")
    print(f"X_test shape: {X_test.shape}")
    print(f"y_train distribution: {np.bincount(y_train.astype(int))}")
    print(f"y_test distribution: {np.bincount(y_test.astype(int))}")
    
    # Save and load test
    preprocessor.save("models/preprocessor.joblib")
    
    new_preprocessor = Preprocessor(config)
    new_preprocessor.load("models/preprocessor.joblib")
    print("\nPreprocessor save/load successful!")
