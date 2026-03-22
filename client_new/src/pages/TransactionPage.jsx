import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import TransactionForm from '../components/TransactionForm';
import TransactionList from '../components/TransactionList';
import { 
  Shield, 
  CreditCard, 
  TrendingUp, 
  AlertTriangle,
  CheckCircle
} from 'lucide-react';

const TransactionPage = () => {
  const { isLoggedIn } = useAuth();
  const [refreshKey, setRefreshKey] = useState(0);

  // Redirect to login if not authenticated
  if (!isLoggedIn) {
    return <Navigate to="/login" replace />;
  }

  const refreshTransactions = () => setRefreshKey(prev => prev + 1);

  const stats = [
    {
      icon: CreditCard,
      label: 'Total Transactions',
      value: '---',
      color: 'from-blue-500 to-cyan-600'
    },
    {
      icon: CheckCircle,
      label: 'Successful',
      value: '---',
      color: 'from-green-500 to-emerald-600'
    },
    {
      icon: AlertTriangle,
      label: 'Flagged',
      value: '---',
      color: 'from-red-500 to-rose-600'
    },
    {
      icon: TrendingUp,
      label: 'Success Rate',
      value: '---',
      color: 'from-purple-500 to-violet-600'
    }
  ];

  return (
    <div className="min-h-screen bg-dark-50 dark:bg-dark-950 pt-24 pb-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-14 h-14 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl flex items-center justify-center shadow-lg shadow-primary-500/25">
              <Shield className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold font-display text-dark-900 dark:text-white">
                Transaction Dashboard
              </h1>
              <p className="text-dark-500 dark:text-dark-400">
                Monitor and manage your secure transactions
              </p>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {stats.map((stat, index) => (
            <div key={index} className="card p-5">
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 bg-gradient-to-br ${stat.color} rounded-xl flex items-center justify-center`}>
                  <stat.icon className="w-5 h-5 text-white" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-dark-900 dark:text-white">
                    {stat.value}
                  </p>
                  <p className="text-xs text-dark-500 dark:text-dark-400">
                    {stat.label}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Main Content */}
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Transaction Form */}
          <div>
            <TransactionForm onTransactionSuccess={refreshTransactions} />
          </div>

          {/* Transaction List */}
          <div>
            <TransactionList refreshKey={refreshKey} />
          </div>
        </div>

        {/* Security Info */}
        <div className="mt-8 p-6 bg-gradient-to-r from-primary-500/10 to-accent-500/10 dark:from-primary-900/20 dark:to-accent-900/20 rounded-2xl border border-primary-200 dark:border-primary-800">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-primary-500 rounded-xl flex items-center justify-center flex-shrink-0">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-dark-900 dark:text-white mb-1">
                AI-Powered Protection Active
              </h3>
              <p className="text-dark-600 dark:text-dark-400 text-sm">
                Every transaction is analyzed by our advanced machine learning model to detect and prevent fraud. 
                Your transactions are monitored in real-time with 99.9% accuracy.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TransactionPage;
