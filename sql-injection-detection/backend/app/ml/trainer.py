import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from imblearn.over_sampling import SMOTE
import joblib
import os
from typing import Dict, Tuple, Any
from datetime import datetime
from app.ml.preprocessor import SQLInjectionPreprocessor
from app.config import settings

class ModelTrainer:
    def __init__(self):
        self.models = {
            'random_forest': RandomForestClassifier(random_state=42),
            'xgboost': XGBClassifier(random_state=42, eval_metric='logloss'),
            'logistic_regression': LogisticRegression(random_state=42, max_iter=1000),
            'svm': SVC(probability=True, random_state=42),
            'naive_bayes': MultinomialNB()
        }
        
        self.hyperparameters = {
            'random_forest': {
                'n_estimators': [100, 200],
                'max_depth': [10, 20, None],
                'min_samples_split': [2, 5],
                'min_samples_leaf': [1, 2]
            },
            'xgboost': {
                'n_estimators': [100, 200],
                'max_depth': [3, 5, 7],
                'learning_rate': [0.01, 0.1, 0.3],
                'subsample': [0.8, 1.0]
            },
            'logistic_regression': {
                'C': [0.1, 1, 10],
                'penalty': ['l2'],
                'solver': ['lbfgs', 'liblinear']
            },
            'svm': {
                'C': [0.1, 1, 10],
                'kernel': ['rbf', 'linear'],
                'gamma': ['scale', 'auto']
            },
            'naive_bayes': {
                'alpha': [0.1, 0.5, 1.0]
            }
        }
        
        self.preprocessor = SQLInjectionPreprocessor()
        
    def load_data(self, file_path: str) -> Tuple[pd.DataFrame, pd.Series]:
        """Load and prepare data"""
        df = pd.read_csv(file_path)
        
        # Assuming columns are 'Query' and 'Label' (1 for malicious, 0 for benign)
        # Adjust column names based on actual dataset
        if 'Sentence' in df.columns:
            df = df.rename(columns={'Sentence': 'Query'})
        
        queries = df['Query'].astype(str).tolist()
        labels = df['Label'].values
        
        return queries, labels
    
    def train_model(
        self, 
        model_name: str,
        X_train: np.ndarray,
        y_train: np.ndarray,
        tune_hyperparameters: bool = False,
        custom_hyperparameters: Dict = None
    ) -> Tuple[Any, Dict]:
        """Train a single model"""
        
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not supported")
        
        print(f"Training {model_name}...")
        
        # Handle class imbalance
        if len(np.unique(y_train)) > 1:
            # Check if we need to balance
            unique, counts = np.unique(y_train, return_counts=True)
            if max(counts) / min(counts) > 2:  # If imbalanced
                smote = SMOTE(random_state=42)
                X_train, y_train = smote.fit_resample(X_train, y_train)
                print(f"Applied SMOTE. New shape: {X_train.shape}")
        
        # Get base model
        model = self.models[model_name]
        
        # Hyperparameter tuning
        if tune_hyperparameters and custom_hyperparameters is None:
            print(f"Tuning hyperparameters for {model_name}...")
            grid_search = GridSearchCV(
                model,
                self.hyperparameters[model_name],
                cv=3,
                scoring='f1',
                n_jobs=-1,
                verbose=1
            )
            grid_search.fit(X_train, y_train)
            model = grid_search.best_estimator_
            best_params = grid_search.best_params_
            print(f"Best parameters: {best_params}")
        elif custom_hyperparameters:
            model.set_params(**custom_hyperparameters)
            best_params = custom_hyperparameters
            model.fit(X_train, y_train)
        else:
            # Use default parameters
            model.fit(X_train, y_train)
            best_params = model.get_params()
        
        return model, best_params
    
    def evaluate_model(self, model: Any, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """Evaluate model performance"""
        y_pred = model.predict(X_test)
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='binary'),
            'recall': recall_score(y_test, y_pred, average='binary'),
            'f1_score': f1_score(y_test, y_pred, average='binary')
        }
        
        print(f"Accuracy: {metrics['accuracy']:.4f}")
        print(f"Precision: {metrics['precision']:.4f}")
        print(f"Recall: {metrics['recall']:.4f}")
        print(f"F1-Score: {metrics['f1_score']:.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        return metrics
    
    def get_feature_importance(self, model: Any, feature_names: list) -> Dict:
        """Get feature importance"""
        importance_dict = {}
        
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            indices = np.argsort(importances)[::-1][:20]  # Top 20
            
            for i in indices:
                if i < len(feature_names):
                    importance_dict[feature_names[i]] = float(importances[i])
        elif hasattr(model, 'coef_'):
            importances = np.abs(model.coef_[0])
            indices = np.argsort(importances)[::-1][:20]
            
            for i in indices:
                if i < len(feature_names):
                    importance_dict[feature_names[i]] = float(importances[i])
        
        return importance_dict
    
    def train_all_models(
        self,
        data_path: str,
        tune_hyperparameters: bool = False
    ) -> Dict:
        """Train all models"""
        
        print("Loading data...")
        queries, labels = self.load_data(data_path)
        
        print(f"Total samples: {len(queries)}")
        print(f"Malicious: {sum(labels)}, Benign: {len(labels) - sum(labels)}")
        
        # Split data
        X_train_queries, X_test_queries, y_train, y_test = train_test_split(
            queries, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        print("Preprocessing data...")
        # Fit preprocessor on training data
        self.preprocessor.fit(X_train_queries, y_train)
        
        # Transform data: standard (may contain negatives) and non-negative (for MultinomialNB)
        X_train, structural_features_train = self.preprocessor.transform(X_train_queries, non_negative=False)
        X_test, structural_features_test = self.preprocessor.transform(X_test_queries, non_negative=False)

        # Non-negative versions used for MultinomialNB
        X_train_nonneg, structural_features_train_nonneg = self.preprocessor.transform(X_train_queries, non_negative=True)
        X_test_nonneg, structural_features_test_nonneg = self.preprocessor.transform(X_test_queries, non_negative=True)

        # Get feature names
        tfidf_features = [f'tfidf_{i}' for i in range(self.preprocessor.tfidf.max_features)]
        structural_feature_names = list(structural_features_train.columns)
        all_feature_names = tfidf_features + structural_feature_names

        print(f"Feature shape: {X_train.shape}")
        
        # Train all models
        results = {}
        
        for model_name in self.models.keys():
            print(f"\n{'='*50}")
            print(f"Training {model_name}")
            print(f"{'='*50}")
            
            # Use non-negative features for MultinomialNB, otherwise use standard features
            if model_name == 'naive_bayes':
                use_X_train = X_train_nonneg
                use_X_test = X_test_nonneg
            else:
                use_X_train = X_train
                use_X_test = X_test

            model, best_params = self.train_model(
                model_name,
                use_X_train,
                y_train,
                tune_hyperparameters=tune_hyperparameters
            )

            metrics = self.evaluate_model(model, use_X_test, y_test)
            
            feature_importance = self.get_feature_importance(model, all_feature_names)
            
            # Save model
            version = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_dir = os.path.join(settings.MODEL_PATH, 'versions', f'{model_name}_{version}')
            os.makedirs(model_dir, exist_ok=True)
            
            model_path = os.path.join(model_dir, 'model.pkl')
            joblib.dump(model, model_path)
            
            # Save preprocessor with each model
            preprocessor_path = os.path.join(model_dir, 'preprocessor.pkl')
            self.preprocessor.save(preprocessor_path)
            
            results[model_name] = {
                'model_path': model_path,
                'preprocessor_path': preprocessor_path,
                'version': version,
                'metrics': metrics,
                'hyperparameters': best_params,
                'feature_importance': feature_importance,
                'training_samples': len(X_train)
            }
        
        return results

if __name__ == "__main__":
    # For standalone training
    trainer = ModelTrainer()
    data_path = os.path.join(settings.DATA_PATH, 'raw', 'sql_injection_dataset.csv')
    results = trainer.train_all_models(data_path, tune_hyperparameters=False)
    
    print("\n" + "="*50)
    print("Training Summary")
    print("="*50)
    
    for model_name, result in results.items():
        print(f"\n{model_name}:")
        print(f"  Version: {result['version']}")
        print(f"  Accuracy: {result['metrics']['accuracy']:.4f}")
        print(f"  F1-Score: {result['metrics']['f1_score']:.4f}")
        print(f"  Model saved to: {result['model_path']}")
