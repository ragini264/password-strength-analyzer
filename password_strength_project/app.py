# app.py
from flask import Flask, render_template, request, jsonify, session
import os
import secrets
from ml_pipeline import PasswordStrengthML

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Initialize ML pipeline
ml_pipeline = PasswordStrengthML()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/train')
def train_model():
    return render_template('training.html')

@app.route('/analyze')
def analyze():
    return render_template('analysis.html')

@app.route('/results')
def results():
    return render_template('results.html')

@app.route('/api/train_model', methods=['POST'])
def api_train_model():
    try:
        print("Starting model training...")
        df = ml_pipeline.generate_dataset()
        results = ml_pipeline.train_models(df)
        
        session['training_results'] = results
        session['model_trained'] = True
        
        return jsonify({
            'status': 'success',
            'message': 'Model trained successfully!',
            'results': results
        })
    except Exception as e:
        print(f"Training error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Training failed: {str(e)}'
        }), 500

@app.route('/api/predict_strength', methods=['POST'])
def api_predict_strength():
    try:
        data = request.get_json()
        password = data.get('password', '')
        
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        if not session.get('model_trained'):
            return jsonify({'error': 'Please train the model first'}), 400
        
        prediction = ml_pipeline.predict_strength(password)
        
        return jsonify({
            'password': password,
            'prediction': prediction['strength'],
            'confidence': prediction['confidence'],
            'probabilities': prediction['probabilities'],
            'features': prediction['features']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/batch_predict', methods=['POST'])
def api_batch_predict():
    try:
        data = request.get_json()
        passwords = data.get('passwords', [])
        
        if not passwords:
            return jsonify({'error': 'Passwords are required'}), 400
        
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
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_training_results')
def api_get_training_results():
    results = session.get('training_results', {})
    return jsonify(results)

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('models', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    print("=" * 60)
    print("🔐 PASSWORD STRENGTH ANALYZER")
    print("=" * 60)
    print("Starting server...")
    print("Open your web browser and go to: http://localhost:5000")
    print("Press Ctrl+C in IDLE to stop the server")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
