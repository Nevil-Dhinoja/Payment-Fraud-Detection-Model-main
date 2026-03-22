import React, { useEffect, useState } from 'react';
import { fetchTransactions } from '../api/transactionApi';

const TransactionList = ({ token }) => {
    const [transactions, setTransactions] = useState([]);

    useEffect(() => {
        const loadTransactions = async () => {
            const data = await fetchTransactions(token);
            setTransactions(data);
        };
        loadTransactions();
    }, [token]);

    return (
        <div className="transaction-list">
            <h2>Transaction History</h2>
            {transactions.length === 0 ? (
                <p>No transactions found.</p>
            ) : (
                <ul>
                    {transactions.map((txn) => (
                        <li key={txn._id}>
                            <p>Amount: ${txn.amount}</p>
                            <p>Status: {txn.status}</p>
                            <p>Date: {new Date(txn.timestamp).toLocaleString()}</p>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default TransactionList;
