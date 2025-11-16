from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import verify_admin, verify_api_key
from app.models.model_version import ModelVersion
from app.models.api_key import APIKey
from app.schemas.request import ModelSwitchRequest, ThresholdUpdateRequest
from app.schemas.model import ModelInfo, ModelComparisonResult
from app.ml.trainer import ModelTrainer
from app.ml.predictor import SQLInjectionPredictor
from app.config import settings
from typing import List
import os

router = APIRouter()

@router.get("/", response_model=List[ModelInfo])
@router.get("", response_model=List[ModelInfo])
async def list_models(
    db: Session = Depends(get_db),
    api_key: APIKey = Depends(verify_api_key)
):
    """List all available models"""
    models = db.query(ModelVersion).order_by(ModelVersion.created_at.desc()).all()
    
    return [
        {
            'id': model.id,
            'model_name': model.model_name,
            'version': model.version,
            'is_active': model.is_active,
            'metrics': {
                'accuracy': model.accuracy or 0,
                'precision': model.precision or 0,
                'recall': model.recall or 0,
                'f1_score': model.f1_score or 0
            } if model.accuracy else None,
            'hyperparameters': model.hyperparameters,
            'feature_importance': model.feature_importance,
            'created_at': model.created_at
        }
        for model in models
    ]

@router.get("/active")
@router.get("/active/")
async def get_active_models(
    db: Session = Depends(get_db),
    api_key: APIKey = Depends(verify_api_key)
):
    """Get currently active models"""
    models = db.query(ModelVersion).filter(ModelVersion.is_active == True).all()
    
    return {
        'models': [
            {
                'model_name': model.model_name,
                'version': model.version,
                'accuracy': model.accuracy,
                'f1_score': model.f1_score
            }
            for model in models
        ]
    }

@router.post("/switch")
async def switch_model(
    request: ModelSwitchRequest,
    db: Session = Depends(get_db),
    api_key: APIKey = Depends(verify_admin)
):
    """Switch to a different model"""
    
    # Find the model
    model = db.query(ModelVersion).filter(
        ModelVersion.model_name == request.model_name,
        ModelVersion.is_active == True
    ).first()
    
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {request.model_name} not found")
    
    # Update settings (in production, you'd want to persist this)
    settings.DEFAULT_MODEL = request.model_name
    
    return {
        'message': f'Switched to {request.model_name}',
        'model_name': model.model_name,
        'version': model.version
    }

@router.post("/activate/{model_id}")
async def activate_model(
    model_id: int,
    db: Session = Depends(get_db),
    api_key: APIKey = Depends(verify_admin)
):
    """Activate a specific model version"""
    
    model = db.query(ModelVersion).filter(ModelVersion.id == model_id).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Deactivate other versions of the same model
    db.query(ModelVersion).filter(
        ModelVersion.model_name == model.model_name,
        ModelVersion.id != model_id
    ).update({'is_active': False})
    
    # Activate this version
    model.is_active = True
    db.commit()
    
    return {
        'message': f'Activated {model.model_name} version {model.version}',
        'model_id': model.id
    }

@router.post("/train/{model_name}")
async def train_model(
    model_name: str,
    tune_hyperparameters: bool = Query(False),
    db: Session = Depends(get_db),
    api_key: APIKey = Depends(verify_admin)
):
    """Train or retrain a specific model"""
    
    try:
        trainer = ModelTrainer()
        data_path = os.path.join(settings.DATA_PATH, 'raw', 'sql_injection_dataset.csv')
        
        if not os.path.exists(data_path):
            raise HTTPException(status_code=404, detail="Training data not found")
        
        # Load data
        queries, labels = trainer.load_data(data_path)
        
        # Split data
        from sklearn.model_selection import train_test_split
        X_train_queries, X_test_queries, y_train, y_test = train_test_split(
            queries, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        # Preprocess
        trainer.preprocessor.fit(X_train_queries, y_train)
        X_train, _ = trainer.preprocessor.transform(X_train_queries)
        X_test, _ = trainer.preprocessor.transform(X_test_queries)
        
        # Train model
        model, best_params = trainer.train_model(
            model_name,
            X_train,
            y_train,
            tune_hyperparameters=tune_hyperparameters
        )
        
        # Evaluate
        metrics = trainer.evaluate_model(model, X_test, y_test)
        
        # Get feature importance
        structural_features = trainer.preprocessor.extract_features([X_train_queries[0]])
        tfidf_features = [f'tfidf_{i}' for i in range(trainer.preprocessor.tfidf.max_features)]
        all_feature_names = tfidf_features + list(structural_features.columns)
        feature_importance = trainer.get_feature_importance(model, all_feature_names)
        
        # Save model
        from datetime import datetime
        import joblib
        
        version = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_dir = os.path.join(settings.MODEL_PATH, 'versions', f'{model_name}_{version}')
        os.makedirs(model_dir, exist_ok=True)
        
        model_path = os.path.join(model_dir, 'model.pkl')
        joblib.dump(model, model_path)
        
        preprocessor_path = os.path.join(model_dir, 'preprocessor.pkl')
        trainer.preprocessor.save(preprocessor_path)
        
        # Save to database
        model_version = ModelVersion(
            model_name=model_name,
            version=version,
            file_path=model_path,
            accuracy=metrics['accuracy'],
            precision=metrics['precision'],
            recall=metrics['recall'],
            f1_score=metrics['f1_score'],
            training_samples=len(X_train),
            hyperparameters=best_params,
            feature_importance=feature_importance,
            is_active=False
        )
        
        db.add(model_version)
        db.commit()
        
        return {
            'message': f'Model {model_name} trained successfully',
            'version': version,
            'metrics': metrics,
            'model_id': model_version.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compare")
async def compare_models(
    model_a: str,
    model_b: str,
    test_samples: int = Query(100, ge=10, le=1000),
    db: Session = Depends(get_db),
    api_key: APIKey = Depends(verify_admin)
):
    """Compare two models side by side"""
    
    try:
        # Load both models
        model_a_version = db.query(ModelVersion).filter(
            ModelVersion.model_name == model_a,
            ModelVersion.is_active == True
        ).first()
        
        model_b_version = db.query(ModelVersion).filter(
            ModelVersion.model_name == model_b,
            ModelVersion.is_active == True
        ).first()
        
        if not model_a_version or not model_b_version:
            raise HTTPException(status_code=404, detail="One or both models not found")
        
        predictor_a = SQLInjectionPredictor()
        predictor_a.load_model(model_a_version.file_path)
        
        predictor_b = SQLInjectionPredictor()
        predictor_b.load_model(model_b_version.file_path)
        
        # Load test data
        import pandas as pd
        data_path = os.path.join(settings.DATA_PATH, 'raw', 'sql_injection_dataset.csv')
        df = pd.read_csv(data_path)
        
        if 'Sentence' in df.columns:
            df = df.rename(columns={'Sentence': 'Query'})
        
        # Sample test data
        test_df = df.sample(n=min(test_samples, len(df)), random_state=42)
        test_queries = test_df['Query'].astype(str).tolist()
        
        # Compare predictions
        predictions_a = predictor_a.predict_batch(test_queries)
        predictions_b = predictor_b.predict_batch(test_queries)
        
        agreements = 0
        disagreements = []
        
        for i, (pred_a, pred_b) in enumerate(zip(predictions_a, predictions_b)):
            if pred_a[0] == pred_b[0]:  # Same prediction
                agreements += 1
            else:
                disagreements.append({
                    'query': test_queries[i][:100],
                    'model_a_prediction': pred_a[0],
                    'model_a_confidence': pred_a[1],
                    'model_b_prediction': pred_b[0],
                    'model_b_confidence': pred_b[1]
                })
        
        agreement_rate = agreements / len(test_queries)
        
        return {
            'model_a': model_a,
            'model_b': model_b,
            'test_samples': len(test_queries),
            'agreement_rate': agreement_rate,
            'model_a_metrics': {
                'accuracy': model_a_version.accuracy,
                'precision': model_a_version.precision,
                'recall': model_a_version.recall,
                'f1_score': model_a_version.f1_score
            },
            'model_b_metrics': {
                'accuracy': model_b_version.accuracy,
                'precision': model_b_version.precision,
                'recall': model_b_version.recall,
                'f1_score': model_b_version.f1_score
            },
            'disagreement_cases': disagreements[:10]  # Show first 10
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{model_name}/feature-importance")
@router.get("/{model_name}/feature-importance/")
async def get_feature_importance(
    model_name: str,
    db: Session = Depends(get_db),
    api_key: APIKey = Depends(verify_api_key)
):
    """Get feature importance for a model"""
    
    model = db.query(ModelVersion).filter(
        ModelVersion.model_name == model_name,
        ModelVersion.is_active == True
    ).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    return {
        'model_name': model_name,
        'version': model.version,
        'feature_importance': model.feature_importance or {}
    }
