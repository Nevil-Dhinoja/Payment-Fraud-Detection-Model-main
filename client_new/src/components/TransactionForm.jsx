import React, { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { createTransaction } from '../api/transactionApi';
import { useAuth } from '../context/AuthContext';
import { 
  Send, 
  DollarSign, 
  MapPin, 
  Smartphone, 
  AlertCircle,
  CheckCircle,
  Loader2
} from 'lucide-react';

const TransactionForm = ({ onTransactionSuccess }) => {
  const { getToken } = useAuth();
  const [amount, setAmount] = useState('');
  const [deviceId, setDeviceId] = useState('');
  const [location, setLocation] = useState({ latitude: '', longitude: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [userId, setUserId] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Automatically generate or fetch user ID
  useEffect(() => {
    let storedUserId = localStorage.getItem('user_id');
    if (!storedUserId) {
      storedUserId = uuidv4();
      localStorage.setItem('user_id', storedUserId);
    }
    setUserId(storedUserId);
  }, []);

  // Automatically generate or fetch device ID
  useEffect(() => {
    let storedDeviceId = localStorage.getItem('device_id');
    if (!storedDeviceId) {
      storedDeviceId = uuidv4();
      localStorage.setItem('device_id', storedDeviceId);
    }
    setDeviceId(storedDeviceId);
  }, []);

  // Automatically fetch device location when component mounts
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setLocation({
            latitude: pos.coords.latitude,
            longitude: pos.coords.longitude,
          });
        },
        (err) => {
          console.error('Error getting location:', err);
          setError('Location access is required for transactions. Please enable location services.');
        }
      );
    } else {
      setError('Geolocation is not supported by your browser.');
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setIsLoading(true);

    if (!amount || !deviceId || !location.latitude || !location.longitude || !userId) {
      setError('All fields are required, including location and user ID.');
      setIsLoading(false);
      return;
    }

    const transactionData = {
      userID: userId,
      amount: Number(amount),
      location: `${location.longitude}`,
      deviceID: deviceId,
      time: Math.floor(Date.now() / 1000),
    };

    try {
      // Step 1: Send data to ML model API
      const mlResponse = await fetch('http://127.0.0.1:5000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(transactionData),
      });

      if (!mlResponse.ok) {
        const errorText = await mlResponse.text();
        setError(`Transaction failed: ${errorText}`);
        setIsLoading(false);
        return;
      }

      const mlResult = await mlResponse.json();

      if (mlResult.isFraud) {
        setError('⚠️ Transaction flagged as potentially fraudulent. Please verify and try again.');
        setIsLoading(false);
        return;
      }

      // Step 2: If genuine, proceed with transaction creation
      const token = getToken();
      await createTransaction(
        { amount, deviceLocation: location, deviceId },
        token
      );
      
      setSuccess('✅ Transaction completed successfully!');
      setAmount('');
      onTransactionSuccess();
    } catch (err) {
      console.error('Error:', err);
      setError('Transaction failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="card p-6 lg:p-8">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center shadow-lg shadow-primary-500/25">
          <Send className="w-6 h-6 text-white" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-dark-900 dark:text-white">
            Make a Transaction
          </h2>
          <p className="text-sm text-dark-500 dark:text-dark-400">
            AI-powered fraud detection enabled
          </p>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <p className="text-red-700 dark:text-red-400 text-sm">{error}</p>
        </div>
      )}

      {success && (
        <div className="mb-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl flex items-start gap-3">
          <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
          <p className="text-green-700 dark:text-green-400 text-sm">{success}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Amount Input */}
        <div>
          <label className="block text-sm font-medium text-dark-700 dark:text-dark-300 mb-2">
            Amount
          </label>
          <div className="relative">
            <DollarSign className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-400" />
            <input
              type="number"
              placeholder="Enter amount"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="input-primary pl-12"
              required
            />
          </div>
        </div>

        {/* Device ID Display */}
        <div>
          <label className="block text-sm font-medium text-dark-700 dark:text-dark-300 mb-2">
            Device ID
          </label>
          <div className="relative">
            <Smartphone className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-400" />
            <input
              type="text"
              value={deviceId.substring(0, 8) + '...'}
              readOnly
              className="input-primary pl-12 bg-dark-50 dark:bg-dark-700 cursor-not-allowed"
            />
          </div>
          <p className="mt-1 text-xs text-dark-500">Auto-generated device identifier</p>
        </div>

        {/* Location Display */}
        <div>
          <label className="block text-sm font-medium text-dark-700 dark:text-dark-300 mb-2">
            Location
          </label>
          <div className="relative">
            <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-400" />
            <input
              type="text"
              value={location.latitude && location.longitude 
                ? `${location.latitude.toFixed(4)}, ${location.longitude.toFixed(4)}`
                : 'Fetching location...'
              }
              readOnly
              className="input-primary pl-12 bg-dark-50 dark:bg-dark-700 cursor-not-allowed"
            />
          </div>
          <p className="mt-1 text-xs text-dark-500">Auto-detected from your device</p>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading || !location.latitude}
          className="btn-primary w-full flex items-center justify-center gap-2"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Processing...
            </>
          ) : (
            <>
              <Send className="w-5 h-5" />
              Send Transaction
            </>
          )}
        </button>
      </form>

      <p className="mt-4 text-xs text-center text-dark-500 dark:text-dark-400">
        🛡️ Protected by AI-powered fraud detection system
      </p>
    </div>
  );
};

export default TransactionForm;
