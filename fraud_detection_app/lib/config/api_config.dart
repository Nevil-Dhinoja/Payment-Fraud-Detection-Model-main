/// API Configuration for Fraud Detection App
/// Author: Manan Monani

class ApiConfig {
  // Base URL for the ML API
  // Change this to your server IP when testing on physical device
  // Use 10.0.2.2 for Android emulator, localhost for iOS simulator
  static const String baseUrl = 'http://10.0.2.2:5000';

  // Alternative URLs for different environments
  static const String localUrl = 'http://localhost:5000';
  static const String emulatorUrl = 'http://10.0.2.2:5000';

  // API Endpoints
  static const String healthEndpoint = '/health';
  static const String predictEndpoint = '/predict';
  static const String batchPredictEndpoint = '/predict/batch';
  static const String modelInfoEndpoint = '/model/info';
  static const String thresholdEndpoint = '/threshold';

  // Timeouts
  static const Duration connectionTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);

  // Backend Server URL (Node.js)
  static const String backendUrl = 'http://10.0.2.2:5001';
  static const String loginEndpoint = '/api/auth/login';
  static const String registerEndpoint = '/api/auth/register';
  static const String transactionsEndpoint = '/api/transactions';
}
