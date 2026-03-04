// static/js/analysis.js
class BatchAnalyzer {
    constructor() {
        this.results = [];
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        document.getElementById('analyzeBatchBtn').addEventListener('click', () => {
            this.analyzeBatch();
        });

        document.getElementById('clearBtn').addEventListener('click', () => {
            this.clearInput();
        });

        document.getElementById('sampleBtn').addEventListener('click', () => {
            this.loadSampleData();
        });
    }

    async analyzeBatch() {
        const passwordText = document.getElementById('passwordList').value.trim();
        
        if (!passwordText) {
            alert('Please enter some passwords to analyze.');
            return;
        }

        const passwords = passwordText.split('\n')
            .map(p => p.trim())
            .filter(p => p.length > 0);

        if (passwords.length === 0) {
            alert('No valid passwords found.');
            return;
        }

        const analyzeBtn = document.getElementById('analyzeBatchBtn');
        const originalText = analyzeBtn.innerHTML;
        
        // Show loading state
        analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
        analyzeBtn.disabled = true;

        try {
            const response = await fetch('/api/batch_predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ passwords: passwords })
            });

            const result = await response.json();

            if (response.ok) {
                this.results = result.results;
                this.displayResults();
            } else {
                throw new Error(result.error || 'Analysis failed');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error analyzing passwords: ' + error.message);
        } finally {
            // Restore button state
            analyzeBtn.innerHTML = originalText;
            analyzeBtn.disabled = false;
        }
    }

    displayResults() {
        const resultsCard = document.getElementById('resultsCard');
        const resultsTable = document.querySelector('#resultsTable tbody');
        
        resultsCard.classList.remove('d-none');
        resultsTable.innerHTML = '';

        this.results.forEach((result, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><code>${this.maskPassword(result.password)}</code></td>
                <td><span class="badge bg-${this.getStrengthColor(result.strength)}">${result.strength}</span></td>
                <td>${(result.confidence * 100).toFixed(1)}%</td>
                <td>${result.password.length}</td>
            `;
            resultsTable.appendChild(row);
        });
    }

    maskPassword(password) {
        if (password.length <= 4) {
            return '*'.repeat(password.length);
        }
        return password.substring(0, 2) + '*'.repeat(password.length - 4) + password.substring(password.length - 2);
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

    clearInput() {
        document.getElementById('passwordList').value = '';
    }

    loadSampleData() {
        const samplePasswords = [
            'password',
            '123456',
            'qwerty',
            'Password123',
            'SecureP@ss1',
            'VeryStrongP@ssw0rd!',
            'admin',
            'letmein',
            'welcome',
            'monkey'
        ].join('\n');

        document.getElementById('passwordList').value = samplePasswords;
    }
}

// Initialize the batch analyzer
const batchAnalyzer = new BatchAnalyzer();
