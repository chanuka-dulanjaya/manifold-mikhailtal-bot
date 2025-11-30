"""
Configuration management for Manifold Trading Bot
"""
import os
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()


class Config:
    """Bot configuration with sensible defaults"""
    
    # API Keys
    MANIFOLD_API_KEY: str = os.getenv('MANIFOLD_API_KEY', '')
    ANTHROPIC_API_KEY: str = os.getenv('ANTHROPIC_API_KEY', '')
    
    # Bot Identity
    BOT_USERNAME: str = os.getenv('BOT_USERNAME', 'MikhailTalBot')
    TARGET_USER: str = os.getenv('TARGET_USER', 'MikhailTal')
    
    # Trading Parameters
    MAX_BET_AMOUNT: int = int(os.getenv('MAX_BET_AMOUNT', '100'))
    MIN_BET_AMOUNT: int = int(os.getenv('MIN_BET_AMOUNT', '10'))
    RISK_TOLERANCE: float = float(os.getenv('RISK_TOLERANCE', '0.25'))
    MIN_EDGE: float = float(os.getenv('MIN_EDGE', '0.05'))
    MAX_POSITIONS: int = int(os.getenv('MAX_POSITIONS', '20'))
    
    # Timing
    TRADING_INTERVAL: int = int(os.getenv('TRADING_INTERVAL', '300'))  # 5 minutes
    
    # Strategy Weights (auto-adjusted based on performance)
    STRATEGY_WEIGHTS: Dict[str, float] = {
        'llm': 0.30,
        'momentum': 0.25,
        'contrarian': 0.15,
        'value': 0.20,
        'sentiment': 0.10,
    }
    
    # LLM Configuration
    LLM_MODEL: str = os.getenv('LLM_MODEL', 'claude-sonnet-4-20250514')
    LLM_MAX_TOKENS: int = int(os.getenv('LLM_MAX_TOKENS', '1000'))
    LLM_TEMPERATURE: float = float(os.getenv('LLM_TEMPERATURE', '0.7'))
    
    # Risk Management
    KELLY_FRACTION: float = float(os.getenv('KELLY_FRACTION', '0.25'))
    MAX_PORTFOLIO_RISK: float = float(os.getenv('MAX_PORTFOLIO_RISK', '0.30'))
    
    # Data Storage
    DATA_DIR: str = os.getenv('DATA_DIR', 'data')
    PERFORMANCE_FILE: str = os.path.join(DATA_DIR, 'performance.json')
    TRADES_FILE: str = os.path.join(DATA_DIR, 'trades.json')
    
    # API Endpoints
    MANIFOLD_API_BASE: str = 'https://api.manifold.markets'
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        if not cls.MANIFOLD_API_KEY:
            raise ValueError("MANIFOLD_API_KEY is required")
        return True
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Export configuration as dictionary"""
        return {
            'bot_username': cls.BOT_USERNAME,
            'target_user': cls.TARGET_USER,
            'max_bet_amount': cls.MAX_BET_AMOUNT,
            'min_bet_amount': cls.MIN_BET_AMOUNT,
            'risk_tolerance': cls.RISK_TOLERANCE,
            'min_edge': cls.MIN_EDGE,
            'max_positions': cls.MAX_POSITIONS,
            'trading_interval': cls.TRADING_INTERVAL,
            'strategy_weights': cls.STRATEGY_WEIGHTS,
        }


# Create data directory if it doesn't exist
os.makedirs(Config.DATA_DIR, exist_ok=True)