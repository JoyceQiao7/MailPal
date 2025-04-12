import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')
    GMAIL_CREDENTIALS_FILE = 'credentials.json'  # Path to Gmail API credentials
    NLP_MODEL = 'distilbert-base-uncased-finetuned-sst-2-english'  # Hugging Face model for sentiment/intent
    TRANSFORMER_MODEL = 'gpt2'  # Placeholder for text generation (replace with GPT-4 or similar in production)

