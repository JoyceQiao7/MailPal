from transformers import pipeline
from config import Config
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.tokenize import word_tokenize
nltk.download('punkt')

class ContextAnalyzer:
    def __init__(self):
        self.sentiment_analyzer = pipeline('sentiment-analysis', model=Config.NLP_MODEL)
        self.intents = ['inquiry', 'meeting_request', 'follow_up', 'apology']  # Example intents

    def extract_keywords(self, text):
        vectorizer = TfidfVectorizer(max_features=10, stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([text])
        return vectorizer.get_feature_names_out().tolist()

    def classify_intent(self, subject, content):
        # Simplified heuristic-based intent classification
        text = f"{subject} {content}".lower()
        if any(word in text for word in ['meeting', 'schedule', 'call']):
            return 'meeting_request'
        elif any(word in text for word in ['sorry', 'apologize', 'regret']):
            return 'apology'
        elif any(word in text for word in ['follow up', 'checking in']):
            return 'follow_up'
        else:
            return 'inquiry'

    def infer_tone(self, content):
        result = self.sentiment_analyzer(content)[0]
        sentiment = result['label'].lower()
        return 'positive' if sentiment == 'positive' else 'neutral' if result['score'] < 0.7 else 'negative'

    def analyze(self, email_data):
        keywords = self.extract_keywords(email_data['content'])
        intent = self.classify_intent(email_data['subject'], email_data['content'])
        tone = self.infer_tone(email_data['content'])

        return {
            'keywords': keywords,
            'intent': intent,
            'tone': tone
        }