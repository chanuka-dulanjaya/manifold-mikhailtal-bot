"""
Market analysis utilities
Helper functions for analyzing market data
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def calculate_volatility(probability_history: List[Dict]) -> float:
    """
    Calculate probability volatility
    
    Args:
        probability_history: List of probability data points
    
    Returns:
        Volatility measure (0-1)
    """
    if len(probability_history) < 2:
        return 0.0
    
    # Calculate standard deviation of probability changes
    changes = []
    for i in range(1, len(probability_history)):
        change = abs(
            probability_history[i].get('probability', 0.5) - 
            probability_history[i-1].get('probability', 0.5)
        )
        changes.append(change)
    
    if not changes:
        return 0.0
    
    mean_change = sum(changes) / len(changes)
    variance = sum((c - mean_change) ** 2 for c in changes) / len(changes)
    volatility = variance ** 0.5
    
    return volatility


def calculate_liquidity_score(market: Dict[str, Any]) -> float:
    """
    Calculate market liquidity score (0-1)
    
    Args:
        market: Market data dictionary
    
    Returns:
        Liquidity score
    """
    pool = market.get('pool', {})
    yes_pool = pool.get('YES', 0)
    no_pool = pool.get('NO', 0)
    total_liquidity = yes_pool + no_pool
    
    volume = market.get('volume', 0)
    num_traders = market.get('uniqueBettorCount', 0)
    
    # Normalize factors
    liquidity_factor = min(1.0, total_liquidity / 1000)
    volume_factor = min(1.0, volume / 5000)
    trader_factor = min(1.0, num_traders / 50)
    
    # Weighted score
    score = (
        liquidity_factor * 0.4 +
        volume_factor * 0.3 +
        trader_factor * 0.3
    )
    
    return score


def calculate_market_efficiency(market: Dict[str, Any], history: List[Dict]) -> float:
    """
    Estimate market efficiency (how well-priced it is)
    
    Args:
        market: Current market data
        history: Probability history
    
    Returns:
        Efficiency score (0-1), higher = more efficient
    """
    num_traders = market.get('uniqueBettorCount', 0)
    volume = market.get('volume', 0)
    volatility = calculate_volatility(history)
    
    # More traders and volume = more efficient
    # Lower volatility = more stable/efficient
    
    trader_factor = min(1.0, num_traders / 30)
    volume_factor = min(1.0, volume / 3000)
    stability_factor = max(0.0, 1.0 - volatility * 5)
    
    efficiency = (
        trader_factor * 0.4 +
        volume_factor * 0.3 +
        stability_factor * 0.3
    )
    
    return min(1.0, max(0.0, efficiency))


def get_time_to_close(market: Dict[str, Any]) -> Optional[int]:
    """
    Get time remaining until market closes (in hours)
    
    Args:
        market: Market data dictionary
    
    Returns:
        Hours until close, or None if no close time
    """
    close_time = market.get('closeTime')
    if not close_time:
        return None
    
    # close_time is in milliseconds
    close_datetime = datetime.fromtimestamp(close_time / 1000)
    now = datetime.now()
    
    time_delta = close_datetime - now
    hours = time_delta.total_seconds() / 3600
    
    return max(0, hours)


def categorize_market(market: Dict[str, Any]) -> str:
    """
    Categorize market by characteristics
    
    Args:
        market: Market data dictionary
    
    Returns:
        Category string
    """
    num_traders = market.get('uniqueBettorCount', 0)
    volume = market.get('volume', 0)
    probability = market.get('probability', 0.5)
    
    # Categorize by activity level
    if num_traders < 5 and volume < 500:
        activity = "low"
    elif num_traders < 20 and volume < 2000:
        activity = "medium"
    else:
        activity = "high"
    
    # Categorize by probability
    if probability < 0.3:
        certainty = "unlikely"
    elif probability < 0.7:
        certainty = "uncertain"
    else:
        certainty = "likely"
    
    return f"{activity}-activity-{certainty}"


def extract_market_features(market: Dict[str, Any], history: List[Dict]) -> Dict[str, Any]:
    """
    Extract useful features from market data
    
    Args:
        market: Market data dictionary
        history: Probability history
    
    Returns:
        Dictionary of extracted features
    """
    return {
        'id': market.get('id'),
        'question': market.get('question'),
        'probability': market.get('probability', 0.5),
        'volume': market.get('volume', 0),
        'liquidity': calculate_liquidity_score(market),
        'num_traders': market.get('uniqueBettorCount', 0),
        'volatility': calculate_volatility(history),
        'efficiency': calculate_market_efficiency(market, history),
        'time_to_close': get_time_to_close(market),
        'category': categorize_market(market),
    }