"""
Script to train all ML models
"""

import sys
import os
import json
import math
import numpy as np
from app.ml.trainer import ModelTrainer
from app.config import settings
from app.database import SessionLocal
from app.models.model_version import ModelVersion

def train_all_models():
    """Train all models and save to database"""
    
    print("="*60)
    print("SQL Injection Detection - Model Training")
    print("="*60)
    
    # Check if dataset exists
    data_path = os.path.join(settings.DATA_PATH, 'raw', 'sql_injection_dataset.csv')
    
    if not os.path.exists(data_path):
        print(f"\n✗ Error: Dataset not found at {data_path}")
        print("\nPlease download the dataset from:")
        print("https://www.kaggle.com/datasets/sajid576/sql-injection-dataset")
        print(f"\nAnd place it at: {data_path}")
        return False
    
    print(f"\n✓ Dataset found at: {data_path}\n")
    
    # Initialize trainer
    trainer = ModelTrainer()
    
    # Train all models
    print("Starting training process...\n")
    results = trainer.train_all_models(
        data_path=data_path,
        tune_hyperparameters=False  # Set to True for hyperparameter tuning (slower)
    )
    
    # Save to database
    print("\nSaving models to database...")
    db = SessionLocal()
    
    try:
        for model_name, result in results.items():
            # Deactivate old versions
            db.query(ModelVersion).filter(
                ModelVersion.model_name == model_name
            ).update({'is_active': False})
            
            # Create new version
            # Sanitize hyperparameters and feature importance for JSON storage
            def _sanitize(obj):
                # Recursively convert objects to JSON-serializable types
                if obj is None:
                    return None
                if isinstance(obj, (str, bool)):
                    return obj
                if isinstance(obj, (int, float, np.floating, np.integer)):
                    # Convert numpy numbers to native Python
                    val = float(obj) if isinstance(obj, (float, np.floating)) else int(obj)
                    # Handle NaN and infinity
                    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
                        return None
                    return val
                if isinstance(obj, dict):
                    return {str(k): _sanitize(v) for k, v in obj.items()}
                if isinstance(obj, (list, tuple, set)):
                    return [_sanitize(v) for v in obj]
                try:
                    # Fallback: try to convert to JSON via default repr
                    return str(obj)
                except Exception:
                    return None

            hyperparams_clean = _sanitize(result.get('hyperparameters'))
            feature_importance_clean = _sanitize(result.get('feature_importance'))

            model_version = ModelVersion(
                model_name=model_name,
                version=result['version'],
                file_path=result['model_path'],
                accuracy=result['metrics']['accuracy'],
                precision=result['metrics']['precision'],
                recall=result['metrics']['recall'],
                f1_score=result['metrics']['f1_score'],
                training_samples=result['training_samples'],
                hyperparameters=hyperparams_clean,
                feature_importance=feature_importance_clean,
                is_active=True,
                notes="Initial training"
            )
            
            db.add(model_version)
        
        db.commit()
        print("✓ Models saved to database")
        
    except Exception as e:
        print(f"✗ Error saving to database: {e}")
        db.rollback()
        return False
    finally:
        db.close()
    
    # Print summary
    print("\n" + "="*60)
    print("Training Summary")
    print("="*60)
    
    for model_name, result in results.items():
        print(f"\n{model_name.upper()}:")
        print(f"  Version: {result['version']}")
        print(f"  Accuracy: {result['metrics']['accuracy']:.4f}")
        print(f"  Precision: {result['metrics']['precision']:.4f}")
        print(f"  Recall: {result['metrics']['recall']:.4f}")
        print(f"  F1-Score: {result['metrics']['f1_score']:.4f}")
    
    print("\n" + "="*60)
    print("✓ All models trained successfully!")
    print("="*60)
    
    return True

if __name__ == "__main__":
    if not train_all_models():
        sys.exit(1)
