"""
Risk Management Module
Handles position sizing and portfolio risk
"""
import logging
from typing import Dict, Any, Optional
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from strategies.base_strategy import StrategySignal

logger = logging.getLogger(__name__)


class RiskManager:
    """Manages trading risk and position sizing"""
    
    def __init__(
        self,
        max_bet_amount: float = 100,
        min_bet_amount: float = 10,
        kelly_fraction: float = 0.25,
        max_portfolio_risk: float = 0.30,
        risk_tolerance: float = 0.25
    ):
        self.max_bet_amount = max_bet_amount
        self.min_bet_amount = min_bet_amount
        self.kelly_fraction = kelly_fraction
        self.max_portfolio_risk = max_portfolio_risk
        self.risk_tolerance = risk_tolerance
        self.open_positions = []
    
    def calculate_bet_size(
        self,
        signal: StrategySignal,
        market: Dict[str, Any],
        balance: float
    ) -> Optional[float]:
        """
        Calculate optimal bet size using Kelly Criterion
        
        Args:
            signal: Trading signal with probability and confidence
            market: Market data
            balance: Current account balance
        
        Returns:
            Bet size in mana, or None if shouldn't bet
        """
        
        market_prob = market.get('probability', 0.5)
        estimated_prob = signal.probability
        
        # Calculate edge
        if signal.direction == 'YES':
            edge = estimated_prob - market_prob
            win_prob = estimated_prob
            lose_prob = 1 - estimated_prob
            win_odds = (1 - market_prob) / market_prob  # Payout ratio
        else:
            edge = market_prob - estimated_prob
            win_prob = 1 - estimated_prob
            lose_prob = estimated_prob
            win_odds = market_prob / (1 - market_prob)
        
        # Require minimum edge
        if edge < 0.05:
            logger.debug(f"Edge too small: {edge:.2%}")
            return None
        
        # Kelly Criterion: f = (p * odds - q) / odds
        # where p = win probability, q = lose probability, odds = win_odds
        kelly_fraction_full = (win_prob * win_odds - lose_prob) / win_odds
        
        if kelly_fraction_full <= 0:
            logger.debug(f"Kelly fraction negative: {kelly_fraction_full:.2%}")
            return None
        
        # Apply fractional Kelly for risk management
        kelly_bet = kelly_fraction_full * self.kelly_fraction * balance
        
        # Adjust for confidence
        confidence_adjusted_bet = kelly_bet * signal.confidence
        
        # Apply limits
        bet_size = max(self.min_bet_amount, min(self.max_bet_amount, confidence_adjusted_bet))
        
        # Check portfolio risk
        if not self._check_portfolio_risk(bet_size, balance):
            logger.warning(f"Bet size {bet_size} exceeds portfolio risk limits")
            # Reduce bet size to fit within limits
            max_additional_risk = self.max_portfolio_risk * balance - self._get_current_risk()
            bet_size = min(bet_size, max_additional_risk)
        
        # Final validation
        if bet_size < self.min_bet_amount:
            return None
        
        logger.info(
            f"Calculated bet size: {bet_size:.0f}M "
            f"(Kelly: {kelly_fraction_full:.1%}, "
            f"Edge: {edge:.1%}, "
            f"Confidence: {signal.confidence:.1%})"
        )
        
        return round(bet_size, 2)
    
    def _check_portfolio_risk(self, new_bet: float, balance: float) -> bool:
        """Check if new bet would exceed portfolio risk limits"""
        
        current_risk = self._get_current_risk()
        total_risk = current_risk + new_bet
        
        max_risk = self.max_portfolio_risk * balance
        
        return total_risk <= max_risk
    
    def _get_current_risk(self) -> float:
        """Calculate current portfolio risk"""
        return sum(pos.get('amount', 0) for pos in self.open_positions)
    
    def add_position(self, position: Dict[str, Any]):
        """Record a new open position"""
        self.open_positions.append(position)
    
    def remove_position(self, market_id: str):
        """Remove a closed position"""
        self.open_positions = [
            pos for pos in self.open_positions
            if pos.get('market_id') != market_id
        ]
    
    def get_portfolio_metrics(self, balance: float) -> Dict[str, float]:
        """Calculate portfolio risk metrics"""
        
        total_exposure = self._get_current_risk()
        num_positions = len(self.open_positions)
        
        return {
            'total_exposure': total_exposure,
            'exposure_ratio': total_exposure / balance if balance > 0 else 0,
            'num_positions': num_positions,
            'avg_position_size': total_exposure / num_positions if num_positions > 0 else 0,
            'available_capital': balance - total_exposure
        }
    
    def should_limit_orders(self, balance: float) -> bool:
        """Check if we should limit new orders due to risk"""
        
        metrics = self.get_portfolio_metrics(balance)
        
        # Limit orders if we're using too much capital
        if metrics['exposure_ratio'] > self.max_portfolio_risk:
            return True
        
        # Limit orders if we have too many positions
        if metrics['num_positions'] >= 20:  # Max positions
            return True
        
        return False