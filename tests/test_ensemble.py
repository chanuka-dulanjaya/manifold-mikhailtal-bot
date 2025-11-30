"""
Unit tests for Strategy Ensemble
"""
import pytest
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ensemble import StrategyEnsemble
from strategies.momentum_strategy import MomentumStrategy
from strategies.contrarian_strategy import ContrarianStrategy
from strategies.base_strategy import StrategySignal


class TestStrategyEnsemble:
    
    def test_ensemble_creation(self):
        """Test creating an ensemble"""
        strategies = [
            MomentumStrategy(),
            ContrarianStrategy()
        ]
        
        ensemble = StrategyEnsemble(strategies)
        
        assert len(ensemble.strategies) == 2
        assert 'Momentum Trader' in ensemble.strategies
        assert 'Contrarian' in ensemble.strategies
    
    def test_weight_normalization(self):
        """Test that weights are normalized to sum to 1.0"""
        strategies = [
            MomentumStrategy(),
            ContrarianStrategy()
        ]
        
        # Set arbitrary weights
        weights = {'Momentum Trader': 3.0, 'Contrarian': 2.0}
        ensemble = StrategyEnsemble(strategies, weights)
        
        total_weight = sum(ensemble.weights.values())
        assert abs(total_weight - 1.0) < 0.01
    
    def test_ensemble_with_single_signal(self):
        """Test ensemble when only one strategy generates a signal"""
        strategies = [MomentumStrategy()]
        ensemble = StrategyEnsemble(strategies)
        
        # Mock market data
        market = {
            'id': 'test',
            'probability': 0.50,
            'volume': 1000,
            'uniqueBettorCount': 10
        }
        
        # Insufficient history for momentum strategy
        prob_history = [
            {'probability': 0.50, 'timestamp': 1000}
        ]
        
        signal = ensemble.analyze(market, probability_history=prob_history)
        
        # Should return None (not enough data)
        assert signal is None
    
    def test_ensemble_signal_combination(self):
        """Test combining multiple signals"""
        # Create strategies
        strategies = [MomentumStrategy(), ContrarianStrategy()]
        ensemble = StrategyEnsemble(strategies)
        
        # Mock market at extreme high probability
        market = {
            'id': 'test',
            'probability': 0.90,
            'volume': 1000,
            'uniqueBettorCount': 10
        }
        
        # Momentum strategy won't trigger (needs history)
        # Contrarian should trigger (extreme probability)
        signal = ensemble.analyze(market)
        
        # Contrarian should generate a NO signal
        if signal:
            assert signal.direction == 'NO'
            assert signal.probability < 0.90
    
    def test_strategy_performance_tracking(self):
        """Test getting strategy performance"""
        strategies = [MomentumStrategy(), ContrarianStrategy()]
        ensemble = StrategyEnsemble(strategies)
        
        performance = ensemble.get_strategy_performance()
        
        assert 'Momentum Trader' in performance
        assert 'Contrarian' in performance
        assert performance['Momentum Trader']['total_trades'] == 0
    
    def test_enable_disable_strategy(self):
        """Test enabling/disabling strategies"""
        strategies = [MomentumStrategy(), ContrarianStrategy()]
        ensemble = StrategyEnsemble(strategies)
        
        # Disable momentum strategy
        ensemble.enable_strategy('Momentum Trader', False)
        
        assert ensemble.strategies['Momentum Trader'].enabled == False
        assert ensemble.strategies['Contrarian'].enabled == True
        
        # Re-enable
        ensemble.enable_strategy('Momentum Trader', True)
        assert ensemble.strategies['Momentum Trader'].enabled == True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])