import re
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import spacy

# Download NLTK data
nltk.download('vader_lexicon', quiet=True)

class ToneAnalyzer:
    """
    Model for analyzing the tone of emails.
    """
    
    def __init__(self):
        """Initialize the ToneAnalyzer model."""
        # Initialize NLTK's sentiment analyzer
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        
        # Load spaCy model for additional linguistic analysis
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except:
            # If model not available, download it
            import subprocess
            subprocess.run(['python', '-m', 'spacy', 'download', 'en_core_web_sm'], 
                         stdout=subprocess.PIPE)
            self.nlp = spacy.load('en_core_web_sm')
        
        # Tone indicators in text
        self.tone_indicators = {
            'formal': [
                r'\brespectfully\b', r'\bhonor(?:ed|able)\b', r'\bregards\b',
                r'\bsincerely\b', r'\bpursuant\b', r'\bhereby\b'
            ],
            'urgent': [
                r'\burgent\b', r'\bimmediate\b', r'\bas soon as possible\b',
                r'\bASAP\b', r'\bpressing\b', r'\btime-sensitive\b'
            ],
            'friendly': [
                r'\bcheers\b', r'\bthanks\b', r'\bappreciate\b', r'\blooking forward\b',
                r'\bhope all is well\b', r'\bhope you(?:\'re| are) doing well\b'
            ],
            'apologetic': [
                r'\bsorry\b', r'\bapologi[sz]e\b', r'\bregret\b',
                r'\bunfortunately\b', r'\bmistake\b', r'\binconvenience\b'
            ],
            'assertive': [
                r'\bmust\b', r'\brequire\b', r'\bnecessary\b',
                r'\bimportant\b', r'\bessential\b', r'\bcritical\b'
            ],
            'appreciative': [
                r'\bthank you\b', r'\bgrateful\b', r'\bappreciate\b',
                r'\bthankful\b', r'\bindebted\b', r'\bvalu(?:e|able)\b'
            ]
        }
    
    def analyze_tone(self, text):
        """
        Analyze the tone of text.
        
        Args:
            text: The text to analyze
            
        Returns:
            A dictionary with tone analysis results
        """
        # Get sentiment scores
        sentiment_scores = self._analyze_sentiment(text)
        
        # Get linguistic features
        linguistic_features = self._analyze_linguistic_features(text)
        
        # Detect specific tones
        specific_tones = self._detect_specific_tones(text)
        
        # Determine the overall tone
        overall_tone = self._determine_overall_tone(sentiment_scores, linguistic_features, specific_tones)
        
        return {
            'sentiment': sentiment_scores,
            'linguistic_features': linguistic_features,
            'specific_tones': specific_tones,
            'overall_tone': overall_tone
        }
    
    def _analyze_sentiment(self, text):
        """
        Analyze sentiment using NLTK's VADER.
        
        Args:
            text: The text to analyze
            
        Returns:
            A dictionary with sentiment scores
        """
        sentiment_scores = self.sentiment_analyzer.polarity_scores(text)
        
        # Interpret the compound score
        compound = sentiment_scores['compound']
        if compound >= 0.05:
            sentiment_label = 'positive'
        elif compound <= -0.05:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'
        
        return {
            'scores': sentiment_scores,
            'label': sentiment_label
        }
    
    def _analyze_linguistic_features(self, text):
        """
        Analyze linguistic features using spaCy.
        
        Args:
            text: The text to analyze
            
        Returns:
            A dictionary with linguistic features
        """
        doc = self.nlp(text)
        
        # Count sentence types
        sentences = list(doc.sents)
        questions = sum(1 for sent in sentences if sent.text.strip().endswith('?'))
        exclamations = sum(1 for sent in sentences if sent.text.strip().endswith('!'))
        
        # Count personal pronouns
        first_person = sum(1 for token in doc if token.text.lower() in ['i', 'me', 'my', 'mine', 'we', 'us', 'our', 'ours'])
        second_person = sum(1 for token in doc if token.text.lower() in ['you', 'your', 'yours'])
        
        # Count modal verbs
        modals = sum(1 for token in doc if token.text.lower() in ['would', 'could', 'might', 'may', 'can', 'should', 'must'])
        
        # Formality indicators
        contractions = len(re.findall(r'\b\w+\'\w+\b', text))  # e.g., I'm, don't
        academic_words = sum(1 for token in doc if token.text.lower() in [
            'therefore', 'thus', 'however', 'consequently', 'furthermore', 'moreover',
            'nevertheless', 'notwithstanding', 'accordingly', 'subsequently'
        ])
        
        return {
            'sentence_count': len(sentences),
            'questions': questions,
            'exclamations': exclamations,
            'first_person': first_person,
            'second_person': second_person,
            'modals': modals,
            'contractions': contractions,
            'academic_words': academic_words,
            'avg_token_length': sum(len(token.text) for token in doc if not token.is_punct) / max(1, sum(1 for token in doc if not token.is_punct)),
            'avg_sentence_length': sum(len(list(sent)) for sent in sentences) / max(1, len(sentences))
        }
    
    def _detect_specific_tones(self, text):
        """
        Detect specific tones based on pattern matching.
        
        Args:
            text: The text to analyze
            
        Returns:
            A dictionary with specific tone scores
        """
        text_lower = text.lower()
        tone_scores = {}
        
        # Check for each tone indicator
        for tone, patterns in self.tone_indicators.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                score += len(matches)
            tone_scores[tone] = score
        
        return tone_scores
    
    def _determine_overall_tone(self, sentiment_scores, linguistic_features, specific_tones):
        """
        Determine the overall tone based on all analyses.
        
        Args:
            sentiment_scores: Dictionary with sentiment analysis results
            linguistic_features: Dictionary with linguistic features
            specific_tones: Dictionary with specific tone scores
            
        Returns:
            A string describing the overall tone
        """
        # Get the sentiment label
        sentiment = sentiment_scores['label']
        
        # Get the most prevalent specific tone
        max_tone_score = max(specific_tones.values()) if specific_tones else 0
        top_tones = [tone for tone, score in specific_tones.items() if score == max_tone_score and score > 0]
        
        # Consider formality based on linguistic features
        formality_score = (
            (linguistic_features['academic_words'] * 2) +
            (linguistic_features['avg_token_length'] > 5) -
            linguistic_features['contractions'] -
            (linguistic_features['first_person'] > 3) -
            (linguistic_features['exclamations'])
        )
        
        formality = 'formal' if formality_score > 2 else 'casual'
        
        # Build the overall tone description
        tone_elements = []
        
        # Add sentiment
        if sentiment == 'positive':
            tone_elements.append('positive')
        elif sentiment == 'negative':
            tone_elements.append('negative')
        
        # Add top specific tones
        tone_elements.extend(top_tones)
        
        # Add formality
        tone_elements.append(formality)
        
        # Special case handling
        if linguistic_features['questions'] / max(1, linguistic_features['sentence_count']) > 0.5:
            tone_elements.append('inquisitive')
        
        if linguistic_features['exclamations'] > 0:
            tone_elements.append('emphatic')
        
        # Return a combined tone description
        return ' and '.join(set(tone_elements[:3]))  # Limit to 3 tone elements