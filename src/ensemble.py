"""
Strategy Ensemble Manager
Combines multiple strategies with weighted voting
"""
from typing import List, Dict, Any, Optional
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from strategies.base_strategy import BaseStrategy, StrategySignal

logger = logging.getLogger(__name__)


class StrategyEnsemble:
    """Manages multiple strategies and combines their signals"""
    
    def __init__(self, strategies: List[BaseStrategy], weights: Dict[str, float] = None):
        self.strategies = {s.name: s for s in strategies}
        self.weights = weights or {s.name: 1.0 / len(strategies) for s in strategies}
        self._normalize_weights()
    
    def _normalize_weights(self):
        """Normalize weights to sum to 1.0"""
        total = sum(self.weights.values())
        if total > 0:
            self.weights = {k: v / total for k, v in self.weights.items()}
    
    def analyze(self, market: Dict[str, Any], **kwargs) -> Optional[StrategySignal]:
        """Get signals from all strategies and combine them"""
        
        signals = {}
        
        # Collect signals from all enabled strategies
        for name, strategy in self.strategies.items():
            if not strategy.enabled:
                continue
            
            try:
                signal = strategy.analyze(market, **kwargs)
                if signal:
                    signals[name] = signal
                    logger.debug(f"{name} signal: {signal.direction} @ {signal.probability:.2%} "
                               f"(confidence: {signal.confidence:.2%})")
            except Exception as e:
                logger.error(f"Error in {name} strategy: {e}")
        
        if not signals:
            return None
        
        # Combine signals using weighted voting
        combined_signal = self._combine_signals(signals)
        
        return combined_signal
    
    def _combine_signals(self, signals: Dict[str, StrategySignal]) -> Optional[StrategySignal]:
        """Combine multiple signals into one consensus signal"""
        
        if not signals:
            return None
        
        # Weighted probability estimate
        total_weight = 0
        weighted_prob = 0
        weighted_confidence = 0
        
        yes_votes = 0
        no_votes = 0
        
        for name, signal in signals.items():
            weight = self.weights.get(name, 0) * signal.confidence
            total_weight += weight
            
            weighted_prob += signal.probability * weight
            weighted_confidence += signal.confidence * weight
            
            if signal.direction == 'YES':
                yes_votes += weight
            else:
                no_votes += weight
        
        if total_weight == 0:
            return None
        
        # Calculate consensus
        consensus_prob = weighted_prob / total_weight
        consensus_confidence = weighted_confidence / total_weight
        consensus_direction = 'YES' if yes_votes > no_votes else 'NO'
        
        # Calculate agreement strength
        agreement = abs(yes_votes - no_votes) / total_weight
        
        # Build reasoning
        reasoning_parts = []
        for name, signal in signals.items():
            weight_pct = self.weights.get(name, 0) * 100
            reasoning_parts.append(
                f"{name} ({weight_pct:.0f}%): {signal.direction} @ {signal.probability:.1%}"
            )
        
        reasoning = "Ensemble: " + "; ".join(reasoning_parts)
        
        return StrategySignal(
            probability=consensus_prob,
            confidence=consensus_confidence,
            direction=consensus_direction,
            reasoning=reasoning,
            strength=agreement
        )
    
    def update_weights(self, performance_data: Dict[str, Dict]):
        """Update strategy weights based on performance"""
        
        # Calculate performance scores
        scores = {}
        for name, perf in performance_data.items():
            if name not in self.strategies:
                continue
            
            win_rate = perf.get('win_rate', 0)
            total_return = perf.get('total_return', 0)
            total_trades = perf.get('total_trades', 0)
            
            # Combined performance score
            if total_trades > 0:
                score = (win_rate * 0.6 + (total_return / total_trades) * 0.4)
                scores[name] = max(0.1, score)  # Minimum score of 0.1
            else:
                scores[name] = 0.5  # Default for strategies without history
        
        if scores:
            # Update weights based on scores
            total_score = sum(scores.values())
            if total_score > 0:
                self.weights = {name: score / total_score for name, score in scores.items()}
                logger.info(f"Updated strategy weights: {self.weights}")
    
    def get_strategy_performance(self) -> Dict[str, Dict]:
        """Get performance metrics for all strategies"""
        return {
            name: strategy.get_performance_metrics()
            for name, strategy in self.strategies.items()
        }
    
    def enable_strategy(self, name: str, enabled: bool = True):
        """Enable or disable a strategy"""
        if name in self.strategies:
            self.strategies[name].enabled = enabled
            logger.info(f"Strategy '{name}' {'enabled' if enabled else 'disabled'}")
    
    def __repr__(self) -> str:
        enabled_strategies = [name for name, s in self.strategies.items() if s.enabled]
        return f"<StrategyEnsemble with {len(enabled_strategies)} active strategies>"