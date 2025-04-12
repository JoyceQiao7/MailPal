from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import json
import os

from modules.email_capture import EmailCapture
from modules.context_analysis import ContextAnalyzer
from modules.refinement_processor import RefinementProcessor
from modules.ai_enhancement import AIEnhancer
from utils.gmail_api import GmailAPI
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Create a Flow instance to handle OAuth 2.0
CLIENT_SECRETS_FILE = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
flow = Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE,
    scopes=SCOPES,
    redirect_uri=Config.GOOGLE_REDIRECT_URI
)

@app.route('/')
def index():
    """Main application page."""
    if 'credentials' not in session:
        return redirect(url_for('login'))
    
    return render_template('index.html')

@app.route('/login')
def login():
    """Login page to authenticate with Google."""
    if 'credentials' in session:
        return redirect(url_for('index'))
    
    # Create the OAuth URL
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    """Handle the OAuth 2.0 callback from Google."""
    # Check for valid state
    state = session.get('state', '')
    if state != request.args.get('state', ''):
        return redirect(url_for('login'))
    
    # Exchange authorization code for credentials
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    
    # Save credentials to session
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    """Log out from the application."""
    if 'credentials' in session:
        del session['credentials']
    
    return redirect(url_for('login'))

@app.route('/api/get_draft', methods=['GET'])
def get_draft():
    """Get the current email draft from Gmail."""
    if 'credentials' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get credentials from session
    credentials_dict = session.get('credentials')
    credentials = Credentials(
        token=credentials_dict['token'],
        refresh_token=credentials_dict['refresh_token'],
        token_uri=credentials_dict['token_uri'],
        client_id=credentials_dict['client_id'],
        client_secret=credentials_dict['client_secret'],
        scopes=credentials_dict['scopes']
    )
    
    # Get draft ID from query params
    draft_id = request.args.get('draft_id')
    if not draft_id:
        return jsonify({'error': 'No draft ID provided'}), 400
    
    # Instantiate Gmail API and email capture
    gmail_api = GmailAPI(credentials)
    email_capture = EmailCapture(gmail_api)
    
    # Get draft data
    email_data = email_capture.capture_draft(draft_id)
    if not email_data:
        return jsonify({'error': 'Draft not found'}), 404
    
    return jsonify(email_data)

@app.route('/api/analyze_email', methods=['POST'])
def analyze_email():
    """Analyze the email context and intent."""
    if 'credentials' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get email data from request
    email_data = request.json
    if not email_data:
        return jsonify({'error': 'No email data provided'}), 400
    
    # Analyze context
    context_analyzer = ContextAnalyzer()
    context_info = context_analyzer.analyze_email_context(email_data)
    
    return jsonify(context_info)

@app.route('/api/refine_email', methods=['POST'])
def refine_email():
    """Refine the email based on context and user instructions."""
    if 'credentials' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get email data and refinement instructions from request
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    email_data = data.get('email_data')
    context_info = data.get('context_info')
    user_instruction = data.get('user_instruction', '')
    
    # Process user refinement instructions
    refinement_processor = RefinementProcessor()
    refined_tone = refinement_processor.merge_user_instructions(context_info, user_instruction)
    
    # Generate refined email
    ai_enhancer = AIEnhancer(api_key=Config.API_KEY, model_name=Config.MODEL_NAME)
    refined_email = ai_enhancer.refine_email_content(email_data, context_info, refined_tone)
    
    return jsonify({'refined_email': refined_email})

@app.route('/api/submit_feedback', methods=['POST'])
def submit_feedback():
    """Submit user feedback for model improvement."""
    if 'credentials' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get feedback data from request
    feedback_data = request.json
    if not feedback_data:
        return jsonify({'error': 'No feedback data provided'}), 400
    
    # Store feedback (this would typically go to a database)
    # For now, just log it
    app.logger.info(f"Feedback received: {json.dumps(feedback_data)}")
    
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=Config.DEBUG)