// static/js/results.js
class ResultsVisualizer {
    constructor() {
        this.displayPerformanceMetrics();
    }

    async displayPerformanceMetrics() {
        try {
            const response = await fetch('/api/get_training_results');
            const trainingResults = await response.json();
            
            this.updateMetrics(trainingResults);
        } catch (error) {
            console.error('Error loading training results:', error);
        }
    }

    updateMetrics(trainingResults) {
        const metricsContainer = document.getElementById('performanceMetrics');
        
        if (!trainingResults || Object.keys(trainingResults).length === 0) {
            metricsContainer.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-warning">
                        <i class="fas fa-exclamation-triangle"></i> 
                        No training results available. Please train the model first.
                    </div>
                </div>
            `;
            return;
        }

        let bestModel = trainingResults.best_model || 'Not Available';
        let bestAccuracy = 0;

        Object.entries(trainingResults).forEach(([modelName, modelData]) => {
            if (modelName !== 'best_model' && modelData.accuracy > bestAccuracy) {
                bestAccuracy = modelData.accuracy;
            }
        });

        metricsContainer.innerHTML = `
            <div class="col-md-3">
                <div class="card text-center bg-primary text-white">
                    <div class="card-body">
                        <h3>${Object.keys(trainingResults).length - 1}</h3>
                        <p class="mb-0">Models Trained</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center bg-success text-white">
                    <div class="card-body">
                        <h3>${bestModel}</h3>
                        <p class="mb-0">Best Model</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center bg-info text-white">
                    <div class="card-body">
                        <h3>${(bestAccuracy * 100).toFixed(1)}%</h3>
                        <p class="mb-0">Best Accuracy</p>
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
        `;
    }
}

// Initialize the visualizer when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ResultsVisualizer();
});
