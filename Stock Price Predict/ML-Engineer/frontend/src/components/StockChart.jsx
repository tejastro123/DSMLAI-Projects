import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const dataPoint = payload[0].payload;
    const value = payload[0].value;
    const isForecast = dataPoint.type === 'forecast';

    return (
      <div style={{ background: 'var(--surface-color)', padding: '1rem', border: 'var(--glass-border)', borderRadius: '8px' }}>
        <p style={{ margin: 0, fontWeight: 'bold' }}>{label}</p>
        <p style={{ margin: 0, color: isForecast ? 'var(--accent-color)' : 'var(--primary-color)' }}>
          Price: ${typeof value === 'number' ? value.toFixed(2) : value}
        </p>
        {isForecast && (
          <p style={{ margin: 0, color: 'var(--accent-color)', fontSize: '0.8rem' }}>AI Forecast</p>
        )}
      </div>
    );
  }
  return null;
};


const StockChart = ({ data, prediction }) => {
  if (!data || data.length === 0) return null;

  const chartData = [];

  // History
  data.forEach(item => {
    chartData.push({
      date: item.date,
      HistoryPrice: item.Close,
      ForecastPrice: null
    });
  });

  // Connect History and Forecast
  // The last point of history should also be the first point of forecast for visual continuity
  if (prediction && Array.isArray(prediction) && prediction.length > 0) {
    const lastHistory = data[data.length - 1];

    // Update the last history entry to ALSO be the start of forecast (graphically)
    // chartData[chartData.length - 1].ForecastPrice = lastHistory.Close; 
    // Actually, Recharts works best if we just have overlapping points or separate lines.

    let lastDate = new Date(lastHistory.date);

    // We explicitly add a "connector" point which is the last history data but for ForecastPrice
    // We don't want to double plot the date on XAxis if it exists?
    // Actually, standard way: 
    // Point N: Date=T, Hist=100, Fore=null
    // Point N: Date=T, Hist=null, Fore=100 (Connects?) -> No, different X.
    // Point N: Date=T, Hist=100, Fore=100 -> This works.

    chartData[chartData.length - 1].ForecastPrice = lastHistory.Close;

    prediction.forEach(p => {
      const nextDate = new Date(lastDate);
      nextDate.setDate(lastDate.getDate() + 1);

      chartData.push({
        date: nextDate.toISOString().split('T')[0],
        HistoryPrice: null,
        ForecastPrice: p.price
      });
      lastDate = nextDate;
    });
  }

  return (
    <div className="glass-panel" style={{ height: '400px', width: '100%', marginTop: '2rem' }}>
      <h3 style={{ marginBottom: '1rem', color: 'var(--text-primary)' }}>Price History & Forecast</h3>
      <ResponsiveContainer width="100%" height="90%">
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="colorHistory" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="var(--primary-color)" stopOpacity={0.8} />
              <stop offset="95%" stopColor="var(--primary-color)" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorForecast" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="var(--accent-color)" stopOpacity={0.8} />
              <stop offset="95%" stopColor="var(--accent-color)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis dataKey="date" stroke="var(--text-secondary)" fontSize={12} tickMargin={10} />
          <YAxis stroke="var(--text-secondary)" fontSize={12} domain={['auto', 'auto']} />
          <Tooltip content={<CustomTooltip />} />

          <Area
            type="monotone"
            dataKey="HistoryPrice"
            name="History"
            stroke="var(--primary-color)"
            fill="url(#colorHistory)"
            strokeWidth={2}
          />
          <Area
            type="monotone"
            dataKey="ForecastPrice"
            name="Forecast"
            stroke="var(--accent-color)"
            fill="url(#colorForecast)"
            strokeWidth={2}
            strokeDasharray="5 5"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default StockChart;
