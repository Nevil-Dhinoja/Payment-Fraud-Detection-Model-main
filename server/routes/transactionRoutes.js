const express = require('express');
const { logTransaction, getTransactions,createTransaction } = require('../controllers/transactionController');
const authenticateToken = require('../middlewares/authMiddleware');
const router = express.Router();

// Route to log a new transaction
router.post('/', authenticateToken, logTransaction);

// Route to fetch all transactions for the authenticated user
router.get('/', authenticateToken, getTransactions);

// Route to create a transaction
router.post('/create', authenticateToken, createTransaction);


module.exports = router;
