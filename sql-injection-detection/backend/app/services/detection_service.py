import time
from typing import Dict, Tuple, Any, Optional
from sqlalchemy.orm import Session
from app.ml.predictor import SQLInjectionPredictor
from app.ml.ensemble import EnsemblePredictor
from app.xai.lime_explainer import LIMEExplainer
from app.xai.shap_explainer import SHAPExplainer
from app.xai.feature_importance import FeatureImportanceExplainer
from app.xai.gemini_service import GeminiExplainer
from app.models.request_log import RequestLog
from app.models.model_version import ModelVersion
from app.utils.helpers import classify_attack_type, calculate_attack_confidence
from app.config import settings
import os

class DetectionService:
    def __init__(self, db: Session):
        self.db = db
        self.gemini = GeminiExplainer()
        self.current_model_name = settings.DEFAULT_MODEL
        self.predictor = None
        self.ensemble = None
        
    def load_model(self, model_name: str = None):
        """Load a specific model"""
        if model_name is None:
            model_name = self.current_model_name
        
        # Get active model version from database
        model_version = self.db.query(ModelVersion).filter(
            ModelVersion.model_name == model_name,
            ModelVersion.is_active == True
        ).first()
        
        if not model_version:
            # Fallback: look for any model file
            model_path = self._find_model_file(model_name)
        else:
            model_path = model_version.file_path
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        self.predictor = SQLInjectionPredictor(model_name=model_name)
        self.predictor.load_model(model_path)
        self.current_model_name = model_name
        
    def load_ensemble(self, model_names: list = None, voting: str = 'soft'):
        """Load ensemble of models"""
        if model_names is None:
            model_names = ['random_forest', 'xgboost', 'logistic_regression']
        
        model_paths = {}
        for model_name in model_names:
            model_version = self.db.query(ModelVersion).filter(
                ModelVersion.model_name == model_name,
                ModelVersion.is_active == True
            ).first()
            
            if model_version:
                model_paths[model_name] = model_version.file_path
            else:
                # Try to find model file
                model_path = self._find_model_file(model_name)
                if model_path:
                    model_paths[model_name] = model_path
        
        if not model_paths:
            raise ValueError("No models found for ensemble")
        
        self.ensemble = EnsemblePredictor(model_paths, voting=voting)
    
    def _find_model_file(self, model_name: str) -> Optional[str]:
        """Find latest model file for a model name"""
        models_dir = os.path.join(settings.MODEL_PATH, 'versions')
        
        if not os.path.exists(models_dir):
            return None
        
        # Find directories matching model_name
        matching_dirs = [d for d in os.listdir(models_dir) if d.startswith(model_name)]
        
        if not matching_dirs:
            return None
        
        # Sort by timestamp (assuming format: modelname_YYYYMMDD_HHMMSS)
        matching_dirs.sort(reverse=True)
        
        model_path = os.path.join(models_dir, matching_dirs[0], 'model.pkl')
        
        if os.path.exists(model_path):
            return model_path
        
        return None
    
    def detect(
        self,
        query: str,
        endpoint: str = None,
        ip_address: str = None,
        use_ensemble: bool = False,
        xai_method: str = 'lime',
        explanation_style: str = 'simple'
    ) -> Dict[str, Any]:
        """
        Perform SQL injection detection with XAI and Gemini explanation
        """
        start_time = time.time()
        
        # Load model if not loaded
        if not use_ensemble and self.predictor is None:
            self.load_model()
        elif use_ensemble and self.ensemble is None:
            self.load_ensemble()
        
        # Perform prediction
        if use_ensemble:
            is_malicious, confidence, ensemble_votes = self.ensemble.predict(query)
            model_used = 'ensemble'
            model_version = None
        else:
            is_malicious, confidence, prob_dict = self.predictor.predict(query)
            ensemble_votes = None
            model_used = self.current_model_name
            model_version = self._get_model_version(model_used)
        
        # Generate XAI explanation
        xai_output = self._generate_xai_explanation(
            query, 
            self.predictor if not use_ensemble else list(self.ensemble.models.values())[0],
            xai_method
        )
        
        # Classify attack type if malicious
        attack_type = None
        attack_confidence = None
        if is_malicious:
            attack_type = classify_attack_type(query)
            attack_confidence = calculate_attack_confidence(query, confidence)
        
        # Generate Gemini explanation
        gemini_explanation = self.gemini.generate_explanation(
            query=query,
            is_malicious=is_malicious,
            confidence=confidence,
            xai_output=xai_output,
            style=explanation_style
        )
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Log to database
        request_log = RequestLog(
            query=query,
            endpoint=endpoint,
            ip_address=ip_address,
            is_malicious=is_malicious,
            confidence_score=confidence,
            model_used=model_used,
            model_version=model_version,
            ensemble_used=use_ensemble,
            ensemble_votes=ensemble_votes,
            xai_method=xai_method,
            xai_features=xai_output.get('features'),
            xai_scores=xai_output.get('visualization_data'),
            gemini_explanation=gemini_explanation,
            explanation_style=explanation_style,
            attack_type=attack_type,
            attack_confidence=attack_confidence,
            processing_time_ms=processing_time_ms
        )
        
        self.db.add(request_log)
        self.db.commit()
        self.db.refresh(request_log)
        
        return {
            'is_malicious': is_malicious,
            'confidence_score': confidence,
            'model_used': model_used,
            'model_version': model_version,
            'ensemble_used': use_ensemble,
            'ensemble_votes': ensemble_votes,
            'attack_type': attack_type,
            'attack_confidence': attack_confidence,
            'xai_output': xai_output,
            'gemini_explanation': gemini_explanation,
            'processing_time_ms': processing_time_ms,
            'request_id': request_log.id,
            'timestamp': request_log.created_at
        }
    
    def _generate_xai_explanation(self, query: str, predictor, method: str = 'lime') -> Dict:
        """Generate XAI explanation using specified method"""
        try:
            if method == 'lime':
                explainer = LIMEExplainer(predictor)
                return explainer.explain(query)
            elif method == 'shap':
                explainer = SHAPExplainer(predictor)
                return explainer.explain(query)
            elif method == 'feature_importance':
                explainer = FeatureImportanceExplainer(predictor)
                return explainer.explain(query)
            else:
                # Default to LIME
                explainer = LIMEExplainer(predictor)
                return explainer.explain(query)
        except Exception as e:
            print(f"XAI explanation failed: {e}")
            # Return empty XAI output
            return {
                'method': method,
                'features': {},
                'top_features': [],
                'visualization_data': {'labels': [], 'values': [], 'colors': []}
            }
    
    def _get_model_version(self, model_name: str) -> Optional[str]:
        """Get version string for a model"""
        model_version = self.db.query(ModelVersion).filter(
            ModelVersion.model_name == model_name,
            ModelVersion.is_active == True
        ).first()
        
        return model_version.version if model_version else None
