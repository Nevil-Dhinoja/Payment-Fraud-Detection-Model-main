const Transaction = require('../models/Transaction');

// Log a new transaction
exports.logTransaction = async (req, res) => {
    try {
        const { amount, deviceLocation, deviceId } = req.body;

        // Create a new transaction
        const transaction = new Transaction({
            userId: req.user._id, // userId from token
            amount,
            deviceLocation,
            deviceId,
        });

        const savedTransaction = await transaction.save();
        res.status(201).json({
            message: 'Transaction logged successfully',
            transaction: savedTransaction,
        });
    } catch (error) {
        res.status(400).json({
            message: 'Error logging transaction',
            error: error.message,
        });
    }
};

// Fetch all transactions for the authenticated user
exports.getTransactions = async (req, res) => {
    try {
        const transactions = await Transaction.find({ userId: req.user._id });
        res.status(200).json(transactions);
    } catch (error) {
        res.status(500).json({
            message: 'Error fetching transactions',
            error: error.message,
        });
    }
};



// Create a transaction
exports.createTransaction = async (req, res) => {
    try {
        const { amount, deviceLocation, deviceId } = req.body;

        // Validate input
        if (!amount || !deviceLocation || !deviceLocation.latitude || !deviceLocation.longitude || !deviceId) {
            return res.status(400).json({ message: 'All fields are required' });
        }
        
        const isTransactionSuccessful = true; // Simulating a successful transaction, replace this with actual logic

        // Create a new transaction
        const transaction = new Transaction({
            userId: req.user._id, // Extracted from the token
            amount,
            deviceLocation,
            deviceId,
            status: isTransactionSuccessful ? 'successful' : 'failed', // Set status based on transaction outcome
        });

        const savedTransaction = await transaction.save();

        res.status(201).json({
            message: 'Transaction created successfully',
            transaction: savedTransaction,
        });
    } catch (error) {
        res.status(500).json({
            message: 'Error creating transaction',
            error: error.message,
        });
    }
};
