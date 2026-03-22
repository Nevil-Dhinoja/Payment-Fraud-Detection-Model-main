"""
Unit Tests for Fraud Detection Pipeline
Author: Manan Monani
========================================

Comprehensive test suite for the fraud detection ML pipeline.
Run with: pytest tests/ -v
"""

import os
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.data_loader import DataLoader, SyntheticDataGenerator
from src.preprocessor import Preprocessor
from src.feature_engineer import FeatureEngineer
from src.model_trainer import ModelTrainer
from src.evaluator import Evaluator
from src.predictor import Predictor, TransactionValidator


class TestConfig:
    """Tests for configuration module."""
    
    def test_config_loads_defaults(self):
        """Test that configuration loads with defaults."""
        config = Config()
        assert config is not None
        assert config.data.test_size == 0.2
        assert config.model.primary_model == "xgboost"
    
    def test_config_singleton(self):
        """Test that Config is a singleton."""
        config1 = Config()
        config2 = Config()
        assert config1 is config2
    
    def test_config_get_absolute_path(self):
        """Test absolute path generation."""
        config = Config()
        path = config.get_absolute_path("data/raw/test.csv")
        assert path.is_absolute()


class TestDataLoader:
    """Tests for data loading module."""
    
    def test_synthetic_data_generation(self):
        """Test synthetic data generator."""
        generator = SyntheticDataGenerator(n_samples=1000)
        df = generator.generate()
        
        assert len(df) == 1000
        assert 'Time' in df.columns
        assert 'Amount' in df.columns
        assert 'Class' in df.columns
        assert all(f'V{i}' in df.columns for i in range(1, 29))
    
    def test_synthetic_data_fraud_ratio(self):
        """Test that fraud ratio is approximately correct."""
        generator = SyntheticDataGenerator(n_samples=10000, fraud_ratio=0.1)
        df = generator.generate()
        
        actual_ratio = df['Class'].mean()
        assert 0.08 < actual_ratio < 0.12  # Allow 20% tolerance
    
    def test_data_loader_initialization(self):
        """Test DataLoader initialization."""
        config = Config()
        loader = DataLoader(config)
        
        assert loader.config is not None


class TestPreprocessor:
    """Tests for preprocessing module."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        generator = SyntheticDataGenerator(n_samples=1000)
        df = generator.generate()
        X = df.drop(columns=['Class'])
        y = df['Class']
        return X, y
    
    def test_preprocessor_fit(self, sample_data):
        """Test preprocessor fitting."""
        X, y = sample_data
        preprocessor = Preprocessor()
        preprocessor.fit(X)
        
        assert preprocessor._is_fitted
        assert preprocessor.scaler is not None
    
    def test_preprocessor_transform(self, sample_data):
        """Test preprocessor transformation."""
        X, y = sample_data
        preprocessor = Preprocessor()
        preprocessor.fit(X)
        X_transformed = preprocessor.transform(X)
        
        assert X_transformed.shape == X.shape
    
    def test_preprocessor_fit_transform(self, sample_data):
        """Test complete preprocessing pipeline."""
        X, y = sample_data
        preprocessor = Preprocessor()
        
        X_train, X_test, y_train, y_test, X_val, y_val = preprocessor.fit_transform(X, y)
        
        assert len(X_train) > 0
        assert len(X_test) > 0
        assert len(y_train) == len(X_train)
        assert len(y_test) == len(X_test)
    
    def test_preprocessor_save_load(self, sample_data):
        """Test preprocessor save and load."""
        X, y = sample_data
        preprocessor = Preprocessor()
        preprocessor.fit(X)
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            temp_path = f.name
        
        try:
            preprocessor.save(temp_path)
            
            new_preprocessor = Preprocessor()
            new_preprocessor.load(temp_path)
            
            assert new_preprocessor._is_fitted
            assert new_preprocessor.feature_names == preprocessor.feature_names
        finally:
            os.unlink(temp_path)


class TestFeatureEngineer:
    """Tests for feature engineering module."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        generator = SyntheticDataGenerator(n_samples=1000)
        df = generator.generate()
        X = df.drop(columns=['Class'])
        y = df['Class']
        return X, y
    
    def test_time_features_creation(self, sample_data):
        """Test time-based feature creation."""
        X, y = sample_data
        engineer = FeatureEngineer()
        
        X_with_time = engineer.create_time_features(X)
        
        assert 'Hour' in X_with_time.columns
        assert 'TimeBin' in X_with_time.columns
    
    def test_amount_features_creation(self, sample_data):
        """Test amount-based feature creation."""
        X, y = sample_data
        engineer = FeatureEngineer()
        
        X_with_amount = engineer.create_amount_features(X)
        
        assert 'Amount_Log' in X_with_amount.columns
        assert 'Amount_Zscore' in X_with_amount.columns
    
    def test_feature_selection(self, sample_data):
        """Test feature selection."""
        X, y = sample_data
        engineer = FeatureEngineer()
        
        X_selected, importances = engineer.select_features_by_importance(X, y, n_features=10)
        
        assert X_selected.shape[1] == 10
        assert len(importances) > 0


class TestModelTrainer:
    """Tests for model training module."""
    
    @pytest.fixture
    def training_data(self):
        """Create training data."""
        generator = SyntheticDataGenerator(n_samples=2000)
        df = generator.generate()
        X = df.drop(columns=['Class']).values
        y = df['Class'].values
        return X, y
    
    def test_train_random_forest(self, training_data):
        """Test Random Forest training."""
        X, y = training_data
        trainer = ModelTrainer()
        
        model = trainer.train_single_model(X, y, model_name='random_forest', optimize=False)
        
        assert model is not None
        assert trainer._is_fitted
    
    def test_predictions(self, training_data):
        """Test model predictions."""
        X, y = training_data
        trainer = ModelTrainer()
        trainer.train_single_model(X, y, model_name='random_forest', optimize=False)
        
        predictions = trainer.predict(X[:10])
        probabilities = trainer.predict_proba(X[:10])
        
        assert len(predictions) == 10
        assert probabilities.shape == (10, 2)
    
    def test_model_save_load(self, training_data):
        """Test model save and load."""
        X, y = training_data
        trainer = ModelTrainer()
        trainer.train_single_model(X, y, model_name='random_forest', optimize=False)
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            temp_path = f.name
        
        try:
            trainer.save(temp_path)
            
            new_trainer = ModelTrainer()
            new_trainer.load(temp_path)
            
            assert new_trainer._is_fitted
            assert new_trainer.model is not None
        finally:
            os.unlink(temp_path)
            # Clean up metadata file if exists
            metadata_path = Path(temp_path).parent / f"{Path(temp_path).stem}_metadata.joblib"
            if metadata_path.exists():
                os.unlink(metadata_path)


class TestEvaluator:
    """Tests for evaluation module."""
    
    def test_compute_metrics(self):
        """Test metrics computation."""
        y_true = np.array([0, 0, 1, 1, 0, 1, 0, 1])
        y_pred = np.array([0, 0, 1, 0, 0, 1, 1, 1])
        y_proba = np.array([0.1, 0.2, 0.9, 0.4, 0.3, 0.8, 0.6, 0.7])
        
        evaluator = Evaluator()
        metrics = evaluator.compute_metrics(y_true, y_pred, y_proba)
        
        assert 'accuracy' in metrics
        assert 'precision' in metrics
        assert 'recall' in metrics
        assert 'f1' in metrics
        assert 'roc_auc' in metrics
    
    def test_optimal_threshold(self):
        """Test optimal threshold finding."""
        np.random.seed(42)
        y_true = np.random.randint(0, 2, 100)
        y_proba = np.random.random(100)
        
        evaluator = Evaluator()
        threshold, metrics = evaluator.find_optimal_threshold(y_true, y_proba, method='f1')
        
        assert 0 <= threshold <= 1


class TestPredictor:
    """Tests for prediction module."""
    
    @pytest.fixture
    def trained_predictor(self):
        """Create a trained predictor."""
        generator = SyntheticDataGenerator(n_samples=1000)
        df = generator.generate()
        X = df.drop(columns=['Class']).values
        y = df['Class'].values
        
        trainer = ModelTrainer()
        trainer.train_single_model(X, y, model_name='random_forest', optimize=False)
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            temp_path = f.name
        
        trainer.save(temp_path)
        
        predictor = Predictor()
        predictor.load_model(temp_path)
        
        return predictor, temp_path, X
    
    def test_single_prediction(self, trained_predictor):
        """Test single prediction."""
        predictor, temp_path, X = trained_predictor
        
        try:
            sample = {f'feature_{i}': X[0, i] for i in range(X.shape[1])}
            result = predictor.predict(sample)
            
            assert 'predictions' in result
            assert len(result['predictions']) == 1
        finally:
            os.unlink(temp_path)
    
    def test_batch_prediction(self, trained_predictor):
        """Test batch prediction."""
        predictor, temp_path, X = trained_predictor
        
        try:
            df = pd.DataFrame(X[:10], columns=[f'feature_{i}' for i in range(X.shape[1])])
            result = predictor.predict_batch(df)
            
            assert len(result) == 10
            assert 'prediction' in result.columns
        finally:
            os.unlink(temp_path)


class TestTransactionValidator:
    """Tests for transaction validation."""
    
    def test_valid_transaction(self):
        """Test valid transaction validation."""
        transaction = {
            'Time': 100,
            'Amount': 150.00,
            **{f'V{i}': np.random.random() for i in range(1, 29)}
        }
        
        is_valid, errors = TransactionValidator.validate(transaction)
        
        assert is_valid
        assert len(errors) == 0
    
    def test_missing_required_field(self):
        """Test validation with missing required field."""
        transaction = {
            'Time': 100,
            # Missing 'Amount'
        }
        
        is_valid, errors = TransactionValidator.validate(transaction)
        
        assert not is_valid
        assert any('Amount' in error for error in errors)
    
    def test_negative_amount(self):
        """Test validation with negative amount."""
        transaction = {
            'Time': 100,
            'Amount': -50.00,
        }
        
        is_valid, errors = TransactionValidator.validate(transaction)
        
        assert not is_valid
        assert any('non-negative' in error for error in errors)


# Integration Tests
class TestIntegration:
    """Integration tests for the complete pipeline."""
    
    def test_full_pipeline(self):
        """Test the complete ML pipeline."""
        # Generate data
        generator = SyntheticDataGenerator(n_samples=2000)
        df = generator.generate()
        
        X = df.drop(columns=['Class'])
        y = df['Class']
        
        # Feature engineering
        engineer = FeatureEngineer()
        X_engineered = engineer.fit_transform(X, y)
        
        # Preprocessing
        preprocessor = Preprocessor()
        X_train, X_test, y_train, y_test, _, _ = preprocessor.fit_transform(
            X_engineered, y,
            apply_resampling=True
        )
        
        # Training
        trainer = ModelTrainer()
        trainer.train_single_model(X_train, y_train, model_name='random_forest', optimize=False)
        
        # Prediction
        y_pred = trainer.predict(X_test)
        y_proba = trainer.predict_proba(X_test)[:, 1]
        
        # Evaluation
        evaluator = Evaluator()
        metrics = evaluator.evaluate(y_test, y_pred, y_proba)
        
        # Assertions
        assert 'accuracy' in metrics
        assert metrics['accuracy'] > 0.5  # Should be better than random
        assert metrics['f1'] > 0  # Should detect some fraud


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
