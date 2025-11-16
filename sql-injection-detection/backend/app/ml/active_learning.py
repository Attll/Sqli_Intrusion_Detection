import pandas as pd
import numpy as np
from typing import List, Tuple, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.request_log import RequestLog
from app.models.feedback import Feedback
from app.ml.trainer import ModelTrainer
from app.ml.preprocessor import SQLInjectionPreprocessor
import os
from app.config import settings
import joblib

class ActiveLearningPipeline:
    def __init__(self, db: Session):
        self.db = db
        self.trainer = ModelTrainer()
    
    def collect_training_data(
        self,
        days: int = 7,
        min_confidence: float = None,
        include_feedback: bool = True
    ) -> Tuple[List[str], List[int]]:
        """
        Collect new training data from logs
        
        Args:
            days: Number of days to look back
            min_confidence: Only include predictions below this confidence
            include_feedback: Include user feedback
        """
        queries = []
        labels = []
        
        # Get data from logs
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = self.db.query(RequestLog).filter(RequestLog.created_at >= cutoff_date)
        
        if min_confidence is not None:
            query = query.filter(RequestLog.confidence_score < min_confidence)
        
        logs = query.all()
        
        for log in logs:
            # Check if there's feedback
            if include_feedback:
                feedback = self.db.query(Feedback).filter(
                    Feedback.request_log_id == log.id,
                    Feedback.used_for_training == False
                ).first()
                
                if feedback:
                    queries.append(log.query)
                    # Map feedback to label
                    if feedback.feedback_type == 'false_positive':
                        labels.append(0)  # Actually benign
                    elif feedback.feedback_type == 'false_negative':
                        labels.append(1)  # Actually malicious
                    elif feedback.feedback_type == 'correct':
                        labels.append(1 if log.is_malicious else 0)
                    
                    # Mark as used
                    feedback.used_for_training = True
                    feedback.trained_at = datetime.utcnow()
            else:
                # Use model's prediction
                queries.append(log.query)
                labels.append(1 if log.is_malicious else 0)
        
        self.db.commit()
        
        return queries, labels
    
    def retrain_model(
        self,
        model_name: str,
        original_data_path: str,
        new_queries: List[str] = None,
        new_labels: List[int] = None,
        days: int = 7
    ) -> Dict:
        """
        Retrain a model with new data
        
        Args:
            model_name: Name of model to retrain
            original_data_path: Path to original training data
            new_queries: New queries to add (optional)
            new_labels: Labels for new queries (optional)
            days: Days to collect data from logs if new_queries not provided
        """
        
        # Load original data
        print("Loading original training data...")
        df_original = pd.read_csv(original_data_path)
        
        if 'Sentence' in df_original.columns:
            df_original = df_original.rename(columns={'Sentence': 'Query'})
        
        original_queries = df_original['Query'].astype(str).tolist()
        original_labels = df_original['Label'].values.tolist()
        
        # Collect new data if not provided
        if new_queries is None or new_labels is None:
            print(f"Collecting new data from last {days} days...")
            new_queries, new_labels = self.collect_training_data(days=days)
        
        if not new_queries:
            print("No new data to train on")
            return {'status': 'skipped', 'reason': 'no_new_data'}
        
        print(f"Found {len(new_queries)} new samples")
        
        # Combine data
        all_queries = original_queries + new_queries
        all_labels = original_labels + new_labels
        
        print(f"Total samples: {len(all_queries)}")
        
        # Split data
        from sklearn.model_selection import train_test_split
        X_train_queries, X_test_queries, y_train, y_test = train_test_split(
            all_queries, all_labels, test_size=0.2, random_state=42, stratify=all_labels
        )
        
        # Preprocess
        print("Preprocessing...")
        preprocessor = SQLInjectionPreprocessor()
        preprocessor.fit(X_train_queries, y_train)
        X_train, _ = preprocessor.transform(X_train_queries)
        X_test, _ = preprocessor.transform(X_test_queries)
        
        # Train model
        print(f"Training {model_name}...")
        model, best_params = self.trainer.train_model(
            model_name,
            X_train,
            y_train,
            tune_hyperparameters=False
        )
        
        # Evaluate
        metrics = self.trainer.evaluate_model(model, X_test, y_test)
        
        # Save model
        version = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_dir = os.path.join(settings.MODEL_PATH, 'versions', f'{model_name}_{version}')
        os.makedirs(model_dir, exist_ok=True)
        
        model_path = os.path.join(model_dir, 'model.pkl')
        joblib.dump(model, model_path)
        
        preprocessor_path = os.path.join(model_dir, 'preprocessor.pkl')
        preprocessor.save(preprocessor_path)
        
        result = {
            'status': 'success',
            'model_name': model_name,
            'version': version,
            'model_path': model_path,
            'preprocessor_path': preprocessor_path,
            'metrics': metrics,
            'new_samples_added': len(new_queries),
            'total_samples': len(all_queries)
        }
        
        return result
    
    def evaluate_uncertainty(self, query: str, predictor) -> float:
        """
        Evaluate prediction uncertainty (for active learning sample selection)
        Returns uncertainty score (0-1, higher = more uncertain)
        """
        _, confidence, _ = predictor.predict(query)
        # Uncertainty is inverse of confidence distance from 0.5
        uncertainty = 1 - abs(confidence - 0.5) * 2
        return uncertainty