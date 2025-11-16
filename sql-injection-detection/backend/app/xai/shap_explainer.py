import shap
import numpy as np
from typing import Dict, List, Any
from app.ml.predictor import SQLInjectionPredictor

class SHAPExplainer:
    def __init__(self, predictor: SQLInjectionPredictor):
        self.predictor = predictor
        self.explainer = None
    
    def setup_explainer(self, background_data: np.ndarray = None):
        """Setup SHAP explainer"""
        if hasattr(self.predictor.model, 'predict_proba'):
            # For tree-based models
            if hasattr(self.predictor.model, 'tree_'):
                self.explainer = shap.TreeExplainer(self.predictor.model)
            else:
                # For other models, use KernelExplainer
                if background_data is not None:
                    self.explainer = shap.KernelExplainer(
                        self.predictor.model.predict_proba,
                        background_data[:100]  # Sample for speed
                    )
    
    def explain(self, query: str, num_features: int = 10) -> Dict[str, Any]:
        """
        Generate SHAP explanation for a query
        
        Returns:
            Dictionary containing SHAP values and visualization data
        """
        # Get features
        features, structural_features = self.predictor.preprocessor.transform([query])
        
        # Get feature names
        tfidf_count = features.shape[1] - len(structural_features.columns)
        tfidf_features = [f'tfidf_{i}' for i in range(tfidf_count)]
        structural_feature_names = list(structural_features.columns)
        feature_names = tfidf_features + structural_feature_names
        
        try:
            # Setup explainer if not already done
            if self.explainer is None:
                # Use TreeExplainer for tree-based models
                if hasattr(self.predictor.model, 'feature_importances_'):
                    self.explainer = shap.TreeExplainer(self.predictor.model)
                else:
                    # Fallback to feature importance
                    return self._fallback_explanation(query, feature_names, num_features)
            
            # Calculate SHAP values
            shap_values = self.explainer.shap_values(features)
            
            # Handle different output formats
            if isinstance(shap_values, list):
                shap_values = shap_values[1]  # Get positive class
            
            if len(shap_values.shape) > 1:
                shap_values = shap_values[0]
            
            # Create feature importance dictionary
            feature_importance = []
            for i, (name, value) in enumerate(zip(feature_names, shap_values)):
                if i < len(shap_values):
                    feature_importance.append((name, float(value)))
            
            # Sort by absolute value
            feature_importance.sort(key=lambda x: abs(x[1]), reverse=True)
            
            features_dict = dict(feature_importance[:num_features])
            top_features = [
                {
                    'feature': feat,
                    'importance': val,
                    'impact': 'increases_risk' if val > 0 else 'decreases_risk'
                }
                for feat, val in feature_importance[:num_features]
            ]
            
            return {
                'method': 'SHAP',
                'features': features_dict,
                'top_features': top_features,
                'visualization_data': {
                    'labels': [f['feature'] for f in top_features],
                    'values': [f['importance'] for f in top_features],
                    'colors': ['#ef4444' if f['importance'] > 0 else '#10b981' for f in top_features]
                }
            }
        except Exception as e:
            print(f"SHAP explanation failed: {e}")
            return self._fallback_explanation(query, feature_names, num_features)
    
    def _fallback_explanation(self, query: str, feature_names: List[str], num_features: int = 10) -> Dict[str, Any]:
        """Fallback to model's feature importance"""
        if hasattr(self.predictor.model, 'feature_importances_'):
            importances = self.predictor.model.feature_importances_
            
            feature_importance = []
            for i, (name, importance) in enumerate(zip(feature_names, importances)):
                feature_importance.append((name, float(importance)))
            
            feature_importance.sort(key=lambda x: abs(x[1]), reverse=True)
            
            features_dict = dict(feature_importance[:num_features])
            top_features = [
                {
                    'feature': feat,
                    'importance': val,
                    'impact': 'feature_weight'
                }
                for feat, val in feature_importance[:num_features]
            ]
            
            return {
                'method': 'Feature Importance',
                'features': features_dict,
                'top_features': top_features,
                'visualization_data': {
                    'labels': [f['feature'] for f in top_features],
                    'values': [f['importance'] for f in top_features],
                    'colors': ['#3b82f6' for _ in top_features]
                }
            }
        
        # Ultimate fallback
        return {
            'method': 'None',
            'features': {},
            'top_features': [],
            'visualization_data': {'labels': [], 'values': [], 'colors': []}
        }
