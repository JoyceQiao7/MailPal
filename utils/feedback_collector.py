import json
import os
from datetime import datetime

class FeedbackCollector:
    """
    Utility class for collecting and storing user feedback.
    """
    
    def __init__(self, feedback_dir=None):
        """
        Initialize the FeedbackCollector.
        
        Args:
            feedback_dir: Directory to store feedback data
        """
        self.feedback_dir = feedback_dir or os.path.join(os.path.dirname(__file__), '../data/feedback')
        
        # Create feedback directory if it doesn't exist
        os.makedirs(self.feedback_dir, exist_ok=True)
    
    def store_feedback(self, feedback_data):
        """
        Store user feedback.
        
        Args:
            feedback_data: A dictionary containing feedback information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate a unique filename using timestamp
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            feedback_id = feedback_data.get('feedback_id', f'feedback_{timestamp}')
            
            # Create the full path for the feedback file
            file_path = os.path.join(self.feedback_dir, f'{feedback_id}.json')
            
            # Add timestamp to feedback data
            feedback_data['timestamp'] = datetime.now().isoformat()
            
            # Write feedback data to file
            with open(file_path, 'w') as f:
                json.dump(feedback_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error storing feedback: {e}")
            return False
    
    def get_feedback(self, feedback_id):
        """
        Retrieve specific feedback by ID.
        
        Args:
            feedback_id: The ID of the feedback to retrieve
            
        Returns:
            The feedback data if found, None otherwise
        """
        try:
            # Create the full path for the feedback file
            file_path = os.path.join(self.feedback_dir, f'{feedback_id}.json')
            
            # Check if the file exists
            if not os.path.exists(file_path):
                return None
            
            # Read and return the feedback data
            with open(file_path, 'r') as f:
                feedback_data = json.load(f)
            
            return feedback_data
            
        except Exception as e:
            print(f"Error retrieving feedback: {e}")
            return None
    
    def get_all_feedback(self, limit=None, sort_by_date=True):
        """
        Retrieve all feedback or a limited number of entries.
        
        Args:
            limit: Maximum number of feedback entries to retrieve
            sort_by_date: Whether to sort entries by date (newest first)
            
        Returns:
            A list of feedback data dictionaries
        """
        try:
            # Get all feedback files
            feedback_files = [f for f in os.listdir(self.feedback_dir) if f.endswith('.json')]
            
            # Sort files by creation time if requested
            if sort_by_date:
                feedback_files.sort(
                    key=lambda f: os.path.getmtime(os.path.join(self.feedback_dir, f)),
                    reverse=True
                )
            
            # Apply limit if specified
            if limit:
                feedback_files = feedback_files[:limit]
            
            # Read each file and collect feedback data
            feedback_list = []
            for file_name in feedback_files:
                file_path = os.path.join(self.feedback_dir, file_name)
                with open(file_path, 'r') as f:
                    feedback_data = json.load(f)
                    feedback_list.append(feedback_data)
            
            return feedback_list
            
        except Exception as e:
            print(f"Error retrieving all feedback: {e}")
            return []
    
    def analyze_feedback(self):
        """
        Analyze collected feedback for trends.
        
        Returns:
            A dictionary with feedback analysis results
        """
        try:
            # Get all feedback
            all_feedback = self.get_all_feedback()
            
            # Count total feedback entries
            total_entries = len(all_feedback)
            
            if total_entries == 0:
                return {'message': 'No feedback data available for analysis'}
            
            # Count positive, negative, and neutral feedback
            positive = sum(1 for f in all_feedback if f.get('rating', 0) > 3)
            negative = sum(1 for f in all_feedback if f.get('rating', 0) < 3)
            neutral = sum(1 for f in all_feedback if f.get('rating', 0) == 3)
            
            # Calculate percentages
            positive_percent = (positive / total_entries) * 100
            negative_percent = (negative / total_entries) * 100
            neutral_percent = (neutral / total_entries) * 100
            
            # Collect common feedback categories
            categories = {}
            for feedback in all_feedback:
                category = feedback.get('category', 'unknown')
                categories[category] = categories.get(category, 0) + 1
            
            # Return analysis results
            return {
                'total_entries': total_entries,
                'positive': positive,
                'negative': negative,
                'neutral': neutral,
                'positive_percent': positive_percent,
                'negative_percent': negative_percent,
                'neutral_percent': neutral_percent,
                'categories': categories
            }
            
        except Exception as e:
            print(f"Error analyzing feedback: {e}")
            return {'error': str(e)}