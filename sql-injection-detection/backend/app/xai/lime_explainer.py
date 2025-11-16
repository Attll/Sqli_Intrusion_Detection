import lime
import lime.lime_tabular
import numpy as np
from typing import Dict, List, Tuple, Any
from app.ml.predictor import SQLInjectionPredictor

class LIMEExplainer:
    def __init__(self, predictor: SQLInjectionPredictor):
        self.predictor = predictor
        self.explainer = None
    
    def setup_explainer(self, training_data: np.ndarray, feature_names: List[str]):
        """Setup LIME explainer with training data"""
        self.explainer = lime.lime_tabular.LimeTabularExplainer(
            training_data,
            feature_names=feature_names,
            class_names=['Benign', 'Malicious'],
            mode='classification'
        )
    
    def explain(self, query: str, num_features: int = 10) -> Dict[str, Any]:
        """
        Generate LIME explanation for a query
        
        Returns:
            Dictionary containing feature importances and visualization data
        """
        if self.explainer is None:
            # Create a simple explainer without training data
            features, structural_features = self.predictor.preprocessor.transform([query])
            
            # Get feature names
            tfidf_count = features.shape[1] - len(structural_features.columns)
            tfidf_features = [f'tfidf_{i}' for i in range(tfidf_count)]
            structural_feature_names = list(structural_features.columns)
            feature_names = tfidf_features + structural_feature_names
            
            # Use zeros as dummy training data
            dummy_training = np.zeros((100, features.shape[1]))
            self.setup_explainer(dummy_training, feature_names)
        
        # Get features
        features, _ = self.predictor.preprocessor.transform([query])
        
        # Create prediction function
        def predict_fn(X):
            if hasattr(self.predictor.model, 'predict_proba'):
                return self.predictor.model.predict_proba(X)
            else:
                predictions = self.predictor.model.predict(X)
                return np.array([[1-p, p] for p in predictions])
        
        # Generate explanation
        try:
            explanation = self.explainer.explain_instance(
                features[0],
                predict_fn,
                num_features=num_features
            )
            
            # Extract feature importances
            feature_importance = explanation.as_list()
            
            # Format for response
            features_dict = {}
            top_features = []
            
            for feature, importance in feature_importance:
                features_dict[feature] = float(importance)
                top_features.append({
                    'feature': feature,
                    'importance': float(importance),
                    'impact': 'increases_risk' if importance > 0 else 'decreases_risk'
                })
            
            # Sort by absolute importance
            top_features.sort(key=lambda x: abs(x['importance']), reverse=True)
            
            return {
                'method': 'LIME',
                'features': features_dict,
                'top_features': top_features[:num_features],
                'visualization_data': {
                    'labels': [f['feature'] for f in top_features[:num_features]],
                    'values': [f['importance'] for f in top_features[:num_features]],
                    'colors': ['#ef4444' if f['importance'] > 0 else '#10b981' for f in top_features[:num_features]]
                }
            }
        except Exception as e:
            print(f"LIME explanation failed: {e}")
            # Fallback to feature importance
            return self._fallback_explanation(query, num_features)
    
    def _fallback_explanation(self, query: str, num_features: int = 10) -> Dict[str, Any]:
        """Fallback explanation using feature values"""
        feature_values = self.predictor.get_feature_values(query)
        
        # Sort by absolute value
        sorted_features = sorted(
            feature_values.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:num_features]
        
        features_dict = dict(sorted_features)
        top_features = [
            {
                'feature': feat,
                'importance': val,
                'impact': 'increases_risk' if val > 0 else 'decreases_risk'
            }
            for feat, val in sorted_features
        ]
        
        return {
            'method': 'Feature Values',
            'features': features_dict,
            'top_features': top_features,
            'visualization_data': {
                'labels': [f['feature'] for f in top_features],
                'values': [f['importance'] for f in top_features],
                'colors': ['#ef4444' if f['importance'] > 0 else '#10b981' for f in top_features]
            }
        }
