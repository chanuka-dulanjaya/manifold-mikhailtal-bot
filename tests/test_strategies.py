"""
Unit tests for trading strategies
"""
import pytest
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from strategies.base_strategy import StrategySignal
from strategies.momentum_strategy import MomentumStrategy
from strategies.contrarian_strategy import ContrarianStrategy


class TestMomentumStrategy:
    
    def test_upward_momentum(self):
        """Test detection of upward momentum"""
        strategy = MomentumStrategy()
        
        market = {
            'id': 'test_market',
            'question': 'Test question?',
            'probability': 0.65,
            'volume': 1000
        }
        
        # Create upward trending probability history
        prob_history = [
            {'probability': 0.50, 'timestamp': 1000},
            {'probability': 0.52, 'timestamp': 2000},
            {'probability': 0.55, 'timestamp': 3000},
            {'probability': 0.58, 'timestamp': 4000},
            {'probability': 0.60, 'timestamp': 5000},
            {'probability': 0.62, 'timestamp': 6000},
            {'probability': 0.65, 'timestamp': 7000},
        ]
        
        signal = strategy.analyze(market, probability_history=prob_history)
        
        assert signal is not None
        assert signal.direction == 'YES'
        assert signal.probability > market['probability']
        assert signal.confidence > 0
    
    def test_insufficient_history(self):
        """Test that strategy returns None with insufficient history"""
        strategy = MomentumStrategy()
        
        market = {
            'id': 'test_market',
            'probability': 0.50
        }
        
        prob_history = [
            {'probability': 0.50, 'timestamp': 1000},
            {'probability': 0.51, 'timestamp': 2000},
        ]
        
        signal = strategy.analyze(market, probability_history=prob_history)
        assert signal is None


class TestContrarianStrategy:
    
    def test_extreme_high_probability(self):
        """Test contrarian signal at extreme high probability"""
        strategy = ContrarianStrategy()
        
        market = {
            'id': 'test_market',
            'question': 'Test question?',
            'probability': 0.90,
            'volume': 1000,
            'uniqueBettorCount': 10
        }
        
        signal = strategy.analyze(market)
        
        assert signal is not None
        assert signal.direction == 'NO'
        assert signal.probability < market['probability']
    
    def test_extreme_low_probability(self):
        """Test contrarian signal at extreme low probability"""
        strategy = ContrarianStrategy()
        
        market = {
            'id': 'test_market',
            'question': 'Test question?',
            'probability': 0.10,
            'volume': 1000,
            'uniqueBettorCount': 10
        }
        
        signal = strategy.analyze(market)
        
        assert signal is not None
        assert signal.direction == 'YES'
        assert signal.probability > market['probability']
    
    def test_normal_probability(self):
        """Test that no signal is generated at normal probabilities"""
        strategy = ContrarianStrategy()
        
        market = {
            'id': 'test_market',
            'question': 'Test question?',
            'probability': 0.50,
            'volume': 1000,
            'uniqueBettorCount': 10
        }
        
        signal = strategy.analyze(market)
        assert signal is None


class TestStrategySignal:
    
    def test_weighted_probability(self):
        """Test weighted probability calculation"""
        signal = StrategySignal(
            probability=0.70,
            confidence=0.80,
            direction='YES',
            reasoning='Test',
            strength=0.75
        )
        
        assert signal.weighted_probability == 0.70 * 0.80
    
    def test_signal_creation(self):
        """Test creating a signal"""
        signal = StrategySignal(
            probability=0.65,
            confidence=0.75,
            direction='NO',
            reasoning='Market overvalued',
            strength=0.80
        )
        
        assert signal.probability == 0.65
        assert signal.confidence == 0.75
        assert signal.direction == 'NO'
        assert 'overvalued' in signal.reasoning.lower()
        assert signal.strength == 0.80


if __name__ == '__main__':
    pytest.main([__file__, '-v'])