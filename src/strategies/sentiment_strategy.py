"""
Sentiment Trading Strategy
Analyzes comment sentiment and trading activity patterns
"""
from typing import Dict, Any, Optional, List
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from strategies.base_strategy import BaseStrategy, StrategySignal

logger = logging.getLogger(__name__)


class SentimentStrategy(BaseStrategy):
    """Strategy that analyzes market sentiment from comments and activity"""
    
    def __init__(self, **kwargs):
        # Extract sentiment-specific config
        self.min_comments = kwargs.pop('min_comments', 3)
        self.sentiment_threshold = kwargs.pop('sentiment_threshold', 0.6)
        
        # Initialize parent
        super().__init__(name='Sentiment Analyzer', **kwargs)
    
    def analyze(self, market: Dict[str, Any], **kwargs) -> Optional[StrategySignal]:
        """Analyze sentiment from comments and trading activity"""
        
        comments = kwargs.get('comments', [])
        bets = kwargs.get('bets', [])
        
        if len(comments) < self.min_comments:
            logger.debug(f"Insufficient comments for sentiment analysis: {len(comments)}")
            return None
        
        # Analyze comment sentiment
        comment_sentiment = self._analyze_comment_sentiment(comments)
        
        # Analyze trading activity sentiment
        trading_sentiment = self._analyze_trading_sentiment(bets)
        
        # Combine sentiments
        combined_sentiment = (comment_sentiment * 0.6 + trading_sentiment * 0.4)
        
        current_prob = market.get('probability', 0.5)
        
        # Check if sentiment diverges significantly from market price
        sentiment_prob = combined_sentiment
        divergence = abs(sentiment_prob - current_prob)
        
        if divergence < 0.10:  # Not enough divergence
            return None
        
        # Determine direction
        if sentiment_prob > current_prob:
            direction = 'YES'
            estimated_prob = min(0.95, current_prob + divergence * 0.5)
        else:
            direction = 'NO'
            estimated_prob = max(0.05, current_prob - divergence * 0.5)
        
        # Confidence based on comment count and sentiment strength
        confidence = self._calculate_confidence(len(comments), len(bets), divergence)
        
        reasoning = (
            f"Sentiment analysis: {sentiment_prob:.1%} (comments: {comment_sentiment:.1%}, "
            f"trading: {trading_sentiment:.1%}). Market at {current_prob:.1%}. "
            f"Divergence: {divergence:.1%}."
        )
        
        return StrategySignal(
            probability=estimated_prob,
            confidence=confidence,
            direction=direction,
            reasoning=reasoning,
            strength=min(1.0, divergence * 2)
        )
    
    def _analyze_comment_sentiment(self, comments: List[Dict]) -> float:
        """
        Analyze sentiment from comments
        
        This is a simplified version. In production, would use:
        - NLP sentiment analysis (TextBlob, VADER, or transformer models)
        - Named entity recognition
        - Argument mining
        """
        
        if not comments:
            return 0.5
        
        # Simple keyword-based sentiment (demonstration only)
        positive_keywords = [
            'yes', 'definitely', 'likely', 'probable', 'confident', 'will',
            'expect', 'sure', 'positive', 'bullish', 'agree', 'correct'
        ]
        
        negative_keywords = [
            'no', 'unlikely', 'doubtful', 'won\'t', 'impossible', 'bearish',
            'disagree', 'wrong', 'negative', 'won\'t happen', 'improbable'
        ]
        
        sentiment_scores = []
        
        for comment in comments[-20:]:  # Look at recent 20 comments
            text = comment.get('text', '').lower()
            
            pos_count = sum(1 for word in positive_keywords if word in text)
            neg_count = sum(1 for word in negative_keywords if word in text)
            
            if pos_count > 0 or neg_count > 0:
                # Normalize to 0-1 range
                score = (pos_count) / (pos_count + neg_count + 1)
                sentiment_scores.append(score)
        
        if not sentiment_scores:
            return 0.5
        
        # Average sentiment
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        
        return avg_sentiment
    
    def _analyze_trading_sentiment(self, bets: List[Dict]) -> float:
        """Analyze sentiment from recent trading activity"""
        
        if not bets:
            return 0.5
        
        # Look at recent bets (last 20)
        recent_bets = bets[:20]
        
        yes_volume = sum(bet.get('amount', 0) for bet in recent_bets if bet.get('outcome') == 'YES')
        no_volume = sum(bet.get('amount', 0) for bet in recent_bets if bet.get('outcome') == 'NO')
        
        total_volume = yes_volume + no_volume
        
        if total_volume == 0:
            return 0.5
        
        # Sentiment based on volume distribution
        sentiment = yes_volume / total_volume
        
        return sentiment
    
    def _calculate_confidence(
        self,
        num_comments: int,
        num_bets: int,
        divergence: float
    ) -> float:
        """Calculate confidence in sentiment signal"""
        
        # More comments = higher confidence
        comment_factor = min(1.0, num_comments / 10)
        
        # More bets = higher confidence
        bet_factor = min(1.0, num_bets / 20)
        
        # Larger divergence = higher confidence
        divergence_factor = min(1.0, divergence * 2)
        
        confidence = (comment_factor * 0.4 + bet_factor * 0.3 + divergence_factor * 0.3)
        
        return max(0.2, min(0.8, confidence))