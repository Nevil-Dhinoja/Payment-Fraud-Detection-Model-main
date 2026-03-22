import React, { useState } from 'react';
import TransactionForm from '../components/TransactionForm';
import TransactionList from '../components/TransactionList';

const TransactionPage = () => {
    const [refresh, setRefresh] = useState(false);
    const token = sessionStorage.getItem('token'); // Assuming authentication token is stored

    const refreshTransactions = () => setRefresh(!refresh);

    return (
        <div>
            <h1>Transaction Page</h1>
            <TransactionForm onTransactionSuccess={refreshTransactions} token={token} />
            <TransactionList token={token} key={refresh} />
        </div>
    );
};

export default TransactionPage;
