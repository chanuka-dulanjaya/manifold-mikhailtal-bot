"""
Momentum Trading Strategy
Follows probability trends and momentum indicators
"""
from typing import Dict, Any, Optional, List
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from strategies.base_strategy import BaseStrategy, StrategySignal

logger = logging.getLogger(__name__)


class MomentumStrategy(BaseStrategy):
    """Strategy that follows probability momentum and trends"""
    
    def __init__(self, **kwargs):
        # Extract momentum-specific config
        self.lookback_periods = kwargs.pop('lookback_periods', [5, 10, 20])
        self.rsi_period = kwargs.pop('rsi_period', 14)
        self.momentum_threshold = kwargs.pop('momentum_threshold', 0.05)
        
        # Initialize parent
        super().__init__(name='Momentum Trader', **kwargs)
    
    def analyze(self, market: Dict[str, Any], **kwargs) -> Optional[StrategySignal]:
        """Analyze market momentum"""
        
        # Get probability history
        prob_history = kwargs.get('probability_history', [])
        
        if len(prob_history) < max(self.lookback_periods):
            logger.debug(f"Insufficient history for momentum analysis: {len(prob_history)} points")
            return None
        
        current_prob = market.get('probability', 0.5)
        
        # Calculate momentum indicators
        momentum_score = self._calculate_momentum(prob_history)
        rsi = self._calculate_rsi(prob_history)
        trend_strength = self._calculate_trend_strength(prob_history)
        
        # Determine signal
        if momentum_score > self.momentum_threshold and rsi < 70:
            # Upward momentum, not overbought
            direction = 'YES'
            estimated_prob = min(0.95, current_prob + momentum_score)
            confidence = min(1.0, trend_strength * 0.8)
            strength = min(1.0, momentum_score * trend_strength)
            
            reasoning = (
                f"Strong upward momentum detected ({momentum_score:.2%}). "
                f"RSI at {rsi:.1f} indicates room for growth. "
                f"Trend strength: {trend_strength:.2f}."
            )
            
        elif momentum_score < -self.momentum_threshold and rsi > 30:
            # Downward momentum, not oversold
            direction = 'NO'
            estimated_prob = max(0.05, current_prob + momentum_score)
            confidence = min(1.0, trend_strength * 0.8)
            strength = min(1.0, abs(momentum_score) * trend_strength)
            
            reasoning = (
                f"Strong downward momentum detected ({momentum_score:.2%}). "
                f"RSI at {rsi:.1f} indicates further decline possible. "
                f"Trend strength: {trend_strength:.2f}."
            )
        else:
            # No clear momentum signal
            return None
        
        return StrategySignal(
            probability=estimated_prob,
            confidence=confidence,
            direction=direction,
            reasoning=reasoning,
            strength=strength
        )
    
    def _calculate_momentum(self, history: List[Dict]) -> float:
        """Calculate probability momentum across multiple timeframes"""
        
        if not history:
            return 0.0
        
        current_prob = history[-1].get('probability', 0.5)
        momentum_scores = []
        
        for period in self.lookback_periods:
            if len(history) >= period:
                past_prob = history[-period].get('probability', current_prob)
                momentum = (current_prob - past_prob) / max(period, 1)
                momentum_scores.append(momentum)
        
        # Weighted average favoring shorter timeframes
        if momentum_scores:
            weights = [1 / (i + 1) for i in range(len(momentum_scores))]
            weighted_momentum = sum(m * w for m, w in zip(momentum_scores, weights)) / sum(weights)
            return weighted_momentum
        
        return 0.0
    
    def _calculate_rsi(self, history: List[Dict], period: int = None) -> float:
        """Calculate Relative Strength Index"""
        
        if period is None:
            period = self.rsi_period
        
        if len(history) < period + 1:
            return 50.0  # Neutral RSI
        
        # Get probability changes
        changes = []
        for i in range(len(history) - period, len(history)):
            if i > 0:
                change = history[i].get('probability', 0.5) - history[i-1].get('probability', 0.5)
                changes.append(change)
        
        if not changes:
            return 50.0
        
        # Calculate gains and losses
        gains = [c for c in changes if c > 0]
        losses = [-c for c in changes if c < 0]
        
        avg_gain = sum(gains) / period if gains else 0
        avg_loss = sum(losses) / period if losses else 0
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_trend_strength(self, history: List[Dict]) -> float:
        """Calculate overall trend strength (0-1)"""
        
        if len(history) < 2:
            return 0.0
        
        # Linear regression to find trend
        n = len(history)
        x = list(range(n))
        y = [h.get('probability', 0.5) for h in history]
        
        # Calculate slope
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        
        # Calculate R-squared
        y_pred = [y_mean + slope * (x[i] - x_mean) for i in range(n)]
        ss_res = sum((y[i] - y_pred[i]) ** 2 for i in range(n))
        ss_tot = sum((y[i] - y_mean) ** 2 for i in range(n))
        
        if ss_tot == 0:
            return 0.0
        
        r_squared = 1 - (ss_res / ss_tot)
        
        # Trend strength is R-squared (how well data fits the trend)
        return max(0.0, min(1.0, r_squared))