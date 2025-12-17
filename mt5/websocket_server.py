"""
WebSocket Server for MT5 communication
"""

import asyncio
import websockets
import json
import logging
import numpy as np
from datetime import datetime
from typing import Dict, Optional
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import config
except ImportError:
    class config:
        WEBSOCKET_HOST = "127.0.0.1"
        WEBSOCKET_PORT = 8080

from engine import MLEngine
from database import validate_token, save_signal, get_user

logger = logging.getLogger(__name__)

class WebSocketServer:
    """
    WebSocket server for receiving OHLC data from EA and sending signals back.
    """
    
    def __init__(self, host: str = None, port: int = None):
        """
        Initialize WebSocket server.
        
        Args:
            host: Server host
            port: Server port
        """
        self.host = host or getattr(config, 'WEBSOCKET_HOST', '127.0.0.1')
        self.port = port or getattr(config, 'WEBSOCKET_PORT', 8080)
        self.ml_engine = MLEngine()
        self.active_connections = {}
        
        logger.info(f"WebSocket server initialized on {self.host}:{self.port}")
    
    async def handle_client(self, websocket, path):
        """
        Handle WebSocket client connection.
        
        Args:
            websocket: WebSocket connection
            path: Connection path
        """
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        self.active_connections[client_id] = websocket
        
        logger.info(f"Client connected: {client_id}")
        
        try:
            async for message in websocket:
                try:
                    # Parse JSON message
                    data = json.loads(message)
                    
                    # Process message
                    response = await self.process_message(data)
                    
                    # Send response
                    await websocket.send(json.dumps(response))
                
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON from {client_id}: {e}")
                    await websocket.send(json.dumps({
                        'error': 'Invalid JSON format'
                    }))
                
                except Exception as e:
                    logger.error(f"Error processing message from {client_id}: {e}")
                    await websocket.send(json.dumps({
                        'error': str(e)
                    }))
        
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {client_id}")
        
        finally:
            if client_id in self.active_connections:
                del self.active_connections[client_id]
    
    async def process_message(self, data: Dict) -> Dict:
        """
        Process message from EA.
        
        Args:
            data: Message data
        
        Returns:
            Response dictionary
        """
        try:
            message_type = data.get('type')
            
            if message_type == 'OHLC':
                return await self.handle_ohlc_data(data)
            
            elif message_type == 'TOKEN_VALIDATE':
                return await self.handle_token_validation(data)
            
            elif message_type == 'HEARTBEAT':
                return {'status': 'OK', 'timestamp': datetime.now().isoformat()}
            
            else:
                return {'error': f'Unknown message type: {message_type}'}
        
        except Exception as e:
            logger.error(f"Error in process_message: {e}")
            return {'error': str(e)}
    
    async def handle_token_validation(self, data: Dict) -> Dict:
        """
        Validate EA token.
        
        Args:
            data: Message with token and mt5_id
        
        Returns:
            Validation response
        """
        try:
            token = data.get('token')
            mt5_id = data.get('mt5_id')
            
            if not token or not mt5_id:
                return {
                    'valid': False,
                    'message': 'Missing token or MT5 ID'
                }
            
            # Validate token
            is_valid = validate_token(token, mt5_id)
            
            if is_valid:
                logger.info(f"Token validated: {token} for MT5 {mt5_id}")
                return {
                    'valid': True,
                    'message': 'Token validated successfully'
                }
            else:
                logger.warning(f"Invalid token: {token} for MT5 {mt5_id}")
                return {
                    'valid': False,
                    'message': 'Invalid token or MT5 ID'
                }
        
        except Exception as e:
            logger.error(f"Error validating token: {e}")
            return {
                'valid': False,
                'message': f'Validation error: {str(e)}'
            }
    
    async def handle_ohlc_data(self, data: Dict) -> Dict:
        """
        Handle OHLC data from EA and generate signal.
        
        Args:
            data: OHLC data message
        
        Returns:
            Trading signal response
        """
        try:
            # Extract data
            mt5_id = data.get('mt5_id')
            token = data.get('token')
            pair = data.get('pair')
            ohlc_data = data.get('data')
            
            # Validate inputs
            if not all([mt5_id, token, pair, ohlc_data]):
                return {
                    'error': 'Missing required fields'
                }
            
            # Validate token
            if not validate_token(token, mt5_id):
                return {
                    'error': 'Invalid token or MT5 ID'
                }
            
            # Get user info from token
            from database import get_token_info
            token_info = get_token_info(token)
            
            if not token_info:
                return {
                    'error': 'Token not found'
                }
            
            tier = token_info.get('tier', 'PREMIUM')
            
            # Convert OHLC data to numpy array
            ohlc_array = np.array(ohlc_data, dtype=np.float32)
            
            logger.info(f"Processing OHLC data for {pair} (MT5: {mt5_id}, Tier: {tier})")
            
            # Get account balance from data or use default from config
            account_balance = data.get('account_balance', 
                                      getattr(config, 'DEFAULT_ACCOUNT_BALANCE', 10000))
            
            # Generate signal using ML Engine
            signal = self.ml_engine.process_signal(
                ohlc_data=ohlc_array,
                tier=tier,
                account_balance=account_balance
            )
            
            # Check if signal is valid
            if signal.get('action') is None:
                logger.info(f"No signal generated: {signal.get('message')}")
                return {
                    'action': None,
                    'message': signal.get('message'),
                    'confidence': signal.get('confidence', 0)
                }
            
            # Log signal to database
            # Get user_id from MT5 ID
            from database import get_all_users
            users = get_all_users()
            user_id = None
            for user in users:
                if user.get('mt5_id') == mt5_id:
                    user_id = user.get('user_id')
                    break
            
            if user_id:
                save_signal(
                    user_id=user_id,
                    pair=pair,
                    action=signal['action'],
                    entry=signal['entry'],
                    sl=signal['sl'],
                    tp=signal['tp'],
                    lot=signal['lot'],
                    confidence=signal['confidence'],
                    predictions=signal.get('predictions', []),
                    tier=tier
                )
            
            # Prepare response
            response = {
                'action': signal['action'],
                'entry': signal['entry'],
                'sl': signal['sl'],
                'tp': signal['tp'],
                'lot': signal['lot'],
                'confidence': signal['confidence'],
                'predictions': signal.get('predictions', []),
                'message': signal.get('message', 'Signal generated'),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Signal generated: {signal['action']} {pair} @ {signal['entry']} (confidence: {signal['confidence']:.2f}%)")
            
            return response
        
        except Exception as e:
            logger.error(f"Error handling OHLC data: {e}")
            return {
                'error': f'Processing error: {str(e)}'
            }
    
    async def start(self):
        """Start the WebSocket server."""
        try:
            logger.info(f"Starting WebSocket server on {self.host}:{self.port}...")
            
            async with websockets.serve(self.handle_client, self.host, self.port):
                logger.info(f"✅ WebSocket server running on ws://{self.host}:{self.port}")
                await asyncio.Future()  # Run forever
        
        except Exception as e:
            logger.error(f"Error starting WebSocket server: {e}")
            raise
    
    def run(self):
        """Run the WebSocket server (blocking)."""
        try:
            asyncio.run(self.start())
        except KeyboardInterrupt:
            logger.info("WebSocket server stopped by user")
        except Exception as e:
            logger.error(f"WebSocket server error: {e}")

def main():
    """Main entry point for WebSocket server."""
    # Setup logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        handlers=[
            logging.FileHandler('logs/websocket.log'),
            logging.StreamHandler()
        ]
    )
    
    # Create and run server
    server = WebSocketServer()
    server.run()

if __name__ == "__main__":
    main()
