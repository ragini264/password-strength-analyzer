# ml_pipeline.py
import pandas as pd
import numpy as np
import string
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import joblib
from create_password_dataset import create_password_csv

class PasswordStrengthML:
    def __init__(self):
        self.models = {}
        self.scaler = StandardScaler()
        self.feature_names = [
            'length', 'uppercase_count', 'lowercase_count', 
            'digit_count', 'special_count', 'entropy',
            'has_uppercase', 'has_lowercase', 'has_digits', 'has_special'
        ]
        self.strength_labels = {0: 'Very Weak', 1: 'Weak', 2: 'Medium', 3: 'Strong', 4: 'Very Strong'}
        
    def load_or_create_dataset(self):
        csv_path = 'data/passwords.csv'
        
        if os.path.exists(csv_path):
            print("Loading existing password dataset...")
            df = pd.read_csv(csv_path)
        else:
            print("Creating new password dataset...")
            os.makedirs('data', exist_ok=True)
            df = create_password_csv()
        
        return df
    
    def calculate_entropy(self, password):
        if len(password) == 0:
            return 0
            
        char_count = {}
        for char in password:
            char_count[char] = char_count.get(char, 0) + 1
            
        entropy = 0
        for count in char_count.values():
            p = count / len(password)
            if p > 0:
                entropy -= p * np.log2(p)
            
        return entropy
    
    def extract_features(self, password):
        features = {}
        
        features['length'] = len(password)
        features['uppercase_count'] = sum(1 for c in password if c.isupper())
        features['lowercase_count'] = sum(1 for c in password if c.islower())
        features['digit_count'] = sum(1 for c in password if c.isdigit())
        features['special_count'] = sum(1 for c in password if c in string.punctuation)
        features['has_uppercase'] = int(features['uppercase_count'] > 0)
        features['has_lowercase'] = int(features['lowercase_count'] > 0)
        features['has_digits'] = int(features['digit_count'] > 0)
        features['has_special'] = int(features['special_count'] > 0)
        features['entropy'] = self.calculate_entropy(password)
        
        return features
    
    def generate_dataset(self):
        return self.load_or_create_dataset()
    
    def train_models(self, df):
        print("Preparing data for training...")
        X = df[self.feature_names]
        y = df['strength']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Use only Random Forest for simplicity
        print("Training Random Forest model...")
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        cv_scores = cross_val_score(model, X_train, y_train, cv=5)
        
        results = {
            'Random Forest': {
                'model': model,
                'accuracy': accuracy,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std()
            },
            'best_model': 'Random Forest'
        }
        
        self.models['Random Forest'] = model
        self.best_model = model
        
        # Save model and scaler
        joblib.dump(self.best_model, 'models/best_model.pkl')
        joblib.dump(self.scaler, 'models/scaler.pkl')
        
        print("Model training completed!")
        return results
    
    def predict_strength(self, password):
        # Extract features
        features = self.extract_features(password)
        
        # Create feature array
        X = np.array([[features[col] for col in self.feature_names]])
        
        # Load model and scaler if not loaded
        if not hasattr(self, 'best_model'):
            try:
                self.best_model = joblib.load('models/best_model.pkl')
                self.scaler = joblib.load('models/scaler.pkl')
            except:
                # If no trained model, use rule-based approach
                strength_score = min(features['length'] // 3 + 
                                   features['has_uppercase'] + 
                                   features['has_lowercase'] + 
                                   features['has_digits'] + 
                                   features['has_special'], 4)
                return {
                    'strength': self.strength_labels[strength_score],
                    'confidence': 0.8,
                    'probabilities': [0.2, 0.2, 0.2, 0.2, 0.2],
                    'features': features
                }
        
        # Scale features and predict
        X_scaled = self.scaler.transform(X)
        
        if hasattr(self.best_model, 'predict_proba'):
            probabilities = self.best_model.predict_proba(X_scaled)[0]
            prediction = self.best_model.predict(X_scaled)[0]
            confidence = max(probabilities)
        else:
            prediction = self.best_model.predict(X_scaled)[0]
            probabilities = [0.2, 0.2, 0.2, 0.2, 0.2]
            confidence = 0.8
        
        return {
            'strength': self.strength_labels[prediction],
            'confidence': float(confidence),
            'probabilities': [float(p) for p in probabilities],
            'features': features
        }
