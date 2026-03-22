/// Local Storage Service
/// Author: Manan Monani

import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/transaction.dart';
import '../models/user.dart';

class StorageService {
  static const String _themeKey = 'theme_mode';
  static const String _userKey = 'user_data';
  static const String _tokenKey = 'auth_token';
  static const String _historyKey = 'transaction_history';
  static const String _apiUrlKey = 'api_url';

  // Theme
  static Future<String> getThemeMode() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_themeKey) ?? 'system';
  }

  static Future<void> setThemeMode(String mode) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_themeKey, mode);
  }

  // User & Auth
  static Future<User?> getUser() async {
    final prefs = await SharedPreferences.getInstance();
    final userData = prefs.getString(_userKey);
    if (userData != null) {
      return User.fromJson(json.decode(userData));
    }
    return null;
  }

  static Future<void> setUser(User user) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_userKey, json.encode(user.toJson()));
  }

  static Future<void> clearUser() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_userKey);
    await prefs.remove(_tokenKey);
  }

  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }

  static Future<void> setToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
  }

  // Transaction History
  static Future<List<TransactionHistory>> getHistory() async {
    final prefs = await SharedPreferences.getInstance();
    final historyData = prefs.getString(_historyKey);
    if (historyData != null) {
      final List<dynamic> historyList = json.decode(historyData);
      return historyList.map((e) => TransactionHistory.fromJson(e)).toList();
    }
    return [];
  }

  static Future<void> addToHistory(TransactionHistory history) async {
    final prefs = await SharedPreferences.getInstance();
    final currentHistory = await getHistory();
    currentHistory.insert(0, history);

    // Keep only last 100 transactions
    if (currentHistory.length > 100) {
      currentHistory.removeLast();
    }

    await prefs.setString(
      _historyKey,
      json.encode(currentHistory.map((e) => e.toJson()).toList()),
    );
  }

  static Future<void> clearHistory() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_historyKey);
  }

  // API URL
  static Future<String?> getApiUrl() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_apiUrlKey);
  }

  static Future<void> setApiUrl(String url) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_apiUrlKey, url);
  }

  // Clear all data
  static Future<void> clearAll() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }
}
