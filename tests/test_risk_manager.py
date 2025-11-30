"""
Unit tests for Risk Manager
"""
import pytest
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from risk_manager import RiskManager
from strategies.base_strategy import StrategySignal


class TestRiskManager:
    
    def test_risk_manager_creation(self):
        """Test creating a risk manager"""
        rm = RiskManager(
            max_bet_amount=100,
            min_bet_amount=10,
            kelly_fraction=0.25
        )
        
        assert rm.max_bet_amount == 100
        assert rm.min_bet_amount == 10
        assert rm.kelly_fraction == 0.25
    
    def test_bet_size_calculation_yes(self):
        """Test bet size calculation for YES bet"""
        rm = RiskManager(max_bet_amount=100, min_bet_amount=10)
        
        signal = StrategySignal(
            probability=0.70,
            confidence=0.80,
            direction='YES',
            reasoning='Test',
            strength=0.75
        )
        
        market = {
            'probability': 0.50,  # Market underpriced
            'volume': 1000
        }
        
        balance = 1000
        bet_size = rm.calculate_bet_size(signal, market, balance)
        
        # Should return a bet size
        assert bet_size is not None
        assert bet_size >= rm.min_bet_amount
        assert bet_size <= rm.max_bet_amount
    
    def test_bet_size_calculation_no(self):
        """Test bet size calculation for NO bet"""
        rm = RiskManager(max_bet_amount=100, min_bet_amount=10)
        
        signal = StrategySignal(
            probability=0.30,
            confidence=0.80,
            direction='NO',
            reasoning='Test',
            strength=0.75
        )
        
        market = {
            'probability': 0.50,  # Market overpriced
            'volume': 1000
        }
        
        balance = 1000
        bet_size = rm.calculate_bet_size(signal, market, balance)
        
        # Should return a bet size
        assert bet_size is not None
        assert bet_size >= rm.min_bet_amount
        assert bet_size <= rm.max_bet_amount
    
    def test_insufficient_edge(self):
        """Test that small edge doesn't trigger bet"""
        rm = RiskManager(max_bet_amount=100, min_bet_amount=10)
        
        signal = StrategySignal(
            probability=0.51,  # Only 1% edge
            confidence=0.80,
            direction='YES',
            reasoning='Test',
            strength=0.50
        )
        
        market = {
            'probability': 0.50,
            'volume': 1000
        }
        
        balance = 1000
        bet_size = rm.calculate_bet_size(signal, market, balance)
        
        # Should not bet with such small edge
        assert bet_size is None
    
    def test_low_confidence(self):
        """Test that low confidence reduces bet size"""
        rm = RiskManager(max_bet_amount=100, min_bet_amount=10)
        
        signal_high = StrategySignal(
            probability=0.70,
            confidence=0.90,
            direction='YES',
            reasoning='Test',
            strength=0.75
        )
        
        signal_low = StrategySignal(
            probability=0.70,
            confidence=0.30,
            direction='YES',
            reasoning='Test',
            strength=0.75
        )
        
        market = {
            'probability': 0.50,
            'volume': 1000
        }
        
        balance = 1000
        
        bet_high = rm.calculate_bet_size(signal_high, market, balance)
        bet_low = rm.calculate_bet_size(signal_low, market, balance)
        
        # Higher confidence should result in larger bet (or low conf returns None)
        if bet_low is not None:
            assert bet_high > bet_low
    
    def test_portfolio_risk_limits(self):
        """Test portfolio risk limits"""
        rm = RiskManager(
            max_bet_amount=100,
            max_portfolio_risk=0.30
        )
        
        # Add some positions
        rm.add_position({'market_id': 'market1', 'amount': 200})
        rm.add_position({'market_id': 'market2', 'amount': 100})
        
        balance = 1000
        
        # Should limit orders when at risk limit
        should_limit = rm.should_limit_orders(balance)
        
        # 300 / 1000 = 30% (at limit)
        assert should_limit == True
    
    def test_position_tracking(self):
        """Test adding and removing positions"""
        rm = RiskManager()
        
        assert len(rm.open_positions) == 0
        
        rm.add_position({'market_id': 'market1', 'amount': 100})
        assert len(rm.open_positions) == 1
        
        rm.add_position({'market_id': 'market2', 'amount': 50})
        assert len(rm.open_positions) == 2
        
        rm.remove_position('market1')
        assert len(rm.open_positions) == 1
        
        # Verify correct position was removed
        assert rm.open_positions[0]['market_id'] == 'market2'
    
    def test_portfolio_metrics(self):
        """Test portfolio metrics calculation"""
        rm = RiskManager()
        
        rm.add_position({'market_id': 'market1', 'amount': 100})
        rm.add_position({'market_id': 'market2', 'amount': 50})
        
        balance = 1000
        metrics = rm.get_portfolio_metrics(balance)
        
        assert metrics['total_exposure'] == 150
        assert metrics['exposure_ratio'] == 0.15
        assert metrics['num_positions'] == 2
        assert metrics['avg_position_size'] == 75
        assert metrics['available_capital'] == 850


if __name__ == '__main__':
    pytest.main([__file__, '-v'])