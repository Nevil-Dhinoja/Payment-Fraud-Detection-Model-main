"""
Main Training Pipeline
Author: Manan Monani
=======================

Complete end-to-end training pipeline for fraud detection model.
This script orchestrates the entire ML pipeline from data loading to model deployment.

Usage:
    python train.py                    # Train with default config
    python train.py --config custom.yaml  # Train with custom config
    python train.py --quick            # Quick training (no optimization)
"""

import argparse
import sys
import time
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
from loguru import logger

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config, setup_logging
from src.data_loader import DataLoader, SyntheticDataGenerator
from src.preprocessor import Preprocessor
from src.feature_engineer import FeatureEngineer
from src.model_trainer import ModelTrainer, ModelComparer
from src.evaluator import Evaluator


def print_banner():
    """Print training banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║        🔍 FRAUD DETECTION ML PIPELINE 🔍                          ║
║                                                                   ║
║        Author: Manan Monani                                       ║
║        Version: 1.0.0                                             ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Fraud Detection Model Training Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        default=None,
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--quick', '-q',
        action='store_true',
        help='Quick training without hyperparameter optimization'
    )
    
    parser.add_argument(
        '--compare',
        action='store_true',
        help='Compare multiple models before training'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default=None,
        choices=['random_forest', 'xgboost', 'lightgbm', 'logistic_regression', 'ensemble'],
        help='Model to train'
    )
    
    parser.add_argument(
        '--synthetic',
        action='store_true',
        help='Use synthetic data for training'
    )
    
    parser.add_argument(
        '--samples',
        type=int,
        default=100000,
        help='Number of synthetic samples (if --synthetic)'
    )
    
    parser.add_argument(
        '--no-plots',
        action='store_true',
        help='Skip generating evaluation plots'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='models',
        help='Output directory for trained models'
    )
    
    return parser.parse_args()


def train_pipeline(args):
    """
    Execute the complete training pipeline.
    
    Steps:
    1. Load configuration
    2. Load data
    3. Preprocess data
    4. Engineer features
    5. Train model
    6. Evaluate model
    7. Save artifacts
    """
    start_time = time.time()
    
    # ===== Step 1: Configuration =====
    logger.info("=" * 60)
    logger.info("STEP 1: Loading Configuration")
    logger.info("=" * 60)
    
    config = Config(args.config)
    setup_logging(config)
    
    # Override config with command line args
    if args.quick:
        config.model.hyperparameter_tuning_enabled = False
        config.model.n_trials = 10
    
    # ===== Step 2: Data Loading =====
    logger.info("\n" + "=" * 60)
    logger.info("STEP 2: Loading Data")
    logger.info("=" * 60)
    
    if args.synthetic:
        logger.info(f"Generating synthetic dataset with {args.samples:,} samples...")
        generator = SyntheticDataGenerator(n_samples=args.samples)
        df = generator.generate()
    else:
        loader = DataLoader(config)
        try:
            df = loader.load_data(download_if_missing=True)
            loader.print_summary()
        except FileNotFoundError:
            logger.warning("Real dataset not found. Using synthetic data...")
            generator = SyntheticDataGenerator(n_samples=args.samples)
            df = generator.generate()
    
    # Separate features and target
    target_col = config.features.target_column
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    logger.info(f"Features shape: {X.shape}")
    logger.info(f"Target distribution: {y.value_counts().to_dict()}")
    
    # ===== Step 3: Feature Engineering =====
    logger.info("\n" + "=" * 60)
    logger.info("STEP 3: Feature Engineering")
    logger.info("=" * 60)
    
    feature_engineer = FeatureEngineer(config)
    X_engineered = feature_engineer.fit_transform(X, y)
    
    logger.info(f"Engineered features: {X_engineered.shape[1]}")
    logger.info(f"Selected features: {feature_engineer.selected_features[:10]}...")
    
    # ===== Step 4: Preprocessing =====
    logger.info("\n" + "=" * 60)
    logger.info("STEP 4: Preprocessing")
    logger.info("=" * 60)
    
    preprocessor = Preprocessor(config)
    X_train, X_test, y_train, y_test, X_val, y_val = preprocessor.fit_transform(
        X_engineered, y,
        apply_resampling=True
    )
    
    logger.info(f"Training set: {X_train.shape[0]:,} samples")
    logger.info(f"Test set: {X_test.shape[0]:,} samples")
    if X_val is not None:
        logger.info(f"Validation set: {X_val.shape[0]:,} samples")
    
    # ===== Step 5: Model Comparison (Optional) =====
    if args.compare:
        logger.info("\n" + "=" * 60)
        logger.info("STEP 5a: Model Comparison")
        logger.info("=" * 60)
        
        comparer = ModelComparer(config)
        comparison_results = comparer.compare(X_train, y_train)
        
        print("\n📊 Model Comparison Results:")
        print(comparison_results.to_string(index=False))
        print()
    
    # ===== Step 5: Model Training =====
    logger.info("\n" + "=" * 60)
    logger.info("STEP 5: Model Training")
    logger.info("=" * 60)
    
    trainer = ModelTrainer(config)
    
    # Determine model type
    use_ensemble = args.model == 'ensemble' or (args.model is None and config.model.use_ensemble)
    model_name = args.model if args.model and args.model != 'ensemble' else config.model.primary_model
    
    if use_ensemble:
        logger.info("Training ensemble model...")
        model = trainer.train_ensemble(X_train, y_train)
    else:
        logger.info(f"Training {model_name} model...")
        model = trainer.train_single_model(
            X_train, y_train,
            model_name=model_name,
            optimize=config.model.hyperparameter_tuning_enabled
        )
    
    # ===== Step 6: Evaluation =====
    logger.info("\n" + "=" * 60)
    logger.info("STEP 6: Model Evaluation")
    logger.info("=" * 60)
    
    evaluator = Evaluator(config)
    
    # Make predictions
    y_pred = trainer.predict(X_test)
    y_proba = trainer.predict_proba(X_test)[:, 1]
    
    # Evaluate
    metrics = evaluator.evaluate(y_test, y_pred, y_proba, optimize_threshold=True)
    
    # Print report
    evaluator.print_report(y_test, y_pred)
    
    # Generate plots
    if not args.no_plots:
        logger.info("Generating evaluation plots...")
        plots_dir = config.get_absolute_path(config.evaluation.plots_path)
        
        # Get feature importance
        feature_importance = trainer.get_feature_importance(feature_engineer.selected_features)
        
        evaluator.plot_all(
            y_test, y_proba, y_pred,
            feature_importance_df=feature_importance,
            save_dir=str(plots_dir)
        )
    
    # ===== Step 7: Save Artifacts =====
    logger.info("\n" + "=" * 60)
    logger.info("STEP 7: Saving Artifacts")
    logger.info("=" * 60)
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save model
    model_path = output_dir / "fraud_detector.joblib"
    trainer.save(model_path)
    
    # Save preprocessor
    preprocessor_path = output_dir / "preprocessor.joblib"
    preprocessor.save(preprocessor_path)
    
    # Save feature engineer
    feature_engineer_path = output_dir / "feature_engineer.joblib"
    feature_engineer.save(feature_engineer_path)
    
    # Save evaluation report
    report_path = output_dir / "evaluation_report.csv"
    evaluator.save_report(report_path)
    
    # Save training metadata
    metadata = {
        'timestamp': datetime.now().isoformat(),
        'model_type': type(trainer.model).__name__,
        'best_params': trainer.best_params,
        'cv_scores': trainer.cv_scores,
        'cv_mean': np.mean(trainer.cv_scores) if trainer.cv_scores else None,
        'cv_std': np.std(trainer.cv_scores) if trainer.cv_scores else None,
        'optimal_threshold': evaluator.optimal_threshold,
        'metrics': metrics,
        'training_samples': X_train.shape[0],
        'test_samples': X_test.shape[0],
        'features': feature_engineer.selected_features,
    }
    
    import joblib
    joblib.dump(metadata, output_dir / "training_metadata.joblib")
    
    # ===== Summary =====
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    print("✅ TRAINING COMPLETE")
    print("=" * 60)
    print(f"\n📊 Final Metrics:")
    print(f"   Accuracy:  {metrics['accuracy']:.4f}")
    print(f"   Precision: {metrics['precision']:.4f}")
    print(f"   Recall:    {metrics['recall']:.4f}")
    print(f"   F1 Score:  {metrics['f1']:.4f}")
    print(f"   ROC AUC:   {metrics.get('roc_auc', 'N/A'):.4f}")
    print(f"   PR AUC:    {metrics.get('pr_auc', 'N/A'):.4f}")
    print(f"\n📁 Artifacts saved to: {output_dir.absolute()}")
    print(f"⏱️  Total time: {elapsed_time:.1f} seconds")
    print("\n" + "=" * 60)
    
    return metrics


def main():
    """Main entry point."""
    print_banner()
    args = parse_args()
    
    try:
        metrics = train_pipeline(args)
        return 0
    except KeyboardInterrupt:
        logger.warning("\nTraining interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"\nTraining failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
