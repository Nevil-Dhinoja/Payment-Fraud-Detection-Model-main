import React, { useEffect, useState } from 'react';
import { fetchTransactions } from '../api/transactionApi';
import { useAuth } from '../context/AuthContext';
import { 
  History, 
  CheckCircle, 
  XCircle, 
  Clock, 
  DollarSign,
  RefreshCcw,
  AlertTriangle
} from 'lucide-react';

const TransactionList = ({ refreshKey }) => {
  const { getToken } = useAuth();
  const [transactions, setTransactions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const loadTransactions = async () => {
    setIsLoading(true);
    setError('');
    try {
      const token = getToken();
      const data = await fetchTransactions(token);
      setTransactions(data);
    } catch (err) {
      setError('Failed to load transactions');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadTransactions();
  }, [refreshKey]);

  const getStatusIcon = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed':
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'failed':
      case 'fraud':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      default:
        return <Clock className="w-5 h-5 text-dark-400" />;
    }
  };

  const getStatusBadge = (status) => {
    const statusLower = status?.toLowerCase();
    const baseClasses = "px-3 py-1 rounded-full text-xs font-medium";
    
    switch (statusLower) {
      case 'completed':
      case 'success':
        return `${baseClasses} bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400`;
      case 'failed':
      case 'fraud':
        return `${baseClasses} bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400`;
      case 'pending':
        return `${baseClasses} bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400`;
      default:
        return `${baseClasses} bg-dark-100 dark:bg-dark-700 text-dark-600 dark:text-dark-400`;
    }
  };

  return (
    <div className="card p-6 lg:p-8">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-gradient-to-br from-accent-500 to-accent-600 rounded-xl flex items-center justify-center shadow-lg shadow-accent-500/25">
            <History className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-dark-900 dark:text-white">
              Transaction History
            </h2>
            <p className="text-sm text-dark-500 dark:text-dark-400">
              {transactions.length} transaction{transactions.length !== 1 ? 's' : ''} found
            </p>
          </div>
        </div>
        
        <button
          onClick={loadTransactions}
          className="p-2.5 rounded-xl bg-dark-100 dark:bg-dark-700 text-dark-600 dark:text-dark-300 hover:bg-primary-100 dark:hover:bg-primary-900/30 hover:text-primary-600 dark:hover:text-primary-400 transition-all duration-300"
          aria-label="Refresh transactions"
        >
          <RefreshCcw className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-red-500" />
          <p className="text-red-700 dark:text-red-400 text-sm">{error}</p>
        </div>
      )}

      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="flex items-center justify-between p-4 bg-dark-50 dark:bg-dark-700/50 rounded-xl">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 bg-dark-200 dark:bg-dark-600 rounded-full" />
                  <div className="space-y-2">
                    <div className="h-4 w-24 bg-dark-200 dark:bg-dark-600 rounded" />
                    <div className="h-3 w-32 bg-dark-200 dark:bg-dark-600 rounded" />
                  </div>
                </div>
                <div className="h-6 w-20 bg-dark-200 dark:bg-dark-600 rounded-full" />
              </div>
            </div>
          ))}
        </div>
      ) : transactions.length === 0 ? (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-dark-100 dark:bg-dark-700 rounded-full flex items-center justify-center mx-auto mb-4">
            <DollarSign className="w-8 h-8 text-dark-400" />
          </div>
          <h3 className="text-lg font-semibold text-dark-700 dark:text-dark-300 mb-2">
            No Transactions Yet
          </h3>
          <p className="text-dark-500 dark:text-dark-400">
            Your transaction history will appear here once you make your first transaction.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {transactions.map((txn) => (
            <div
              key={txn._id}
              className="flex items-center justify-between p-4 bg-dark-50 dark:bg-dark-700/50 rounded-xl hover:bg-dark-100 dark:hover:bg-dark-700 transition-colors duration-200"
            >
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 bg-gradient-to-br from-primary-500/20 to-primary-600/20 rounded-full flex items-center justify-center">
                  {getStatusIcon(txn.status)}
                </div>
                <div>
                  <p className="font-semibold text-dark-900 dark:text-white flex items-center gap-2">
                    <DollarSign className="w-4 h-4" />
                    {txn.amount?.toLocaleString() || '0.00'}
                  </p>
                  <p className="text-sm text-dark-500 dark:text-dark-400">
                    {txn.timestamp ? new Date(txn.timestamp).toLocaleString() : 'Unknown date'}
                  </p>
                </div>
              </div>
              <span className={getStatusBadge(txn.status)}>
                {txn.status || 'Unknown'}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TransactionList;
