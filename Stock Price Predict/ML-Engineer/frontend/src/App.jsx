import { useState } from 'react';
import PredictionForm from './components/PredictionForm';
import ResultCard from './components/ResultCard';
import StockChart from './components/StockChart';
import AnalysisPanel from './components/AnalysisPanel';
import './index.css';

function App() {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handlePrediction = (data) => {
    setPrediction(data);
    setError(null);
  };

  return (
    <div className="app-container">
      <header style={{ marginBottom: '3rem', textAlign: 'center' }}>
        <h1 style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>
          Stock <span className="text-gradient">Predictor</span>
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.2rem' }}>
          AI-Powered Market Forecasting
        </p>
      </header>

      <main className="grid-layout">
        <section>
          <PredictionForm
            onPrediction={handlePrediction}
            setLoading={setLoading}
            setError={setError}
          />
          {error && <div className="error-msg">{error}</div>}
        </section>

        <section>
          <ResultCard
            data={prediction}
            loading={loading}
          />
          {prediction && (
            <>
              <StockChart
                data={prediction.history}
                prediction={prediction.forecast}
              />
              <AnalysisPanel
                indicators={prediction.indicators}
              />
            </>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
