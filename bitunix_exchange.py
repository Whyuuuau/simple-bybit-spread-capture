"""Bitunix Exchange Adapter for CCXT-like interface"""
import aiohttp
import asyncio
import hmac
import hashlib
import time
import json
import uuid
from urllib.parse import urlencode
from datetime import datetime
from logger_config import setup_logger

logger = setup_logger('BitunixExchange')

class BitunixExchange:
    def __init__(self, config):
        self.api_key = config['apiKey']
        self.secret = config['secret']
        self.base_url = "https://fapi.bitunix.com/api/v1"
        self.timeout = 10
        self.session = None
        self.options = config.get('options', {})
        self.price_precision = self.options.get('price_precision', 2)
        self.amount_precision = self.options.get('amount_precision', 3)
        
        # Helper for Duck Typing
        self.has = {
            'fetchMarkets': False,
            'fetchTicker': True,
            'fetchBalance': True,
            'fetchPositions': True,
            'fetchOpenOrders': True,
            'createOrder': True,
            'cancelOrder': True,
            'setLeverage': True,
            'setPositionMode': True, # Mocked
            'fetchOrderBook': True,
            'fetchOHLCV': True,
            'fetchFundingHistory': True,
        }

    async def _init_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    def _generate_signature(self, nonce, timestamp, query_params, body_str):
        """
        Double SHA256 Signature Generation
        1. digest_input = nonce + timestamp + api_key + queryParams + body
        2. digest = sha256(digest_input)
        3. sign_input = digest + secret
        4. sign = sha256(sign_input)
        """
        # Sort query params
        if query_params:
            sorted_keys = sorted(query_params.keys())
            query_str = "".join([f"{k}{query_params[k]}" for k in sorted_keys])
        else:
            query_str = ""
            
        digest_input = f"{nonce}{timestamp}{self.api_key}{query_str}{body_str}"
        
        digest = hashlib.sha256(digest_input.encode('utf-8')).hexdigest()
        
        sign_input = f"{digest}{self.secret}"
        sign = hashlib.sha256(sign_input.encode('utf-8')).hexdigest()
        
        return sign

    async def _request(self, method, endpoint, params=None, body=None, signed=False):
        await self._init_session()
        
        url = f"{self.base_url}{endpoint}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Only add Content-Type for non-GET or if body exists
        if method != 'GET' or body:
            headers['Content-Type'] = 'application/json'
        
        
        # Prepare params and body for signature
        query_str_for_sign = ""
        body_str_for_sign = ""
        
        # Handle Query Params
        if params:
            # Drop None values
            params = {k: v for k, v in params.items() if v is not None}
            # Create query string for URL
            url += "?" + urlencode(params)
        
        # Handle Body
        json_body = None
        body_str_for_sign = ""
        
        if body:
             # Drop None values
            body = {k: v for k, v in body.items() if v is not None}
            # Compact JSON for signature (no spaces)
            # IMPORTANT: Use sort_keys=True to ensure deterministic order for signature AND request
            body_str_for_sign = json.dumps(body, separators=(',', ':'), sort_keys=True)
        
        if signed:
            nonce = str(uuid.uuid4()).replace('-', '')
            timestamp = str(int(time.time() * 1000))
            
            sign = self._generate_signature(nonce, timestamp, params, body_str_for_sign)
            
            headers.update({
                'api-key': self.api_key,
                'nonce': nonce,
                'timestamp': timestamp,
                'sign': sign
            })
            
        try:
            # Use 'data' with pre-serialized string to ensure signature match
            # CRITICAL FIX: Pass params=None because we already appended them to 'url' above!
            async with self.session.request(method, url, headers=headers, params=None, data=body_str_for_sign if body else None) as response:
                text = await response.text()
                try:
                    data = json.loads(text)
                except:
                    raise Exception(f"Bitunix Response Error: {text}")
                
                if data.get('code') != 0:
                    print(f"❌ API Request Failed: URL={url} | Params={params} | Body={body_str_for_sign}")
                    raise Exception(f"Bitunix API Error {data.get('code')}: {data.get('msg')}")
                
                return data['data']
                
        except Exception as e:
            # Re-raise nicely
            raise Exception(f"Bitunix Request Failed: {e}")

    # ==========================================================
    # Public Methods
    # ==========================================================
    
    async def fetch_markets(self):
        """Fetch all available markets"""
        data = await self._request('GET', '/futures/market/tickers')
        return data

    async def fetch_ticker(self, symbol):
        """
        Get ticker. Note: Bitunix symbols usually formatted like 'ETHUSDT'
        We need to handle the internal 'ETH/USDT:USDT' format.
        """
        clean_symbol = symbol.replace('/', '').replace(':', '').split('USDT')[0] + 'USDT'
        
        try:
            # 1. Try 'tickers' endpoint (plural) which is known to work for Last Price
            # Singular 'ticker' endpoint is broken.
            tickers_data = await self._request('GET', '/futures/market/tickers', params={'symbol': clean_symbol})
            
            # Response is a list of tickers. Find ours.
            ticker_data = None
            if isinstance(tickers_data, list):
                for t in tickers_data:
                    if t.get('symbol') == clean_symbol:
                        ticker_data = t
                        break
            
            if not ticker_data:
                 # Fallback: Maybe it's a dict?
                 if isinstance(tickers_data, dict) and tickers_data.get('symbol') == clean_symbol:
                     ticker_data = tickers_data
            
            if not ticker_data:
                raise Exception(f"Symbol {clean_symbol} not found in tickers response")

            # Parse Last Price
            last = float(ticker_data.get('lastPrice', ticker_data.get('last', 0)))
            
            # 2. Bid/Ask are often MISSING in the summary ticker. 
            # We must try to get them from 'depth' or just falback to 'last' to allow bot to run.
            bid = float(ticker_data.get('buyOne', 0))
            ask = float(ticker_data.get('sellOne', 0))
            
            # If 0, try to fetch depth briefly? Or just use last.
            # Fetching depth every ticker call is expensive. Let's rely on 'last' for approximation
            # OR - use the known working depth endpoint if bid/ask are strictly needed.
            
            if bid == 0 or ask == 0:
                 # Fast depth check for better precision
                 try:
                     depth = await self._request('GET', '/futures/market/depth', params={'symbol': clean_symbol, 'limit': 5})
                     bids = depth.get('bids', [])
                     asks = depth.get('asks', [])
                     if bids: bid = float(bids[0][0])
                     if asks: ask = float(asks[0][0])
                 except:
                     pass # Fallback to last
            
            # Final Fallback
            if bid == 0: bid = last
            if ask == 0: ask = last
            
            return {
                'symbol': symbol,
                'bid': bid, # Best Bid
                'ask': ask, # Best Ask
                'last': last,
                'timestamp': int(time.time() * 1000)
            }
            
        except Exception as e:
            print(f"Error fetching ticker: {e}")
            # Emergency fallback to avoid bot crash
            return {
                'symbol': symbol,
                'bid': 0,
                'ask': 0,
                'last': 0,
                'timestamp': int(time.time() * 1000)
            }

    async def fetch_order_book(self, symbol, limit=20):
        """Fetch Order Book"""
        clean_symbol = symbol.replace('/', '').replace(':', '').split('USDT')[0] + 'USDT'
        
        # Endpoint: /futures/market/depth
        # Params: symbol, limit (optional? default usually 20)
        data = await self._request('GET', '/futures/market/depth', params={'symbol': clean_symbol})
        
        # Map to CCXT structure: {'bids': [[price, size], ...], 'asks': ...}
        bids = []
        asks = []
        
        for b in data.get('bids', []):
            bids.append([float(b[0]), float(b[1])])
            
        for a in data.get('asks', []):
            asks.append([float(a[0]), float(a[1])])
            
        return {
            'symbol': symbol,
            'bids': bids,
            'asks': asks,
            'timestamp': data.get('timestamp')
        }

    async def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limit=100):
        """
        Fetch OHLCV Data with Pagination support for large limits (up to 100k).
        Auto-pagination backwards from latest or until 'since' is reached.
        """
        clean_symbol = symbol.replace('/', '').replace(':', '').split('USDT')[0] + 'USDT'
        
        
        # Max limit per request (Bitunix usually caps at 1000, reducing to 500 for safety)
        MAX_LIMIT_PER_REQ = 500
        
        
        # Prepare timeframe in ms for pagination calculations
        tf_ms_map = {
            '1m': 60000,
            '3m': 180000,
            '5m': 300000,
            '15m': 900000,
            '30m': 1800000,
            '1h': 3600000,
            '2h': 7200000,
            '4h': 14400000,
            '6h': 21600000,
            '12h': 43200000,
            '1d': 86400000,
            '1w': 604800000,
            '1M': 2592000000
        }
        interval_ms = tf_ms_map.get(timeframe, 60000) # Default 1m

        all_ohlcv = []
        
        # We need to fetch 'limit' candles total.
        # Simplest Strategy: Backward pagination from NOW (or from endTime if we had it).
        # Since 'since' is optional, if provided we could fetch forward, but backward is usually safer for getting "latest N".
        # If 'since' is NOT provided, user wants LATEST 'limit' candles. -> Backward loop.
        # If 'since' IS provided, user wants data FROM 'since'. -> Forward loop (using startTime).
        
        current_limit = limit
        
        if since:
            # FORWARD PAGINATION (using startTime)
            current_start_time = since
            
            while len(all_ohlcv) < limit:
                # Calculate how many to fetch this batch
                remaining = limit - len(all_ohlcv)
                batch_size = min(remaining, MAX_LIMIT_PER_REQ)
                
                params = {
                    'symbol': clean_symbol,
                    'interval': timeframe,
                    'limit': batch_size,
                    'startTime': current_start_time
                }
                
                data = await self._request('GET', '/futures/market/kline', params=params)
                
                if not data or not isinstance(data, list) or len(data) == 0:
                    break # No more data
                
                batch_ohlcv = self._parse_ohlcv_response(data)
                all_ohlcv.extend(batch_ohlcv)
                
                # Next start time = last item time + interval
                last_time = batch_ohlcv[-1][0]
                current_start_time = last_time + interval_ms
                
                # Safety break if we aren't moving (duplicates)
                if len(batch_ohlcv) < batch_size: 
                    break # End of history reached
                    
        else:
            # BACKWARD PAGINATION (Latest -> Past)
            # Bitunix 'endTime' is usually inclusive or exclusive. 
            # We assume we want data BEFORE a certain time.
            
            # Initial end_time can be omitted to get latest
            current_end_time = None 
            
            while len(all_ohlcv) < limit:
                remaining = limit - len(all_ohlcv)
                batch_size = min(remaining, MAX_LIMIT_PER_REQ)
                
                params = {
                    'symbol': clean_symbol,
                    'interval': timeframe,
                    'limit': batch_size
                }
                
                if current_end_time:
                    params['endTime'] = current_end_time
                
                try:
                    data = await self._request('GET', '/futures/market/kline', params=params)
                except Exception as e:
                    print(f"Fetch error: {e}")
                    break

                if not data or not isinstance(data, list) or len(data) == 0:
                    break

                batch_ohlcv = self._parse_ohlcv_response(data)
                
                # If we requested with endTime, the API might return data ending at endTime.
                # Since we want to prepend/append, let's just collect all then sort.
                # Actually, backward fetch means we get [T-1000 ... T]. 
                # We want the next batch to be [T-2000 ... T-1001].
                
                # Prepend to our main list because we are going backwards?
                # Actually, easier to extend and then sort/reverse at the end if we want.
                # BUT standard is to keep them sorted old->new. 
                # So if we fetch [Old ... New], we should Insert at beginning? 
                # Yes, all_ohlcv = batch_ohlcv + all_ohlcv
                
                all_ohlcv = batch_ohlcv + all_ohlcv
                
                # Next end_time = oldest in this batch (index 0) - 1ms (or interval)
                oldest_time_in_batch = batch_ohlcv[0][0]
                current_end_time = oldest_time_in_batch - 1 # Minus 1ms to be safe/exclusive
                
                # Optimization: if API returned fewer than we asked, we probably hit the beginning of time
                # REMOVED: Bitunix might cap at 200 even if we ask for 1000. 
                # We should only break if we get 0 items (handled above).
                # if len(batch_ohlcv) < batch_size:
                #    break
                    
        # Final Trim (in case we over-fetched due to batching)
        if len(all_ohlcv) > limit:
            if since:
                all_ohlcv = all_ohlcv[:limit] # Keep first N
            else:
                all_ohlcv = all_ohlcv[-limit:] # Keep last N
                
        return all_ohlcv

    def _parse_ohlcv_response(self, data):
        ohlcv = []
        for candle in data:
            ts, o, h, l, c, v = 0, 0, 0, 0, 0, 0
            
            if isinstance(candle, dict):
                 ts = int(candle.get('time', 0))
                 o = float(candle.get('open', 0))
                 h = float(candle.get('high', 0))
                 l = float(candle.get('low', 0))
                 c = float(candle.get('close', 0))
                 v = float(candle.get('vol', 0)) # Note: vol not volume per previous check
            elif isinstance(candle, list) and len(candle) >= 6:
                 ts = int(candle[0])
                 o = float(candle[1])
                 h = float(candle[2])
                 l = float(candle[3])
                 c = float(candle[4])
                 v = float(candle[5])
            
            ohlcv.append([ts, o, h, l, c, v])
        
        # Ensure sorted by timestamp generic
        ohlcv.sort(key=lambda x: x[0])
        return ohlcv

    # ==========================================================
    # Private Methods (Trading)
    # ==========================================================

    async def fetch_balance(self):
        """
        Get USDT Balance
        Endpoint: /api/v1/futures/account based on docs
        """
        # Endpoint: /futures/account?marginCoin=USDT
        data = await self._request('GET', '/futures/account', params={'marginCoin': 'USDT'}, signed=True)
        
        # Doc response example: 
        # "data": [{"marginCoin":"USDT", "available":"1000", "margin":"10", ...}]
        
        balance_data = None
        if isinstance(data, list) and len(data) > 0:
            balance_data = data[0]
        elif isinstance(data, dict):
            balance_data = data
            
        if not balance_data:
             return {'USDT': {'total': 0.0, 'used': 0.0, 'free': 0.0}}

        total = float(balance_data.get('accountEquity', getattr(balance_data, 'marginBalance', 0) or 0)) 
        # Note: Docs use 'accountEquity' in some places, 'available'+'margin' in others. 
        # Let's trust 'accountEquity' if present, else sum available + margin.
        if 'accountEquity' not in balance_data:
             avail = float(balance_data.get('available', 0))
             margin = float(balance_data.get('margin', 0))
             total = avail + margin
        
        free = float(balance_data.get('available', 0))
        used = float(balance_data.get('margin', 0))
        
        return {
            'USDT': {
                'total': total,
                'used': used,
                'free': free
            }
        }

    async def create_order(self, symbol, type, side, amount, price=None, params={}):
        """
        Create Order
        Bitunix Keys: symbol, side(1/2), orderType(1/2), qty, price
        """
        clean_symbol = symbol.replace('/', '').replace(':', '').split('USDT')[0] + 'USDT'
        
        # Mappings based on Docs (Corrected via Browser Research)
        # Side: BUY, SELL (Strings, UPPERCASE)
        # OrderType: LIMIT, MARKET (Strings, UPPERCASE)
        # Effect: GTC, IOC, FOK (Strings, UPPERCASE)
        
        side_map = {'buy': 'BUY', 'sell': 'SELL'}
        type_map = {'limit': 'LIMIT', 'market': 'MARKET'}
        
        # Get Precision from options or default
        p_prec = self.options.get('price_precision', 2)
        a_prec = self.options.get('amount_precision', 2)
        
        # Strict formatting
        qty_str = f"{float(amount):.{a_prec}f}"
        
        body = {
            'symbol': clean_symbol,
            'side': side_map[side.lower()],
            'tradeSide': 'OPEN', # Mandatory!
            'orderType': type_map[type.lower()],
            'qty': qty_str
        }
        
        # Optional params
        if params.get('reduceOnly'):
            # body['reduceOnly'] = True  <-- CAUSES ERROR 10002! Bitunix uses tradeSide only.
            body['tradeSide'] = 'CLOSE' # If reduceOnly, it's a close
            
            # CRITICAL: positionId is REQUIRED when tradeSide='CLOSE' in hedge mode
            position_id = params.get('positionId')
            if position_id:
                body['positionId'] = str(position_id)
            else:
                logger.warning("⚠️ CLOSE order without positionId - may fail in hedge mode!")
            
        if type.lower() == 'limit':
            if not price:
                raise Exception("Price required for limit order")
            body['price'] = f"{float(price):.{p_prec}f}"
            body['effect'] = 'GTC'
        
        
        
            
        data = await self._request('POST', '/futures/trade/place_order', body=body, signed=True)
        
        # Response: {"orderId": "...", ...}
        return {
            'id': str(data.get('orderId')),
            'symbol': symbol,
            'side': side,
            'type': type,
            'amount': amount,
            'price': price,
            'status': 'open'
        }
        
    async def create_limit_buy_order(self, symbol, amount, price, params={}):
        return await self.create_order(symbol, 'limit', 'buy', amount, price, params)

    async def create_limit_sell_order(self, symbol, amount, price, params={}):
        return await self.create_order(symbol, 'limit', 'sell', amount, price, params)

    async def create_market_buy_order(self, symbol, amount, params={}):
        return await self.create_order(symbol, 'market', 'buy', amount, params=params)

    async def create_market_sell_order(self, symbol, amount, params={}):
        return await self.create_order(symbol, 'market', 'sell', amount, params=params)

    async def cancel_orders(self, ids, symbol):
        """Batch Cancel Orders"""
        clean_symbol = symbol.replace('/', '').replace(':', '').split('USDT')[0] + 'USDT'
        
        # Endpoint: /futures/trade/cancel_orders
        # Body: {"symbol": "SOLUSDT", "orderList": [id1, id2, ...]}
        
        # Bitunix might require list of dicts or just list of IDs?
        # Docs usually imply list of objects or IDs. 
        # API Doc Reference: "orderList": [{"orderId": 1}, {"orderId": 2}] OR [1, 2]
        # Let's try list of objects first as it's common for complex APIs, 
        # BUT search result said "orderList containing orderId".
        # Let's try simple list of IDs first, if fails try list of dicts.
        # Actually safe bet is generating both if generic.
        # Standard Bitunix pattern for batch usually expects list of dicts:
        # [{"orderId": "..."}]
        
        order_list = [{'orderId': str(x)} for x in ids]
        
        body = {
            'symbol': clean_symbol,
            'orderList': order_list
        }
        
        return await self._request('POST', '/futures/trade/cancel_orders', body=body, signed=True)

    async def cancel_order(self, id, symbol):
        """Cancel Order by ID"""
        clean_symbol = symbol.replace('/', '').replace(':', '').split('USDT')[0] + 'USDT'
        
        body = {
            'orderId': str(id),
            'symbol': clean_symbol
        }
        
        return await self._request('POST', '/futures/trade/cancel_order', body=body, signed=True)

    async def fetch_funding_history(self, symbol, since=None, limit=100):
        # Stub
        return []

    async def fetch_open_orders(self, symbol):
        """Fetch Open Orders"""
        clean_symbol = symbol.replace('/', '').replace(':', '').split('USDT')[0] + 'USDT'
        
        # Endpoint: /futures/trade/get_pending_orders (CORRECTED per docs)
        try:
             # Params usually symbol needed
             data = await self._request('GET', '/futures/trade/get_pending_orders', params={'symbol': clean_symbol}, signed=True)
        except Exception as e:
             logger.error(f"fetch_open_orders error: {e}")
             return []
        
        logger.debug(f"🔍 Raw API response type: {type(data)}, keys: {data.keys() if isinstance(data, dict) else 'N/A'}")
        
        orders = []
        
        # CRITICAL FIX: Bitunix returns {"data": {"orderList": [...], "total": N}}
        # NOT just an array!
        if isinstance(data, dict) and 'orderList' in data:
            order_list = data['orderList']
            logger.debug(f"🔍 Processing {len(order_list)} orders from data.orderList")
            
            for o in order_list:
                # Mapping side/type back
                # Bitunix uses: side=1(BUY)/2(SELL), orderType=1(LIMIT)/2(MARKET)
                s_map = {1: 'buy', 2: 'sell'}
                t_map = {1: 'limit', 2: 'market'}
                
                orders.append({
                    'id': str(o.get('orderId')),
                    'symbol': symbol,
                    'status': 'open',
                    'side': s_map.get(o.get('side'), 'buy'),
                    'type': t_map.get(o.get('orderType'), 'limit'),
                    'price': float(o.get('price', 0)),
                    'amount': float(o.get('qty', 0)),
                    'filled': float(o.get('tradeQty', 0)),
                    'timestamp': o.get('ctime')
                })
        
        logger.info(f"✅ fetch_open_orders returning {len(orders)} orders")
        return orders
        
    async def fetch_positions(self, symbols=None):
        """
        Fetch Positions
        Endpoint: /api/v1/futures/position/get_pending_positions
        """
        params = {'marginCoin': 'USDT'}
        # If specific symbol requested, API might support 'symbol' param
        target_symbol = symbols[0] if symbols and len(symbols) > 0 else None
        
        if target_symbol:
             clean_target = target_symbol.replace('/', '').replace(':', '').split('USDT')[0] + 'USDT'
             params['symbol'] = clean_target

        data = await self._request('GET', '/futures/position/get_pending_positions', params=params, signed=True)
        
        positions = []
        
        # Ensure data is list
        if not isinstance(data, list):
             return []
             
        for p in data:
            raw_symbol = p.get('symbol', 'UNKNOWN')
            
            # Map back to internal format
            final_symbol = raw_symbol
            # Simple heuristic since we only trade USDT pairs
            if raw_symbol.endswith('USDT'):
                base = raw_symbol.replace('USDT', '')
                final_symbol = f"{base}/USDT:USDT"

            size = float(p.get('qty', 0)) 
            side_str = p.get('side', '').upper() # "LONG" or "SHORT" or int 1/2? Docs say "LONG" string in example?
            # Docs example: "side": "LONG"
            
            if side_str == 'LONG':
                 signed_contracts = size
                 side_key = 'long'
            elif side_str == 'SHORT':
                 signed_contracts = -size
                 side_key = 'short'
            else:
                 # Fallback if int
                 if side_str == 1: 
                     signed_contracts = size
                     side_key = 'long'
                 else:
                     signed_contracts = -size
                     side_key = 'short'

            positions.append({
                'symbol': final_symbol,
                'contracts': signed_contracts,
                'notional': float(p.get('value') or p.get('entryValue') or 0), 
                'unrealizedPnl': float(p.get('unrealizedPNL') or 0), # Correct exact key from docs
                'entryPrice': float(p.get('entryPrice') or 0),
                'liquidationPrice': float(p.get('liqPrice') or 0),
                'leverage': float(p.get('leverage') or 0),
                'initialMargin': float(p.get('margin') or 0),
                'side': side_key,
                'positionId': p.get('positionId', '')  # REQUIRED for CLOSE orders in hedge mode
            })
        
        return positions

    async def set_leverage(self, leverage, symbol):
        """
        Set Leverage
        Endpoint: /api/v1/futures/account/change_leverage
        """
        clean_symbol = symbol.replace('/', '').replace(':', '').split('USDT')[0] + 'USDT'
        
        body = {
            'symbol': clean_symbol,
            'leverage': int(leverage),
            'marginCoin': 'USDT'
        }
        
        await self._request('POST', '/futures/account/change_leverage', body=body, signed=True)
        return True

    async def set_position_mode(self, hedged, symbol):
        # Implementation depends on specific endpoint availability
        pass

    # ==========================================================
    # Helper Methods
    # ==========================================================
    
    def price_to_precision(self, symbol, price):
        return "{:.{p}f}".format(float(price), p=self.price_precision)

    def amount_to_precision(self, symbol, amount):
        return "{:.{p}f}".format(float(amount), p=self.amount_precision)
        
    async def fetch_my_trades(self, symbol, limit=50):
        """
        Fetch Data for PnL Calculation (Dual Source for Reliability)
        Source 1: /api/v1/futures/trade/get_history_trades (Fills)
        Source 2: /api/v1/futures/trade/get_history_orders (Completed Orders)
        """
        clean_symbol = symbol.replace('/', '').replace(':', '').split('USDT')[0] + 'USDT'
        trades_map = {} # Deduplicate by ID
        
        # 1. Fetch Trades (Fills)
        try:
             data1 = await self._request('GET', '/futures/trade/get_history_trades', params={'symbol': clean_symbol, 'limit': limit}, signed=True)
             if isinstance(data1, list):
                 for t in data1:
                     tid = str(t.get('id', t.get('tradeId')))
                     trades_map[tid] = {
                        'id': tid,
                        'order': str(t.get('orderId')),
                        'symbol': symbol,
                        'side': {1: 'buy', 2: 'sell'}.get(t.get('side'), 'buy'),
                        'price': float(t.get('price', 0)),
                        'amount': float(t.get('qty', 0)),
                        'fee': {'cost': float(t.get('fee', 0)), 'currency': 'USDT'},
                        'timestamp': t.get('createTime') or t.get('ctime') or int(time.time()*1000)
                     }
        except Exception as e:
             print(f"Fetch history_trades error: {e}")

        # 2. Fetch Orders (Completed) - FALLBACK
        try:
             # state=2 (Completed), state=3 (Cancelled) - We want Completed for fills
             data2 = await self._request('GET', '/futures/trade/get_history_orders', params={'symbol': clean_symbol, 'limit': limit, 'state': 2}, signed=True)
             if isinstance(data2, list):
                 for o in data2:
                     filled = float(o.get('cumQty', 0))
                     if filled <= 0: continue # Skip unfilled
                     
                     oid = str(o.get('orderId'))
                     # Use orderId as tradeId if we don't have a specific trade record
                     # But prefer existing trade record if possible
                     
                     # Check if we already have this order processed via trades? 
                     # Hard to know mapping. Let's append if unique.
                     # Actually, a single order can have multiple trades.
                     # Safest is to rely on 'trades' for volume. 
                     # But if 'trades' is empty, use 'orders' as proxy.
                     
                     if not trades_map: # Only backfill if trades failed
                         avg_price = float(o.get('avgPrice', 0) or o.get('price', 0))
                         trades_map[oid] = {
                            'id': oid,
                            'order': oid,
                            'symbol': symbol,
                            'side': {1: 'buy', 2: 'sell'}.get(o.get('side'), 'buy'),
                            'price': avg_price,
                            'amount': filled,
                            'fee': {'cost': float(o.get('fee', 0)), 'currency': 'USDT'},
                            'timestamp': o.get('createTime') or o.get('ctime') or int(time.time()*1000)
                         }
        except Exception as e:
             print(f"Fetch history_orders error: {e}")
             
        results = list(trades_map.values())
        return results

