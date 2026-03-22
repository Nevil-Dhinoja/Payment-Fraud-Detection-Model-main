/// Transaction Screen
/// Author: Manan Monani

import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import '../models/transaction.dart';
import '../providers/transaction_provider.dart';

class TransactionScreen extends StatefulWidget {
  const TransactionScreen({super.key});

  @override
  State<TransactionScreen> createState() => _TransactionScreenState();
}

class _TransactionScreenState extends State<TransactionScreen> {
  final _formKey = GlobalKey<FormState>();
  final _amountController = TextEditingController();
  final _timeController = TextEditingController();

  final Map<String, TextEditingController> _vControllers = {};
  bool _showAdvanced = false;
  bool _useRandomValues = true;

  @override
  void initState() {
    super.initState();
    // Initialize V feature controllers
    for (int i = 1; i <= 28; i++) {
      _vControllers['V$i'] = TextEditingController(text: '0.0');
    }
    _generateRandomValues();
  }

  @override
  void dispose() {
    _amountController.dispose();
    _timeController.dispose();
    for (var controller in _vControllers.values) {
      controller.dispose();
    }
    super.dispose();
  }

  void _generateRandomValues() {
    final random = Random();

    // Generate realistic random values
    _amountController.text = (random.nextDouble() * 1000).toStringAsFixed(2);
    _timeController.text = (random.nextInt(
      172800,
    )).toString(); // 0-48 hours in seconds

    for (int i = 1; i <= 28; i++) {
      // V features are typically normalized, so generate values between -5 and 5
      double value = (random.nextDouble() * 10) - 5;
      _vControllers['V$i']!.text = value.toStringAsFixed(4);
    }

    setState(() {});
  }

  void _generateFraudPattern() {
    final random = Random();

    // High amount transaction
    _amountController.text = (5000 + random.nextDouble() * 10000)
        .toStringAsFixed(2);
    _timeController.text = (random.nextInt(86400) + 86400)
        .toString(); // Night hours

    // Generate suspicious patterns
    _vControllers['V1']!.text = (-3 - random.nextDouble() * 2).toStringAsFixed(
      4,
    );
    _vControllers['V2']!.text = (2 + random.nextDouble() * 3).toStringAsFixed(
      4,
    );
    _vControllers['V3']!.text = (-4 + random.nextDouble()).toStringAsFixed(4);
    _vControllers['V4']!.text = (3 + random.nextDouble() * 2).toStringAsFixed(
      4,
    );
    _vControllers['V5']!.text = (-2 - random.nextDouble()).toStringAsFixed(4);

    for (int i = 6; i <= 28; i++) {
      double value = (random.nextDouble() * 6) - 3;
      if (i % 3 == 0) value = value.abs() * -1.5;
      _vControllers['V$i']!.text = value.toStringAsFixed(4);
    }

    setState(() {});
  }

  void _generateLegitPattern() {
    final random = Random();

    // Normal amount
    _amountController.text = (10 + random.nextDouble() * 200).toStringAsFixed(
      2,
    );
    _timeController.text = (random.nextInt(43200) + 28800)
        .toString(); // Business hours

    // Generate normal patterns (values closer to 0)
    for (int i = 1; i <= 28; i++) {
      double value = (random.nextDouble() * 2) - 1;
      _vControllers['V$i']!.text = value.toStringAsFixed(4);
    }

    setState(() {});
  }

  Future<void> _submitPrediction() async {
    if (!_formKey.currentState!.validate()) return;

    final transactionProvider = context.read<TransactionProvider>();

    if (!transactionProvider.isApiHealthy) {
      _showErrorSnackbar('ML API is offline. Please check connection.');
      return;
    }

    Map<String, double> vFeatures = {};
    for (int i = 1; i <= 28; i++) {
      vFeatures['V$i'] = double.tryParse(_vControllers['V$i']!.text) ?? 0.0;
    }

    final transaction = Transaction(
      amount: double.parse(_amountController.text),
      time: double.parse(_timeController.text),
      vFeatures: vFeatures,
    );

    final result = await transactionProvider.predict(transaction);

    if (result != null && mounted) {
      _showResultDialog(result);
    } else if (transactionProvider.error != null) {
      _showErrorSnackbar(transactionProvider.error!);
    }
  }

  void _showResultDialog(PredictionResult result) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: (result.isFraud ? Colors.red : Colors.green).withValues(
                  alpha: 0.1,
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                result.isFraud ? Icons.warning : Icons.check_circle,
                color: result.isFraud ? Colors.red : Colors.green,
                size: 28,
              ),
            ),
            const SizedBox(width: 12),
            Text(result.isFraud ? 'Fraud Detected!' : 'Legitimate'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildResultRow('Prediction', result.label),
            _buildResultRow(
              'Probability',
              '${(result.probability * 100).toStringAsFixed(2)}%',
            ),
            _buildResultRow(
              'Confidence',
              '${(result.confidence * 100).toStringAsFixed(2)}%',
            ),
            _buildResultRow('Risk Level', result.riskLevel),
            const SizedBox(height: 16),
            LinearProgressIndicator(
              value: result.probability,
              backgroundColor: Colors.green.withValues(alpha: 0.2),
              valueColor: AlwaysStoppedAnimation<Color>(
                result.isFraud ? Colors.red : Colors.green,
              ),
              minHeight: 8,
              borderRadius: BorderRadius.circular(4),
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Legitimate',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.green.withValues(alpha: 0.8),
                  ),
                ),
                Text(
                  'Fraud',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.red.withValues(alpha: 0.8),
                  ),
                ),
              ],
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              _generateRandomValues();
            },
            child: const Text('New Prediction'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  Widget _buildResultRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TextStyle(
              color: Theme.of(
                context,
              ).colorScheme.onSurface.withValues(alpha: 0.7),
            ),
          ),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  void _showErrorSnackbar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final transactionProvider = context.watch<TransactionProvider>();
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Transaction Analysis'),
        actions: [
          IconButton(
            icon: const Icon(Icons.help_outline),
            onPressed: _showHelpDialog,
          ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // API Status
            if (!transactionProvider.isApiHealthy)
              Container(
                padding: const EdgeInsets.all(12),
                margin: const EdgeInsets.only(bottom: 16),
                decoration: BoxDecoration(
                  color: Colors.red.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.red.withValues(alpha: 0.3)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.cloud_off, color: Colors.red),
                    const SizedBox(width: 12),
                    const Expanded(
                      child: Text(
                        'ML API is offline. Please check connection.',
                        style: TextStyle(color: Colors.red),
                      ),
                    ),
                    TextButton(
                      onPressed: transactionProvider.checkApiHealth,
                      child: const Text('Retry'),
                    ),
                  ],
                ),
              ).animate().fadeIn().shake(),

            // Quick Actions
            Card(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Quick Generate',
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        _buildChip(
                          'Random',
                          Icons.shuffle,
                          Colors.blue,
                          _generateRandomValues,
                        ),
                        _buildChip(
                          'Fraud Pattern',
                          Icons.warning,
                          Colors.red,
                          _generateFraudPattern,
                        ),
                        _buildChip(
                          'Legit Pattern',
                          Icons.check,
                          Colors.green,
                          _generateLegitPattern,
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ).animate().fadeIn(duration: 300.ms),

            const SizedBox(height: 16),

            // Main Fields
            Card(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Transaction Details',
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _amountController,
                      keyboardType: const TextInputType.numberWithOptions(
                        decimal: true,
                      ),
                      inputFormatters: [
                        FilteringTextInputFormatter.allow(
                          RegExp(r'^\d+\.?\d*'),
                        ),
                      ],
                      decoration: InputDecoration(
                        labelText: 'Amount',
                        hintText: 'Transaction amount',
                        prefixIcon: const Icon(Icons.attach_money),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Amount is required';
                        }
                        if (double.tryParse(value) == null) {
                          return 'Invalid amount';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _timeController,
                      keyboardType: TextInputType.number,
                      inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                      decoration: InputDecoration(
                        labelText: 'Time (seconds)',
                        hintText: 'Seconds from reference',
                        prefixIcon: const Icon(Icons.access_time),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        helperText: 'Elapsed seconds from first transaction',
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Time is required';
                        }
                        return null;
                      },
                    ),
                  ],
                ),
              ),
            ).animate().fadeIn(delay: 100.ms, duration: 300.ms),

            const SizedBox(height: 16),

            // V Features Section
            Card(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                children: [
                  ListTile(
                    title: Text(
                      'V Features (PCA Components)',
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    subtitle: const Text('28 anonymized features from PCA'),
                    trailing: IconButton(
                      icon: Icon(
                        _showAdvanced ? Icons.expand_less : Icons.expand_more,
                      ),
                      onPressed: () {
                        setState(() {
                          _showAdvanced = !_showAdvanced;
                        });
                      },
                    ),
                  ),
                  if (_showAdvanced) ...[
                    const Divider(height: 1),
                    Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        children: [
                          Row(
                            children: [
                              Expanded(
                                child: Text(
                                  'Auto-generate random V features',
                                  style: theme.textTheme.bodyMedium,
                                ),
                              ),
                              Switch(
                                value: _useRandomValues,
                                onChanged: (value) {
                                  setState(() {
                                    _useRandomValues = value;
                                  });
                                },
                              ),
                            ],
                          ),
                          const SizedBox(height: 16),
                          GridView.builder(
                            shrinkWrap: true,
                            physics: const NeverScrollableScrollPhysics(),
                            gridDelegate:
                                const SliverGridDelegateWithFixedCrossAxisCount(
                                  crossAxisCount: 2,
                                  childAspectRatio: 2.5,
                                  crossAxisSpacing: 8,
                                  mainAxisSpacing: 8,
                                ),
                            itemCount: 28,
                            itemBuilder: (context, index) {
                              final key = 'V${index + 1}';
                              return TextFormField(
                                controller: _vControllers[key],
                                keyboardType:
                                    const TextInputType.numberWithOptions(
                                      decimal: true,
                                      signed: true,
                                    ),
                                style: const TextStyle(fontSize: 12),
                                decoration: InputDecoration(
                                  labelText: key,
                                  isDense: true,
                                  contentPadding: const EdgeInsets.symmetric(
                                    horizontal: 12,
                                    vertical: 8,
                                  ),
                                  border: OutlineInputBorder(
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                ),
                              );
                            },
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ).animate().fadeIn(delay: 200.ms, duration: 300.ms),

            const SizedBox(height: 24),

            // Submit Button
            SizedBox(
              height: 56,
              child: ElevatedButton(
                onPressed: transactionProvider.isLoading
                    ? null
                    : _submitPrediction,
                style: ElevatedButton.styleFrom(
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                ),
                child: transactionProvider.isLoading
                    ? const SizedBox(
                        width: 24,
                        height: 24,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.analytics),
                          SizedBox(width: 8),
                          Text(
                            'Analyze Transaction',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
              ),
            ).animate().fadeIn(delay: 300.ms, duration: 300.ms),
          ],
        ),
      ),
    );
  }

  Widget _buildChip(
    String label,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return ActionChip(
      avatar: Icon(icon, size: 18, color: color),
      label: Text(label),
      onPressed: onTap,
      backgroundColor: color.withValues(alpha: 0.1),
      side: BorderSide(color: color.withValues(alpha: 0.3)),
    );
  }

  void _showHelpDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Row(
          children: [
            Icon(Icons.help_outline),
            SizedBox(width: 8),
            Text('How It Works'),
          ],
        ),
        content: const SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'Transaction Features',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              SizedBox(height: 8),
              Text(
                '• Amount: The transaction amount in currency units\n'
                '• Time: Seconds elapsed from the first transaction\n'
                '• V1-V28: PCA-transformed features from original data',
              ),
              SizedBox(height: 16),
              Text(
                'Quick Generate Options',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              SizedBox(height: 8),
              Text(
                '• Random: Generate random values\n'
                '• Fraud Pattern: Simulate suspicious transaction\n'
                '• Legit Pattern: Simulate normal transaction',
              ),
              SizedBox(height: 16),
              Text(
                'The ML model analyzes these features to predict if a transaction is fraudulent.',
                style: TextStyle(fontStyle: FontStyle.italic),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Got it'),
          ),
        ],
      ),
    );
  }
}
