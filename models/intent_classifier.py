import re
import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np

class IntentClassifier:
    """
    Model for classifying the intent of emails.
    """
    
    def __init__(self, model_path=None):
        """
        Initialize the IntentClassifier model.
        
        Args:
            model_path: Path to a pre-trained model (if available)
        """
        # Define intent categories
        self.intent_categories = [
            'inquiry', 'meeting_request', 'follow_up', 'status_update',
            'problem_report', 'complaint', 'apology', 'thank_you',
            'introduction', 'request', 'sales_pitch', 'feedback',
            'invitation', 'announcement', 'application'
        ]
        
        # Intent patterns dictionary (simplified rule-based approach)
        self.intent_patterns = {
            'inquiry': [
                r'\b(?:what|who|when|where|why|how)\b.*\?',
                r'\bask(?:ing)?\b.*\babout\b',
                r'\bcurious\b|\bwonder(?:ing)?\b'
            ],
            'meeting_request': [
                r'\bmeet(?:ing)?\b.*\b(?:schedule|discuss|talk|available|time)\b',
                r'\b(?:schedule|set up|arrange)\b.*\b(?:meeting|call|discussion)\b',
                r'\bavailab(?:le|ility)\b.*\b(?:meet|discuss|talk)\b'
            ],
            'follow_up': [
                r'\bfollow(?:ing)? up\b',
                r'\bjust check(?:ing)?\b',
                r'\bany update\b|\bany progress\b',
                r'\bhaven\'t heard\b'
            ],
            'status_update': [
                r'\bupdate\b.*\b(?:progress|status|project)\b',
                r'\bprogress report\b',
                r'\b(?:completed|finished|working on)\b.*\btask\b'
            ],
            'problem_report': [
                r'\bissue\b|\bproblem\b|\berror\b|\bfail(?:ed|ure)?\b',
                r'\bdifficult(?:y|ies)\b|\btrouble\b|\bnot working\b',
                r'\b(?:fix|resolve|address)\b.*\b(?:issue|problem)\b'
            ],
            'complaint': [
                r'\bdissatisf(?:ied|action)\b|\bunhappy\b|\bfrustrat(?:ed|ing)\b',
                r'\bcomplain(?:t)?\b|\bdisappoint(?:ed|ing)\b',
                r'\bnot acceptable\b|\bunacceptable\b'
            ],
            'apology': [
                r'\b(?:I\'m|I am|we\'re|we are) sorry\b',
                r'\bapologi(?:ze|se|es)\b',
                r'\bregret\b|\bmistake\b.*\bour\b',
                r'\bmy bad\b'
            ],
            'thank_you': [
                r'\bthank(?:s|ing|ful)?\b|\bapprec[ie]at\w+\b',
                r'\bgrateful\b|\bappreciation\b'
            ],
            'introduction': [
                r'\bintroduc(?:e|ing|tion)\b|\bnice to meet\b',
                r'\bmy name is\b|\bI am\b.*\bfrom\b',
                r'\bI\'d like to introduce\b'
            ],
            'request': [
                r'\b(?:request|asking for|would like|need)\b.*\b(?:help|assistance|support|information)\b',
                r'\bcan you\b|\bcould you\b|\bwould you\b',
                r'\bplease\b.*\b(?:provide|send|review|consider)\b'
            ],
            'sales_pitch': [
                r'\b(?:offer|discount|promotion|deal|sale)\b',
                r'\b(?:product|service|solution)\b.*\b(?:benefit|feature|advantage)\b',
                r'\b(?:opportunity|limited time|special)\b'
            ],
            'feedback': [
                r'\b(?:feedback|thoughts|opinion|suggestion|review)\b',
                r'\b(?:what do you think|your input|your view)\b',
                r'\b(?:evaluate|assessment|evaluation)\b'
            ],
            'invitation': [
                r'\b(?:invite|invitation|join us|attend|participate)\b',
                r'\b(?:event|webinar|conference|party|celebration)\b',
                r'\bwould love for you to\b'
            ],
            'announcement': [
                r'\b(?:announce|announcing|pleased to|happy to)\b.*\b(?:inform|share|tell)\b',
                r'\b(?:news|update|launch|release)\b',
                r'\bwe\'re excited\b|\bI\'m excited\b'
            ],
            'application': [
                r'\b(?:apply|applying|application)\b',
                r'\b(?:resume|CV|cover letter|portfolio)\b',
                r'\b(?:position|job|role|opportunity)\b.*\b(?:interest|consideration)\b'
            ]
        }
        
        # Try to load the transformer model if available
        try:
            if model_path and os.path.exists(model_path):
                self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
                self.has_transformer_model = True
            else:
                # Use a default model if available
                try:
                    self.tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
                    self.model = AutoModelForSequenceClassification.from_pretrained(
                        "distilbert-base-uncased", 
                        num_labels=len(self.intent_categories)
                    )
                    self.has_transformer_model = True
                except Exception as e:
                    print(f"Could not load transformer model: {e}")
                    self.has_transformer_model = False
        except Exception as e:
            print(f"Error loading transformer model: {e}")
            self.has_transformer_model = False
    
    def predict(self, text):
        """
        Predict the intent of an email.
        
        Args:
            text: The email text (subject + content)
            
        Returns:
            The predicted intent category
        """
        # Try to use transformer model if available
        if hasattr(self, 'has_transformer_model') and self.has_transformer_model:
            try:
                return self._predict_with_transformer(text)
            except Exception as e:
                print(f"Error using transformer model: {e}")
                # Fall back to rule-based approach
                
        # Use rule-based approach
        return self._predict_with_rules(text)
    
    def _predict_with_transformer(self, text):
        """
        Predict intent using the transformer model.
        
        Args:
            text: The email text
            
        Returns:
            The predicted intent category
        """
        # Tokenize the text
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        
        # Get model predictions
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            predicted_class_id = logits.argmax().item()
        
        # Return the predicted intent category
        return self.intent_categories[predicted_class_id]
    
    def _predict_with_rules(self, text):
        """
        Predict intent using rule-based pattern matching.
        
        Args:
            text: The email text
            
        Returns:
            The predicted intent category
        """
        # Lowercase the text for case-insensitive matching
        text_lower = text.lower()
        
        # Score for each intent category
        intent_scores = {intent: 0 for intent in self.intent_categories}
        
        # Check for matches with each pattern
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                intent_scores[intent] += len(matches)
        
        # Get the intent with the highest score
        max_score = max(intent_scores.values())
        
        # If no patterns match, default to 'inquiry'
        if max_score == 0:
            return 'inquiry'
        
        # Get all intents with the highest score
        top_intents = [intent for intent, score in intent_scores.items() if score == max_score]
        
        # If multiple intents have the same score, prioritize certain intents
        priority_order = [
            'apology', 'thank_you', 'problem_report', 'complaint', 
            'meeting_request', 'follow_up', 'inquiry', 'request'
        ]
        
        for priority_intent in priority_order:
            if priority_intent in top_intents:
                return priority_intent
        
        # If no priority match, return the first intent with highest score
        return top_intents[0]
    
    def train(self, training_data):
        """
        Train the intent classifier model.
        
        Args:
            training_data: A list of (text, intent) tuples
            
        Returns:
            None
        """
        # This would be implemented for a real model but is a placeholder here
        if not hasattr(self, 'has_transformer_model') or not self.has_transformer_model:
            print("Transformer model not available for training")
            return
        
        # Training code would go here
        pass