#!/usr/bin/env python3
"""
Simple test to verify bot components work
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_imports():
    """Test that all imports work"""
    print("Testing imports...")
    
    try:
        from strategies.base_strategy import BaseStrategy, StrategySignal
        print("✓ Base strategy imported")
    except ImportError as e:
        print(f"✗ Failed to import base strategy: {e}")
        return False
    
    try:
        from strategies.momentum_strategy import MomentumStrategy
        print("✓ Momentum strategy imported")
    except ImportError as e:
        print(f"✗ Failed to import momentum strategy: {e}")
        return False
    
    try:
        from strategies.contrarian_strategy import ContrarianStrategy
        print("✓ Contrarian strategy imported")
    except ImportError as e:
        print(f"✗ Failed to import contrarian strategy: {e}")
        return False
    
    try:
        from manifold_client import ManifoldClient
        print("✓ Manifold client imported")
    except ImportError as e:
        print(f"✗ Failed to import manifold client: {e}")
        return False
    
    try:
        from ensemble import StrategyEnsemble
        print("✓ Ensemble imported")
    except ImportError as e:
        print(f"✗ Failed to import ensemble: {e}")
        return False
    
    try:
        from risk_manager import RiskManager
        print("✓ Risk manager imported")
    except ImportError as e:
        print(f"✗ Failed to import risk manager: {e}")
        return False
    
    return True

def test_strategy_creation():
    """Test creating strategy instances"""
    print("\nTesting strategy creation...")
    
    try:
        from strategies.momentum_strategy import MomentumStrategy
        from strategies.contrarian_strategy import ContrarianStrategy
        
        momentum = MomentumStrategy()
        print(f"✓ Created momentum strategy: {momentum}")
        
        contrarian = ContrarianStrategy()
        print(f"✓ Created contrarian strategy: {contrarian}")
        
        return True
    except Exception as e:
        print(f"✗ Failed to create strategies: {e}")
        return False

def test_signal_creation():
    """Test creating a strategy signal"""
    print("\nTesting signal creation...")
    
    try:
        from strategies.base_strategy import StrategySignal
        
        signal = StrategySignal(
            probability=0.65,
            confidence=0.75,
            direction='YES',
            reasoning='Test signal',
            strength=0.80
        )
        
        print(f"✓ Created signal: {signal.direction} @ {signal.probability:.1%}")
        print(f"  Confidence: {signal.confidence:.1%}, Strength: {signal.strength:.2f}")
        print(f"  Weighted probability: {signal.weighted_probability:.1%}")
        
        return True
    except Exception as e:
        print(f"✗ Failed to create signal: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from config import Config
        
        print(f"✓ Config loaded")
        print(f"  Bot username: {Config.BOT_USERNAME}")
        print(f"  Target user: {Config.TARGET_USER}")
        print(f"  Max bet: {Config.MAX_BET_AMOUNT}")
        print(f"  Risk tolerance: {Config.RISK_TOLERANCE}")
        
        return True
    except Exception as e:
        print(f"✗ Failed to load config: {e}")
        return False

def main():
    print("=" * 60)
    print("Manifold MikhailTal Bot - Component Test")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Strategy Creation", test_strategy_creation()))
    results.append(("Signal Creation", test_signal_creation()))
    results.append(("Configuration", test_config()))
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("=" * 60)
    if all_passed:
        print("All tests passed! ✓")
        print("\nYou can now run the bot with:")
        print("  python src/main.py --dry-run --once")
    else:
        print("Some tests failed! ✗")
        print("\nPlease check the error messages above.")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())