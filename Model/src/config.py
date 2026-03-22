"""
Configuration Management Module
Author: Manan Monani
================================

This module handles loading and managing configuration settings from YAML files.
Provides a singleton configuration object for easy access throughout the pipeline.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from loguru import logger


@dataclass
class DataConfig:
    """Data-related configuration settings."""
    raw_data_path: str = "data/raw/creditcard.csv"
    processed_data_path: str = "data/processed/"
    test_size: float = 0.2
    validation_size: float = 0.1
    random_state: int = 42


@dataclass
class FeatureConfig:
    """Feature engineering configuration settings."""
    drop_columns: list = field(default_factory=list)
    target_column: str = "Class"
    scaling_method: str = "robust"
    feature_selection_enabled: bool = True
    feature_selection_method: str = "importance"
    n_features: int = 20


@dataclass
class ModelConfig:
    """Model configuration settings."""
    primary_model: str = "xgboost"
    use_ensemble: bool = True
    ensemble_models: list = field(default_factory=lambda: ["random_forest", "xgboost", "lightgbm"])
    hyperparameter_tuning_enabled: bool = True
    hyperparameter_tuning_method: str = "optuna"
    n_trials: int = 50
    cv_folds: int = 5


@dataclass
class ImbalanceConfig:
    """Class imbalance handling configuration."""
    method: str = "smote"
    sampling_strategy: float = 0.5


@dataclass
class TrainingConfig:
    """Training configuration settings."""
    epochs: int = 100
    batch_size: int = 256
    early_stopping_enabled: bool = True
    early_stopping_patience: int = 10
    early_stopping_min_delta: float = 0.001
    cross_validation_enabled: bool = True
    cv_n_folds: int = 5
    cv_stratified: bool = True


@dataclass
class EvaluationConfig:
    """Evaluation configuration settings."""
    metrics: list = field(default_factory=lambda: [
        "accuracy", "precision", "recall", "f1", "roc_auc", "pr_auc"
    ])
    threshold_optimization_enabled: bool = True
    threshold_optimization_method: str = "f1"
    save_plots: bool = True
    plots_path: str = "logs/plots/"


@dataclass
class APIConfig:
    """API configuration settings."""
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = False
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 100
    include_probability: bool = True
    include_feature_importance: bool = False


@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    level: str = "INFO"
    log_file: str = "logs/training.log"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class Config:
    """
    Configuration management class.
    
    Loads and provides access to all configuration settings from YAML files.
    Implements a singleton pattern for consistent configuration access.
    
    Usage:
        config = Config("configs/config.yaml")
        print(config.data.raw_data_path)
        print(config.model.primary_model)
    """
    
    _instance: Optional['Config'] = None
    _initialized: bool = False
    
    def __new__(cls, config_path: Optional[str] = None):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration from YAML file.
        
        Args:
            config_path: Path to the YAML configuration file.
        """
        if self._initialized and config_path is None:
            return
            
        self.base_path = Path(__file__).parent.parent
        
        if config_path is None:
            config_path = self.base_path / "configs" / "config.yaml"
        else:
            config_path = Path(config_path)
            if not config_path.is_absolute():
                config_path = self.base_path / config_path
        
        self.config_path = config_path
        self._raw_config: Dict[str, Any] = {}
        
        self._load_config()
        self._parse_config()
        
        Config._initialized = True
        logger.info(f"Configuration loaded from {self.config_path}")
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            logger.warning(f"Config file not found at {self.config_path}. Using defaults.")
            self._raw_config = {}
            return
            
        try:
            with open(self.config_path, 'r') as f:
                self._raw_config = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            logger.error(f"Error parsing config file: {e}")
            raise ValueError(f"Invalid YAML configuration: {e}")
    
    def _parse_config(self) -> None:
        """Parse raw configuration into dataclass objects."""
        # Data configuration
        data_cfg = self._raw_config.get('data', {})
        self.data = DataConfig(
            raw_data_path=data_cfg.get('raw_data_path', 'data/raw/creditcard.csv'),
            processed_data_path=data_cfg.get('processed_data_path', 'data/processed/'),
            test_size=data_cfg.get('test_size', 0.2),
            validation_size=data_cfg.get('validation_size', 0.1),
            random_state=data_cfg.get('random_state', 42)
        )
        
        # Feature configuration
        feat_cfg = self._raw_config.get('features', {})
        feat_sel = feat_cfg.get('feature_selection', {})
        self.features = FeatureConfig(
            drop_columns=feat_cfg.get('drop_columns', []),
            target_column=feat_cfg.get('target_column', 'Class'),
            scaling_method=feat_cfg.get('scaling_method', 'robust'),
            feature_selection_enabled=feat_sel.get('enabled', True),
            feature_selection_method=feat_sel.get('method', 'importance'),
            n_features=feat_sel.get('n_features', 20)
        )
        
        # Model configuration
        model_cfg = self._raw_config.get('model', {})
        hp_cfg = model_cfg.get('hyperparameter_tuning', {})
        self.model = ModelConfig(
            primary_model=model_cfg.get('primary_model', 'xgboost'),
            use_ensemble=model_cfg.get('use_ensemble', True),
            ensemble_models=model_cfg.get('ensemble_models', ['random_forest', 'xgboost', 'lightgbm']),
            hyperparameter_tuning_enabled=hp_cfg.get('enabled', True),
            hyperparameter_tuning_method=hp_cfg.get('method', 'optuna'),
            n_trials=hp_cfg.get('n_trials', 50),
            cv_folds=hp_cfg.get('cv_folds', 5)
        )
        
        # Imbalance configuration
        imb_cfg = self._raw_config.get('imbalance', {})
        self.imbalance = ImbalanceConfig(
            method=imb_cfg.get('method', 'smote'),
            sampling_strategy=imb_cfg.get('sampling_strategy', 0.5)
        )
        
        # Training configuration
        train_cfg = self._raw_config.get('training', {})
        es_cfg = train_cfg.get('early_stopping', {})
        cv_cfg = train_cfg.get('cross_validation', {})
        self.training = TrainingConfig(
            epochs=train_cfg.get('epochs', 100),
            batch_size=train_cfg.get('batch_size', 256),
            early_stopping_enabled=es_cfg.get('enabled', True),
            early_stopping_patience=es_cfg.get('patience', 10),
            early_stopping_min_delta=es_cfg.get('min_delta', 0.001),
            cross_validation_enabled=cv_cfg.get('enabled', True),
            cv_n_folds=cv_cfg.get('n_folds', 5),
            cv_stratified=cv_cfg.get('stratified', True)
        )
        
        # Evaluation configuration
        eval_cfg = self._raw_config.get('evaluation', {})
        thresh_cfg = eval_cfg.get('threshold_optimization', {})
        self.evaluation = EvaluationConfig(
            metrics=eval_cfg.get('metrics', ['accuracy', 'precision', 'recall', 'f1', 'roc_auc', 'pr_auc']),
            threshold_optimization_enabled=thresh_cfg.get('enabled', True),
            threshold_optimization_method=thresh_cfg.get('method', 'f1'),
            save_plots=eval_cfg.get('save_plots', True),
            plots_path=eval_cfg.get('plots_path', 'logs/plots/')
        )
        
        # API configuration
        api_cfg = self._raw_config.get('api', {})
        rate_cfg = api_cfg.get('rate_limit', {})
        resp_cfg = api_cfg.get('response', {})
        self.api = APIConfig(
            host=api_cfg.get('host', '0.0.0.0'),
            port=api_cfg.get('port', 5000),
            debug=api_cfg.get('debug', False),
            rate_limit_enabled=rate_cfg.get('enabled', True),
            rate_limit_requests_per_minute=rate_cfg.get('requests_per_minute', 100),
            include_probability=resp_cfg.get('include_probability', True),
            include_feature_importance=resp_cfg.get('include_feature_importance', False)
        )
        
        # Logging configuration
        log_cfg = self._raw_config.get('logging', {})
        self.logging = LoggingConfig(
            level=log_cfg.get('level', 'INFO'),
            log_file=log_cfg.get('log_file', 'logs/training.log'),
            format=log_cfg.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by dot-notation key.
        
        Args:
            key: Dot-notation key (e.g., 'data.raw_data_path')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self._raw_config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_absolute_path(self, relative_path: str) -> Path:
        """
        Convert a relative path to absolute path based on project root.
        
        Args:
            relative_path: Path relative to project root
            
        Returns:
            Absolute path
        """
        path = Path(relative_path)
        if path.is_absolute():
            return path
        return self.base_path / path
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Configuration as nested dictionary
        """
        return self._raw_config.copy()
    
    def __repr__(self) -> str:
        """String representation of configuration."""
        return f"Config(path={self.config_path})"


def setup_logging(config: Config) -> None:
    """
    Setup logging based on configuration.
    
    Args:
        config: Configuration object
    """
    log_config = config.logging
    log_path = config.get_absolute_path(log_config.log_file)
    
    # Create log directory if it doesn't exist
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure loguru
    logger.remove()  # Remove default handler
    
    # Add console handler
    logger.add(
        sink=lambda msg: print(msg, end=''),
        level=log_config.level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # Add file handler
    logger.add(
        sink=str(log_path),
        level=log_config.level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="7 days"
    )
    
    logger.info("Logging configured successfully")


if __name__ == "__main__":
    # Test configuration loading
    config = Config()
    setup_logging(config)
    
    print(f"Data path: {config.data.raw_data_path}")
    print(f"Primary model: {config.model.primary_model}")
    print(f"API port: {config.api.port}")
