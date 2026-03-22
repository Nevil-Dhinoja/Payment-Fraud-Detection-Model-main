"""
Dataset Download Script
Author: Manan Monani
========================

Script to download the Credit Card Fraud Detection dataset from Kaggle.

Usage:
    python download_data.py

Requirements:
    - Kaggle API credentials configured
    - Install kaggle package: pip install kaggle
"""

import os
import sys
import zipfile
from pathlib import Path

try:
    from kaggle.api.kaggle_api_extended import KaggleApi
    KAGGLE_AVAILABLE = True
except ImportError:
    KAGGLE_AVAILABLE = False


def setup_kaggle_credentials():
    """Print instructions for setting up Kaggle credentials."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                    KAGGLE API SETUP REQUIRED                      ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  To download the dataset, you need to setup Kaggle API:          ║
║                                                                   ║
║  1. Create a Kaggle account at https://www.kaggle.com            ║
║                                                                   ║
║  2. Go to Account Settings → Create New API Token                ║
║     This will download a kaggle.json file                        ║
║                                                                   ║
║  3. Place kaggle.json in:                                        ║
║     - Windows: C:\\Users\\<username>\\.kaggle\\kaggle.json         ║
║     - Linux/Mac: ~/.kaggle/kaggle.json                           ║
║                                                                   ║
║  4. Run this script again                                        ║
║                                                                   ║
║  Alternatively, download manually from:                          ║
║  https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud         ║
║  and place creditcard.csv in data/raw/                           ║
║                                                                   ║
╚══════════════════════════════════════════════════════════════════╝
    """)


def download_dataset():
    """Download the Credit Card Fraud Detection dataset from Kaggle."""
    
    # Check if Kaggle is available
    if not KAGGLE_AVAILABLE:
        print("❌ Kaggle package not installed.")
        print("   Run: pip install kaggle")
        setup_kaggle_credentials()
        return False
    
    # Setup paths
    base_path = Path(__file__).parent
    raw_data_path = base_path / "data" / "raw"
    csv_path = raw_data_path / "creditcard.csv"
    
    # Check if data already exists
    if csv_path.exists():
        print(f"✅ Dataset already exists at {csv_path}")
        
        # Print file info
        size_mb = csv_path.stat().st_size / (1024 * 1024)
        print(f"   File size: {size_mb:.1f} MB")
        
        response = input("\n   Do you want to re-download? (y/N): ").strip().lower()
        if response != 'y':
            print("   Skipping download.")
            return True
    
    # Create directory
    raw_data_path.mkdir(parents=True, exist_ok=True)
    
    print("\n📥 Downloading Credit Card Fraud Detection Dataset...")
    print("   Source: kaggle.com/datasets/mlg-ulb/creditcardfraud")
    print()
    
    try:
        # Initialize API
        api = KaggleApi()
        api.authenticate()
        
        print("   ✅ Kaggle API authenticated")
        
        # Download dataset
        print("   ⏳ Downloading dataset (this may take a few minutes)...")
        api.dataset_download_files(
            "mlg-ulb/creditcardfraud",
            path=str(raw_data_path),
            unzip=True
        )
        
        print("   ✅ Download complete!")
        
        # Verify download
        if csv_path.exists():
            size_mb = csv_path.stat().st_size / (1024 * 1024)
            print(f"\n✅ Dataset saved to: {csv_path}")
            print(f"   File size: {size_mb:.1f} MB")
            
            # Quick data check
            import pandas as pd
            df = pd.read_csv(csv_path, nrows=5)
            print(f"   Columns: {len(df.columns)}")
            print(f"   Sample columns: {list(df.columns[:5])}...")
            
            return True
        else:
            print("❌ Download completed but file not found")
            return False
            
    except Exception as e:
        print(f"\n❌ Error downloading dataset: {e}")
        setup_kaggle_credentials()
        return False


def main():
    """Main entry point."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║           CREDIT CARD FRAUD DETECTION DATASET DOWNLOADER         ║
║                                                                   ║
║                       By Manan Monani                            ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    success = download_dataset()
    
    if success:
        print("""
╔══════════════════════════════════════════════════════════════════╗
║                         NEXT STEPS                               ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  1. Train the model:                                             ║
║     python train.py                                              ║
║                                                                   ║
║  2. Quick training (no optimization):                            ║
║     python train.py --quick                                      ║
║                                                                   ║
║  3. Start the API server:                                        ║
║     python -m api.app                                            ║
║                                                                   ║
╚══════════════════════════════════════════════════════════════════╝
        """)
    else:
        print("""
╔══════════════════════════════════════════════════════════════════╗
║                     ALTERNATIVE OPTIONS                          ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  You can still train the model using synthetic data:             ║
║     python train.py --synthetic --samples 100000                 ║
║                                                                   ║
║  Or download the dataset manually from:                          ║
║  https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud         ║
║                                                                   ║
╚══════════════════════════════════════════════════════════════════╝
        """)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
