import numpy as np
from typing import Dict, List, Tuple, Any
from app.ml.predictor import SQLInjectionPredictor
import os

class EnsemblePredictor:
    def __init__(self, model_paths: Dict[str, str], voting: str = 'soft'):
        """
        Initialize ensemble predictor
        
        Args:
            model_paths: Dict mapping model names to their paths
            voting: 'hard' for majority vote, 'soft' for probability averaging
        """
        self.models = {}
        self.voting = voting
        
        # Load all models
        for model_name, model_path in model_paths.items():
            predictor = SQLInjectionPredictor()
            predictor.load_model(model_path)
            self.models[model_name] = predictor
    
    def predict(self, query: str) -> Tuple[bool, float, Dict[str, Any]]:
        """
        Ensemble prediction
        Returns: (is_malicious, confidence, votes_dict)
        """
        if not self.models:
            raise ValueError("No models loaded in ensemble")
        
        predictions = {}
        probabilities = {}
        
        # Get predictions from all models
        for model_name, predictor in self.models.items():
            is_mal, conf, prob_dict = predictor.predict(query)
            predictions[model_name] = {
                'is_malicious': is_mal,
                'confidence': conf,
                'probabilities': prob_dict
            }
            probabilities[model_name] = prob_dict['malicious']
        
        # Combine predictions
        if self.voting == 'hard':
            # Majority voting
            votes = [pred['is_malicious'] for pred in predictions.values()]
            is_malicious = sum(votes) > len(votes) / 2
            confidence = sum(votes) / len(votes)
        else:
            # Soft voting (average probabilities)
            avg_prob_malicious = np.mean(list(probabilities.values()))
            is_malicious = avg_prob_malicious > 0.5
            confidence = float(avg_prob_malicious if is_malicious else 1 - avg_prob_malicious)
        
        # Prepare votes dictionary
        votes_dict = {
            'voting_method': self.voting,
            'individual_predictions': predictions,
            'final_confidence': confidence,
            'agreement_rate': self._calculate_agreement(predictions)
        }
        
        return is_malicious, confidence, votes_dict
    
    def _calculate_agreement(self, predictions: Dict) -> float:
        """Calculate agreement rate among models"""
        votes = [pred['is_malicious'] for pred in predictions.values()]
        majority = sum(votes) > len(votes) / 2
        agreement = sum(1 for v in votes if v == majority)
        return agreement / len(votes)
