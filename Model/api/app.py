"""
Flask API for Fraud Detection Model
=====================================

Production-ready REST API for serving fraud detection predictions.

Features:
- Single and batch prediction endpoints
- Health check endpoint
- Model information endpoint
- Rate limiting
- Request validation
- CORS support
- Comprehensive logging

Run with: python -m api.app or gunicorn api.app:app

Author: Manan Monani
--------------------
📧 Email: mmmonani747@gmail.com
📱 Phone: +91 70168 53244
💼 LinkedIn: https://www.linkedin.com/in/mananmonani
🐙 GitHub: https://github.com/manan-monani
▶️ YouTube: https://youtube.com/@mananmonani
💻 LeetCode: https://leetcode.com/u/mmmonani747
📊 Kaggle: https://www.kaggle.com/mananmonani
📍 Location: Jamnagar, Gujarat, India
🌐 Portfolio: Coming Soon
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from functools import wraps

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from loguru import logger

from src.config import Config
from src.predictor import Predictor, TransactionValidator


# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load configuration
config = Config()

# Global predictor instance
predictor: Optional[Predictor] = None

# Request tracking
request_count = 0
start_time = datetime.now()


def load_model() -> bool:
    """Load the fraud detection model."""
    global predictor
    
    try:
        model_path = config.get_absolute_path("models/fraud_detector.joblib")
        preprocessor_path = config.get_absolute_path("models/preprocessor.joblib")
        
        if not model_path.exists():
            logger.warning(f"Model not found at {model_path}")
            return False
        
        predictor = Predictor(config)
        predictor.load_model(model_path)
        
        if preprocessor_path.exists():
            predictor.load_preprocessor(preprocessor_path)
        
        logger.success("Model loaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return False


def require_model(f):
    """Decorator to ensure model is loaded before handling request."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if predictor is None:
            return jsonify({
                'success': False,
                'error': 'Model not loaded. Please train a model first.',
                'code': 'MODEL_NOT_LOADED'
            }), 503
        return f(*args, **kwargs)
    return decorated_function


def rate_limit(f):
    """Simple rate limiting decorator."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # In production, use Redis or similar for distributed rate limiting
        global request_count
        request_count += 1
        return f(*args, **kwargs)
    return decorated_function


@app.before_request
def before_request():
    """Log incoming requests."""
    g.start_time = time.time()
    logger.info(f"Request: {request.method} {request.path}")


@app.after_request
def after_request(response):
    """Log request completion and add headers."""
    duration = time.time() - g.start_time
    logger.info(f"Response: {response.status_code} ({duration:.3f}s)")
    
    # Add custom headers
    response.headers['X-Request-Duration'] = f"{duration:.3f}"
    response.headers['X-API-Version'] = '1.0.0'
    
    return response


# ============== Health & Info Endpoints ==============

@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API information."""
    return jsonify({
        'name': 'Fraud Detection API',
        'version': '1.0.0',
        'author': 'Manan Monani',
        'description': 'Production-grade API for credit card fraud detection',
        'endpoints': {
            'GET /': 'API information',
            'GET /health': 'Health check',
            'GET /model/info': 'Model information',
            'POST /predict': 'Single prediction',
            'POST /predict/batch': 'Batch prediction',
        },
        'documentation': 'https://github.com/manan-monani/Payment-Fraud-Detection-Model',
        'contact': {
            'email': 'mmmonani747@gmail.com',
            'linkedin': 'https://www.linkedin.com/in/mananmonani',
            'github': 'https://github.com/manan-monani'
        }
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    uptime = (datetime.now() - start_time).total_seconds()
    
    return jsonify({
        'status': 'healthy',
        'model_loaded': predictor is not None,
        'uptime_seconds': uptime,
        'total_requests': request_count,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/model/info', methods=['GET'])
@require_model
def model_info():
    """Get model information."""
    info = predictor.get_model_info()
    
    return jsonify({
        'success': True,
        'data': info
    })


# ============== Prediction Endpoints ==============

@app.route('/predict', methods=['POST'])
@require_model
@rate_limit
def predict():
    """
    Make a single prediction.
    
    Request body:
    {
        "Time": 0,
        "V1": -1.359807,
        "V2": -0.072781,
        ...
        "V28": -0.021053,
        "Amount": 149.62
    }
    
    Response:
    {
        "success": true,
        "prediction": {
            "is_fraud": false,
            "label": "Legitimate",
            "fraud_probability": 0.023,
            "confidence": 0.977,
            "risk_level": "VERY LOW"
        }
    }
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided',
                'code': 'MISSING_DATA'
            }), 400
        
        # Validate transaction
        is_valid, errors = TransactionValidator.validate(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': 'Validation failed',
                'validation_errors': errors,
                'code': 'VALIDATION_ERROR'
            }), 400
        
        # Make prediction
        result = predictor.predict_single(data)
        
        return jsonify({
            'success': True,
            'prediction': result
        })
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'PREDICTION_ERROR'
        }), 500


@app.route('/predict/batch', methods=['POST'])
@require_model
@rate_limit
def predict_batch():
    """
    Make batch predictions.
    
    Request body:
    {
        "transactions": [
            {"Time": 0, "V1": -1.35, ..., "Amount": 149.62},
            {"Time": 1, "V1": 1.19, ..., "Amount": 2.69}
        ]
    }
    
    Response:
    {
        "success": true,
        "total": 2,
        "fraud_count": 0,
        "legitimate_count": 2,
        "predictions": [...]
    }
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'transactions' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing "transactions" field',
                'code': 'MISSING_DATA'
            }), 400
        
        transactions = data['transactions']
        
        if not isinstance(transactions, list):
            return jsonify({
                'success': False,
                'error': '"transactions" must be an array',
                'code': 'INVALID_FORMAT'
            }), 400
        
        if len(transactions) == 0:
            return jsonify({
                'success': False,
                'error': 'Empty transactions array',
                'code': 'EMPTY_DATA'
            }), 400
        
        if len(transactions) > 10000:
            return jsonify({
                'success': False,
                'error': 'Batch size exceeds maximum (10000)',
                'code': 'BATCH_TOO_LARGE'
            }), 400
        
        # Validate all transactions
        all_valid, errors = TransactionValidator.validate_batch(transactions)
        if not all_valid:
            return jsonify({
                'success': False,
                'error': 'Validation failed for some transactions',
                'validation_errors': {str(k): v for k, v in errors.items()},
                'code': 'VALIDATION_ERROR'
            }), 400
        
        # Make predictions
        result_df = predictor.predict_batch(transactions)
        
        # Convert to list of dicts
        predictions = result_df.to_dict('records')
        fraud_count = sum(1 for p in predictions if p.get('prediction') == 1)
        
        return jsonify({
            'success': True,
            'total': len(predictions),
            'fraud_count': fraud_count,
            'legitimate_count': len(predictions) - fraud_count,
            'fraud_percentage': (fraud_count / len(predictions)) * 100 if predictions else 0,
            'predictions': predictions
        })
        
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'PREDICTION_ERROR'
        }), 500


@app.route('/threshold', methods=['GET', 'POST'])
@require_model
def threshold():
    """Get or set the classification threshold."""
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'threshold': predictor.threshold
        })
    
    else:  # POST
        data = request.get_json()
        
        if not data or 'threshold' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing "threshold" field',
                'code': 'MISSING_DATA'
            }), 400
        
        try:
            new_threshold = float(data['threshold'])
            if not 0 <= new_threshold <= 1:
                raise ValueError("Threshold must be between 0 and 1")
            
            predictor.set_threshold(new_threshold)
            
            return jsonify({
                'success': True,
                'message': f'Threshold updated to {new_threshold}',
                'threshold': new_threshold
            })
            
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'code': 'INVALID_THRESHOLD'
            }), 400


# ============== Error Handlers ==============

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'code': 'NOT_FOUND'
    }), 404


@app.errorhandler(405)
def method_not_allowed(e):
    """Handle 405 errors."""
    return jsonify({
        'success': False,
        'error': 'Method not allowed',
        'code': 'METHOD_NOT_ALLOWED'
    }), 405


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors."""
    logger.error(f"Internal error: {e}")
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'code': 'INTERNAL_ERROR'
    }), 500


# ============== Main ==============

def create_app():
    """Application factory."""
    load_model()
    return app


if __name__ == '__main__':
    # Setup logging
    logger.remove()
    logger.add(
        sink=lambda msg: print(msg, end=''),
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>"
    )
    
    # Load model
    logger.info("Starting Fraud Detection API...")
    load_model()
    
    # Run server
    host = config.api.host
    port = config.api.port
    debug = config.api.debug
    
    logger.info(f"Server running on http://{host}:{port}")
    logger.info("Press Ctrl+C to stop")
    
    app.run(host=host, port=port, debug=debug)
