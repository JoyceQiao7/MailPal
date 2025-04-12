import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter

# Download necessary NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

class NLPUtils:
    """
    Utility class for natural language processing functions.
    """
    
    def __init__(self):
        """Initialize the NLPUtils class."""
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
    
    def preprocess_text(self, text):
        """
        Preprocess text by tokenizing, removing stopwords, and lemmatizing.
        
        Args:
            text: The text to preprocess
            
        Returns:
            A list of preprocessed tokens
        """
        # Lowercase and tokenize
        tokens = word_tokenize(text.lower())
        
        # Remove stopwords and punctuation
        filtered_tokens = []
        for token in tokens:
            if token not in self.stop_words and token.isalnum():
                filtered_tokens.append(self.lemmatizer.lemmatize(token))
        
        return filtered_tokens
    
    def extract_keywords(self, text, num_keywords=10):
        """
        Extract the most important keywords from text.
        
        Args:
            text: The text to extract keywords from
            num_keywords: The number of keywords to extract
            
        Returns:
            A list of keywords
        """
        tokens = self.preprocess_text(text)
        
        # Count frequencies
        word_freq = Counter(tokens)
        
        # Get the most common words
        keywords = [word for word, count in word_freq.most_common(num_keywords)]
        
        return keywords
    
    def detect_entities(self, text, entities):
        """
        Detect specific entities in text.
        
        Args:
            text: The text to search in
            entities: A list of entity strings to look for
            
        Returns:
            A list of found entities
        """
        found_entities = []
        text_lower = text.lower()
        
        for entity in entities:
            entity_lower = entity.lower()
            if entity_lower in text_lower:
                found_entities.append(entity)
        
        return found_entities
    
    def calculate_readability(self, text):
        """
        Calculate readability metrics for text.
        
        Args:
            text: The text to analyze
            
        Returns:
            A dictionary with readability metrics
        """
        # Tokenize sentences and words
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        
        # Count total words and sentences
        num_words = len(words)
        num_sentences = len(sentences)
        
        # Calculate average sentence length
        avg_sentence_length = num_words / max(1, num_sentences)
        
        # Count syllables (simplified approach)
        def count_syllables(word):
            word = word.lower()
            # Remove punctuation
            word = re.sub(r'[^\w\s]', '', word)
            # Count vowel groups
            return max(1, len(re.findall(r'[aeiouy]+', word)))
        
        total_syllables = sum(count_syllables(word) for word in words)
        avg_syllables_per_word = total_syllables / max(1, num_words)
        
        # Calculate Flesch Reading Ease
        # Higher scores indicate easier to read text (90-100: Very easy, 0-30: Very difficult)
        flesch_ease = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        # Calculate Flesch-Kincaid Grade Level
        # Corresponds to US grade level required to understand the text
        flesch_kincaid = 0.39 * avg_sentence_length + 11.8 * avg_syllables_per_word - 15.59
        
        return {
            'avg_sentence_length': avg_sentence_length,
            'avg_syllables_per_word': avg_syllables_per_word,
            'flesch_ease': flesch_ease,
            'flesch_kincaid_grade': flesch_kincaid
        }
    
    def analyze_email_structure(self, email_text):
        """
        Analyze the structure of an email.
        
        Args:
            email_text: The email text to analyze
            
        Returns:
            A dictionary with structural elements
        """
        # Split the email into lines
        lines = email_text.split('\n')
        
        # Look for greeting
        greeting = None
        for i, line in enumerate(lines[:5]):  # Check first 5 lines
            line = line.strip()
            if re.match(r'^(Dear|Hi|Hello|Hey|Good morning|Good afternoon|Good evening)', line):
                greeting = line
                break
        
        # Look for signature (simplified approach)
        signature_markers = ['Best', 'Regards', 'Sincerely', 'Thanks', 'Thank you', 'Cheers']
        signature = None
        signature_start_idx = None
        
        for i, line in enumerate(reversed(lines)):
            line = line.strip()
            if any(marker in line for marker in signature_markers):
                signature_start_idx = len(lines) - i - 1
                signature = '\n'.join(lines[signature_start_idx:])
                break
        
        # Extract body (everything between greeting and signature)
        body_start = 0
        if greeting:
            greeting_idx = lines.index(greeting.strip())
            body_start = greeting_idx + 1
        
        body_end = len(lines)
        if signature_start_idx:
            body_end = signature_start_idx
        
        body = '\n'.join(lines[body_start:body_end]).strip()
        
        return {
            'greeting': greeting,
            'body': body,
            'signature': signature
        }