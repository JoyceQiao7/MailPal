class RefinementProcessor:
    """
    Module responsible for processing user-directed refinement instructions.
    """
    
    def __init__(self):
        """Initialize the RefinementProcessor module."""
        # Dictionary of common refinement terms and their corresponding tone adjustments
        self.refinement_terms = {
            'formal': 'formal and professional',
            'professional': 'business-appropriate and polished',
            'friendly': 'warm and personable',
            'casual': 'relaxed and conversational',
            'concise': 'brief and to the point',
            'detailed': 'thorough and comprehensive',
            'persuasive': 'compelling and convincing',
            'assertive': 'confident and direct',
            'humble': 'modest and respectful',
            'enthusiastic': 'excited and positive',
            'urgent': 'time-sensitive and pressing',
            'empathetic': 'understanding and compassionate',
            'appreciative': 'grateful and thankful',
            'considerate': 'thoughtful and respectful',
            'apologetic': 'regretful and remorseful',
            'firm': 'resolute and unwavering',
            'diplomatic': 'tactful and sensitive',
            'respectful': 'courteous and deferential',
            'clear': 'straightforward and unambiguous',
            'encouraging': 'supportive and motivating'
        }
    
    def merge_user_instructions(self, context_info, user_instruction):
        """
        Merge the context-inferred tone with user instructions.
        
        Args:
            context_info: A dictionary containing the context analysis results
            user_instruction: The user's refinement instruction(s)
            
        Returns:
            A refined tone instruction for the AI model
        """
        # Get the inferred tone from context
        inferred_tone = context_info.get('tone', 'professional')
        
        # If no user instruction, return the inferred tone
        if not user_instruction:
            return inferred_tone
        
        # Parse user instructions
        tone_adjustments = self._parse_instructions(user_instruction)
        
        # If tone adjustments found, combine with inferred tone
        if tone_adjustments:
            return f"{inferred_tone}, while also being {', '.join(tone_adjustments)}"
        else:
            # If no recognized tone adjustments, append the raw instruction
            return f"{inferred_tone}, {user_instruction}"
    
    def _parse_instructions(self, user_instruction):
        """
        Parse user instructions to identify tone adjustments.
        
        Args:
            user_instruction: The user's refinement instruction(s)
            
        Returns:
            A list of identified tone adjustments
        """
        # Convert to lowercase for matching
        instruction_lower = user_instruction.lower()
        
        # List to store identified tone adjustments
        tone_adjustments = []
        
        # Look for known refinement terms
        for term, adjustment in self.refinement_terms.items():
            # Check if the term is in the instruction
            if term in instruction_lower:
                # For "more X" or "less X" patterns, adjust accordingly
                if f"more {term}" in instruction_lower:
                    tone_adjustments.append(f"more {adjustment}")
                elif f"less {term}" in instruction_lower:
                    tone_adjustments.append(f"less {adjustment}")
                else:
                    tone_adjustments.append(adjustment)
        
        # Look for "be more X" or "be less X" patterns
        be_more_match = re.search(r'be more (\w+)', instruction_lower)
        if be_more_match:
            tone_adjustments.append(f"more {be_more_match.group(1)}")
        
        be_less_match = re.search(r'be less (\w+)', instruction_lower)
        if be_less_match:
            tone_adjustments.append(f"less {be_less_match.group(1)}")
        
        return tone_adjustments