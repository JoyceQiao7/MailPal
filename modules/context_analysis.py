import spacy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from collections import Counter
import re

from models.intent_classifier import IntentClassifier
from models.tone_analyzer import ToneAnalyzer

# Download necessary NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

class ContextAnalyzer:
    """
    Module responsible for analyzing email context and intent.
    """
    
    def __init__(self):
        """Initialize the ContextAnalyzer module."""
        # Load spaCy model
        self.nlp = spacy.load('en_core_web_sm')
        
        # Initialize NLTK components
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Initialize intent classifier and tone analyzer
        self.intent_classifier = IntentClassifier()
        self.tone_analyzer = ToneAnalyzer()
    
    def analyze_email_context(self, email_data):
        """
        Analyze the context and intent of an email.
        
        Args:
            email_data: A dictionary containing the email's subject and content
            
        Returns:
            A dictionary containing keywords, intent, and tone recommendation
        """
        subject = email_data.get('subject', '')
        content = email_data.get('content', '')
        
        # Extract keywords
        keywords = self._extract_keywords(subject, content)
        
        # Classify intent
        intent = self._classify_intent(subject, content)
        
        # Determine initial tone recommendation
        tone = self._infer_tone_from_intent(intent)
        
        return {
            'keywords': keywords,
            'intent': intent,
            'tone': tone
        }
    
    def _extract_keywords(self, subject, content):
        """
        Extract important keywords from the email subject and content.
        
        Args:
            subject: The email subject
            content: The email content
            
        Returns:
            A list of important keywords
        """
        # Combine subject and content for processing
        text = f"{subject} {content}"
        
        # Process text with spaCy
        doc = self.nlp(text)
        
        # Extract named entities
        entities = [ent.text.lower() for ent in doc.ents]
        
        # Tokenize text
        tokens = word_tokenize(text.lower())
        
        # Remove stopwords and punctuation, then lemmatize
        filtered_tokens = []
        for token in tokens:
            if (token not in self.stop_words and 
                token.isalnum() and 
                len(token) > 2):
                filtered_tokens.append(self.lemmatizer.lemmatize(token))
        
        # Count token frequencies
        token_counts = Counter(filtered_tokens)
        
        # Get the most common tokens (excluding very common words)
        common_tokens = [token for token, count in token_counts.most_common(10) 
                        if token not in ['email', 'thanks', 'dear', 'hello', 'hi', 'regards']]
        
        # Combine entities and common tokens, removing duplicates
        all_keywords = list(set(entities + common_tokens))
        
        # Return top keywords (limit to 10)
        return all_keywords[:10]
    
    def _classify_intent(self, subject, content):
        """
        Classify the intent of the email.
        
        Args:
            subject: The email subject
            content: The email content
            
        Returns:
            The classified intent (e.g., 'inquiry', 'meeting_request', etc.)
        """
        # Combine subject and content
        full_text = f"{subject} {content}"
        
        # Use the intent classifier model
        intent = self.intent_classifier.predict(full_text)
        
        return intent
    
    def _infer_tone_from_intent(self, intent):
        """
        Infer an appropriate tone based on the email's intent.
        
        Args:
            intent: The classified intent of the email
            
        Returns:
            A recommended tone (e.g., 'professional', 'friendly', etc.)
        """
        # Intent-to-tone mapping
        intent_tone_map = {
            'inquiry': 'professional and inquisitive',
            'meeting_request': 'professional and courteous',
            'follow_up': 'friendly but persistent',
            'status_update': 'informative and clear',
            'problem_report': 'concerned but composed',
            'complaint': 'firm but respectful',
            'apology': 'genuine and humble',
            'thank_you': 'appreciative and warm',
            'introduction': 'friendly and professional',
            'request': 'polite and clear',
            'sales_pitch': 'persuasive but not pushy',
            'feedback': 'constructive and thoughtful',
            'invitation': 'welcoming and enthusiastic',
            'announcement': 'informative and engaging',
            'application': 'confident and professional'
        }
        
        # Get tone from map, default to 'professional'
        return intent_tone_map.get(intent, 'professional')