# password_analyzer.py - COMPLETE PASSWORD STRENGTH ANALYZER
import pandas as pd
import numpy as np
import random
import string
import secrets
from sklearn.utils import shuffle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import joblib
import os
from flask import Flask, render_template, request, jsonify, session
import json


# PASSWORD DATASET GENERATOR

class PasswordDatasetGenerator:
    def __init__(self):
        self.strength_labels = {
            0: 'Very Weak',
            1: 'Weak', 
            2: 'Medium',
            3: 'Strong',
            4: 'Very Strong'
        }
    
    def generate_weak_passwords(self):
        passwords = []
        strengths = []
        
        # Common weak passwords
        common_weak = [
            '123456', 'password', '12345678', 'qwerty', '123456789',
            '12345', '1234', '111111', '1234567', 'dragon',
            '123123', 'baseball', 'abc123', 'football', 'monkey'
        ]
        
        for pwd in common_weak:
            passwords.append(pwd)
            strengths.append(0)
            
        # Sequential patterns
        for i in range(50):
            passwords.append(str(i) * 3)
            strengths.append(0)
            passwords.append('abc' + str(i))
            strengths.append(0)
            
        # Keyboard patterns
        keyboard_patterns = ['qwerty', 'asdfgh', 'zxcvbn', 'qazwsx']
        for pattern in keyboard_patterns:
            passwords.append(pattern)
            strengths.append(0)
            passwords.append(pattern + '123')
            strengths.append(1)
        
        # Weak variations
        for base in common_weak[:10]:
            for i in range(3):
                passwords.append(base + str(i))
                strengths.append(1)
        
        return passwords, strengths
    
    def generate_medium_passwords(self):
        passwords = []
        strengths = []
        
        base_words = ['pass', 'secure', 'safe', 'guard', 'shield']
        special_chars = ['!', '@', '#', '$', '%']
        
        for word in base_words:
            for i in range(20):
                pwd = word.capitalize() + str(i) + random.choice(special_chars)
                passwords.append(pwd)
                strengths.append(2)
                
                pwd = word.upper() + str(i*10) + word.lower()
                passwords.append(pwd)
                strengths.append(2)
        
        # Random medium passwords
        for _ in range(100):
            length = random.randint(8, 10)
            pwd = ''.join(random.choice(string.ascii_letters + string.digits) 
                         for _ in range(length))
            if (any(c.islower() for c in pwd) and 
                any(c.isupper() for c in pwd) and 
                any(c.isdigit() for c in pwd)):
                passwords.append(pwd)
                strengths.append(2)
        
        return passwords, strengths
    
    def generate_strong_passwords(self):
        passwords = []
        strengths = []
        
        # Strong passwords
        for i in range(100):
            length = random.randint(10, 12)
            pwd = ''.join(random.choice(string.ascii_letters + string.digits + '!@#$%') 
                         for _ in range(length))
            if (sum(1 for c in pwd if c.islower()) >= 2 and
                sum(1 for c in pwd if c.isupper()) >= 2 and
                sum(1 for c in pwd if c.isdigit()) >= 2 and
                sum(1 for c in pwd if c in '!@#$%') >= 1):
                passwords.append(pwd)
                strengths.append(3)
        
        # Very strong passwords
        for i in range(100):
            length = random.randint(14, 18)
            pwd = ''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$%^&*') 
                         for _ in range(length))
            passwords.append(pwd)
            strengths.append(4)
        
        return passwords, strengths
    
    def calculate_features(self, password):
        features = {
            'length': len(password),
            'uppercase_count': sum(1 for c in password if c.isupper()),
            'lowercase_count': sum(1 for c in password if c.islower()),
            'digit_count': sum(1 for c in password if c.isdigit()),
            'special_count': sum(1 for c in password if c in string.punctuation),
            'has_uppercase': int(any(c.isupper() for c in password)),
            'has_lowercase': int(any(c.islower() for c in password)),
            'has_digits': int(any(c.isdigit() for c in password)),
            'has_special': int(any(c in string.punctuation for c in password))
        }
        
        # Calculate entropy
        if len(password) == 0:
            features['entropy'] = 0
        else:
            char_count = {}
            for char in password:
                char_count[char] = char_count.get(char, 0) + 1
            entropy = 0
            for count in char_count.values():
                p = count / len(password)
                if p > 0:
                    entropy -= p * np.log2(p)
            features['entropy'] = entropy
        
        return features
    
    def generate_complete_dataset(self, total_samples=800):
        print("Generating password dataset...")
        
        # Generate passwords of different strengths
        weak_passwords, weak_strengths = self.generate_weak_passwords()
        medium_passwords, medium_strengths = self.generate_medium_passwords()
        strong_passwords, strong_strengths = self.generate_strong_passwords()
        
        # Combine all passwords
        all_passwords = weak_passwords + medium_passwords + strong_passwords
        all_strengths = weak_strengths + medium_strengths + strong_strengths
        
        # Remove duplicates
        seen = set()
        unique_passwords = []
        unique_strengths = []
        for pwd, strength in zip(all_passwords, all_strengths):
            if pwd not in seen:
                seen.add(pwd)
                unique_passwords.append(pwd)
                unique_strengths.append(strength)
        
        # Shuffle
        unique_passwords, unique_strengths = shuffle(
            unique_passwords, unique_strengths, random_state=42
        )
        
        # Take requested number of samples
        if len(unique_passwords) > total_samples:
            unique_passwords = unique_passwords[:total_samples]
            unique_strengths = unique_strengths[:total_samples]
        
        print(f"Generated {len(unique_passwords)} unique passwords")
        
        # Calculate features
        feature_data = []
        for password in unique_passwords:
            features = self.calculate_features(password)
            feature_data.append(features)
        
        # Create DataFrame
        df = pd.DataFrame({
            'password': unique_passwords,
            'strength': unique_strengths
        })
        
        # Add feature columns
        for feature_name in feature_data[0].keys():
            df[feature_name] = [features[feature_name] for features in feature_data]
        
        # Add strength labels
        df['strength_label'] = df['strength'].map(self.strength_labels)
        
        # Display statistics
        self.print_dataset_stats(df)
        
        return df
    
    def print_dataset_stats(self, df):
        print("\nDataset Statistics:")
        print("=" * 40)
        print(f"Total passwords: {len(df)}")
        print("\nStrength Distribution:")
        strength_counts = df['strength_label'].value_counts().sort_index()
        for strength, count in strength_counts.items():
            percentage = (count / len(df)) * 100
            print(f"  {strength}: {count} ({percentage:.1f}%)")

# MACHINE LEARNING PIPELINE

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
        self.dataset_generator = PasswordDatasetGenerator()
        self.model_trained = False
        
    def load_or_create_dataset(self):
        csv_path = 'data/passwords.csv'
        
        if os.path.exists(csv_path):
            print("Loading existing password dataset...")
            df = pd.read_csv(csv_path)
        else:
            print("Creating new password dataset...")
            os.makedirs('data', exist_ok=True)
            df = self.dataset_generator.generate_complete_dataset(500)
            df.to_csv(csv_path, index=False)
        
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
        
        # Use Random Forest
        print("Training Random Forest model...")
        model = RandomForestClassifier(n_estimators=50, random_state=42)
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        cv_scores = cross_val_score(model, X_train, y_train, cv=3)
        
        # Store model
        self.models['Random Forest'] = model
        self.best_model = model
        self.model_trained = True
        
        # Save model and scaler
        joblib.dump(self.best_model, 'models/best_model.pkl')
        joblib.dump(self.scaler, 'models/scaler.pkl')
        
        print("Model training completed!")
        
        # Return only serializable data
        return {
            'accuracy': float(accuracy),
            'cv_mean': float(cv_scores.mean()),
            'cv_std': float(cv_scores.std()),
            'best_model': 'Random Forest'
        }
    
    def predict_strength(self, password):
        # Extract features
        features = self.extract_features(password)
        
        # Create feature array
        X = np.array([[features[col] for col in self.feature_names]])
        
        # Load model and scaler if not loaded
        if not self.model_trained:
            try:
                self.best_model = joblib.load('models/best_model.pkl')
                self.scaler = joblib.load('models/scaler.pkl')
                self.model_trained = True
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

# FLASK WEB APPLICATION

app = Flask(__name__)
app.secret_key = 'password_strength_secret_key'

# Initialize ML pipeline
ml_pipeline = PasswordStrengthML()

# HTML Templates
HOME_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Password Strength Analyzer</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; font-family: Arial, sans-serif; padding-top: 20px; }
        .card { border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .strength-meter { background: #e9ecef; height: 20px; border-radius: 10px; overflow: hidden; margin: 10px 0; }
        .strength-bar { height: 100%; transition: all 0.3s; }
        .strength-very-weak { background-color: #dc3545; width: 20%; }
        .strength-weak { background-color: #fd7e14; width: 40%; }
        .strength-medium { background-color: #ffc107; width: 60%; }
        .strength-strong { background-color: #20c997; width: 80%; }
        .strength-very-strong { background-color: #198754; width: 100%; }
        .feature-item { padding: 8px; margin: 5px 0; background: #f8f9fa; border-radius: 5px; border-left: 4px solid #007bff; }
        .feature-good { border-left-color: #198754; background: #d4edda; }
        .feature-bad { border-left-color: #dc3545; background: #f8d7da; }
    </style>
</head>
<body>
    <div class="container">
        <div class="row">
            <div class="col-md-8 mx-auto">
                <div class="text-center mb-4">
                    <h1 class="text-primary">🔐 Password Strength Analyzer</h1>
                    <p class="lead">Check your password strength using Machine Learning</p>
                </div>

                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h4 class="mb-0">Check Password Strength</h4>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label class="form-label">Enter Password:</label>
                            <div class="input-group">
                                <input type="password" class="form-control" id="passwordInput" placeholder="Enter password to analyze">
                                <button class="btn btn-outline-secondary" type="button" onclick="togglePassword()">
                                    👁️
                                </button>
                            </div>
                            <div class="form-text">We don't store any passwords you analyze.</div>
                        </div>
                        <button class="btn btn-success w-100" onclick="analyzePassword()">
                            🔍 Analyze Strength
                        </button>
                    </div>
                </div>

                <div class="card d-none" id="resultsCard">
                    <div class="card-header">
                        <h4 class="mb-0">Analysis Results</h4>
                    </div>
                    <div class="card-body">
                        <div class="strength-meter">
                            <div class="strength-bar" id="strengthBar"></div>
                        </div>
                        <div class="row mb-3">
                            <div class="col-6">
                                <h5>Strength: <span id="strengthText" class="badge">-</span></h5>
                            </div>
                            <div class="col-6">
                                <h5>Confidence: <span id="confidenceText">-</span></h5>
                            </div>
                        </div>
                        <div id="featureDetails"></div>
                    </div>
                </div>

                <div class="row mt-4">
                    <div class="col-md-4">
                        <div class="card text-center h-100">
                            <div class="card-body">
                                <h5>🤖 Train Model</h5>
                                <p>Train the ML model first</p>
                                <a href="/train" class="btn btn-outline-primary">Train Model</a>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card text-center h-100">
                            <div class="card-body">
                                <h5>📊 Batch Analysis</h5>
                                <p>Analyze multiple passwords</p>
                                <a href="/analyze" class="btn btn-outline-success">Batch Analyze</a>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card text-center h-100">
                            <div class="card-body">
                                <h5>📈 Results</h5>
                                <p>View model performance</p>
                                <a href="/results" class="btn btn-outline-info">View Results</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function togglePassword() {
            const input = document.getElementById('passwordInput');
            input.type = input.type === 'password' ? 'text' : 'password';
        }

        function analyzePassword() {
            const password = document.getElementById('passwordInput').value;
            if (!password) {
                alert('Please enter a password');
                return;
            }

            const button = event.target;
            button.disabled = true;
            button.innerHTML = '⏳ Analyzing...';

            fetch('/api/predict', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({password: password})
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert('Error: ' + data.error);
                } else {
                    displayResults(data);
                }
                button.disabled = false;
                button.innerHTML = '🔍 Analyze Strength';
            })
            .catch(error => {
                alert('Error: ' + error);
                button.disabled = false;
                button.innerHTML = '🔍 Analyze Strength';
            });
        }

        function displayResults(result) {
            document.getElementById('resultsCard').classList.remove('d-none');
            
            // Update strength
            const strengthText = document.getElementById('strengthText');
            strengthText.textContent = result.strength;
            strengthText.className = 'badge bg-' + getStrengthColor(result.strength);
            
            // Update confidence
            document.getElementById('confidenceText').textContent = (result.confidence * 100).toFixed(1) + '%';
            
            // Update strength bar
            const strengthBar = document.getElementById('strengthBar');
            strengthBar.className = 'strength-bar strength-' + result.strength.toLowerCase().replace(' ', '-');
            
            // Update features
            const features = result.features;
            let featureHTML = '<h6>Feature Analysis:</h6><div class="row">';
            
            const featureConfig = [
                {label: 'Length', value: features.length + ' chars', good: features.length >= 12},
                {label: 'Uppercase', value: features.has_uppercase ? 'Present ✓' : 'Missing ✗', good: features.has_uppercase},
                {label: 'Lowercase', value: features.has_lowercase ? 'Present ✓' : 'Missing ✗', good: features.has_lowercase},
                {label: 'Numbers', value: features.has_digits ? 'Present ✓' : 'Missing ✗', good: features.has_digits},
                {label: 'Special Chars', value: features.has_special ? 'Present ✓' : 'Missing ✗', good: features.has_special},
                {label: 'Entropy', value: features.entropy.toFixed(2), good: features.entropy >= 3}
            ];
            
            featureConfig.forEach(feature => {
                featureHTML += `
                    <div class="col-md-6 mb-2">
                        <div class="feature-item ${feature.good ? 'feature-good' : 'feature-bad'}">
                            <strong>${feature.label}:</strong> ${feature.value}
                        </div>
                    </div>
                `;
            });
            
            featureHTML += '</div>';
            document.getElementById('featureDetails').innerHTML = featureHTML;
        }

        function getStrengthColor(strength) {
            const colors = {
                'Very Weak': 'danger',
                'Weak': 'warning', 
                'Medium': 'info',
                'Strong': 'success',
                'Very Strong': 'primary'
            };
            return colors[strength] || 'secondary';
        }
    </script>
</body>
</html>
'''

TRAIN_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Train Model</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; padding-top: 20px; }
        .card { border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div class="container">
        <div class="row">
            <div class="col-md-6 mx-auto">
                <div class="text-center mb-4">
                    <h1 class="text-warning">🤖 Train Model</h1>
                    <p class="lead">Train the machine learning model</p>
                </div>

                <div class="card">
                    <div class="card-header bg-warning text-dark">
                        <h4 class="mb-0">Model Training</h4>
                    </div>
                    <div class="card-body">
                        <p>Click the button below to train the model with password data. This may take a few seconds.</p>
                        <button class="btn btn-primary w-100" onclick="trainModel()">🚀 Start Training</button>
                        <div id="trainingResult" class="mt-3"></div>
                    </div>
                </div>
                
                <div class="text-center mt-3">
                    <a href="/" class="btn btn-secondary">← Back to Home</a>
                </div>
            </div>
        </div>
    </div>

    <script>
        function trainModel() {
            const button = event.target;
            button.disabled = true;
            button.innerHTML = '⏳ Training...';
            
            document.getElementById('trainingResult').innerHTML = `
                <div class="alert alert-info">
                    <strong>Training started...</strong><br>
                    Generating dataset and training model. Please wait.
                </div>
            `;
            
            fetch('/api/train', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    document.getElementById('trainingResult').innerHTML = `
                        <div class="alert alert-success">
                            <h5>🎉 Training Completed!</h5>
                            <p><strong>Accuracy:</strong> ${(data.results.accuracy * 100).toFixed(2)}%</p>
                            <p><strong>Cross-Validation Score:</strong> ${(data.results.cv_mean * 100).toFixed(2)}%</p>
                            <p class="mb-0"><strong>Best Model:</strong> ${data.results.best_model}</p>
                        </div>
                        <div class="text-center">
                            <a href="/" class="btn btn-success">✅ Go Analyze Passwords</a>
                        </div>
                    `;
                } else {
                    document.getElementById('trainingResult').innerHTML = `
                        <div class="alert alert-danger">
                            <h5>❌ Training Failed</h5>
                            <p>${data.message}</p>
                        </div>
                    `;
                }
                button.disabled = false;
                button.innerHTML = '🚀 Start Training';
            })
            .catch(error => {
                document.getElementById('trainingResult').innerHTML = `
                    <div class="alert alert-danger">
                        <h5>❌ Error</h5>
                        <p>${error}</p>
                    </div>
                `;
                button.disabled = false;
                button.innerHTML = '🚀 Start Training';
            });
        }
    </script>
</body>
</html>
'''

ANALYZE_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Batch Analysis</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; padding-top: 20px; }
        .card { border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div class="container">
        <div class="row">
            <div class="col-md-8 mx-auto">
                <div class="text-center mb-4">
                    <h1 class="text-success">📊 Batch Analysis</h1>
                    <p class="lead">Analyze multiple passwords at once</p>
                </div>

                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h4 class="mb-0">Password Input</h4>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label class="form-label">Enter passwords (one per line):</label>
                            <textarea class="form-control" id="passwordList" rows="6" placeholder="password123&#10;SecureP@ss1&#10;VeryStrongP@ssw0rd!"></textarea>
                        </div>
                        <div class="d-flex gap-2">
                            <button class="btn btn-success" onclick="analyzeBatch()">🔍 Analyze Passwords</button>
                            <button class="btn btn-outline-secondary" onclick="loadSample()">📋 Load Sample</button>
                            <button class="btn btn-outline-danger" onclick="clearInput()">🗑️ Clear</button>
                        </div>
                    </div>
                </div>

                <div class="card mt-4 d-none" id="resultsCard">
                    <div class="card-header bg-success text-white">
                        <h4 class="mb-0">Analysis Results</h4>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Password</th>
                                        <th>Strength</th>
                                        <th>Confidence</th>
                                        <th>Length</th>
                                    </tr>
                                </thead>
                                <tbody id="resultsTable">
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <div class="text-center mt-3">
                    <a href="/" class="btn btn-secondary">← Back to Home</a>
                </div>
            </div>
        </div>
    </div>

    <script>
        function analyzeBatch() {
            const passwordsText = document.getElementById('passwordList').value;
            const passwords = passwordsText.split('\\n').filter(p => p.trim().length > 0);
            
            if (passwords.length === 0) {
                alert('Please enter some passwords');
                return;
            }

            const button = event.target;
            button.disabled = true;
            button.innerHTML = '⏳ Analyzing...';

            fetch('/api/batch_predict', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({passwords: passwords})
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert('Error: ' + data.error);
                } else {
                    displayBatchResults(data.results);
                document.getElementById('resultsCard').classList.remove('d-none');
                button.disabled = false;
                    button.innerHTML = '🔍 Analyze Passwords';
                }
            })
            .catch(error => {
                alert('Error: ' + error);
                button.disabled = false;
                button.innerHTML = '🔍 Analyze Passwords';
            });
        }

        function displayBatchResults(results) {
            const table = document.getElementById('resultsTable');
            table.innerHTML = '';
            
            results.forEach(result => {
                const row = document.createElement('tr');
                const maskedPassword = result.password.length <= 4 ? 
                    '*'.repeat(result.password.length) :
                    result.password.substring(0, 2) + '*'.repeat(result.password.length - 4) + result.password.substring(result.password.length - 2);
                
                row.innerHTML = `
                    <td><code>${maskedPassword}</code></td>
                    <td><span class="badge bg-${getStrengthColor(result.strength)}">${result.strength}</span></td>
                    <td>${(result.confidence * 100).toFixed(1)}%</td>
                    <td>${result.password.length}</td>
                `;
                table.appendChild(row);
            });
        }

        function getStrengthColor(strength) {
            const colors = {
                'Very Weak': 'danger',
                'Weak': 'warning',
                'Medium': 'info',
                'Strong': 'success', 
                'Very Strong': 'primary'
            };
            return colors[strength] || 'secondary';
        }

        function loadSample() {
            document.getElementById('passwordList').value = 
                'password\\n123456\\nPassword123\\nSecureP@ss1\\nVeryStrongP@ssw0rd!\\nadmin\\nqwerty\\nletmein';
        }

        function clearInput() {
            document.getElementById('passwordList').value = '';
        }
    </script>
</body>
</html>
'''

RESULTS_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Results</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; padding-top: 20px; }
        .card { border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .tip-item { padding: 15px; margin: 10px 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="row">
            <div class="col-md-10 mx-auto">
                <div class="text-center mb-4">
                    <h1 class="text-info">📈 Model Results</h1>
                    <p class="lead">View model performance and insights</p>
                </div>

                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h4 class="mb-0">📊 Model Information</h4>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-3">
                                <div class="card text-center bg-success text-white">
                                    <div class="card-body">
                                        <h3>Random Forest</h3>
                                        <p class="mb-0">Algorithm</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="card text-center bg-info text-white">
                                    <div class="card-body">
                                        <h3>10</h3>
                                        <p class="mb-0">Features</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="card text-center bg-warning text-white">
                                    <div class="card-body">
                                        <h3>5</h3>
                                        <p class="mb-0">Strength Levels</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="card text-center bg-secondary text-white">
                                    <div class="card-body">
                                        <h3>500+</h3>
                                        <p class="mb-0">Passwords</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header bg-success text-white">
                        <h4 class="mb-0">💡 Password Strength Tips</h4>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="tip-item">
                                    <h5>📏 Use Long Passwords</h5>
                                    <p>Passwords with 12+ characters are much stronger. Each additional character increases security exponentially.</p>
                                </div>
                                <div class="tip-item">
                                    <h5>🔤 Mix Character Types</h5>
                                    <p>Use uppercase letters, lowercase letters, numbers, and special characters for maximum strength.</p>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="tip-item">
                                    <h5>🚫 Avoid Common Patterns</h5>
                                    <p>Don't use sequential numbers, common words, or keyboard patterns like "qwerty" or "123456".</p>
                                </div>
                                <div class="tip-item">
                                    <h5>🛡️ Use Unique Passwords</h5>
                                    <p>Never reuse passwords across different websites or services.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header bg-warning text-dark">
                        <h4 class="mb-0">⚖️ What Makes a Password Strong?</h4>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <h6>Password Length (Most Important - 40%)</h6>
                            <div class="progress" style="height: 25px;">
                                <div class="progress-bar bg-success" style="width: 40%">12+ Characters</div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <h6>Character Variety (25%)</h6>
                            <div class="progress" style="height: 25px;">
                                <div class="progress-bar bg-info" style="width: 25%">Mixed Types</div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <h6>Special Characters (15%)</h6>
                            <div class="progress" style="height: 25px;">
                                <div class="progress-bar bg-primary" style="width: 15%">!@#$% etc.</div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <h6>Randomness (10%)</h6>
                            <div class="progress" style="height: 25px;">
                                <div class="progress-bar bg-warning" style="width: 10%">High Entropy</div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <h6>Numbers & Uppercase (10%)</h6>
                            <div class="progress" style="height: 25px;">
                                <div class="progress-bar bg-secondary" style="width: 10%">A-Z, 0-9</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="text-center mt-3">
                    <a href="/" class="btn btn-secondary">← Back to Home</a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

# Routes
@app.route('/')
def index():
    return HOME_PAGE

@app.route('/train')
def train_page():
    return TRAIN_PAGE

@app.route('/analyze')
def analyze_page():
    return ANALYZE_PAGE

@app.route('/results')
def results_page():
    return RESULTS_PAGE

# API Routes
@app.route('/api/train', methods=['POST'])
def api_train():
    try:
        print("Starting model training...")
        df = ml_pipeline.generate_dataset()
        results = ml_pipeline.train_models(df)
        session['model_trained'] = True
        return jsonify({'status': 'success', 'results': results})
    except Exception as e:
        print(f"Training error: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/predict', methods=['POST'])
def api_predict():
    try:
        data = request.get_json()
        password = data.get('password', '')
        
        if not password:
            return jsonify({'error': 'Password is required'})
        
        if not ml_pipeline.model_trained and not session.get('model_trained'):
            return jsonify({'error': 'Please train the model first by going to /train'})
        
        prediction = ml_pipeline.predict_strength(password)
        return jsonify(prediction)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/batch_predict', methods=['POST'])
def api_batch_predict():
    try:
        data = request.get_json()
        passwords = data.get('passwords', [])
        
        if not passwords:
            return jsonify({'error': 'Passwords are required'})
        
        results = []
        for password in passwords:
            prediction = ml_pipeline.predict_strength(password)
            results.append({
                'password': password,
                'strength': prediction['strength'],
                'confidence': prediction['confidence']
            })
        
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)})

# =============================================================================
# MAIN EXECUTION
# =============================================================================
if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('models', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    print("=" * 60)
    print("🔐 PASSWORD STRENGTH ANALYZER")
    print("=" * 60)
    print("Starting server...")
    print("Open your web browser and go to: http://localhost:5000")
    print("")
    print("INSTRUCTIONS:")
    print("1. First, train the model: http://localhost:5000/train")
    print("2. Then analyze passwords: http://localhost:5000")
    print("3. Use batch analysis for multiple passwords")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
