"""
Manifold Markets API Client
Provides a clean interface to the Manifold Markets API
"""
import requests
import time
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ManifoldClient:
    """Client for interacting with Manifold Markets API"""
    
    def __init__(self, api_key: str, base_url: str = 'https://api.manifold.markets'):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Key {api_key}',
            'Content-Type': 'application/json'
        })
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Make API request with error handling and retries"""
        url = f"{self.base_url}{endpoint}"
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json() if response.content else None
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Rate limit
                    wait_time = retry_delay * (2 ** attempt)
                    logger.warning(f"Rate limited, waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue
                logger.error(f"HTTP error: {e}")
                raise
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    logger.error(f"Request failed after {max_retries} attempts: {e}")
                    raise
                time.sleep(retry_delay)
        
        return None
    
    def get_markets_by_user(self, username: str, limit: int = 100) -> List[Dict]:
        """Get all markets created by a specific user"""
        try:
            # Get user ID first
            user = self._request('GET', f'/v0/user/{username}')
            if not user:
                logger.error(f"User {username} not found")
                return []
            
            user_id = user.get('id')
            
            # Get markets by user ID
            params = {
                'userId': user_id,
                'limit': limit,
                'sort': 'created-time',
                'order': 'desc'
            }
            markets = self._request('GET', '/v0/markets', params=params)
            return markets or []
        except Exception as e:
            logger.error(f"Error fetching markets for {username}: {e}")
            return []
    
    def get_market(self, market_id: str) -> Optional[Dict]:
        """Get detailed information about a specific market"""
        try:
            return self._request('GET', f'/v0/market/{market_id}')
        except Exception as e:
            logger.error(f"Error fetching market {market_id}: {e}")
            return None
    
    def get_bets(self, market_id: str, limit: int = 100) -> List[Dict]:
        """Get bets for a specific market"""
        try:
            params = {
                'contractId': market_id,
                'limit': limit,
                'order': 'desc'
            }
            bets = self._request('GET', '/v0/bets', params=params)
            return bets or []
        except Exception as e:
            logger.error(f"Error fetching bets for market {market_id}: {e}")
            return []
    
    def place_bet(
        self,
        market_id: str,
        outcome: str,
        amount: float,
        limit_prob: Optional[float] = None
    ) -> Optional[Dict]:
        """
        Place a bet on a market
        
        Args:
            market_id: ID of the market
            outcome: 'YES' or 'NO' for binary markets
            amount: Amount of mana to bet
            limit_prob: Optional limit probability for limit orders
        """
        try:
            data = {
                'contractId': market_id,
                'outcome': outcome,
                'amount': amount
            }
            
            if limit_prob is not None:
                data['limitProb'] = limit_prob
            
            result = self._request('POST', '/v0/bet', json=data)
            logger.info(f"Placed {outcome} bet of {amount}M on market {market_id}")
            return result
        except Exception as e:
            logger.error(f"Error placing bet: {e}")
            return None
    
    def get_comments(self, market_id: str, limit: int = 100) -> List[Dict]:
        """Get comments for a specific market"""
        try:
            params = {
                'contractId': market_id,
                'limit': limit
            }
            comments = self._request('GET', '/v0/comments', params=params)
            return comments or []
        except Exception as e:
            logger.error(f"Error fetching comments for market {market_id}: {e}")
            return []
    
    def get_user_balance(self, username: str) -> Optional[float]:
        """Get user's current mana balance"""
        try:
            user = self._request('GET', f'/v0/user/{username}')
            if user:
                return user.get('balance', 0)
            return None
        except Exception as e:
            logger.error(f"Error fetching balance for {username}: {e}")
            return None
    
    def get_user_positions(self, username: str) -> List[Dict]:
        """Get all open positions for a user"""
        try:
            # This would need to be implemented by fetching user's bets
            # and calculating current positions
            user = self._request('GET', f'/v0/user/{username}')
            if not user:
                return []
            
            # Note: This is a simplified version
            # In production, you'd want to track positions more carefully
            return []
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return []
    
    def get_market_probability_history(self, market_id: str) -> List[Dict]:
        """Get historical probability data for a market"""
        try:
            # Get bets which contain probability updates
            bets = self.get_bets(market_id, limit=1000)
            
            history = []
            for bet in bets:
                if 'probAfter' in bet:
                    history.append({
                        'timestamp': bet.get('createdTime'),
                        'probability': bet.get('probAfter'),
                        'amount': bet.get('amount'),
                        'outcome': bet.get('outcome')
                    })
            
            return sorted(history, key=lambda x: x['timestamp'])
        except Exception as e:
            logger.error(f"Error fetching probability history: {e}")
            return []
    
    def is_market_open(self, market: Dict) -> bool:
        """Check if a market is still open for trading"""
        if market.get('isResolved'):
            return False
        
        close_time = market.get('closeTime')
        if close_time:
            return close_time > int(time.time() * 1000)
        
        return True
    
    def get_market_metrics(self, market: Dict) -> Dict[str, Any]:
        """Calculate useful metrics for a market"""
        return {
            'id': market.get('id'),
            'question': market.get('question'),
            'probability': market.get('probability', 0.5),
            'volume': market.get('volume', 0),
            'liquidity': market.get('pool', {}).get('YES', 0) + market.get('pool', {}).get('NO', 0),
            'num_traders': market.get('uniqueBettorCount', 0),
            'created_time': market.get('createdTime'),
            'close_time': market.get('closeTime'),
            'is_open': self.is_market_open(market),
            'creator': market.get('creatorUsername'),
            'description': market.get('description', ''),
        }