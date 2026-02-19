import React from 'react';

const ResultCard = ({ data, loading }) => {
  if (loading) {
    return (
      <div className="glass-panel flex-center" style={{ height: '100%', minHeight: '300px' }}>
        <div style={{ textAlign: 'center' }}>
          <div className="loader" style={{
            border: '4px solid rgba(255, 255, 255, 0.1)',
            borderTop: '4px solid var(--primary-color)',
            borderRadius: '50%',
            width: '40px',
            height: '40px',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 1rem'
          }}></div>
          <p style={{ color: 'var(--text-secondary)', letterSpacing: '0.05em' }}>
            Running Inference Models...
          </p>
          <style>{`
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
          `}</style>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="glass-panel flex-center" style={{ height: '100%', minHeight: '300px', opacity: 0.7 }}>
        <div style={{ textAlign: 'center' }}>
          <span style={{ fontSize: '3rem', display: 'block', marginBottom: '1rem', opacity: 0.5 }}>
            📈
          </span>
          <p style={{ color: 'var(--text-secondary)' }}>
            Enter a ticker symbol to view AI-generated price predictions.
          </p>
        </div>
      </div>
    );
  }

  const isBullish = data.sentiment === 'Bullish';
  const sentimentColor = isBullish ? 'var(--success-color)' : 'var(--error-color)';

  return (
    <div className="glass-panel" style={{ height: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <span className="card-title">Prediction Result</span>
          <h2 style={{ fontSize: '2.5rem', margin: 0 }}>{data.ticker}</h2>
        </div>
        <div style={{
          background: `rgba(${isBullish ? '16, 185, 129' : '239, 68, 68'}, 0.2)`,
          color: sentimentColor,
          padding: '0.5rem 1rem',
          borderRadius: '2rem',
          fontWeight: '700',
          fontSize: '0.875rem',
          textTransform: 'uppercase'
        }}>
          {data.sentiment}
        </div>
      </div>

      <div style={{ marginBottom: '2rem' }}>
        <span className="card-title">Predicted Closing Price ({data.forecast.length} Days)</span>
        <div style={{
          fontSize: '3.5rem',
          fontWeight: '700',
          color: 'var(--text-primary)',
          letterSpacing: '-0.02em',
          textShadow: '0 0 20px rgba(255, 255, 255, 0.2)'
        }}>
          ${data.forecast[data.forecast.length - 1].price.toFixed(2)}
        </div>
      </div>

      <div style={{
        borderTop: '1px solid rgba(255, 255, 255, 0.1)',
        paddingTop: '1.5rem',
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '1rem'
      }}>
        <div>
          <span className="card-title" style={{ fontSize: '0.75rem' }}>Confidence Score</span>
          <div style={{ fontSize: '1.25rem', fontWeight: '600' }}>87%</div>
        </div>
        <div>
          <span className="card-title" style={{ fontSize: '0.75rem' }}>Processing Time</span>
          <div style={{ fontSize: '1.25rem', fontWeight: '600' }}>0.4s</div>
        </div>
      </div>
    </div>
  );
};

export default ResultCard;
