import { useState } from 'react';
import axios from 'axios';

const PredictionForm = ({ onPrediction, setLoading, setError }) => {
  const [ticker, setTicker] = useState('');
  const [days, setDays] = useState(7);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!ticker) return;

    setLoading(true);
    onPrediction(null);
    setError(null);

    try {
      const response = await axios.post('http://localhost:5000/api/predict', { ticker, days });
      onPrediction(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch prediction');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel" style={{ height: '100%' }}>
      <h2 style={{ marginBottom: '1.5rem', color: 'var(--accent-color)' }}>
        Analyze Stock
      </h2>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <div>
          <label
            htmlFor="ticker"
            style={{
              display: 'block',
              marginBottom: '0.5rem',
              color: 'var(--text-secondary)',
              fontSize: '0.9rem',
              fontWeight: '500'
            }}
          >
            TICKER SYMBOL
          </label>
          <input
            id="ticker"
            type="text"
            className="input-field"
            placeholder="e.g. AAPL, TSLA, GOOGL"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            style={{
              fontSize: '1.25rem',
              letterSpacing: '0.05em',
              textTransform: 'uppercase'
            }}
          />
        </div>

        <button
          type="submit"
          className="btn-primary"
          disabled={!ticker}
        >
          Generate Prediction
        </button>
      </form>

      <div style={{ marginTop: '2rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
        <p>Supported Markets: US Stocks (NYSE, NASDAQ)</p>
        <p>Model: XGBoost (Pre-trained)</p>
      </div>
    </div>
  );
};

export default PredictionForm;
