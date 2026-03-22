/// Auth Provider
/// Author: Manan Monani

import 'package:flutter/material.dart';
import '../models/user.dart';
import '../services/storage_service.dart';

class AuthProvider with ChangeNotifier {
  User? _user;
  bool _isLoading = false;
  bool _isInitialized = false;
  String? _error;

  User? get user => _user;
  bool get isLoading => _isLoading;
  bool get isInitialized => _isInitialized;
  bool get isAuthenticated => _user != null;
  String? get error => _error;

  AuthProvider() {
    _loadUser();
  }

  Future<void> _loadUser() async {
    _isLoading = true;
    notifyListeners();

    try {
      _user = await StorageService.getUser();
    } catch (e) {
      _error = 'Failed to load user data';
    } finally {
      _isLoading = false;
      _isInitialized = true;
      notifyListeners();
    }
  }

  Future<bool> login(String email, String password) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      // For demo purposes, we'll create a local user
      // In production, this would call your backend API
      await Future.delayed(const Duration(seconds: 1));

      if (email.isEmpty || password.isEmpty) {
        throw Exception('Email and password are required');
      }

      // Simulate successful login
      _user = User(
        id: 'local_user_${DateTime.now().millisecondsSinceEpoch}',
        name: email.split('@').first,
        email: email,
        token: 'demo_token_${DateTime.now().millisecondsSinceEpoch}',
      );

      await StorageService.setUser(_user!);
      await StorageService.setToken(_user!.token!);

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> register(String name, String email, String password) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      await Future.delayed(const Duration(seconds: 1));

      if (name.isEmpty || email.isEmpty || password.isEmpty) {
        throw Exception('All fields are required');
      }

      if (password.length < 6) {
        throw Exception('Password must be at least 6 characters');
      }

      // Simulate successful registration
      _user = User(
        id: 'local_user_${DateTime.now().millisecondsSinceEpoch}',
        name: name,
        email: email,
        token: 'demo_token_${DateTime.now().millisecondsSinceEpoch}',
      );

      await StorageService.setUser(_user!);
      await StorageService.setToken(_user!.token!);

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<void> logout() async {
    _isLoading = true;
    notifyListeners();

    await StorageService.clearUser();
    _user = null;

    _isLoading = false;
    notifyListeners();
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}
