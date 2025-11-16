import joblib
import numpy as np
from typing import Dict, Tuple, List, Any
import os
from app.ml.preprocessor import SQLInjectionPreprocessor
from app.config import settings

class SQLInjectionPredictor:
    def __init__(self, model_name: str = None, model_path: str = None):
        self.model_name = model_name or settings.DEFAULT_MODEL
        self.model = None
        self.preprocessor = SQLInjectionPreprocessor()
        
        if model_path:
            self.load_model(model_path)
    
    def load_model(self, model_path: str):
        """Load model and preprocessor"""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")
        
        # Load model
        self.model = joblib.load(model_path)
        
        # Load preprocessor (should be in same directory)
        model_dir = os.path.dirname(model_path)
        preprocessor_path = os.path.join(model_dir, 'preprocessor.pkl')
        
        if os.path.exists(preprocessor_path):
            self.preprocessor.load(preprocessor_path)
        else:
            raise FileNotFoundError(f"Preprocessor not found at {preprocessor_path}")
    
    def predict(self, query: str) -> Tuple[bool, float, Dict]:
        """
        Predict if query is malicious
        Returns: (is_malicious, confidence_score, probabilities)
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        # Preprocess
        features, structural_features = self.preprocessor.transform([query])
        
        # Predict
        prediction = self.model.predict(features)[0]
        
        # Get probability scores
        if hasattr(self.model, 'predict_proba'):
            probabilities = self.model.predict_proba(features)[0]
            confidence = float(max(probabilities))
            prob_dict = {
                'benign': float(probabilities[0]),
                'malicious': float(probabilities[1])
            }
        else:
            # For models without predict_proba
            confidence = 1.0
            prob_dict = {
                'benign': 0.0 if prediction == 1 else 1.0,
                'malicious': 1.0 if prediction == 1 else 0.0
            }
        
        is_malicious = bool(prediction == 1)
        
        return is_malicious, confidence, prob_dict
    
    def predict_batch(self, queries: List[str]) -> List[Tuple[bool, float, Dict]]:
        """Predict multiple queries"""
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        # Preprocess
        features, structural_features = self.preprocessor.transform(queries)
        
        # Predict
        predictions = self.model.predict(features)
        
        # Get probabilities
        if hasattr(self.model, 'predict_proba'):
            all_probabilities = self.model.predict_proba(features)
        else:
            all_probabilities = None
        
        results = []
        for i, prediction in enumerate(predictions):
            if all_probabilities is not None:
                probabilities = all_probabilities[i]
                confidence = float(max(probabilities))
                prob_dict = {
                    'benign': float(probabilities[0]),
                    'malicious': float(probabilities[1])
                }
            else:
                confidence = 1.0
                prob_dict = {
                    'benign': 0.0 if prediction == 1 else 1.0,
                    'malicious': 1.0 if prediction == 1 else 0.0
                }
            
            is_malicious = bool(prediction == 1)
            results.append((is_malicious, confidence, prob_dict))
        
        return results
    
    def get_feature_values(self, query: str) -> Dict[str, float]:
        """Get feature values for a query"""
        features, structural_features = self.preprocessor.transform([query])
        
        # Get feature names
        tfidf_features = [f'tfidf_{i}' for i in range(features.shape[1] - len(structural_features.columns))]
        structural_feature_names = list(structural_features.columns)
        all_feature_names = tfidf_features + structural_feature_names
        
        # Create dictionary
        feature_dict = {}
        for i, name in enumerate(all_feature_names):
            if i < features.shape[1]:
                feature_dict[name] = float(features[0][i])
        
        return feature_dict
