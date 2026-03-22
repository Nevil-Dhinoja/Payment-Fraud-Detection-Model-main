/// History Screen
/// Author: Manan Monani

import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import '../providers/transaction_provider.dart';
import '../models/transaction.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  String _filter = 'all';
  String _sortBy = 'newest';

  @override
  Widget build(BuildContext context) {
    final transactionProvider = context.watch<TransactionProvider>();
    final theme = Theme.of(context);

    List<TransactionHistory> filteredHistory = _getFilteredHistory(
      transactionProvider.history,
    );

    return Scaffold(
      appBar: AppBar(
        title: const Text('Prediction History'),
        actions: [
          PopupMenuButton<String>(
            icon: const Icon(Icons.filter_list),
            onSelected: (value) => setState(() => _filter = value),
            itemBuilder: (context) => [
              _buildPopupItem('all', 'All Transactions', _filter == 'all'),
              _buildPopupItem('fraud', 'Fraud Only', _filter == 'fraud'),
              _buildPopupItem('legit', 'Legitimate Only', _filter == 'legit'),
            ],
          ),
          PopupMenuButton<String>(
            icon: const Icon(Icons.sort),
            onSelected: (value) => setState(() => _sortBy = value),
            itemBuilder: (context) => [
              _buildPopupItem('newest', 'Newest First', _sortBy == 'newest'),
              _buildPopupItem('oldest', 'Oldest First', _sortBy == 'oldest'),
              _buildPopupItem('highest', 'Highest Risk', _sortBy == 'highest'),
              _buildPopupItem('lowest', 'Lowest Risk', _sortBy == 'lowest'),
            ],
          ),
          if (transactionProvider.history.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.delete_outline),
              onPressed: () => _showClearDialog(context),
            ),
        ],
      ),
      body: filteredHistory.isEmpty
          ? _buildEmptyState(theme)
          : _buildHistoryList(filteredHistory, theme),
    );
  }

  PopupMenuItem<String> _buildPopupItem(
    String value,
    String text,
    bool selected,
  ) {
    return PopupMenuItem(
      value: value,
      child: Row(
        children: [
          if (selected)
            const Icon(Icons.check, size: 18)
          else
            const SizedBox(width: 18),
          const SizedBox(width: 8),
          Text(text),
        ],
      ),
    );
  }

  List<TransactionHistory> _getFilteredHistory(
    List<TransactionHistory> history,
  ) {
    List<TransactionHistory> filtered;

    // Filter
    switch (_filter) {
      case 'fraud':
        filtered = history.where((h) => h.result.isFraud).toList();
        break;
      case 'legit':
        filtered = history.where((h) => !h.result.isFraud).toList();
        break;
      default:
        filtered = List.from(history);
    }

    // Sort
    switch (_sortBy) {
      case 'oldest':
        filtered.sort((a, b) => a.timestamp.compareTo(b.timestamp));
        break;
      case 'highest':
        filtered.sort(
          (a, b) => b.result.probability.compareTo(a.result.probability),
        );
        break;
      case 'lowest':
        filtered.sort(
          (a, b) => a.result.probability.compareTo(b.result.probability),
        );
        break;
      default: // newest
        filtered.sort((a, b) => b.timestamp.compareTo(a.timestamp));
    }

    return filtered;
  }

  Widget _buildEmptyState(ThemeData theme) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.history,
            size: 80,
            color: theme.colorScheme.onSurface.withValues(alpha: 0.2),
          ),
          const SizedBox(height: 16),
          Text(
            _filter == 'all'
                ? 'No predictions yet'
                : 'No ${_filter == 'fraud' ? 'fraud' : 'legitimate'} predictions',
            style: theme.textTheme.titleLarge?.copyWith(
              color: theme.colorScheme.onSurface.withValues(alpha: 0.5),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Make predictions to see history here',
            style: theme.textTheme.bodyMedium?.copyWith(
              color: theme.colorScheme.onSurface.withValues(alpha: 0.4),
            ),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () => Navigator.pushNamed(context, '/transaction'),
            icon: const Icon(Icons.add),
            label: const Text('Make Prediction'),
          ),
        ],
      ),
    ).animate().fadeIn();
  }

  Widget _buildHistoryList(List<TransactionHistory> history, ThemeData theme) {
    return Column(
      children: [
        // Summary Bar
        Container(
          padding: const EdgeInsets.all(16),
          color: theme.colorScheme.surface,
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildSummaryItem(
                'Total',
                history.length.toString(),
                Icons.analytics,
                theme.colorScheme.primary,
              ),
              _buildSummaryItem(
                'Fraud',
                history.where((h) => h.result.isFraud).length.toString(),
                Icons.warning,
                Colors.red,
              ),
              _buildSummaryItem(
                'Legit',
                history.where((h) => !h.result.isFraud).length.toString(),
                Icons.check_circle,
                Colors.green,
              ),
            ],
          ),
        ),

        const Divider(height: 1),

        // List
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: history.length,
            itemBuilder: (context, index) {
              final item = history[index];
              return _buildHistoryCard(item, index);
            },
          ),
        ),
      ],
    );
  }

  Widget _buildSummaryItem(
    String label,
    String value,
    IconData icon,
    Color color,
  ) {
    return Column(
      children: [
        Icon(icon, color: color, size: 24),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Theme.of(
              context,
            ).colorScheme.onSurface.withValues(alpha: 0.6),
          ),
        ),
      ],
    );
  }

  Widget _buildHistoryCard(TransactionHistory item, int index) {
    final isFraud = item.result.isFraud;
    final color = isFraud ? Colors.red : Colors.green;

    return Card(
          margin: const EdgeInsets.only(bottom: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: BorderSide(color: color.withValues(alpha: 0.3), width: 1),
          ),
          child: InkWell(
            onTap: () => _showDetailDialog(item),
            borderRadius: BorderRadius.circular(12),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: color.withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Icon(
                          isFraud ? Icons.warning : Icons.check_circle,
                          color: color,
                          size: 24,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              isFraud ? 'Fraud Detected' : 'Legitimate',
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 16,
                                color: color,
                              ),
                            ),
                            Text(
                              DateFormat(
                                'MMM d, yyyy • h:mm a',
                              ).format(item.timestamp),
                              style: TextStyle(
                                fontSize: 12,
                                color: Theme.of(
                                  context,
                                ).colorScheme.onSurface.withValues(alpha: 0.5),
                              ),
                            ),
                          ],
                        ),
                      ),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: [
                          Text(
                            '\$${item.transaction.amount.toStringAsFixed(2)}',
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 16,
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 2,
                            ),
                            decoration: BoxDecoration(
                              color: _getRiskColor(
                                item.result.riskLevel,
                              ).withValues(alpha: 0.1),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Text(
                              item.result.riskLevel,
                              style: TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                                color: _getRiskColor(item.result.riskLevel),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  // Progress bar
                  ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: LinearProgressIndicator(
                      value: item.result.probability,
                      backgroundColor: Colors.grey.withValues(alpha: 0.2),
                      valueColor: AlwaysStoppedAnimation<Color>(color),
                      minHeight: 6,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Fraud Probability: ${(item.result.probability * 100).toStringAsFixed(1)}%',
                        style: const TextStyle(fontSize: 12),
                      ),
                      Text(
                        'Confidence: ${(item.result.confidence * 100).toStringAsFixed(1)}%',
                        style: TextStyle(
                          fontSize: 12,
                          color: Theme.of(
                            context,
                          ).colorScheme.onSurface.withValues(alpha: 0.6),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        )
        .animate()
        .fadeIn(
          delay: Duration(milliseconds: index * 50),
          duration: 300.ms,
        )
        .slideX(begin: 0.1, end: 0);
  }

  Color _getRiskColor(String riskLevel) {
    switch (riskLevel.toLowerCase()) {
      case 'critical':
        return Colors.red.shade900;
      case 'high':
        return Colors.red;
      case 'medium':
        return Colors.orange;
      case 'low':
        return Colors.green;
      default:
        return Colors.grey;
    }
  }

  void _showDetailDialog(TransactionHistory item) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.6,
        minChildSize: 0.4,
        maxChildSize: 0.9,
        expand: false,
        builder: (context, scrollController) => SingleChildScrollView(
          controller: scrollController,
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.grey.withValues(alpha: 0.3),
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 20),

              // Header
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: (item.result.isFraud ? Colors.red : Colors.green)
                          .withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(
                      item.result.isFraud ? Icons.warning : Icons.check_circle,
                      color: item.result.isFraud ? Colors.red : Colors.green,
                      size: 32,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          item.result.label,
                          style: const TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          DateFormat(
                            'MMMM d, yyyy at h:mm:ss a',
                          ).format(item.timestamp),
                          style: TextStyle(
                            color: Theme.of(
                              context,
                            ).colorScheme.onSurface.withValues(alpha: 0.6),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 24),
              const Divider(),
              const SizedBox(height: 16),

              // Transaction Details
              const Text(
                'Transaction Details',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 12),
              _buildDetailRow(
                'Amount',
                '\$${item.transaction.amount.toStringAsFixed(2)}',
              ),
              _buildDetailRow(
                'Time',
                '${item.transaction.time.toInt()} seconds',
              ),

              const SizedBox(height: 24),

              // Prediction Results
              const Text(
                'Prediction Results',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 12),
              _buildDetailRow(
                'Fraud Probability',
                '${(item.result.probability * 100).toStringAsFixed(2)}%',
              ),
              _buildDetailRow(
                'Confidence',
                '${(item.result.confidence * 100).toStringAsFixed(2)}%',
              ),
              _buildDetailRow('Risk Level', item.result.riskLevel),

              const SizedBox(height: 24),

              // V Features (collapsed)
              ExpansionTile(
                title: const Text(
                  'V Features',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                children: [
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: item.transaction.vFeatures.entries
                        .map(
                          (e) => Chip(
                            label: Text(
                              '${e.key}: ${e.value.toStringAsFixed(2)}',
                              style: const TextStyle(fontSize: 10),
                            ),
                          ),
                        )
                        .toList(),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
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

  void _showClearDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text('Clear History'),
        content: const Text(
          'Are you sure you want to clear all prediction history? This action cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              context.read<TransactionProvider>().clearHistory();
              Navigator.pop(context);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
            ),
            child: const Text('Clear'),
          ),
        ],
      ),
    );
  }
}
