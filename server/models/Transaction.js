const mongoose = require('mongoose');

const transactionSchema = new mongoose.Schema({
    userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    amount: { type: Number, required: true },
    timestamp: { type: Date, default: Date.now },
    status: { type: String, default: 'sucessful' },
    deviceLocation: { type: { latitude: Number, longitude: Number }, required: true },
    deviceId: { type: String, required: true }
});

module.exports = mongoose.model('Transaction', transactionSchema);