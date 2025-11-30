"""
LLM-Powered Trading Strategy
Uses Claude to analyze market questions and estimate probabilities
"""
from typing import Dict, Any, Optional
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from strategies.base_strategy import BaseStrategy, StrategySignal

logger = logging.getLogger(__name__)

try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    logger.warning("Anthropic package not installed. LLM strategy will be disabled.")


class LLMStrategy(BaseStrategy):
    """Strategy that uses Claude to analyze markets"""
    
    def __init__(self, api_key: str = None, model: str = 'claude-sonnet-4-20250514', **kwargs):
        # Extract config before passing to parent
        self.model = model
        self.max_tokens = kwargs.pop('max_tokens', 1000)
        self.temperature = kwargs.pop('temperature', 0.7)
        
        # Initialize parent class
        super().__init__(name='LLM Analyst', **kwargs)
        
        if HAS_ANTHROPIC and api_key:
            self.client = Anthropic(api_key=api_key)
            self.enabled = True
        else:
            self.client = None
            self.enabled = False
            if not api_key:
                logger.warning("No Anthropic API key provided. LLM strategy disabled.")
    
    def analyze(self, market: Dict[str, Any], **kwargs) -> Optional[StrategySignal]:
        """Use Claude to analyze the market question"""
        
        if not self.enabled or not self.client:
            return None
        
        try:
            # Prepare the prompt
            question = market.get('question', '')
            description = market.get('description', '')
            current_prob = market.get('probability', 0.5)
            close_time = market.get('closeTime')
            
            prompt = self._build_prompt(
                question=question,
                description=description,
                current_prob=current_prob,
                close_time=close_time
            )
            
            # Call Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Parse response
            signal = self._parse_response(response.content[0].text, current_prob)
            return signal
            
        except Exception as e:
            error_msg = str(e)
            
            # Check if it's an authentication error
            if 'authentication_error' in error_msg or '401' in error_msg:
                logger.warning("LLM strategy disabled: Invalid Anthropic API key. Add a valid key to .env to enable.")
                self.enabled = False  # Disable strategy to prevent repeated errors
                return None
            
            logger.error(f"Error in LLM analysis: {error_msg}")
            return None
    
    def _build_prompt(
        self,
        question: str,
        description: str,
        current_prob: float,
        close_time: int
    ) -> str:
        """Build prompt for Claude"""
        
        return f"""You are an expert prediction market analyst. Analyze this prediction market question and provide your assessment.

QUESTION: {question}

DESCRIPTION: {description[:500] if description else 'No description provided'}

CURRENT MARKET PROBABILITY: {current_prob:.1%}

Your task is to estimate the TRUE probability of this event occurring. Consider:
1. Base rates and historical precedents
2. The specific resolution criteria
3. Time horizon until resolution
4. Any logical or statistical reasoning
5. Potential biases in the current market price

Respond in this exact format:

PROBABILITY: [your probability estimate as a number between 0 and 1]
CONFIDENCE: [your confidence in this estimate, 0 to 1]
DIRECTION: [YES or NO - which direction you'd bet]
REASONING: [2-3 sentences explaining your estimate]
STRENGTH: [signal strength 0 to 1, how strongly you feel about this trade]

Example response:
PROBABILITY: 0.65
CONFIDENCE: 0.75
DIRECTION: YES
REASONING: Historical data shows this type of event occurs 60-70% of the time. The current market is underpricing this due to recency bias. The resolution criteria are clear and favor a YES outcome.
STRENGTH: 0.8

Now analyze the question above:"""
    
    def _parse_response(self, response: str, current_prob: float) -> Optional[StrategySignal]:
        """Parse Claude's response into a StrategySignal"""
        
        try:
            lines = response.strip().split('\n')
            parsed = {}
            
            for line in lines:
                line = line.strip()
                if line.startswith('PROBABILITY:'):
                    prob_str = line.split(':', 1)[1].strip()
                    parsed['probability'] = float(prob_str)
                elif line.startswith('CONFIDENCE:'):
                    conf_str = line.split(':', 1)[1].strip()
                    parsed['confidence'] = float(conf_str)
                elif line.startswith('DIRECTION:'):
                    dir_str = line.split(':', 1)[1].strip().upper()
                    parsed['direction'] = dir_str
                elif line.startswith('REASONING:'):
                    reasoning_str = line.split(':', 1)[1].strip()
                    parsed['reasoning'] = reasoning_str
                elif line.startswith('STRENGTH:'):
                    strength_str = line.split(':', 1)[1].strip()
                    parsed['strength'] = float(strength_str)
            
            # Collect any reasoning that spans multiple lines
            reasoning_started = False
            full_reasoning = []
            for line in lines:
                if line.startswith('REASONING:'):
                    reasoning_started = True
                    full_reasoning.append(line.split(':', 1)[1].strip())
                elif reasoning_started and line.startswith('STRENGTH:'):
                    break
                elif reasoning_started and line.strip():
                    full_reasoning.append(line.strip())
            
            if full_reasoning:
                parsed['reasoning'] = ' '.join(full_reasoning)
            
            # Validate required fields
            required = ['probability', 'confidence', 'direction', 'reasoning']
            if not all(k in parsed for k in required):
                logger.error(f"Missing required fields in LLM response: {parsed.keys()}")
                return None
            
            # Use default strength if not provided
            if 'strength' not in parsed:
                # Calculate strength based on edge and confidence
                edge = abs(parsed['probability'] - current_prob)
                parsed['strength'] = min(1.0, edge * parsed['confidence'] * 2)
            
            return StrategySignal(**parsed)
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            logger.debug(f"Response was: {response}")
            return None