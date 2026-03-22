"""
Feature Engineering Module
Author: Manan Monani
===========================

This module handles advanced feature engineering including:
- Feature creation (aggregations, interactions, etc.)
- Feature selection (importance-based, correlation, RFE)
- Dimensionality reduction (PCA, feature importance)
- Time-based feature engineering

Designed for credit card fraud detection datasets.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from loguru import logger
from sklearn.feature_selection import (
    SelectKBest,
    f_classif,
    mutual_info_classif,
    RFE,
    SelectFromModel,
)
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
import joblib

from src.config import Config


class FeatureEngineer:
    """
    Feature engineering class for fraud detection.
    
    Handles:
    - Feature creation and transformation
    - Feature selection using multiple methods
    - Time-based feature engineering
    - Feature importance analysis
    
    Attributes:
        config: Configuration object
        selected_features: List of selected feature names
        feature_importances: Dictionary of feature importances
        
    Usage:
        engineer = FeatureEngineer()
        X_engineered = engineer.fit_transform(X, y)
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize FeatureEngineer.
        
        Args:
            config: Configuration object. If None, loads default config.
        """
        self.config = config or Config()
        
        self.selected_features: List[str] = []
        self.feature_importances: Dict[str, float] = {}
        self.selector = None
        self.pca = None
        
        self._is_fitted = False
        self._original_features: List[str] = []
        
        logger.info("FeatureEngineer initialized")
    
    def create_time_features(self, df: pd.DataFrame, time_column: str = 'Time') -> pd.DataFrame:
        """
        Create time-based features from the Time column.
        
        The Time column in the credit card dataset represents seconds elapsed
        from the first transaction in the dataset.
        
        Args:
            df: Input DataFrame
            time_column: Name of the time column
            
        Returns:
            DataFrame with additional time features
        """
        if time_column not in df.columns:
            logger.warning(f"Time column '{time_column}' not found. Skipping time features.")
            return df
        
        df = df.copy()
        
        # Hour of the day (assuming first transaction at midnight)
        df['Hour'] = (df[time_column] / 3600) % 24
        
        # Time bins (night, morning, afternoon, evening)
        df['TimeBin'] = pd.cut(
            df['Hour'],
            bins=[0, 6, 12, 18, 24],
            labels=['Night', 'Morning', 'Afternoon', 'Evening'],
            include_lowest=True
        )
        
        # Convert TimeBin to numeric for ML models
        time_bin_map = {'Night': 0, 'Morning': 1, 'Afternoon': 2, 'Evening': 3}
        df['TimeBin'] = df['TimeBin'].map(time_bin_map)
        
        # Is weekend (rough approximation - every 2 days)
        df['IsWeekend'] = ((df[time_column] / 86400) % 7 >= 5).astype(int)
        
        # Transaction velocity (transactions per hour window)
        df['TimeHour'] = (df[time_column] / 3600).astype(int)
        
        logger.info("Created time-based features: Hour, TimeBin, IsWeekend, TimeHour")
        
        return df
    
    def create_amount_features(self, df: pd.DataFrame, amount_column: str = 'Amount') -> pd.DataFrame:
        """
        Create amount-based features.
        
        Args:
            df: Input DataFrame
            amount_column: Name of the amount column
            
        Returns:
            DataFrame with additional amount features
        """
        if amount_column not in df.columns:
            logger.warning(f"Amount column '{amount_column}' not found. Skipping amount features.")
            return df
        
        df = df.copy()
        
        # Log-transformed amount (handles skewness)
        df['Amount_Log'] = np.log1p(df[amount_column])
        
        # Amount bins
        df['Amount_Bin'] = pd.qcut(
            df[amount_column],
            q=5,
            labels=['Very_Low', 'Low', 'Medium', 'High', 'Very_High'],
            duplicates='drop'
        )
        
        # Convert to numeric
        amount_bin_map = {'Very_Low': 0, 'Low': 1, 'Medium': 2, 'High': 3, 'Very_High': 4}
        df['Amount_Bin'] = df['Amount_Bin'].map(amount_bin_map).fillna(2)  # Default to Medium
        
        # Amount percentile
        df['Amount_Percentile'] = df[amount_column].rank(pct=True)
        
        # Is high amount (top 5%)
        threshold = df[amount_column].quantile(0.95)
        df['Is_High_Amount'] = (df[amount_column] > threshold).astype(int)
        
        # Amount deviation from mean
        df['Amount_Zscore'] = (df[amount_column] - df[amount_column].mean()) / df[amount_column].std()
        
        logger.info("Created amount-based features: Amount_Log, Amount_Bin, Amount_Percentile, Is_High_Amount, Amount_Zscore")
        
        return df
    
    def create_pca_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create interaction features from PCA components.
        
        The V1-V28 columns are PCA-transformed features. This method creates
        meaningful interactions between them.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with interaction features
        """
        df = df.copy()
        pca_cols = [col for col in df.columns if col.startswith('V')]
        
        if len(pca_cols) < 2:
            logger.warning("Not enough PCA columns found. Skipping interaction features.")
            return df
        
        # Create interactions between top PCA components
        # V1 and V2 are typically the most important
        if 'V1' in df.columns and 'V2' in df.columns:
            df['V1_V2_Interaction'] = df['V1'] * df['V2']
        
        if 'V1' in df.columns and 'V3' in df.columns:
            df['V1_V3_Interaction'] = df['V1'] * df['V3']
        
        # Sum of absolute values of top PCA components
        top_pca = ['V1', 'V2', 'V3', 'V4', 'V5']
        existing_top_pca = [col for col in top_pca if col in df.columns]
        if existing_top_pca:
            df['PCA_Sum_Abs'] = df[existing_top_pca].abs().sum(axis=1)
            df['PCA_Mean'] = df[existing_top_pca].mean(axis=1)
            df['PCA_Std'] = df[existing_top_pca].std(axis=1)
        
        # Distance from origin in PCA space
        if pca_cols:
            df['PCA_Distance'] = np.sqrt((df[pca_cols] ** 2).sum(axis=1))
        
        logger.info("Created PCA interaction features")
        
        return df
    
    def create_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all feature engineering steps.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with all engineered features
        """
        logger.info("Starting feature engineering...")
        
        df = self.create_time_features(df)
        df = self.create_amount_features(df)
        df = self.create_pca_interaction_features(df)
        
        logger.success(f"Feature engineering complete. New shape: {df.shape}")
        
        return df
    
    def select_features_by_importance(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        n_features: Optional[int] = None
    ) -> Tuple[pd.DataFrame, Dict[str, float]]:
        """
        Select features using Random Forest feature importance.
        
        Args:
            X: Feature DataFrame
            y: Target Series
            n_features: Number of features to select
            
        Returns:
            Tuple of (selected features DataFrame, feature importances dict)
        """
        n_features = n_features or self.config.features.n_features
        n_features = min(n_features, X.shape[1])
        
        logger.info(f"Selecting top {n_features} features by importance...")
        
        # Train a Random Forest to get feature importances
        rf = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=self.config.data.random_state,
            n_jobs=-1
        )
        rf.fit(X, y)
        
        # Get feature importances
        importances = pd.Series(rf.feature_importances_, index=X.columns)
        importances = importances.sort_values(ascending=False)
        
        self.feature_importances = importances.to_dict()
        
        # Select top features
        self.selected_features = importances.head(n_features).index.tolist()
        
        # Use SelectFromModel for consistent API
        self.selector = SelectFromModel(
            rf,
            max_features=n_features,
            prefit=True
        )
        
        logger.info(f"Top 5 features: {self.selected_features[:5]}")
        
        return X[self.selected_features], self.feature_importances
    
    def select_features_by_correlation(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        n_features: Optional[int] = None
    ) -> Tuple[pd.DataFrame, Dict[str, float]]:
        """
        Select features using correlation with target.
        
        Args:
            X: Feature DataFrame
            y: Target Series
            n_features: Number of features to select
            
        Returns:
            Tuple of (selected features DataFrame, correlation scores dict)
        """
        n_features = n_features or self.config.features.n_features
        n_features = min(n_features, X.shape[1])
        
        logger.info(f"Selecting top {n_features} features by correlation...")
        
        # Calculate correlation with target
        correlations = X.apply(lambda x: abs(x.corr(y)))
        correlations = correlations.sort_values(ascending=False)
        
        self.feature_importances = correlations.to_dict()
        self.selected_features = correlations.head(n_features).index.tolist()
        
        logger.info(f"Top 5 correlated features: {self.selected_features[:5]}")
        
        return X[self.selected_features], self.feature_importances
    
    def select_features_by_mutual_info(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        n_features: Optional[int] = None
    ) -> Tuple[pd.DataFrame, Dict[str, float]]:
        """
        Select features using mutual information.
        
        Args:
            X: Feature DataFrame
            y: Target Series
            n_features: Number of features to select
            
        Returns:
            Tuple of (selected features DataFrame, mutual info scores dict)
        """
        n_features = n_features or self.config.features.n_features
        n_features = min(n_features, X.shape[1])
        
        logger.info(f"Selecting top {n_features} features by mutual information...")
        
        # Calculate mutual information
        self.selector = SelectKBest(mutual_info_classif, k=n_features)
        self.selector.fit(X, y)
        
        # Get scores
        scores = pd.Series(self.selector.scores_, index=X.columns)
        scores = scores.sort_values(ascending=False)
        
        self.feature_importances = scores.to_dict()
        self.selected_features = scores.head(n_features).index.tolist()
        
        logger.info(f"Top 5 features by MI: {self.selected_features[:5]}")
        
        return X[self.selected_features], self.feature_importances
    
    def select_features_by_rfe(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        n_features: Optional[int] = None
    ) -> Tuple[pd.DataFrame, Dict[str, float]]:
        """
        Select features using Recursive Feature Elimination.
        
        Args:
            X: Feature DataFrame
            y: Target Series
            n_features: Number of features to select
            
        Returns:
            Tuple of (selected features DataFrame, feature rankings dict)
        """
        n_features = n_features or self.config.features.n_features
        n_features = min(n_features, X.shape[1])
        
        logger.info(f"Selecting top {n_features} features by RFE...")
        
        # Use Random Forest as base estimator
        base_estimator = RandomForestClassifier(
            n_estimators=50,
            max_depth=5,
            random_state=self.config.data.random_state,
            n_jobs=-1
        )
        
        self.selector = RFE(
            estimator=base_estimator,
            n_features_to_select=n_features,
            step=1
        )
        self.selector.fit(X, y)
        
        # Get rankings (1 = selected)
        rankings = pd.Series(self.selector.ranking_, index=X.columns)
        
        # Convert rankings to scores (lower ranking = higher score)
        max_rank = rankings.max()
        scores = (max_rank - rankings + 1) / max_rank
        
        self.feature_importances = scores.to_dict()
        self.selected_features = X.columns[self.selector.support_].tolist()
        
        logger.info(f"Selected features: {self.selected_features[:5]}...")
        
        return X[self.selected_features], self.feature_importances
    
    def select_features(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        method: Optional[str] = None,
        n_features: Optional[int] = None
    ) -> Tuple[pd.DataFrame, Dict[str, float]]:
        """
        Select features using the specified method.
        
        Args:
            X: Feature DataFrame
            y: Target Series
            method: Selection method ('importance', 'correlation', 'mutual_info', 'rfe')
            n_features: Number of features to select
            
        Returns:
            Tuple of (selected features DataFrame, feature scores dict)
        """
        method = method or self.config.features.feature_selection_method
        
        selection_methods = {
            'importance': self.select_features_by_importance,
            'correlation': self.select_features_by_correlation,
            'mutual_info': self.select_features_by_mutual_info,
            'rfe': self.select_features_by_rfe,
        }
        
        if method not in selection_methods:
            logger.warning(f"Unknown method '{method}'. Using 'importance'.")
            method = 'importance'
        
        return selection_methods[method](X, y, n_features)
    
    def fit(self, X: pd.DataFrame, y: pd.Series) -> 'FeatureEngineer':
        """
        Fit the feature engineer.
        
        Args:
            X: Feature DataFrame
            y: Target Series
            
        Returns:
            Self
        """
        logger.info("Fitting feature engineer...")
        
        self._original_features = list(X.columns)
        
        # Create features
        X_engineered = self.create_all_features(X)
        
        # Select features if enabled
        if self.config.features.feature_selection_enabled:
            X_selected, _ = self.select_features(X_engineered, y)
            self.selected_features = list(X_selected.columns)
        else:
            self.selected_features = list(X_engineered.columns)
        
        self._is_fitted = True
        logger.success("Feature engineer fitted successfully")
        
        return self
    
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transform data using fitted feature engineer.
        
        Args:
            X: Feature DataFrame
            
        Returns:
            Transformed DataFrame
        """
        if not self._is_fitted:
            raise ValueError("FeatureEngineer not fitted. Call fit() first.")
        
        # Create features
        X_engineered = self.create_all_features(X)
        
        # Select features
        available_features = [f for f in self.selected_features if f in X_engineered.columns]
        
        if len(available_features) != len(self.selected_features):
            missing = set(self.selected_features) - set(available_features)
            logger.warning(f"Missing features in transform: {missing}")
        
        return X_engineered[available_features]
    
    def fit_transform(self, X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
        """
        Fit and transform in one step.
        
        Args:
            X: Feature DataFrame
            y: Target Series
            
        Returns:
            Transformed DataFrame
        """
        self.fit(X, y)
        return self.transform(X)
    
    def get_feature_importance_df(self) -> pd.DataFrame:
        """
        Get feature importances as a DataFrame.
        
        Returns:
            DataFrame with feature names and importance scores
        """
        if not self.feature_importances:
            raise ValueError("No feature importances available. Fit the engineer first.")
        
        df = pd.DataFrame([
            {'feature': k, 'importance': v}
            for k, v in self.feature_importances.items()
        ])
        df = df.sort_values('importance', ascending=False).reset_index(drop=True)
        
        return df
    
    def save(self, path: Union[str, Path]) -> None:
        """
        Save feature engineer to disk.
        
        Args:
            path: Path to save the feature engineer
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        save_dict = {
            'selected_features': self.selected_features,
            'feature_importances': self.feature_importances,
            'selector': self.selector,
            'original_features': self._original_features,
            'is_fitted': self._is_fitted,
        }
        
        joblib.dump(save_dict, path)
        logger.info(f"Feature engineer saved to {path}")
    
    def load(self, path: Union[str, Path]) -> 'FeatureEngineer':
        """
        Load feature engineer from disk.
        
        Args:
            path: Path to load from
            
        Returns:
            Self
        """
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"Feature engineer file not found: {path}")
        
        save_dict = joblib.load(path)
        
        self.selected_features = save_dict['selected_features']
        self.feature_importances = save_dict['feature_importances']
        self.selector = save_dict['selector']
        self._original_features = save_dict['original_features']
        self._is_fitted = save_dict['is_fitted']
        
        logger.info(f"Feature engineer loaded from {path}")
        
        return self


if __name__ == "__main__":
    # Test feature engineer
    from src.data_loader import SyntheticDataGenerator
    
    config = Config()
    
    # Generate synthetic data
    generator = SyntheticDataGenerator(n_samples=10000)
    df = generator.generate()
    
    X = df.drop(columns=['Class'])
    y = df['Class']
    
    # Initialize feature engineer
    engineer = FeatureEngineer(config)
    
    # Fit and transform
    X_transformed = engineer.fit_transform(X, y)
    
    print(f"\nFeature Engineering Results:")
    print(f"Original features: {len(X.columns)}")
    print(f"Transformed features: {len(X_transformed.columns)}")
    print(f"\nSelected features: {engineer.selected_features}")
    
    # Get importance DataFrame
    importance_df = engineer.get_feature_importance_df()
    print(f"\nTop 10 Feature Importances:")
    print(importance_df.head(10))
    
    # Save and load test
    engineer.save("models/feature_engineer.joblib")
    
    new_engineer = FeatureEngineer(config)
    new_engineer.load("models/feature_engineer.joblib")
    print("\nFeature engineer save/load successful!")
