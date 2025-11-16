import pandas as pd
import numpy as np
import re
from typing import List, Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import joblib
import os

class SQLInjectionPreprocessor:
    def __init__(self):
        self.tfidf = TfidfVectorizer(
            max_features=100,
            ngram_range=(1, 3),
            analyzer='char'
        )
        self.scaler = StandardScaler()
        self.minmax = MinMaxScaler(feature_range=(0, 1))
        self.is_fitted = False
        
    def extract_features(self, queries: List[str]) -> pd.DataFrame:
        """Extract features from SQL queries"""
        features = []
        
        for query in queries:
            feature_dict = {
                # Length features
                'query_length': len(query),
                'word_count': len(query.split()),
                
                # SQL keyword counts
                'select_count': query.lower().count('select'),
                'union_count': query.lower().count('union'),
                'insert_count': query.lower().count('insert'),
                'delete_count': query.lower().count('delete'),
                'drop_count': query.lower().count('drop'),
                'update_count': query.lower().count('update'),
                'where_count': query.lower().count('where'),
                'or_count': query.lower().count(' or '),
                'and_count': query.lower().count(' and '),
                
                # Special characters
                'quote_count': query.count("'") + query.count('"'),
                'semicolon_count': query.count(';'),
                'comment_count': query.count('--') + query.count('/*') + query.count('#'),
                'equals_count': query.count('='),
                'dash_count': query.count('--'),
                'star_count': query.count('*'),
                'percent_count': query.count('%'),
                
                # Suspicious patterns
                'has_exec': int('exec' in query.lower()),
                'has_execute': int('execute' in query.lower()),
                'has_sp_': int('sp_' in query.lower()),
                'has_xp_': int('xp_' in query.lower()),
                'has_concat': int('concat' in query.lower()),
                'has_char': int('char(' in query.lower()),
                'has_waitfor': int('waitfor' in query.lower()),
                'has_sleep': int('sleep(' in query.lower()),
                'has_benchmark': int('benchmark(' in query.lower()),
                
                # Evasion techniques
                'has_hex': int(bool(re.search(r'0x[0-9a-fA-F]+', query))),
        'has_encoding': int('%' in query and any(c.isdigit() for c in query)), # <-- MUST end with a comma
        
        # Boolean-based SQLi
        'has_tautology': int(bool(re.search(r"('|\")\s*or\s*('|\")?\s*1\s*=\s*1", query.lower()))),
        'has_always_true': int("1=1" in query or "1' or '1'='1" in query.lower()),

                # Ratio features
                'special_char_ratio': sum(not c.isalnum() and not c.isspace() for c in query) / max(len(query), 1),
                'uppercase_ratio': sum(c.isupper() for c in query) / max(len(query), 1),
                'digit_ratio': sum(c.isdigit() for c in query) / max(len(query), 1),
            }
            
            features.append(feature_dict)
        
        return pd.DataFrame(features)
    
    def fit(self, queries: List[str], labels: np.ndarray = None):
        """Fit the preprocessor"""
        # Fit TF-IDF
        self.tfidf.fit(queries)
        
        # Extract features
        structural_features = self.extract_features(queries)
        
        # Fit scalers
        self.scaler.fit(structural_features)
        self.minmax.fit(structural_features)
        
        self.is_fitted = True
        
    def transform(self, queries: List[str], non_negative: bool = False) -> Tuple[np.ndarray, pd.DataFrame]:
        """Transform queries to features

        Args:
            queries: list of query strings
            non_negative: if True, structural features are scaled to [0,1] using MinMaxScaler
        Returns:
            Tuple of combined feature array and structural features dataframe
        """
        if not self.is_fitted:
            raise ValueError("Preprocessor must be fitted before transform")

        # TF-IDF features
        tfidf_features = self.tfidf.transform(queries).toarray()

        # Structural features
        structural_features = self.extract_features(queries)
        if non_negative:
            structural_features_scaled = self.minmax.transform(structural_features)
        else:
            structural_features_scaled = self.scaler.transform(structural_features)

        # Combine features
        combined_features = np.hstack([tfidf_features, structural_features_scaled])

        return combined_features, structural_features
    
    def fit_transform(self, queries: List[str], labels: np.ndarray = None) -> Tuple[np.ndarray, pd.DataFrame]:
        """Fit and transform"""
        self.fit(queries, labels)
        return self.transform(queries)
    
    def save(self, path: str):
        """Save preprocessor"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            'tfidf': self.tfidf,
            'scaler': self.scaler,
            'is_fitted': self.is_fitted
        }, path)
    
    def load(self, path: str):
        """Load preprocessor"""
        data = joblib.load(path)
        self.tfidf = data['tfidf']
        self.scaler = data['scaler']
        self.is_fitted = data['is_fitted']
