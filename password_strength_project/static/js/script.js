// static/js/script.js
class PasswordAnalyzer {
    constructor() {
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Password visibility toggle
        document.getElementById('togglePassword').addEventListener('click', (e) => {
            this.togglePasswordVisibility();
        });

        // Analyze button
        document.getElementById('analyzeBtn').addEventListener('click', () => {
            this.analyzePassword();
        });

        // Enter key support
        document.getElementById('passwordInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.analyzePassword();
            }
        });
    }

    togglePasswordVisibility() {
        const passwordInput = document.getElementById('passwordInput');
        const toggleIcon = document.getElementById('togglePassword').querySelector('i');
        
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            toggleIcon.className = 'fas fa-eye-slash';
        } else {
            passwordInput.type = 'password';
            toggleIcon.className = 'fas fa-eye';
        }
    }

    async analyzePassword() {
        const password = document.getElementById('passwordInput').value.trim();
        
        if (!password) {
            alert('Please enter a password to analyze.');
            return;
        }

        const analyzeBtn = document.getElementById('analyzeBtn');
        const originalText = analyzeBtn.innerHTML;
        
        // Show loading state
        analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
        analyzeBtn.disabled = true;

        try {
            const response = await fetch('/api/predict_strength', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ password: password })
            });

            const result = await response.json();

            if (response.ok) {
                this.displayResults(result);
            } else {
                throw new Error(result.error || 'Analysis failed');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error analyzing password: ' + error.message);
        } finally {
            // Restore button state
            analyzeBtn.innerHTML = originalText;
            analyzeBtn.disabled = false;
        }
    }

    displayResults(result) {
        const resultsCard = document.getElementById('resultsCard');
        resultsCard.classList.remove('d-none');

        // Update strength text and badge
        const strengthText = document.getElementById('strengthText');
        strengthText.textContent = result.prediction;
        strengthText.className = `badge badge-strength bg-${this.getStrengthColor(result.prediction)}`;

        // Update confidence
        document.getElementById('confidenceText').textContent = 
            `${(result.confidence * 100).toFixed(1)}%`;

        // Update strength meter
        this.updateStrengthMeter(result.prediction);

        // Update probability bars
        this.updateProbabilityBars(result.probabilities);

        // Display feature analysis
        this.displayFeatureAnalysis(result.features);
    }

    getStrengthColor(strength) {
        const colorMap = {
            'Very Weak': 'danger',
            'Weak': 'warning',
            'Medium': 'info',
            'Strong': 'success',
            'Very Strong': 'primary'
        };
        return colorMap[strength] || 'secondary';
    }

    updateStrengthMeter(strength) {
        const strengthBar = document.querySelector('.strength-bar');
        strengthBar.className = 'strength-bar';
        
        const strengthClass = `strength-${strength.toLowerCase().replace(' ', '-')}`;
        strengthBar.classList.add(strengthClass);
    }

    updateProbabilityBars(probabilities) {
        const bars = ['weakBar', 'mediumBar', 'strongBar', 'vstrongBar', 'excellentBar'];
        const labels = ['Very Weak', 'Weak', 'Medium', 'Strong', 'Very Strong'];
        
        bars.forEach((barId, index) => {
            const bar = document.getElementById(barId);
            const percentage = (probabilities[index] * 100).toFixed(1);
            bar.style.width = `${percentage}%`;
            bar.textContent = `${labels[index]} (${percentage}%)`;
        });
    }

    displayFeatureAnalysis(features) {
        const featureContainer = document.getElementById('featureDetails');
        featureContainer.innerHTML = '';

        const featureConfig = [
            {
                key: 'length',
                label: 'Length',
                good: features.length >= 12,
                warning: features.length >= 8 && features.length < 12,
                message: `${features.length} characters`
            },
            {
                key: 'has_uppercase',
                label: 'Uppercase Letters',
                good: features.has_uppercase,
                message: features.has_uppercase ? 'Present' : 'Missing'
            },
            {
                key: 'has_lowercase',
                label: 'Lowercase Letters',
                good: features.has_lowercase,
                message: features.has_lowercase ? 'Present' : 'Missing'
            },
            {
                key: 'has_digits',
                label: 'Numbers',
                good: features.has_digits,
                message: features.has_digits ? 'Present' : 'Missing'
            },
            {
                key: 'has_special',
                label: 'Special Characters',
                good: features.has_special,
                message: features.has_special ? 'Present' : 'Missing'
            },
            {
                key: 'entropy',
                label: 'Entropy',
                good: features.entropy >= 3,
                warning: features.entropy >= 2 && features.entropy < 3,
                message: `Entropy: ${features.entropy.toFixed(2)}`
            }
        ];

        featureConfig.forEach(feature => {
            const featureDiv = document.createElement('div');
            featureDiv.className = 'col-md-6 mb-2';
            
            let featureClass = 'feature-item';
            if (feature.good) {
                featureClass += ' feature-good';
            } else if (feature.warning) {
                featureClass += ' feature-warning';
            } else {
                featureClass += ' feature-bad';
            }

            featureDiv.innerHTML = `
                <div class="${featureClass}">
                    <strong>${feature.label}:</strong> ${feature.message}
                </div>
            `;
            
            featureContainer.appendChild(featureDiv);
        });
    }
}

// Initialize the analyzer when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new PasswordAnalyzer();
});
