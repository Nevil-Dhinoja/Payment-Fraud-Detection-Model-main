// Transaction Provider
// Author: Manan Monani

import 'package:flutter/material.dart';
import '../models/transaction.dart';
import '../services/api_service.dart';
import '../services/storage_service.dart';

class TransactionProvider with ChangeNotifier {
  List<TransactionHistory> _history = [];
  PredictionResult? _lastResult;
  bool _isLoading = false;
  bool _isApiHealthy = false;
  String? _error;
  Map<String, dynamic>? _modelInfo;
  double _threshold = 0.5;

  List<TransactionHistory> get history => _history;
  PredictionResult? get lastResult => _lastResult;
  bool get isLoading => _isLoading;
  bool get isApiHealthy => _isApiHealthy;
  String? get error => _error;
  Map<String, dynamic>? get modelInfo => _modelInfo;
  double get threshold => _threshold;

  TransactionProvider() {
    _loadHistory();
    checkApiHealth();
  }

  Future<void> _loadHistory() async {
    try {
      _history = await StorageService.getHistory();
      notifyListeners();
    } catch (e) {
      _error = 'Failed to load history';
      notifyListeners();
    }
  }

  Future<void> checkApiHealth() async {
    try {
      final result = await ApiService.checkHealth();
      _isApiHealthy = result['success'] == true;

      if (_isApiHealthy) {
        await loadModelInfo();
        await loadThreshold();
      }
    } catch (e) {
      _isApiHealthy = false;
    }
    notifyListeners();
  }

  Future<void> loadModelInfo() async {
    try {
      final result = await ApiService.getModelInfo();
      if (result['success'] == true) {
        _modelInfo = result['data'];
      }
      notifyListeners();
    } catch (e) {
      // Silently fail
    }
  }

  Future<void> loadThreshold() async {
    try {
      final result = await ApiService.getThreshold();
      if (result['success'] == true && result['data'] != null) {
        _threshold = (result['data']['threshold'] as num?)?.toDouble() ?? 0.5;
      }
      notifyListeners();
    } catch (e) {
      // Silently fail
    }
  }

  Future<void> setThreshold(double value) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final result = await ApiService.setThreshold(value);
      if (result['success'] == true) {
        _threshold = value;
      } else {
        _error = result['error'] ?? 'Failed to set threshold';
      }
    } catch (e) {
      _error = 'Failed to set threshold: $e';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<PredictionResult?> predict(Transaction transaction) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final result = await ApiService.predict(transaction);

      if (result['success'] == true && result['prediction'] != null) {
        final predictionResult = result['prediction'] as PredictionResult;
        _lastResult = predictionResult;

        // Add to history
        final historyEntry = TransactionHistory(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          transaction: transaction,
          result: predictionResult,
          timestamp: DateTime.now(),
        );

        _history.insert(0, historyEntry);
        await StorageService.addToHistory(historyEntry);

        _isLoading = false;
        notifyListeners();
        return predictionResult;
      } else {
        _error = result['error'] ?? 'Prediction failed';
        _isLoading = false;
        notifyListeners();
        return null;
      }
    } catch (e) {
      _error = 'Prediction failed: $e';
      _isLoading = false;
      notifyListeners();
      return null;
    }
  }

  Future<List<PredictionResult>?> predictBatch(
    List<Transaction> transactions,
  ) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final result = await ApiService.predictBatch(transactions);

      if (result['success'] == true && result['data'] != null) {
        final predictions = (result['data']['predictions'] as List)
            .map((p) => PredictionResult.fromJson(p))
            .toList();

        // Add all to history
        for (
          int i = 0;
          i < transactions.length && i < predictions.length;
          i++
        ) {
          final historyEntry = TransactionHistory(
            id: '${DateTime.now().millisecondsSinceEpoch}_$i',
            transaction: transactions[i],
            result: predictions[i],
            timestamp: DateTime.now(),
          );
          _history.insert(0, historyEntry);
          await StorageService.addToHistory(historyEntry);
        }

        _isLoading = false;
        notifyListeners();
        return predictions;
      } else {
        _error = result['error'] ?? 'Batch prediction failed';
        _isLoading = false;
        notifyListeners();
        return null;
      }
    } catch (e) {
      _error = 'Batch prediction failed: $e';
      _isLoading = false;
      notifyListeners();
      return null;
    }
  }

  Future<void> clearHistory() async {
    _history.clear();
    await StorageService.clearHistory();
    notifyListeners();
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }

  void clearLastResult() {
    _lastResult = null;
    notifyListeners();
  }

  // Stats
  int get totalPredictions => _history.length;

  int get fraudCount => _history.where((h) => h.result.isFraud).length;

  int get legitCount => _history.where((h) => !h.result.isFraud).length;

  double get fraudPercentage =>
      totalPredictions > 0 ? (fraudCount / totalPredictions) * 100 : 0;

  List<TransactionHistory> get recentHistory => _history.take(10).toList();

  List<TransactionHistory> getHistoryByDate(DateTime date) {
    return _history
        .where(
          (h) =>
              h.timestamp.year == date.year &&
              h.timestamp.month == date.month &&
              h.timestamp.day == date.day,
        )
        .toList();
  }
}
