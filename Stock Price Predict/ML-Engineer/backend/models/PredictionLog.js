const mongoose = require('mongoose');

const PredictionLogSchema = new mongoose.Schema({
  ticker: {
    type: String,
    required: true,
    trim: true,
    uppercase: true
  },
  predictedPrice: {
    type: Number,
    required: true
  },
  timestamp: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('PredictionLog', PredictionLogSchema);
