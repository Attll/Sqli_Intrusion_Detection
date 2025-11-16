import numpy as np
from typing import Dict, List, Any
from app.ml.predictor import SQLInjectionPredictor

class FeatureImportanceExplainer:
    def __init__(self, predictor: SQLInjectionPredictor):
        self.predictor = predictor
    
    def explain(self, query: str, num_features: int = 10) -> Dict[str, Any]:
        """
        Generate explanation using model's built-in feature importance
        
        Returns:
            Dictionary containing feature importances
        """
        # Get features
        features, structural_features = self.predictor.preprocessor.transform([query])
        
        # Get feature names
        tfidf_count = features.shape[1] - len(structural_features.columns)
        tfidf_features = [f'tfidf_{i}' for i in range(tfidf_count)]
        structural_feature_names = list(structural_features.columns)
        feature_names = tfidf_features + structural_feature_names
        
        # Get feature values for this query
        feature_values = self.predictor.get_feature_values(query)
        
        # Get model's feature importance
        if hasattr(self.predictor.model, 'feature_importances_'):
            model_importance = self.predictor.model.feature_importances_
        elif hasattr(self.predictor.model, 'coef_'):
            model_importance = np.abs(self.predictor.model.coef_[0])
        else:
            # Fallback: use feature values
            model_importance = np.abs(features[0])
        
        # Combine feature importance with actual values
        combined_importance = []
        for i, name in enumerate(feature_names):
            if i < len(model_importance) and name in feature_values:
                # Importance = model weight * feature value
                importance = float(model_importance[i] * abs(feature_values[name]))
                combined_importance.append((name, importance, feature_values[name]))
        
        # Sort by importance
        combined_importance.sort(key=lambda x: abs(x[1]), reverse=True)
        
        # Format response
        features_dict = {name: imp for name, imp, _ in combined_importance[:num_features]}
        
        top_features = [
            {
                'feature': name,
                'importance': imp,
                'feature_value': val,
                'impact': 'high' if imp > np.median([x[1] for x in combined_importance]) else 'medium'
            }
            for name, imp, val in combined_importance[:num_features]
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
