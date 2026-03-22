"""
Model Trainer Module
Author: Manan Monani
=====================

This module handles training of fraud detection models including:
- Multiple algorithm support (Random Forest, XGBoost, LightGBM, etc.)
- Hyperparameter optimization using Optuna
- Cross-validation
- Ensemble learning
- Model persistence

Designed for production-grade fraud detection.
"""

import warnings
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from loguru import logger
import joblib

# Scikit-learn models
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    AdaBoostClassifier,
    VotingClassifier,
    StackingClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.calibration import CalibratedClassifierCV

# XGBoost and LightGBM
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logger.warning("XGBoost not installed. Some features will be unavailable.")

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    logger.warning("LightGBM not installed. Some features will be unavailable.")

# Optuna for hyperparameter optimization
try:
    import optuna
    from optuna.samplers import TPESampler
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False
    logger.warning("Optuna not installed. Hyperparameter tuning will be limited.")

from src.config import Config

# Suppress warnings during training
warnings.filterwarnings('ignore', category=UserWarning)


class ModelTrainer:
    """
    Model training class for fraud detection.
    
    Supports:
    - Multiple ML algorithms
    - Hyperparameter optimization
    - Cross-validation
    - Ensemble methods
    - Model saving/loading
    
    Attributes:
        config: Configuration object
        model: Trained model
        best_params: Best hyperparameters found
        cv_scores: Cross-validation scores
        
    Usage:
        trainer = ModelTrainer()
        trainer.train(X_train, y_train)
        predictions = trainer.predict(X_test)
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize ModelTrainer.
        
        Args:
            config: Configuration object. If None, loads default config.
        """
        self.config = config or Config()
        
        self.model: Optional[BaseEstimator] = None
        self.best_params: Dict[str, Any] = {}
        self.cv_scores: List[float] = []
        self.training_history: List[Dict[str, Any]] = []
        
        self._is_fitted = False
        
        logger.info("ModelTrainer initialized")
    
    def _get_base_model(self, model_name: str, params: Optional[Dict] = None) -> BaseEstimator:
        """
        Get a base model instance.
        
        Args:
            model_name: Name of the model
            params: Model parameters
            
        Returns:
            Model instance
        """
        params = params or {}
        random_state = self.config.data.random_state
        
        models = {
            'random_forest': lambda: RandomForestClassifier(
                random_state=random_state,
                n_jobs=-1,
                **params
            ),
            'logistic_regression': lambda: LogisticRegression(
                random_state=random_state,
                max_iter=1000,
                **params
            ),
            'gradient_boosting': lambda: GradientBoostingClassifier(
                random_state=random_state,
                **params
            ),
            'adaboost': lambda: AdaBoostClassifier(
                random_state=random_state,
                **params
            ),
        }
        
        if XGBOOST_AVAILABLE:
            models['xgboost'] = lambda: xgb.XGBClassifier(
                random_state=random_state,
                eval_metric='logloss',
                use_label_encoder=False,
                **params
            )
        
        if LIGHTGBM_AVAILABLE:
            models['lightgbm'] = lambda: lgb.LGBMClassifier(
                random_state=random_state,
                verbose=-1,
                **params
            )
        
        if model_name.lower() not in models:
            available = list(models.keys())
            raise ValueError(f"Unknown model '{model_name}'. Available: {available}")
        
        return models[model_name.lower()]()
    
    def _get_param_space(self, model_name: str, trial: 'optuna.Trial') -> Dict[str, Any]:
        """
        Get hyperparameter search space for Optuna.
        
        Args:
            model_name: Name of the model
            trial: Optuna trial object
            
        Returns:
            Dictionary of hyperparameters
        """
        if model_name == 'random_forest':
            return {
                'n_estimators': trial.suggest_int('n_estimators', 100, 500),
                'max_depth': trial.suggest_int('max_depth', 5, 30),
                'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
                'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10),
                'max_features': trial.suggest_categorical('max_features', ['sqrt', 'log2', None]),
                'class_weight': trial.suggest_categorical('class_weight', ['balanced', 'balanced_subsample', None]),
            }
        
        elif model_name == 'xgboost':
            return {
                'n_estimators': trial.suggest_int('n_estimators', 100, 500),
                'max_depth': trial.suggest_int('max_depth', 3, 15),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
                'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
                'reg_alpha': trial.suggest_float('reg_alpha', 1e-8, 10.0, log=True),
                'reg_lambda': trial.suggest_float('reg_lambda', 1e-8, 10.0, log=True),
                'scale_pos_weight': trial.suggest_float('scale_pos_weight', 1, 100),
            }
        
        elif model_name == 'lightgbm':
            return {
                'n_estimators': trial.suggest_int('n_estimators', 100, 500),
                'max_depth': trial.suggest_int('max_depth', 3, 15),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
                'num_leaves': trial.suggest_int('num_leaves', 20, 150),
                'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
                'reg_alpha': trial.suggest_float('reg_alpha', 1e-8, 10.0, log=True),
                'reg_lambda': trial.suggest_float('reg_lambda', 1e-8, 10.0, log=True),
                'class_weight': trial.suggest_categorical('class_weight', ['balanced', None]),
            }
        
        elif model_name == 'logistic_regression':
            return {
                'C': trial.suggest_float('C', 1e-4, 100, log=True),
                'penalty': trial.suggest_categorical('penalty', ['l1', 'l2']),
                'solver': 'saga',
                'class_weight': trial.suggest_categorical('class_weight', ['balanced', None]),
            }
        
        elif model_name == 'gradient_boosting':
            return {
                'n_estimators': trial.suggest_int('n_estimators', 100, 300),
                'max_depth': trial.suggest_int('max_depth', 3, 10),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
                'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
                'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10),
                'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            }
        
        else:
            return {}
    
    def optimize_hyperparameters(
        self,
        X: np.ndarray,
        y: np.ndarray,
        model_name: Optional[str] = None,
        n_trials: Optional[int] = None,
        scoring: str = 'f1'
    ) -> Dict[str, Any]:
        """
        Optimize hyperparameters using Optuna.
        
        Args:
            X: Training features
            y: Training labels
            model_name: Model to optimize
            n_trials: Number of optimization trials
            scoring: Scoring metric for optimization
            
        Returns:
            Best hyperparameters
        """
        if not OPTUNA_AVAILABLE:
            logger.warning("Optuna not available. Using default parameters.")
            return {}
        
        model_name = model_name or self.config.model.primary_model
        n_trials = n_trials or self.config.model.n_trials
        cv_folds = self.config.model.cv_folds
        
        logger.info(f"Starting hyperparameter optimization for {model_name}...")
        logger.info(f"Trials: {n_trials}, CV Folds: {cv_folds}, Scoring: {scoring}")
        
        def objective(trial: optuna.Trial) -> float:
            """Optuna objective function."""
            params = self._get_param_space(model_name, trial)
            model = self._get_base_model(model_name, params)
            
            cv = StratifiedKFold(
                n_splits=cv_folds,
                shuffle=True,
                random_state=self.config.data.random_state
            )
            
            scores = cross_val_score(model, X, y, cv=cv, scoring=scoring, n_jobs=-1)
            
            return scores.mean()
        
        # Create Optuna study
        sampler = TPESampler(seed=self.config.data.random_state)
        study = optuna.create_study(direction='maximize', sampler=sampler)
        
        # Run optimization
        optuna.logging.set_verbosity(optuna.logging.WARNING)
        study.optimize(objective, n_trials=n_trials, show_progress_bar=True)
        
        self.best_params = study.best_params
        
        logger.success(f"Best {scoring} score: {study.best_value:.4f}")
        logger.info(f"Best parameters: {self.best_params}")
        
        return self.best_params
    
    def train_single_model(
        self,
        X: np.ndarray,
        y: np.ndarray,
        model_name: Optional[str] = None,
        params: Optional[Dict] = None,
        optimize: bool = True
    ) -> BaseEstimator:
        """
        Train a single model.
        
        Args:
            X: Training features
            y: Training labels
            model_name: Name of the model to train
            params: Model parameters (if None and optimize=True, will optimize)
            optimize: Whether to optimize hyperparameters
            
        Returns:
            Trained model
        """
        model_name = model_name or self.config.model.primary_model
        
        logger.info(f"Training {model_name} model...")
        
        # Optimize hyperparameters if needed
        if optimize and self.config.model.hyperparameter_tuning_enabled and params is None:
            params = self.optimize_hyperparameters(X, y, model_name)
        
        params = params or {}
        
        # Create and train model
        model = self._get_base_model(model_name, params)
        model.fit(X, y)
        
        # Cross-validation scores
        cv = StratifiedKFold(
            n_splits=self.config.model.cv_folds,
            shuffle=True,
            random_state=self.config.data.random_state
        )
        
        self.cv_scores = cross_val_score(model, X, y, cv=cv, scoring='f1', n_jobs=-1).tolist()
        
        logger.success(f"Model trained. CV F1 Score: {np.mean(self.cv_scores):.4f} (+/- {np.std(self.cv_scores):.4f})")
        
        return model
    
    def train_ensemble(
        self,
        X: np.ndarray,
        y: np.ndarray,
        model_names: Optional[List[str]] = None,
        method: str = 'voting'
    ) -> BaseEstimator:
        """
        Train an ensemble of models.
        
        Args:
            X: Training features
            y: Training labels
            model_names: List of model names to include
            method: Ensemble method ('voting' or 'stacking')
            
        Returns:
            Trained ensemble model
        """
        model_names = model_names or self.config.model.ensemble_models
        
        logger.info(f"Training {method} ensemble with models: {model_names}")
        
        # Train individual models
        estimators = []
        for name in model_names:
            try:
                # Quick training without full optimization for ensemble
                model = self._get_base_model(name)
                estimators.append((name, model))
                logger.info(f"Added {name} to ensemble")
            except ValueError as e:
                logger.warning(f"Skipping {name}: {e}")
        
        if len(estimators) < 2:
            logger.warning("Not enough models for ensemble. Using single model.")
            return self.train_single_model(X, y, model_names[0] if model_names else None)
        
        # Create ensemble
        if method == 'voting':
            ensemble = VotingClassifier(
                estimators=estimators,
                voting='soft',
                n_jobs=-1
            )
        elif method == 'stacking':
            # Use logistic regression as meta-learner
            meta_learner = LogisticRegression(
                random_state=self.config.data.random_state,
                max_iter=1000
            )
            ensemble = StackingClassifier(
                estimators=estimators,
                final_estimator=meta_learner,
                cv=5,
                n_jobs=-1
            )
        else:
            raise ValueError(f"Unknown ensemble method: {method}")
        
        # Train ensemble
        ensemble.fit(X, y)
        
        # Cross-validation
        cv = StratifiedKFold(
            n_splits=self.config.model.cv_folds,
            shuffle=True,
            random_state=self.config.data.random_state
        )
        
        self.cv_scores = cross_val_score(ensemble, X, y, cv=cv, scoring='f1', n_jobs=-1).tolist()
        
        logger.success(f"Ensemble trained. CV F1 Score: {np.mean(self.cv_scores):.4f} (+/- {np.std(self.cv_scores):.4f})")
        
        return ensemble
    
    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        model_name: Optional[str] = None,
        use_ensemble: Optional[bool] = None
    ) -> BaseEstimator:
        """
        Main training method.
        
        Args:
            X: Training features
            y: Training labels
            model_name: Model to train (if not using ensemble)
            use_ensemble: Whether to use ensemble (defaults to config)
            
        Returns:
            Trained model
        """
        use_ensemble = use_ensemble if use_ensemble is not None else self.config.model.use_ensemble
        
        if use_ensemble:
            self.model = self.train_ensemble(X, y)
        else:
            self.model = self.train_single_model(X, y, model_name)
        
        self._is_fitted = True
        
        return self.model
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions.
        
        Args:
            X: Features to predict
            
        Returns:
            Predicted labels
        """
        if not self._is_fitted or self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        return self.model.predict(X)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Get prediction probabilities.
        
        Args:
            X: Features to predict
            
        Returns:
            Prediction probabilities
        """
        if not self._is_fitted or self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        if not hasattr(self.model, 'predict_proba'):
            raise ValueError("Model does not support probability predictions")
        
        return self.model.predict_proba(X)
    
    def get_feature_importance(self, feature_names: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Get feature importances from the trained model.
        
        Args:
            feature_names: List of feature names
            
        Returns:
            DataFrame with feature importances
        """
        if not self._is_fitted or self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Extract base model if ensemble
        model = self.model
        if isinstance(model, VotingClassifier):
            # Use first model with feature_importances_
            for name, est in model.named_estimators_.items():
                if hasattr(est, 'feature_importances_'):
                    model = est
                    break
        
        if not hasattr(model, 'feature_importances_'):
            logger.warning("Model does not have feature_importances_ attribute")
            return pd.DataFrame()
        
        importances = model.feature_importances_
        
        if feature_names is None:
            feature_names = [f'feature_{i}' for i in range(len(importances))]
        
        df = pd.DataFrame({
            'feature': feature_names,
            'importance': importances
        })
        df = df.sort_values('importance', ascending=False).reset_index(drop=True)
        
        return df
    
    def save(self, path: Union[str, Path], save_metadata: bool = True) -> None:
        """
        Save model to disk.
        
        Args:
            path: Path to save the model
            save_metadata: Whether to save training metadata
        """
        if not self._is_fitted or self.model is None:
            raise ValueError("No model to save. Train a model first.")
        
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save model
        joblib.dump(self.model, path)
        logger.info(f"Model saved to {path}")
        
        # Save metadata
        if save_metadata:
            metadata = {
                'best_params': self.best_params,
                'cv_scores': self.cv_scores,
                'cv_mean': np.mean(self.cv_scores) if self.cv_scores else None,
                'cv_std': np.std(self.cv_scores) if self.cv_scores else None,
            }
            
            metadata_path = path.parent / f"{path.stem}_metadata.joblib"
            joblib.dump(metadata, metadata_path)
            logger.info(f"Metadata saved to {metadata_path}")
    
    def load(self, path: Union[str, Path], load_metadata: bool = True) -> 'ModelTrainer':
        """
        Load model from disk.
        
        Args:
            path: Path to load the model from
            load_metadata: Whether to load training metadata
            
        Returns:
            Self
        """
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")
        
        self.model = joblib.load(path)
        self._is_fitted = True
        
        logger.info(f"Model loaded from {path}")
        
        # Load metadata if available
        if load_metadata:
            metadata_path = path.parent / f"{path.stem}_metadata.joblib"
            if metadata_path.exists():
                metadata = joblib.load(metadata_path)
                self.best_params = metadata.get('best_params', {})
                self.cv_scores = metadata.get('cv_scores', [])
                logger.info(f"Metadata loaded from {metadata_path}")
        
        return self


class ModelComparer:
    """
    Compare multiple models to find the best one.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize ModelComparer."""
        self.config = config or Config()
        self.results: List[Dict[str, Any]] = []
    
    def compare(
        self,
        X: np.ndarray,
        y: np.ndarray,
        models: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Compare multiple models using cross-validation.
        
        Args:
            X: Training features
            y: Training labels
            models: List of model names to compare
            
        Returns:
            DataFrame with comparison results
        """
        if models is None:
            models = ['random_forest', 'logistic_regression', 'gradient_boosting']
            if XGBOOST_AVAILABLE:
                models.append('xgboost')
            if LIGHTGBM_AVAILABLE:
                models.append('lightgbm')
        
        logger.info(f"Comparing models: {models}")
        
        self.results = []
        trainer = ModelTrainer(self.config)
        
        cv = StratifiedKFold(
            n_splits=5,
            shuffle=True,
            random_state=self.config.data.random_state
        )
        
        for model_name in models:
            try:
                logger.info(f"Evaluating {model_name}...")
                model = trainer._get_base_model(model_name)
                
                # Calculate multiple metrics
                f1_scores = cross_val_score(model, X, y, cv=cv, scoring='f1', n_jobs=-1)
                precision_scores = cross_val_score(model, X, y, cv=cv, scoring='precision', n_jobs=-1)
                recall_scores = cross_val_score(model, X, y, cv=cv, scoring='recall', n_jobs=-1)
                roc_auc_scores = cross_val_score(model, X, y, cv=cv, scoring='roc_auc', n_jobs=-1)
                
                self.results.append({
                    'model': model_name,
                    'f1_mean': np.mean(f1_scores),
                    'f1_std': np.std(f1_scores),
                    'precision_mean': np.mean(precision_scores),
                    'recall_mean': np.mean(recall_scores),
                    'roc_auc_mean': np.mean(roc_auc_scores),
                })
                
            except Exception as e:
                logger.error(f"Error evaluating {model_name}: {e}")
        
        results_df = pd.DataFrame(self.results)
        results_df = results_df.sort_values('f1_mean', ascending=False).reset_index(drop=True)
        
        logger.success("Model comparison complete")
        
        return results_df


if __name__ == "__main__":
    # Test model trainer
    from src.data_loader import SyntheticDataGenerator
    from src.preprocessor import Preprocessor
    
    config = Config()
    
    # Generate synthetic data
    generator = SyntheticDataGenerator(n_samples=10000)
    df = generator.generate()
    
    X = df.drop(columns=['Class'])
    y = df['Class']
    
    # Preprocess
    preprocessor = Preprocessor(config)
    X_train, X_test, y_train, y_test, _, _ = preprocessor.fit_transform(X, y, apply_resampling=True)
    
    # Compare models
    comparer = ModelComparer(config)
    results = comparer.compare(X_train, y_train)
    print("\nModel Comparison Results:")
    print(results.to_string())
    
    # Train best model
    trainer = ModelTrainer(config)
    trainer.train(X_train, y_train, use_ensemble=False)
    
    # Make predictions
    predictions = trainer.predict(X_test)
    probabilities = trainer.predict_proba(X_test)
    
    print(f"\nPredictions shape: {predictions.shape}")
    print(f"Probability shape: {probabilities.shape}")
    
    # Save model
    trainer.save("models/fraud_detector.joblib")
    
    # Load and verify
    new_trainer = ModelTrainer(config)
    new_trainer.load("models/fraud_detector.joblib")
    print("\nModel save/load successful!")
