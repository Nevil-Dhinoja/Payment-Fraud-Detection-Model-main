/// API Service for Fraud Detection
/// Author: Manan Monani

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import '../models/transaction.dart';

class ApiService {
  static String _baseUrl = ApiConfig.baseUrl;

  static void setBaseUrl(String url) {
    _baseUrl = url;
  }

  static String get baseUrl => _baseUrl;

  /// Check API health status
  static Future<Map<String, dynamic>> checkHealth() async {
    try {
      final response = await http
          .get(Uri.parse('$_baseUrl${ApiConfig.healthEndpoint}'))
          .timeout(ApiConfig.connectionTimeout);

      if (response.statusCode == 200) {
        return {'success': true, 'data': json.decode(response.body)};
      } else {
        return {
          'success': false,
          'error': 'Server returned status ${response.statusCode}',
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Connection failed: ${e.toString()}'};
    }
  }

  /// Get model information
  static Future<Map<String, dynamic>> getModelInfo() async {
    try {
      final response = await http
          .get(Uri.parse('$_baseUrl${ApiConfig.modelInfoEndpoint}'))
          .timeout(ApiConfig.connectionTimeout);

      if (response.statusCode == 200) {
        return {'success': true, 'data': json.decode(response.body)};
      } else {
        return {'success': false, 'error': 'Failed to get model info'};
      }
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }

  /// Make a single prediction
  static Future<Map<String, dynamic>> predict(Transaction transaction) async {
    try {
      final response = await http
          .post(
            Uri.parse('$_baseUrl${ApiConfig.predictEndpoint}'),
            headers: {'Content-Type': 'application/json'},
            body: json.encode(transaction.toJson()),
          )
          .timeout(ApiConfig.connectionTimeout);

      final responseData = json.decode(response.body);

      if (response.statusCode == 200 && responseData['success'] == true) {
        return {
          'success': true,
          'prediction': PredictionResult.fromJson(responseData['prediction']),
        };
      } else {
        return {
          'success': false,
          'error': responseData['error'] ?? 'Prediction failed',
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Connection error: ${e.toString()}'};
    }
  }

  /// Make batch predictions
  static Future<Map<String, dynamic>> predictBatch(
    List<Transaction> transactions,
  ) async {
    try {
      final response = await http
          .post(
            Uri.parse('$_baseUrl${ApiConfig.batchPredictEndpoint}'),
            headers: {'Content-Type': 'application/json'},
            body: json.encode({
              'transactions': transactions.map((t) => t.toJson()).toList(),
            }),
          )
          .timeout(ApiConfig.connectionTimeout);

      final responseData = json.decode(response.body);

      if (response.statusCode == 200 && responseData['success'] == true) {
        return {'success': true, 'data': responseData};
      } else {
        return {
          'success': false,
          'error': responseData['error'] ?? 'Batch prediction failed',
        };
      }
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }

  /// Get current threshold
  static Future<Map<String, dynamic>> getThreshold() async {
    try {
      final response = await http
          .get(Uri.parse('$_baseUrl${ApiConfig.thresholdEndpoint}'))
          .timeout(ApiConfig.connectionTimeout);

      if (response.statusCode == 200) {
        return {'success': true, 'data': json.decode(response.body)};
      } else {
        return {'success': false, 'error': 'Failed to get threshold'};
      }
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }

  /// Set threshold
  static Future<Map<String, dynamic>> setThreshold(double threshold) async {
    try {
      final response = await http
          .post(
            Uri.parse('$_baseUrl${ApiConfig.thresholdEndpoint}'),
            headers: {'Content-Type': 'application/json'},
            body: json.encode({'threshold': threshold}),
          )
          .timeout(ApiConfig.connectionTimeout);

      final responseData = json.decode(response.body);

      if (response.statusCode == 200) {
        return {'success': true, 'data': responseData};
      } else {
        return {
          'success': false,
          'error': responseData['error'] ?? 'Failed to set threshold',
        };
      }
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }
}
