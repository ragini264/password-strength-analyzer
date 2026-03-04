// static/js/training.js
class ModelTrainer {
    constructor() {
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        document.getElementById('trainBtn').addEventListener('click', () => {
            this.startTraining();
        });
    }

    async startTraining() {
        const trainBtn = document.getElementById('trainBtn');
        const progressCard = document.getElementById('progressCard');
        const resultsCard = document.getElementById('resultsCard');
        
        // Show progress card
        progressCard.classList.remove('d-none');
        trainBtn.disabled = true;
        trainBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Training...';

        const trainingLog = document.getElementById('trainingLog');
        trainingLog.innerHTML = '';

        try {
            this.logMessage('Starting model training...');
            this.logMessage('Generating password dataset...');
            
            const response = await fetch('/api/train_model', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const result = await response.json();

            if (response.ok) {
                this.logMessage('Training completed successfully!', 'success');
                this.displayResults(result.results);
                resultsCard.classList.remove('d-none');
            } else {
                throw new Error(result.message || 'Training failed');
            }
        } catch (error) {
            console.error('Error:', error);
            this.logMessage(`Error: ${error.message}`, 'error');
        } finally {
            trainBtn.disabled = false;
            trainBtn.innerHTML = '<i class="fas fa-play"></i> Start Training';
        }
    }

    logMessage(message, type = 'info') {
        const trainingLog = document.getElementById('trainingLog');
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry text-${type === 'error' ? 'danger' : 'success'}`;
        
        const timestamp = new Date().toLocaleTimeString();
        logEntry.innerHTML = `<strong>[${timestamp}]</strong> ${message}`;
        
        trainingLog.appendChild(logEntry);
        trainingLog.scrollTop = trainingLog.scrollHeight;
    }

    displayResults(results) {
        const modelResults = document.getElementById('modelResults');
        
        // Display best model
        if (results.best_model) {
            const bestModelData = results[results.best_model];
            modelResults.innerHTML = `
                <div class="alert alert-success">
                    <h5><i class="fas fa-trophy"></i> Best Model: ${results.best_model}</h5>
                    <p><strong>Accuracy:</strong> ${(bestModelData.accuracy * 100).toFixed(2)}%</p>
                    <p><strong>Cross-Validation Score:</strong> ${(bestModelData.cv_mean * 100).toFixed(2)}%</p>
                    <p class="mb-0"><strong>Model trained successfully and ready to use!</strong></p>
                </div>
                <div class="mt-3">
                    <p>You can now go to the homepage and analyze passwords!</p>
                    <a href="/" class="btn btn-success">Go to Password Analyzer</a>
                </div>
            `;
        }
    }
}

// Initialize the trainer when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ModelTrainer();
});
