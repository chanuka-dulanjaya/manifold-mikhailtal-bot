"""
Contrarian Trading Strategy
Bets against extreme probabilities, looking for mean reversion
"""
from typing import Dict, Any, Optional, List
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from strategies.base_strategy import BaseStrategy, StrategySignal

logger = logging.getLogger(__name__)


class ContrarianStrategy(BaseStrategy):
    """Strategy that fades extreme probabilities"""
    
    def __init__(self, **kwargs):
        # Extract contrarian-specific config
        self.extreme_threshold_high = kwargs.pop('extreme_threshold_high', 0.85)
        self.extreme_threshold_low = kwargs.pop('extreme_threshold_low', 0.15)
        self.reversion_target = kwargs.pop('reversion_target', 0.5)
        
        # Initialize parent
        super().__init__(name='Contrarian', **kwargs)
    
    def analyze(self, market: Dict[str, Any], **kwargs) -> Optional[StrategySignal]:
        """Look for extreme probabilities to fade"""
        
        current_prob = market.get('probability', 0.5)
        volume = market.get('volume', 0)
        num_traders = market.get('uniqueBettorCount', 0)
        
        # Need reasonable market participation for contrarian bets
        if num_traders < 3:
            return None
        
        # Check for extreme high probability
        if current_prob >= self.extreme_threshold_high:
            # Bet NO (against the crowd)
            estimated_prob = self._calculate_reversion_target(current_prob, 'high')
            confidence = self._calculate_confidence(current_prob, volume, num_traders, 'high')
            strength = (current_prob - self.extreme_threshold_high) * confidence
            
            reasoning = (
                f"Market at extreme high probability ({current_prob:.1%}). "
                f"Expect mean reversion. {num_traders} traders may be overconfident. "
                f"Historical patterns suggest reversion toward {estimated_prob:.1%}."
            )
            
            return StrategySignal(
                probability=estimated_prob,
                confidence=confidence,
                direction='NO',
                reasoning=reasoning,
                strength=min(1.0, strength)
            )
        
        # Check for extreme low probability
        elif current_prob <= self.extreme_threshold_low:
            # Bet YES (against the crowd)
            estimated_prob = self._calculate_reversion_target(current_prob, 'low')
            confidence = self._calculate_confidence(current_prob, volume, num_traders, 'low')
            strength = (self.extreme_threshold_low - current_prob) * confidence
            
            reasoning = (
                f"Market at extreme low probability ({current_prob:.1%}). "
                f"Expect mean reversion. {num_traders} traders may be overly pessimistic. "
                f"Historical patterns suggest reversion toward {estimated_prob:.1%}."
            )
            
            return StrategySignal(
                probability=estimated_prob,
                confidence=confidence,
                direction='YES',
                reasoning=reasoning,
                strength=min(1.0, strength)
            )
        
        # Not extreme enough
        return None
    
    def _calculate_reversion_target(self, current_prob: float, extreme_type: str) -> float:
        """Calculate expected reversion target"""
        
        # Partial reversion toward mean
        reversion_strength = 0.3  # 30% reversion
        
        if extreme_type == 'high':
            # Revert from high toward mean
            target = current_prob - (current_prob - self.reversion_target) * reversion_strength
        else:
            # Revert from low toward mean
            target = current_prob + (self.reversion_target - current_prob) * reversion_strength
        
        return max(0.05, min(0.95, target))
    
    def _calculate_confidence(
        self,
        current_prob: float,
        volume: float,
        num_traders: int,
        extreme_type: str
    ) -> float:
        """Calculate confidence in the contrarian signal"""
        
        # Base confidence on how extreme the probability is
        if extreme_type == 'high':
            extremeness = (current_prob - self.extreme_threshold_high) / (1.0 - self.extreme_threshold_high)
        else:
            extremeness = (self.extreme_threshold_low - current_prob) / self.extreme_threshold_low
        
        extremeness = max(0, min(1, extremeness))
        
        # More confidence with more market participation
        # But not too much - we want to fade the crowd
        participation_factor = min(1.0, num_traders / 10)
        
        # Lower confidence with very high volume (harder to move market)
        volume_factor = max(0.3, 1.0 - min(1.0, volume / 10000))
        
        confidence = extremeness * 0.5 + participation_factor * 0.3 + volume_factor * 0.2
        
        return max(0.2, min(0.8, confidence))
    
    def should_trade(self, market: Dict[str, Any], signal: StrategySignal) -> bool:
        """Override to add contrarian-specific logic"""
        
        if not super().should_trade(market, signal):
            return False
        
        # Contrarian trades need higher confidence since we're betting against consensus
        if signal.confidence < 0.4:
            return False
        
        # Need minimum signal strength
        if signal.strength < 0.3:
            return False
        
        return True