"""
Kraken exchange integration using CCXT library.
"""
from typing import Optional, Dict, Any, List
import ccxt
from datetime import datetime
from config import settings


class KrakenClient:
    """Wrapper for Kraken exchange operations via CCXT."""
    
    def __init__(self):
        """Initialize Kraken exchange client."""
        self.exchange = None
        self._initialize_exchange()
    
    def _initialize_exchange(self):
        """Initialize the CCXT exchange object."""
        try:
            if settings.kraken_testnet:
                # Use Kraken sandbox/testnet if available
                self.exchange = ccxt.kraken({
                    'apiKey': settings.kraken_api_key,
                    'secret': settings.kraken_api_secret,
                    'enableRateLimit': True,
                    'options': {
                        'defaultType': 'spot',
                    }
                })
            else:
                self.exchange = ccxt.kraken({
                    'apiKey': settings.kraken_api_key,
                    'secret': settings.kraken_api_secret,
                    'enableRateLimit': True,
                })
        except Exception as e:
            print(f"Warning: Failed to initialize Kraken exchange: {e}")
            self.exchange = None
    
    async def get_balance(self) -> Dict[str, Any]:
        """
        Get account balance.
        
        Returns:
            Dictionary of balances by currency
        """
        if not self.exchange:
            return {"error": "Exchange not initialized"}
        
        try:
            balance = self.exchange.fetch_balance()
            return balance
        except Exception as e:
            return {"error": f"Failed to fetch balance: {str(e)}"}
    
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        Get current ticker data for a symbol.
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USD')
            
        Returns:
            Ticker data dictionary
        """
        if not self.exchange:
            return {"error": "Exchange not initialized"}
        
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker
        except Exception as e:
            return {"error": f"Failed to fetch ticker for {symbol}: {str(e)}"}
    
    async def get_ohlcv(
        self, 
        symbol: str, 
        timeframe: str = '1h', 
        limit: int = 100
    ) -> List[List]:
        """
        Get OHLCV (candlestick) data.
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USD')
            timeframe: Timeframe (e.g., '1m', '5m', '1h', '1d')
            limit: Number of candles to fetch
            
        Returns:
            List of OHLCV data
        """
        if not self.exchange:
            return []
        
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            return ohlcv
        except Exception as e:
            print(f"Failed to fetch OHLCV for {symbol}: {e}")
            return []
    
    async def create_order(
        self,
        symbol: str,
        order_type: str,
        side: str,
        amount: float,
        price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Create a new order.
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USD')
            order_type: 'market' or 'limit'
            side: 'buy' or 'sell'
            amount: Amount to trade
            price: Price for limit orders (optional)
            
        Returns:
            Order details dictionary
        """
        if not self.exchange:
            return {"error": "Exchange not initialized"}
        
        try:
            if order_type == 'market':
                order = self.exchange.create_market_order(symbol, side, amount)
            elif order_type == 'limit':
                if price is None:
                    return {"error": "Price required for limit orders"}
                order = self.exchange.create_limit_order(symbol, side, amount, price)
            else:
                return {"error": f"Unknown order type: {order_type}"}
            
            return order
        except Exception as e:
            return {"error": f"Failed to create order: {str(e)}"}
    
    async def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        Cancel an existing order.
        
        Args:
            order_id: Exchange order ID
            symbol: Trading pair
            
        Returns:
            Cancellation result dictionary
        """
        if not self.exchange:
            return {"error": "Exchange not initialized"}
        
        try:
            result = self.exchange.cancel_order(order_id, symbol)
            return result
        except Exception as e:
            return {"error": f"Failed to cancel order: {str(e)}"}
    
    async def get_order_status(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        Get status of an order.
        
        Args:
            order_id: Exchange order ID
            symbol: Trading pair
            
        Returns:
            Order status dictionary
        """
        if not self.exchange:
            return {"error": "Exchange not initialized"}
        
        try:
            order = self.exchange.fetch_order(order_id, symbol)
            return order
        except Exception as e:
            return {"error": f"Failed to fetch order status: {str(e)}"}
    
    async def get_markets(self) -> List[str]:
        """
        Get list of available trading markets.
        
        Returns:
            List of market symbols
        """
        if not self.exchange:
            return []
        
        try:
            markets = self.exchange.load_markets()
            return list(markets.keys())
        except Exception as e:
            print(f"Failed to fetch markets: {e}")
            return []
    
    def is_initialized(self) -> bool:
        """Check if exchange client is properly initialized."""
        return self.exchange is not None


# Global Kraken client instance
kraken_client = KrakenClient()
