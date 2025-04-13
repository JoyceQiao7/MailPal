from flask import request, jsonify
from functools import wraps

def require_gmail_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Missing token'}), 401
        # Validate token with Google (simplified for demo)
        return f(*args, **kwargs)
    return decorated

@main.route('/api/analyze', methods=['POST'])
@require_gmail_token
def analyze_email():
    # Existing code, unchanged
    pass

@main.route('/api/refine', methods=['POST'])
@require_gmail_token
def refine_email():
    # Existing code, unchanged
    pass