import os
import json
import requests
from typing import Dict, Any

class AIEnhancer:
    """
    Module responsible for AI-driven tone and wording enhancement.
    """
    
    def __init__(self, api_key=None, model_name='gpt-4'):
        """
        Initialize the AIEnhancer module.
        
        Args:
            api_key: API key for the AI service
            model_name: Name of the AI model to use
        """
        self.api_key = api_key or os.environ.get('AI_API_KEY')
        self.model_name = model_name
        self.api_endpoint = "https://api.openai.com/v1/chat/completions"
    
    def refine_email_content(self, email_data, context_info, refined_tone):
        """
        Generate a refined version of the email based on context and tone.
        
        Args:
            email_data: A dictionary containing the email's subject and content
            context_info: A dictionary containing the context analysis results
            refined_tone: The refined tone instruction
            
        Returns:
            The refined email content
        """
        subject = email_data.get('subject', '')
        content = email_data.get('content', '')
        intent = context_info.get('intent', 'general')
        
        # Construct the prompt
        prompt = self._construct_prompt(subject, content, intent, refined_tone)
        
        # Generate the refined email
        refined_content = self._generate_text(prompt)
        
        return refined_content
    
    def _construct_prompt(self, subject, content, intent, refined_tone):
        """
        Construct a prompt for the AI model.
        
        Args:
            subject: The email subject
            content: The email content
            intent: The classified intent of the email
            refined_tone: The refined tone instruction
            
        Returns:
            A prompt for the AI model
        """
        return (
            f"You are an expert email editor who helps refine emails to make them more effective. "
            f"Please rewrite the following email with the subject line: '{subject}'\n\n"
            f"The email's purpose is {intent}, and it should have a tone that is {refined_tone}.\n\n"
            f"Original email content:\n\n{content}\n\n"
            f"Please provide an improved version that maintains the same information and intent, "
            f"but with refined language, tone, and structure. Keep the email concise and impactful."
        )
    
    def _generate_text(self, prompt):
        """
        Generate text using the AI model.
        
        Args:
            prompt: The prompt for the AI model
            
        Returns:
            The generated text
        """
        if not self.api_key:
            # For demonstration, return a mock response if no API key
            return f"[AI would generate a refined email here based on the provided prompt]"
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            response = requests.post(
                self.api_endpoint,
                headers=headers,
                data=json.dumps(data)
            )
            
            if response.status_code == 200:
                response_data = response.json()
                return response_data['choices'][0]['message']['content'].strip()
            else:
                print(f"Error from API: {response.status_code}")
                print(response.text)
                return f"Error generating refined email: {response.status_code}"
                
        except Exception as e:
            print(f"Error making API request: {e}")
            return f"Error generating refined email: {str(e)}"