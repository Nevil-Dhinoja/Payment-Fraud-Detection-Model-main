"""
Predictor Module
Author: Manan Monani
====================

This module provides a unified interface for making predictions using
trained fraud detection models. Includes:
- Single and batch prediction
- Preprocessing integration
- Confidence scoring
- Prediction explanation

Production-ready prediction interface.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from loguru import logger
import joblib

from src.config import Config
from src.preprocessor import Preprocessor
from src.feature_engineer import FeatureEngineer
from src.model_trainer import ModelTrainer


class Predictor:
    """
    Production-ready prediction interface.
    
    Handles:
    - Model and preprocessor loading
    - Data preprocessing for new predictions
    - Single and batch predictions
    - Confidence scoring
    
    Attributes:
        config: Configuration object
        model: Loaded model
        preprocessor: Loaded preprocessor
        feature_engineer: Loaded feature engineer
        
    Usage:
        predictor = Predictor()
        predictor.load_model('models/fraud_detector.joblib')
        result = predictor.predict(transaction_data)
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize Predictor.
        
        Args:
            config: Configuration object. If None, loads default config.
        """
        self.config = config or Config()
        
        self.model = None
        self.preprocessor: Optional[Preprocessor] = None
        self.feature_engineer: Optional[FeatureEngineer] = None
        self.threshold: float = 0.5
        
        self._model_loaded = False
        self._preprocessor_loaded = False
        self._feature_engineer_loaded = False
        
        logger.info("Predictor initialized")
    
    def load_model(self, model_path: Union[str, Path]) -> 'Predictor':
        """
        Load a trained model.
        
        Args:
            model_path: Path to the saved model
            
        Returns:
            Self
        """
        model_path = Path(model_path)
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        self.model = joblib.load(model_path)
        self._model_loaded = True
        
        # Try to load metadata for optimal threshold
        metadata_path = model_path.parent / f"{model_path.stem}_metadata.joblib"
        if metadata_path.exists():
            metadata = joblib.load(metadata_path)
            if 'optimal_threshold' in metadata:
                self.threshold = metadata['optimal_threshold']
        
        logger.info(f"Model loaded from {model_path}")
        
        return self
    
    def load_preprocessor(self, preprocessor_path: Union[str, Path]) -> 'Predictor':
        """
        Load a fitted preprocessor.
        
        Args:
            preprocessor_path: Path to the saved preprocessor
            
        Returns:
            Self
        """
        self.preprocessor = Preprocessor(self.config)
        self.preprocessor.load(preprocessor_path)
        self._preprocessor_loaded = True
        
        logger.info(f"Preprocessor loaded from {preprocessor_path}")
        
        return self
    
    def load_feature_engineer(self, feature_engineer_path: Union[str, Path]) -> 'Predictor':
        """
        Load a fitted feature engineer.
        
        Args:
            feature_engineer_path: Path to the saved feature engineer
            
        Returns:
            Self
        """
        self.feature_engineer = FeatureEngineer(self.config)
        self.feature_engineer.load(feature_engineer_path)
        self._feature_engineer_loaded = True
        
        logger.info(f"Feature engineer loaded from {feature_engineer_path}")
        
        return self
    
    def load_all(
        self,
        model_path: Union[str, Path],
        preprocessor_path: Optional[Union[str, Path]] = None,
        feature_engineer_path: Optional[Union[str, Path]] = None
    ) -> 'Predictor':
        """
        Load all components needed for prediction.
        
        Args:
            model_path: Path to the saved model
            preprocessor_path: Path to the saved preprocessor (optional)
            feature_engineer_path: Path to the saved feature engineer (optional)
            
        Returns:
            Self
        """
        self.load_model(model_path)
        
        if preprocessor_path:
            self.load_preprocessor(preprocessor_path)
        
        if feature_engineer_path:
            self.load_feature_engineer(feature_engineer_path)
        
        return self
    
    def preprocess(self, X: pd.DataFrame) -> np.ndarray:
        """
        Preprocess input data for prediction.
        
        Args:
            X: Input DataFrame
            
        Returns:
            Preprocessed numpy array
        """
        # Apply feature engineering if loaded
        if self._feature_engineer_loaded and self.feature_engineer:
            X = self.feature_engineer.transform(X)
        
        # Apply preprocessing if loaded
        if self._preprocessor_loaded and self.preprocessor:
            X = self.preprocessor.transform(X)
        
        return np.array(X)
    
    def predict(
        self,
        X: Union[pd.DataFrame, Dict[str, Any], np.ndarray],
        return_proba: bool = True,
        apply_threshold: bool = True
    ) -> Dict[str, Any]:
        """
        Make predictions on new data.
        
        Args:
            X: Input data (DataFrame, dict for single record, or numpy array)
            return_proba: Whether to return probabilities
            apply_threshold: Whether to apply optimal threshold
            
        Returns:
            Dictionary with predictions and metadata
        """
        if not self._model_loaded or self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        # Convert input to DataFrame if needed
        if isinstance(X, dict):
            X = pd.DataFrame([X])
        elif isinstance(X, np.ndarray):
            X = pd.DataFrame(X)
        
        # Preprocess
        X_processed = self.preprocess(X)
        
        # Make predictions
        threshold = self.threshold if apply_threshold else 0.5
        
        if return_proba and hasattr(self.model, 'predict_proba'):
            probabilities = self.model.predict_proba(X_processed)
            fraud_proba = probabilities[:, 1]
            predictions = (fraud_proba >= threshold).astype(int)
        else:
            predictions = self.model.predict(X_processed)
            fraud_proba = None
        
        # Build result
        result = {
            'predictions': predictions.tolist(),
            'labels': ['Fraud' if p == 1 else 'Legitimate' for p in predictions],
            'threshold': threshold,
            'n_samples': len(predictions),
        }
        
        if fraud_proba is not None:
            result['probabilities'] = fraud_proba.tolist()
            result['confidence'] = [
                max(p, 1-p) for p in fraud_proba
            ]
        
        return result
    
    def predict_single(
        self,
        transaction: Dict[str, Any],
        return_explanation: bool = False
    ) -> Dict[str, Any]:
        """
        Make prediction for a single transaction.
        
        Args:
            transaction: Dictionary with transaction features
            return_explanation: Whether to return feature contributions
            
        Returns:
            Dictionary with prediction details
        """
        result = self.predict(transaction, return_proba=True)
        
        # Simplify for single prediction
        prediction = {
            'is_fraud': bool(result['predictions'][0]),
            'label': result['labels'][0],
            'fraud_probability': result['probabilities'][0] if 'probabilities' in result else None,
            'confidence': result['confidence'][0] if 'confidence' in result else None,
            'threshold': result['threshold'],
        }
        
        # Risk level
        if prediction['fraud_probability']:
            prob = prediction['fraud_probability']
            if prob >= 0.8:
                prediction['risk_level'] = 'HIGH'
            elif prob >= 0.5:
                prediction['risk_level'] = 'MEDIUM'
            elif prob >= 0.2:
                prediction['risk_level'] = 'LOW'
            else:
                prediction['risk_level'] = 'VERY LOW'
        
        return prediction
    
    def predict_batch(
        self,
        transactions: Union[pd.DataFrame, List[Dict[str, Any]]],
        batch_size: int = 1000
    ) -> pd.DataFrame:
        """
        Make predictions for a batch of transactions.
        
        Args:
            transactions: DataFrame or list of transaction dictionaries
            batch_size: Size of processing batches
            
        Returns:
            DataFrame with predictions
        """
        if isinstance(transactions, list):
            transactions = pd.DataFrame(transactions)
        
        logger.info(f"Processing batch of {len(transactions)} transactions...")
        
        all_predictions = []
        all_probas = []
        
        for start in range(0, len(transactions), batch_size):
            end = min(start + batch_size, len(transactions))
            batch = transactions.iloc[start:end]
            
            result = self.predict(batch, return_proba=True)
            all_predictions.extend(result['predictions'])
            if 'probabilities' in result:
                all_probas.extend(result['probabilities'])
        
        # Create result DataFrame
        result_df = transactions.copy()
        result_df['prediction'] = all_predictions
        result_df['label'] = ['Fraud' if p == 1 else 'Legitimate' for p in all_predictions]
        
        if all_probas:
            result_df['fraud_probability'] = all_probas
            result_df['confidence'] = [max(p, 1-p) for p in all_probas]
        
        logger.success(f"Batch prediction complete. Frauds detected: {sum(all_predictions)}")
        
        return result_df
    
    def set_threshold(self, threshold: float) -> None:
        """
        Set the classification threshold.
        
        Args:
            threshold: New threshold value (0-1)
        """
        if not 0 <= threshold <= 1:
            raise ValueError("Threshold must be between 0 and 1")
        
        self.threshold = threshold
        logger.info(f"Threshold set to {threshold}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model information
        """
        info = {
            'model_loaded': self._model_loaded,
            'preprocessor_loaded': self._preprocessor_loaded,
            'feature_engineer_loaded': self._feature_engineer_loaded,
            'threshold': self.threshold,
        }
        
        if self._model_loaded and self.model:
            info['model_type'] = type(self.model).__name__
            
            # Get feature names if available
            if hasattr(self.model, 'feature_names_in_'):
                info['n_features'] = len(self.model.feature_names_in_)
                info['features'] = list(self.model.feature_names_in_)
        
        return info


class TransactionValidator:
    """
    Validate transaction data before prediction.
    """
    
    REQUIRED_FIELDS = ['Time', 'Amount']
    PCA_FIELDS = [f'V{i}' for i in range(1, 29)]
    
    @classmethod
    def validate(cls, transaction: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a transaction dictionary.
        
        Args:
            transaction: Transaction data
            
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        # Check required fields
        for field in cls.REQUIRED_FIELDS:
            if field not in transaction:
                errors.append(f"Missing required field: {field}")
        
        # Check Amount is non-negative
        if 'Amount' in transaction:
            if not isinstance(transaction['Amount'], (int, float)):
                errors.append("Amount must be numeric")
            elif transaction['Amount'] < 0:
                errors.append("Amount must be non-negative")
        
        # Check Time is non-negative
        if 'Time' in transaction:
            if not isinstance(transaction['Time'], (int, float)):
                errors.append("Time must be numeric")
            elif transaction['Time'] < 0:
                errors.append("Time must be non-negative")
        
        # Check PCA fields
        pca_count = sum(1 for f in cls.PCA_FIELDS if f in transaction)
        if pca_count > 0 and pca_count < 28:
            errors.append(f"Incomplete PCA features. Found {pca_count}/28")
        
        is_valid = len(errors) == 0
        
        return is_valid, errors
    
    @classmethod
    def validate_batch(cls, transactions: List[Dict[str, Any]]) -> Tuple[bool, Dict[int, List[str]]]:
        """
        Validate a batch of transactions.
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            Tuple of (all_valid, dict of index -> errors)
        """
        all_errors = {}
        
        for i, transaction in enumerate(transactions):
            is_valid, errors = cls.validate(transaction)
            if not is_valid:
                all_errors[i] = errors
        
        all_valid = len(all_errors) == 0
        
        return all_valid, all_errors


if __name__ == "__main__":
    # Test predictor
    from src.data_loader import SyntheticDataGenerator
    from src.preprocessor import Preprocessor
    from src.model_trainer import ModelTrainer
    
    config = Config()
    
    # Generate synthetic data
    generator = SyntheticDataGenerator(n_samples=10000)
    df = generator.generate()
    
    X = df.drop(columns=['Class'])
    y = df['Class']
    
    # Preprocess
    preprocessor = Preprocessor(config)
    X_train, X_test, y_train, y_test, _, _ = preprocessor.fit_transform(X, y, apply_resampling=True)
    
    # Train model
    trainer = ModelTrainer(config)
    trainer.train(X_train, y_train, use_ensemble=False)
    
    # Save model and preprocessor
    trainer.save("models/fraud_detector.joblib")
    preprocessor.save("models/preprocessor.joblib")
    
    # Test predictor
    predictor = Predictor(config)
    predictor.load_all(
        model_path="models/fraud_detector.joblib",
        preprocessor_path="models/preprocessor.joblib"
    )
    
    # Get model info
    info = predictor.get_model_info()
    print(f"\nModel Info: {info}")
    
    # Single prediction
    sample = X.iloc[0].to_dict()
    result = predictor.predict_single(sample)
    print(f"\nSingle Prediction: {result}")
    
    # Batch prediction
    batch_result = predictor.predict_batch(X.head(100))
    print(f"\nBatch Prediction Summary:")
    print(batch_result[['prediction', 'label', 'fraud_probability']].head(10))
    
    # Validate transaction
    is_valid, errors = TransactionValidator.validate(sample)
    print(f"\nValidation: {'Valid' if is_valid else 'Invalid'}")
    if errors:
        print(f"Errors: {errors}")
