/// Transaction Model
/// Author: Manan Monani

class Transaction {
  final String? id;
  final double time;
  final double amount;
  final Map<String, double> vFeatures;
  final DateTime? createdAt;
  final PredictionResult? prediction;

  Transaction({
    this.id,
    required this.time,
    required this.amount,
    required this.vFeatures,
    this.createdAt,
    this.prediction,
  });

  factory Transaction.fromJson(Map<String, dynamic> json) {
    Map<String, double> vFeatures = {};
    for (int i = 1; i <= 28; i++) {
      String key = 'V$i';
      if (json.containsKey(key)) {
        vFeatures[key] = (json[key] as num).toDouble();
      }
    }

    return Transaction(
      id: json['_id'] ?? json['id'],
      time: (json['Time'] as num?)?.toDouble() ?? 0,
      amount: (json['Amount'] as num?)?.toDouble() ?? 0,
      vFeatures: vFeatures,
      createdAt: json['createdAt'] != null
          ? DateTime.tryParse(json['createdAt'])
          : null,
      prediction: json['prediction'] != null
          ? PredictionResult.fromJson(json['prediction'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    Map<String, dynamic> json = {'Time': time, 'Amount': amount};

    vFeatures.forEach((key, value) {
      json[key] = value;
    });

    return json;
  }

  // Create a sample transaction for testing
  factory Transaction.sample() {
    Map<String, double> vFeatures = {};
    for (int i = 1; i <= 28; i++) {
      vFeatures['V$i'] = 0.0;
    }

    return Transaction(time: 0, amount: 100.0, vFeatures: vFeatures);
  }

  // Create from form input
  factory Transaction.fromForm({
    required double time,
    required double amount,
    required List<double> vValues,
  }) {
    Map<String, double> vFeatures = {};
    for (int i = 0; i < vValues.length && i < 28; i++) {
      vFeatures['V${i + 1}'] = vValues[i];
    }

    // Fill remaining with zeros if not provided
    for (int i = vValues.length; i < 28; i++) {
      vFeatures['V${i + 1}'] = 0.0;
    }

    return Transaction(
      time: time,
      amount: amount,
      vFeatures: vFeatures,
      createdAt: DateTime.now(),
    );
  }
}

class PredictionResult {
  final bool isFraud;
  final String label;
  final double probability;
  final double confidence;
  final String riskLevel;
  final double threshold;

  PredictionResult({
    required this.isFraud,
    required this.label,
    required this.probability,
    required this.confidence,
    required this.riskLevel,
    required this.threshold,
  });

  factory PredictionResult.fromJson(Map<String, dynamic> json) {
    return PredictionResult(
      isFraud: json['is_fraud'] ?? false,
      label: json['label'] ?? 'Unknown',
      probability: (json['fraud_probability'] as num?)?.toDouble() ?? 0.0,
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
      riskLevel: json['risk_level'] ?? 'Unknown',
      threshold: (json['threshold'] as num?)?.toDouble() ?? 0.5,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'is_fraud': isFraud,
      'label': label,
      'fraud_probability': probability,
      'confidence': confidence,
      'risk_level': riskLevel,
      'threshold': threshold,
    };
  }
}

class TransactionHistory {
  final String id;
  final Transaction transaction;
  final PredictionResult result;
  final DateTime timestamp;

  TransactionHistory({
    required this.id,
    required this.transaction,
    required this.result,
    required this.timestamp,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'transaction': transaction.toJson(),
      'result': result.toJson(),
      'timestamp': timestamp.toIso8601String(),
    };
  }

  factory TransactionHistory.fromJson(Map<String, dynamic> json) {
    return TransactionHistory(
      id: json['id'],
      transaction: Transaction.fromJson(json['transaction']),
      result: PredictionResult.fromJson(json['result']),
      timestamp: DateTime.parse(json['timestamp']),
    );
  }
}
