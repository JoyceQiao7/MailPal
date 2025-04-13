from transformers import pipeline
from config import Config

class ToneRefiner:
    def __init__(self):
        self.generator = pipeline('text-generation', model=Config.TRANSFORMER_MODEL)

    def merge_user_instructions(self, context_info, user_instruction):
        base_tone = context_info['tone']
        if user_instruction:
            return f"{base_tone}, {user_instruction}"
        return base_tone

    def refine_email(self, email_data, context_info, user_instruction):
        refined_tone = self.merge_user_instructions(context_info, user_instruction)
        prompt = (
            f"Rewrite the following email for a {context_info['intent']} purpose with a tone that is {refined_tone}:\n\n"
            f"Subject: {email_data['subject']}\n"
            f"Body: {email_data['content']}"
        )

        # Generate refined text
        result = self.generator(prompt, max_length=200, num_return_sequences=1)[0]
        refined_text = result['generated_text'].split('\n\n')[-1]  # Extract the rewritten body

        return refined_text