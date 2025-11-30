"""
Main Trading Bot
Orchestrates all components and executes trading loop
"""
import time
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional
import sys
import argparse

from config import Config
from manifold_client import ManifoldClient
from ensemble import StrategyEnsemble
from risk_manager import RiskManager
from strategies.llm_strategy import LLMStrategy
from strategies.momentum_strategy import MomentumStrategy
from strategies.contrarian_strategy import ContrarianStrategy

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class TradingBot:
    """Main trading bot orchestrator"""
    
    def __init__(self, config: Config, dry_run: bool = False):
        self.config = config
        self.dry_run = dry_run
        
        # Initialize components
        self.client = ManifoldClient(config.MANIFOLD_API_KEY, config.MANIFOLD_API_BASE)
        self.risk_manager = RiskManager(
            max_bet_amount=config.MAX_BET_AMOUNT,
            min_bet_amount=config.MIN_BET_AMOUNT,
            kelly_fraction=config.KELLY_FRACTION,
            max_portfolio_risk=config.MAX_PORTFOLIO_RISK,
            risk_tolerance=config.RISK_TOLERANCE
        )
        
        # Initialize strategies
        strategies = self._init_strategies()
        self.ensemble = StrategyEnsemble(strategies, config.STRATEGY_WEIGHTS)
        
        # Load historical data
        self.performance_data = self._load_performance_data()
        self.trades_history = self._load_trades_history()
        
        logger.info(f"Trading Bot initialized (dry_run={dry_run})")
        logger.info(f"Target user: {config.TARGET_USER}")
        logger.info(f"Active strategies: {[s.name for s in strategies if s.enabled]}")
    
    def _init_strategies(self) -> List:
        """Initialize all trading strategies"""
        strategies = []
        
        # LLM Strategy (if API key available)
        if self.config.ANTHROPIC_API_KEY:
            llm_strategy = LLMStrategy(
                api_key=self.config.ANTHROPIC_API_KEY,
                model=self.config.LLM_MODEL,
                max_tokens=self.config.LLM_MAX_TOKENS,
                temperature=self.config.LLM_TEMPERATURE
            )
            strategies.append(llm_strategy)
            logger.info("LLM strategy enabled")
        else:
            logger.warning("LLM strategy disabled (no API key)")
        
        # Momentum Strategy
        strategies.append(MomentumStrategy())
        
        # Contrarian Strategy
        strategies.append(ContrarianStrategy())
        
        # Value Strategy
        from strategies.value_strategy import ValueStrategy
        strategies.append(ValueStrategy())
        
        # Sentiment Strategy
        from strategies.sentiment_strategy import SentimentStrategy
        strategies.append(SentimentStrategy())
        
        return strategies
    
    def run_once(self):
        """Execute one trading cycle"""
        logger.info("=" * 80)
        logger.info("Starting trading cycle")
        
        try:
            # Get markets created by target user
            markets = self.client.get_markets_by_user(self.config.TARGET_USER)
            logger.info(f"Found {len(markets)} markets by {self.config.TARGET_USER}")
            
            # Filter for open markets
            open_markets = [m for m in markets if self.client.is_market_open(m)]
            logger.info(f"{len(open_markets)} markets are open for trading")
            
            # Get current balance
            balance = self.client.get_user_balance(self.config.BOT_USERNAME)
            if balance is None:
                logger.error("Could not fetch balance")
                return
            
            logger.info(f"Current balance: {balance:.0f}M")
            
            # Check portfolio risk
            if self.risk_manager.should_limit_orders(balance):
                logger.warning("Portfolio risk limits reached, skipping new trades")
                return
            
            # Analyze each market
            trades_executed = 0
            for market in open_markets:
                try:
                    result = self._analyze_and_trade(market, balance)
                    if result:
                        trades_executed += 1
                except Exception as e:
                    logger.error(f"Error processing market {market.get('id')}: {e}")
            
            logger.info(f"Trading cycle complete. Executed {trades_executed} trades.")
            
            # Update performance metrics
            self._update_performance_metrics()
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}", exc_info=True)
    
    def _analyze_and_trade(self, market: Dict, balance: float) -> bool:
        """Analyze a market and potentially place a trade"""
        
        market_id = market.get('id')
        question = market.get('question', '')
        
        logger.info(f"\nAnalyzing: {question[:80]}...")
        
        # Get additional market data
        prob_history = self.client.get_market_probability_history(market_id)
        comments = self.client.get_comments(market_id, limit=50)
        bets = self.client.get_bets(market_id, limit=100)
        
        # Get ensemble signal
        signal = self.ensemble.analyze(
            market,
            probability_history=prob_history,
            comments=comments,
            bets=bets
        )
        
        if not signal:
            logger.debug("No signal generated - no strategy consensus")
            return False
        
        logger.info(
            f"✓ Signal: {signal.direction} @ {signal.probability:.1%} "
            f"(confidence: {signal.confidence:.1%}, strength: {signal.strength:.2f})"
        )
        logger.info(f"  Reasoning: {signal.reasoning[:100]}...")
        
        # Calculate bet size
        bet_size = self.risk_manager.calculate_bet_size(signal, market, balance)
        
        if not bet_size:
            logger.info("✗ Risk manager declined bet (insufficient edge or risk limits)")
            return False
        
        logger.info(f"✓ Bet size approved: {bet_size:.0f}M")
        
        # Execute trade
        if self.dry_run:
            logger.info(f"[DRY RUN] Would place {signal.direction} bet of {bet_size:.0f}M")
            return True
        else:
            result = self.client.place_bet(
                market_id=market_id,
                outcome=signal.direction,
                amount=bet_size
            )
            
            if result:
                logger.info(f"✓ Trade executed: {signal.direction} {bet_size:.0f}M on {question[:60]}...")
                
                # Record trade
                trade_record = {
                    'timestamp': datetime.now().isoformat(),
                    'market_id': market_id,
                    'question': question,
                    'direction': signal.direction,
                    'amount': bet_size,
                    'probability': market.get('probability'),
                    'signal': {
                        'probability': signal.probability,
                        'confidence': signal.confidence,
                        'strength': signal.strength,
                        'reasoning': signal.reasoning
                    }
                }
                self.trades_history.append(trade_record)
                self._save_trades_history()
                
                # Update risk manager
                self.risk_manager.add_position({
                    'market_id': market_id,
                    'amount': bet_size,
                    'direction': signal.direction
                })
                
                return True
            else:
                logger.error(f"✗ Trade failed")
                return False
    
    def run_continuous(self, interval: int = None):
        """Run bot continuously"""
        if interval is None:
            interval = self.config.TRADING_INTERVAL
        
        logger.info(f"Starting continuous mode (interval: {interval}s)")
        
        while True:
            try:
                self.run_once()
                logger.info(f"Sleeping for {interval}s...")
                time.sleep(interval)
            except KeyboardInterrupt:
                logger.info("Shutting down...")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                time.sleep(interval)
    
    def _update_performance_metrics(self):
        """Update and save performance metrics"""
        strategy_perf = self.ensemble.get_strategy_performance()
        
        self.performance_data = {
            'timestamp': datetime.now().isoformat(),
            'total_trades': len(self.trades_history),
            'strategies': strategy_perf
        }
        
        self._save_performance_data()
        
        # Update ensemble weights based on performance
        self.ensemble.update_weights(strategy_perf)
    
    def _load_performance_data(self) -> Dict:
        """Load performance data from disk"""
        try:
            if not os.path.exists(self.config.PERFORMANCE_FILE):
                return {}
            
            with open(self.config.PERFORMANCE_FILE, 'r') as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load performance data: {e}. Starting fresh.")
            return {}
    
    def _save_performance_data(self):
        """Save performance data to disk"""
        try:
            os.makedirs(os.path.dirname(self.config.PERFORMANCE_FILE), exist_ok=True)
            with open(self.config.PERFORMANCE_FILE, 'w') as f:
                json.dump(self.performance_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving performance data: {e}")
    
    def _load_trades_history(self) -> List:
        """Load trades history from disk"""
        try:
            if not os.path.exists(self.config.TRADES_FILE):
                return []
            
            with open(self.config.TRADES_FILE, 'r') as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load trades history: {e}. Starting fresh.")
            return []
    
    def _save_trades_history(self):
        """Save trades history to disk"""
        try:
            os.makedirs(os.path.dirname(self.config.TRADES_FILE), exist_ok=True)
            with open(self.config.TRADES_FILE, 'w') as f:
                json.dump(self.trades_history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving trades history: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Manifold Markets Trading Bot')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--dry-run', action='store_true', help='Simulate trades without executing')
    parser.add_argument('--config', type=str, help='Path to config file')
    parser.add_argument('--interval', type=int, help='Trading interval in seconds')
    
    args = parser.parse_args()
    
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    
    # Initialize bot
    bot = TradingBot(Config, dry_run=args.dry_run)
    
    # Run
    if args.once:
        bot.run_once()
    else:
        bot.run_continuous(interval=args.interval)


if __name__ == '__main__':
    main()