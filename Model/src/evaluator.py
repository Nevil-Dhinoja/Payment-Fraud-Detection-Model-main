"""
Model Evaluator Module
Author: Manan Monani
=======================

This module handles comprehensive model evaluation including:
- Classification metrics (accuracy, precision, recall, F1, etc.)
- ROC curves and PR curves
- Confusion matrix analysis
- Threshold optimization
- Business metrics (cost analysis)

Generates publication-quality visualizations.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from loguru import logger

# Scikit-learn metrics
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    classification_report,
    precision_recall_curve,
    roc_curve,
    matthews_corrcoef,
    balanced_accuracy_score,
)

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns

from src.config import Config


class Evaluator:
    """
    Comprehensive model evaluation class.
    
    Provides:
    - Multiple classification metrics
    - Threshold optimization
    - Visualization of results
    - Cost-based analysis
    
    Attributes:
        config: Configuration object
        metrics: Dictionary of computed metrics
        optimal_threshold: Optimal classification threshold
        
    Usage:
        evaluator = Evaluator()
        metrics = evaluator.evaluate(y_true, y_pred, y_proba)
        evaluator.plot_all(y_true, y_proba)
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize Evaluator.
        
        Args:
            config: Configuration object. If None, loads default config.
        """
        self.config = config or Config()
        
        self.metrics: Dict[str, float] = {}
        self.optimal_threshold: float = 0.5
        self.confusion_mat: Optional[np.ndarray] = None
        
        # Set plot style
        plt.style.use('seaborn-v0_8-whitegrid')
        sns.set_palette("husl")
        
        logger.info("Evaluator initialized")
    
    def compute_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: Optional[np.ndarray] = None
    ) -> Dict[str, float]:
        """
        Compute comprehensive classification metrics.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_proba: Prediction probabilities (for positive class)
            
        Returns:
            Dictionary of metrics
        """
        logger.info("Computing classification metrics...")
        
        self.metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'balanced_accuracy': balanced_accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, zero_division=0),
            'recall': recall_score(y_true, y_pred, zero_division=0),
            'f1': f1_score(y_true, y_pred, zero_division=0),
            'mcc': matthews_corrcoef(y_true, y_pred),
        }
        
        # Probability-based metrics
        if y_proba is not None:
            self.metrics['roc_auc'] = roc_auc_score(y_true, y_proba)
            self.metrics['pr_auc'] = average_precision_score(y_true, y_proba)
        
        # Confusion matrix derived metrics
        self.confusion_mat = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = self.confusion_mat.ravel()
        
        self.metrics['true_positives'] = int(tp)
        self.metrics['true_negatives'] = int(tn)
        self.metrics['false_positives'] = int(fp)
        self.metrics['false_negatives'] = int(fn)
        
        # Specificity (True Negative Rate)
        self.metrics['specificity'] = tn / (tn + fp) if (tn + fp) > 0 else 0
        
        # False Positive Rate
        self.metrics['false_positive_rate'] = fp / (fp + tn) if (fp + tn) > 0 else 0
        
        # Negative Predictive Value
        self.metrics['npv'] = tn / (tn + fn) if (tn + fn) > 0 else 0
        
        logger.success("Metrics computed successfully")
        
        return self.metrics
    
    def find_optimal_threshold(
        self,
        y_true: np.ndarray,
        y_proba: np.ndarray,
        method: str = 'f1'
    ) -> Tuple[float, Dict[str, float]]:
        """
        Find the optimal classification threshold.
        
        Args:
            y_true: True labels
            y_proba: Prediction probabilities (for positive class)
            method: Optimization method ('f1', 'youden', 'cost')
            
        Returns:
            Tuple of (optimal threshold, metrics at optimal threshold)
        """
        logger.info(f"Finding optimal threshold using method: {method}")
        
        thresholds = np.linspace(0.01, 0.99, 99)
        best_threshold = 0.5
        best_score = 0
        
        if method == 'f1':
            for threshold in thresholds:
                y_pred = (y_proba >= threshold).astype(int)
                score = f1_score(y_true, y_pred, zero_division=0)
                if score > best_score:
                    best_score = score
                    best_threshold = threshold
        
        elif method == 'youden':
            # Youden's J statistic: Sensitivity + Specificity - 1
            fpr, tpr, thresh = roc_curve(y_true, y_proba)
            j_scores = tpr - fpr
            best_idx = np.argmax(j_scores)
            best_threshold = thresh[best_idx]
        
        elif method == 'cost':
            # Cost-based optimization
            # Assuming FN is 10x more costly than FP (missing fraud is worse)
            cost_fn = 10
            cost_fp = 1
            
            for threshold in thresholds:
                y_pred = (y_proba >= threshold).astype(int)
                cm = confusion_matrix(y_true, y_pred)
                tn, fp, fn, tp = cm.ravel()
                cost = cost_fn * fn + cost_fp * fp
                if best_score == 0 or cost < best_score:
                    best_score = cost
                    best_threshold = threshold
        
        else:
            logger.warning(f"Unknown method '{method}'. Using default threshold 0.5")
        
        self.optimal_threshold = best_threshold
        
        # Compute metrics at optimal threshold
        y_pred_optimal = (y_proba >= best_threshold).astype(int)
        optimal_metrics = self.compute_metrics(y_true, y_pred_optimal, y_proba)
        
        logger.info(f"Optimal threshold: {best_threshold:.4f}")
        
        return best_threshold, optimal_metrics
    
    def evaluate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: Optional[np.ndarray] = None,
        optimize_threshold: bool = True
    ) -> Dict[str, float]:
        """
        Complete evaluation pipeline.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_proba: Prediction probabilities
            optimize_threshold: Whether to find optimal threshold
            
        Returns:
            Dictionary of all metrics
        """
        # Compute basic metrics
        self.compute_metrics(y_true, y_pred, y_proba)
        
        # Optimize threshold if probabilities available
        if y_proba is not None and optimize_threshold:
            method = self.config.evaluation.threshold_optimization_method
            optimal_thresh, _ = self.find_optimal_threshold(y_true, y_proba, method)
            self.metrics['optimal_threshold'] = optimal_thresh
        
        return self.metrics
    
    def print_report(self, y_true: np.ndarray, y_pred: np.ndarray) -> None:
        """
        Print a formatted classification report.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
        """
        print("\n" + "="*60)
        print("📊 CLASSIFICATION REPORT")
        print("="*60)
        
        # Sklearn classification report
        print("\n" + classification_report(
            y_true, y_pred,
            target_names=['Legitimate', 'Fraud'],
            digits=4
        ))
        
        # Additional metrics
        if self.metrics:
            print("\n📈 Additional Metrics:")
            print("-"*40)
            for key, value in self.metrics.items():
                if isinstance(value, float):
                    print(f"  {key.replace('_', ' ').title()}: {value:.4f}")
                else:
                    print(f"  {key.replace('_', ' ').title()}: {value}")
        
        print("="*60 + "\n")
    
    def plot_confusion_matrix(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        save_path: Optional[str] = None,
        figsize: Tuple[int, int] = (8, 6)
    ) -> plt.Figure:
        """
        Plot confusion matrix.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            save_path: Path to save the figure
            figsize: Figure size
            
        Returns:
            Matplotlib figure
        """
        cm = confusion_matrix(y_true, y_pred)
        
        fig, ax = plt.subplots(figsize=figsize)
        
        sns.heatmap(
            cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=['Legitimate', 'Fraud'],
            yticklabels=['Legitimate', 'Fraud'],
            ax=ax,
            annot_kws={'size': 14}
        )
        
        ax.set_xlabel('Predicted Label', fontsize=12)
        ax.set_ylabel('True Label', fontsize=12)
        ax.set_title('Confusion Matrix', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Confusion matrix saved to {save_path}")
        
        return fig
    
    def plot_roc_curve(
        self,
        y_true: np.ndarray,
        y_proba: np.ndarray,
        save_path: Optional[str] = None,
        figsize: Tuple[int, int] = (8, 6)
    ) -> plt.Figure:
        """
        Plot ROC curve.
        
        Args:
            y_true: True labels
            y_proba: Prediction probabilities
            save_path: Path to save the figure
            figsize: Figure size
            
        Returns:
            Matplotlib figure
        """
        fpr, tpr, thresholds = roc_curve(y_true, y_proba)
        roc_auc = roc_auc_score(y_true, y_proba)
        
        fig, ax = plt.subplots(figsize=figsize)
        
        ax.plot(fpr, tpr, color='#2196F3', lw=2, label=f'ROC Curve (AUC = {roc_auc:.4f})')
        ax.plot([0, 1], [0, 1], color='gray', lw=1, linestyle='--', label='Random Classifier')
        
        # Mark optimal threshold point
        if hasattr(self, 'optimal_threshold'):
            optimal_idx = np.argmin(np.abs(thresholds - self.optimal_threshold))
            ax.scatter(
                fpr[optimal_idx], tpr[optimal_idx],
                color='red', s=100, zorder=5,
                label=f'Optimal Threshold ({self.optimal_threshold:.3f})'
            )
        
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        ax.set_xlabel('False Positive Rate', fontsize=12)
        ax.set_ylabel('True Positive Rate', fontsize=12)
        ax.set_title('Receiver Operating Characteristic (ROC) Curve', fontsize=14, fontweight='bold')
        ax.legend(loc='lower right')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"ROC curve saved to {save_path}")
        
        return fig
    
    def plot_precision_recall_curve(
        self,
        y_true: np.ndarray,
        y_proba: np.ndarray,
        save_path: Optional[str] = None,
        figsize: Tuple[int, int] = (8, 6)
    ) -> plt.Figure:
        """
        Plot Precision-Recall curve.
        
        Args:
            y_true: True labels
            y_proba: Prediction probabilities
            save_path: Path to save the figure
            figsize: Figure size
            
        Returns:
            Matplotlib figure
        """
        precision, recall, thresholds = precision_recall_curve(y_true, y_proba)
        pr_auc = average_precision_score(y_true, y_proba)
        
        fig, ax = plt.subplots(figsize=figsize)
        
        ax.plot(recall, precision, color='#4CAF50', lw=2, label=f'PR Curve (AUC = {pr_auc:.4f})')
        
        # Baseline (random classifier)
        baseline = np.mean(y_true)
        ax.axhline(y=baseline, color='gray', linestyle='--', label=f'Baseline ({baseline:.4f})')
        
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        ax.set_xlabel('Recall', fontsize=12)
        ax.set_ylabel('Precision', fontsize=12)
        ax.set_title('Precision-Recall Curve', fontsize=14, fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"PR curve saved to {save_path}")
        
        return fig
    
    def plot_threshold_metrics(
        self,
        y_true: np.ndarray,
        y_proba: np.ndarray,
        save_path: Optional[str] = None,
        figsize: Tuple[int, int] = (10, 6)
    ) -> plt.Figure:
        """
        Plot metrics across different thresholds.
        
        Args:
            y_true: True labels
            y_proba: Prediction probabilities
            save_path: Path to save the figure
            figsize: Figure size
            
        Returns:
            Matplotlib figure
        """
        thresholds = np.linspace(0.01, 0.99, 50)
        precisions = []
        recalls = []
        f1_scores = []
        
        for threshold in thresholds:
            y_pred = (y_proba >= threshold).astype(int)
            precisions.append(precision_score(y_true, y_pred, zero_division=0))
            recalls.append(recall_score(y_true, y_pred, zero_division=0))
            f1_scores.append(f1_score(y_true, y_pred, zero_division=0))
        
        fig, ax = plt.subplots(figsize=figsize)
        
        ax.plot(thresholds, precisions, label='Precision', color='#2196F3', lw=2)
        ax.plot(thresholds, recalls, label='Recall', color='#4CAF50', lw=2)
        ax.plot(thresholds, f1_scores, label='F1 Score', color='#FF9800', lw=2)
        
        # Mark optimal threshold
        if hasattr(self, 'optimal_threshold'):
            ax.axvline(x=self.optimal_threshold, color='red', linestyle='--', 
                      label=f'Optimal Threshold ({self.optimal_threshold:.3f})')
        
        ax.set_xlabel('Threshold', fontsize=12)
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title('Metrics vs. Classification Threshold', fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0, 1])
        ax.set_ylim([0, 1.05])
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Threshold metrics plot saved to {save_path}")
        
        return fig
    
    def plot_feature_importance(
        self,
        feature_importance_df: pd.DataFrame,
        top_n: int = 20,
        save_path: Optional[str] = None,
        figsize: Tuple[int, int] = (10, 8)
    ) -> plt.Figure:
        """
        Plot feature importance.
        
        Args:
            feature_importance_df: DataFrame with 'feature' and 'importance' columns
            top_n: Number of top features to show
            save_path: Path to save the figure
            figsize: Figure size
            
        Returns:
            Matplotlib figure
        """
        df = feature_importance_df.head(top_n).copy()
        df = df.sort_values('importance', ascending=True)
        
        fig, ax = plt.subplots(figsize=figsize)
        
        colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(df)))
        
        ax.barh(df['feature'], df['importance'], color=colors)
        
        ax.set_xlabel('Importance', fontsize=12)
        ax.set_ylabel('Feature', fontsize=12)
        ax.set_title(f'Top {top_n} Feature Importances', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Feature importance plot saved to {save_path}")
        
        return fig
    
    def plot_all(
        self,
        y_true: np.ndarray,
        y_proba: np.ndarray,
        y_pred: Optional[np.ndarray] = None,
        feature_importance_df: Optional[pd.DataFrame] = None,
        save_dir: Optional[str] = None
    ) -> None:
        """
        Generate all evaluation plots.
        
        Args:
            y_true: True labels
            y_proba: Prediction probabilities
            y_pred: Predicted labels (if None, uses optimal threshold)
            feature_importance_df: Feature importance DataFrame
            save_dir: Directory to save plots
        """
        if save_dir:
            save_dir = Path(save_dir)
            save_dir.mkdir(parents=True, exist_ok=True)
        
        if y_pred is None:
            y_pred = (y_proba >= self.optimal_threshold).astype(int)
        
        # Confusion Matrix
        self.plot_confusion_matrix(
            y_true, y_pred,
            save_path=str(save_dir / 'confusion_matrix.png') if save_dir else None
        )
        
        # ROC Curve
        self.plot_roc_curve(
            y_true, y_proba,
            save_path=str(save_dir / 'roc_curve.png') if save_dir else None
        )
        
        # PR Curve
        self.plot_precision_recall_curve(
            y_true, y_proba,
            save_path=str(save_dir / 'pr_curve.png') if save_dir else None
        )
        
        # Threshold Metrics
        self.plot_threshold_metrics(
            y_true, y_proba,
            save_path=str(save_dir / 'threshold_metrics.png') if save_dir else None
        )
        
        # Feature Importance
        if feature_importance_df is not None and not feature_importance_df.empty:
            self.plot_feature_importance(
                feature_importance_df,
                save_path=str(save_dir / 'feature_importance.png') if save_dir else None
            )
        
        if save_dir:
            logger.success(f"All plots saved to {save_dir}")
        
        plt.show()
    
    def get_metrics_df(self) -> pd.DataFrame:
        """
        Get metrics as a DataFrame.
        
        Returns:
            DataFrame with metrics
        """
        return pd.DataFrame([self.metrics])
    
    def save_report(self, path: Union[str, Path]) -> None:
        """
        Save evaluation report to file.
        
        Args:
            path: Path to save the report
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            'metrics': self.metrics,
            'optimal_threshold': self.optimal_threshold,
            'confusion_matrix': self.confusion_mat.tolist() if self.confusion_mat is not None else None,
        }
        
        df = pd.DataFrame([self.metrics])
        df.to_csv(path, index=False)
        
        logger.info(f"Evaluation report saved to {path}")


if __name__ == "__main__":
    # Test evaluator
    from src.data_loader import SyntheticDataGenerator
    from src.preprocessor import Preprocessor
    from src.model_trainer import ModelTrainer
    
    config = Config()
    
    # Generate and prepare data
    generator = SyntheticDataGenerator(n_samples=10000)
    df = generator.generate()
    
    X = df.drop(columns=['Class'])
    y = df['Class']
    
    preprocessor = Preprocessor(config)
    X_train, X_test, y_train, y_test, _, _ = preprocessor.fit_transform(X, y, apply_resampling=True)
    
    # Train model
    trainer = ModelTrainer(config)
    trainer.train(X_train, y_train, use_ensemble=False)
    
    # Get predictions
    y_pred = trainer.predict(X_test)
    y_proba = trainer.predict_proba(X_test)[:, 1]
    
    # Evaluate
    evaluator = Evaluator(config)
    metrics = evaluator.evaluate(y_test, y_pred, y_proba)
    
    # Print report
    evaluator.print_report(y_test, y_pred)
    
    # Get feature importance
    feature_importance = trainer.get_feature_importance(list(X.columns))
    
    # Plot all
    evaluator.plot_all(y_test, y_proba, y_pred, feature_importance, save_dir='logs/plots')
    
    # Save report
    evaluator.save_report('logs/evaluation_report.csv')
