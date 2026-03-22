import axios from 'axios';

const API_URL = 'http://localhost:7000/api/transactions';

// Get all transactions for the user
export const fetchTransactions = async (token) => {
    try {
        const response = await axios.get(API_URL, {
            headers: { Authorization: `Bearer ${token}` },
        });
        return response.data;
    } catch (error) {
        console.error('Error fetching transactions:', error);
        return [];
    }
};

// Create a new transaction
export const createTransaction = async (data, token) => {
    try {
        const response = await axios.post(API_URL, data, {
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`,
            },
        });
        return response.data;
    } catch (error) {
        console.error('Error creating transaction:', error);
        throw error;
    }
};
