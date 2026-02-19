import React from 'react';

const AnalysisPanel = ({ indicators }) => {
  if (!indicators) return null;

  return (
    <div className="glass-panel" style={{ height: '100%', marginTop: '2rem' }}>
      <h3 style={{ marginBottom: '1.5rem', color: 'var(--accent-color)' }}>Technical Indicators</h3>

      <div className="grid-layout" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '1rem' }}>

        <div style={{ background: 'rgba(255,255,255,0.05)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
          <span className="card-title" style={{ fontSize: '0.75rem' }}>RSI (14)</span>
          <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: indicators.RSI > 70 ? 'var(--error-color)' : indicators.RSI < 30 ? 'var(--success-color)' : 'var(--text-primary)' }}>
            {indicators.RSI.toFixed(2)}
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
            {indicators.RSI > 70 ? 'Overbought' : indicators.RSI < 30 ? 'Oversold' : 'Neutral'}
          </span>
        </div>

        <div style={{ background: 'rgba(255,255,255,0.05)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
          <span className="card-title" style={{ fontSize: '0.75rem' }}>MACD</span>
          <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: indicators.MACD > indicators.Signal ? 'var(--success-color)' : 'var(--error-color)' }}>
            {indicators.MACD.toFixed(2)}
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
            Signal: {indicators.Signal.toFixed(2)}
          </span>
        </div>

        <div style={{ background: 'rgba(255,255,255,0.05)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
          <span className="card-title" style={{ fontSize: '0.75rem' }}>SMA (20)</span>
          <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
            {indicators.SMA_20.toFixed(2)}
          </div>
        </div>

        <div style={{ background: 'rgba(255,255,255,0.05)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
          <span className="card-title" style={{ fontSize: '0.75rem' }}>SMA (50)</span>
          <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: indicators.SMA_20 > indicators.SMA_50 ? 'var(--success-color)' : 'var(--error-color)' }}>
            {indicators.SMA_50.toFixed(2)}
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
            Trend: {indicators.SMA_20 > indicators.SMA_50 ? 'Uptrend' : 'Downtrend'}
          </span>
        </div>

      </div>
    </div>
  );
};

export default AnalysisPanel;
