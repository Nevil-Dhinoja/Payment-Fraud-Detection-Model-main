"""
Fraud Detection ML Pipeline
Author: Manan Monani
==========================

A production-grade machine learning pipeline for credit card fraud detection.
This package provides tools for data preprocessing, model training, evaluation,
and serving predictions via a REST API.

Features:
- Automated data preprocessing and feature engineering
- Multiple ML algorithms with ensemble capabilities
- Hyperparameter optimization using Optuna
- Class imbalance handling with SMOTE/ADASYN
- Comprehensive model evaluation metrics
- Production-ready Flask API for model serving
- Extensive logging and monitoring
"""

__version__ = "1.0.0"
__author__ = "Manan Monani"
__email__ = "mmmonani747@gmail.com"
__license__ = "MIT"

from src.config import Config
from src.data_loader import DataLoader
from src.preprocessor import Preprocessor
from src.feature_engineer import FeatureEngineer
from src.model_trainer import ModelTrainer
from src.evaluator import Evaluator
from src.predictor import Predictor

__all__ = [
    "Config",
    "DataLoader", 
    "Preprocessor",
    "FeatureEngineer",
    "ModelTrainer",
    "Evaluator",
    "Predictor",
]
