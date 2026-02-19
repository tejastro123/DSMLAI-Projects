const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const dotenv = require('dotenv');
const { spawn } = require('child_process');
const path = require('path');
const PredictionLog = require('./models/PredictionLog');

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// MongoDB Connection
mongoose.connect(process.env.MONGO_URI || 'mongodb://localhost:27017/stock_predictor')
  .then(() => console.log('MongoDB Connected'))
  .catch(err => console.error('MongoDB Connection Error:', err));

// Routes
app.post('/api/predict', async (req, res) => {
  const { ticker, days } = req.body;
  const daysToPredict = days || 7; // Default to 7 days if not specified

  if (!ticker) {
    return res.status(400).json({ error: 'Ticker is required' });
  }

  // Spawn Python Process
  const pythonScriptPath = path.join(__dirname, 'python', 'predict_worker.py');

  // Use local venv python for stability
  const pythonExecutable = path.join(__dirname, 'venv', 'Scripts', 'python.exe');
  const pythonProcess = spawn(pythonExecutable, [pythonScriptPath, ticker, daysToPredict.toString()]);

  let dataString = '';
  let errorString = '';

  pythonProcess.stdout.on('data', (data) => {
    dataString += data.toString();
  });

  pythonProcess.stderr.on('data', (data) => {
    errorString += data.toString();
  });

  pythonProcess.on('error', (err) => {
    console.error('Failed to start python process:', err);
    res.status(500).json({ error: 'Failed to execute prediction script', details: err.message });
  });

  pythonProcess.on('close', async (code) => {
    if (code !== 0) {
      console.error(`Python script exited with code ${code}`);
      console.error(`Error output: ${errorString}`);
      console.error(`Standard output: ${dataString}`); // Log stdout as it may contain the JSON error
      return res.status(500).json({ error: 'Prediction failed', details: errorString || dataString });
    }

    try {
      const result = JSON.parse(dataString);

      if (result.error) {
        return res.status(400).json({ error: result.error });
      }

      // Log to Database (Store the first prediction or last, depending on preference. Here we store the first day)
      const newLog = new PredictionLog({
        ticker: result.ticker,
        predictedPrice: result.forecast[0].price
      });
      await newLog.save();

      res.json(result);
    } catch (err) {
      console.error('Error parsing JSON from python script:', err);
      res.status(500).json({ error: 'Internal Server Error', details: 'Invalid response from predictor' });
    }
  });
});

app.get('/api/history', async (req, res) => {
  try {
    const history = await PredictionLog.find().sort({ timestamp: -1 }).limit(10);
    res.json(history);
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch history' });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
