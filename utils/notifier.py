"""
Notifier Module
Send notifications via Telegram
"""

import logging
from typing import Optional
from datetime import datetime
import asyncio
from telegram import Bot
from telegram.error import TelegramError


class TelegramNotifier:
    """
    Send notifications via Telegram bot
    """
    
    def __init__(self, bot_token: str, chat_id: str, enabled: bool = True):
        """
        Initialize Telegram notifier
        
        Args:
            bot_token: Telegram bot token
            chat_id: Telegram chat ID
            enabled: Enable/disable notifications
        """
        self.logger = logging.getLogger(__name__)
        self.enabled = enabled
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot = None
        
        if enabled and bot_token and chat_id:
            try:
                self.bot = Bot(token=bot_token)
                self.logger.info("Telegram notifier initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Telegram bot: {e}")
                self.enabled = False
        else:
            self.logger.warning("Telegram notifications disabled")
    
    async def send_message(self, message: str, parse_mode: str = 'HTML'):
        """
        Send message to Telegram
        
        Args:
            message: Message text
            parse_mode: Parse mode (HTML, Markdown)
        """
        if not self.enabled or not self.bot:
            self.logger.debug("Telegram notification skipped (disabled)")
            return
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode
            )
            self.logger.debug("Telegram message sent")
        except TelegramError as e:
            self.logger.error(f"Failed to send Telegram message: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error sending Telegram message: {e}")
    
    def send_message_sync(self, message: str, parse_mode: str = 'HTML'):
        """
        Synchronous wrapper for send_message
        
        Args:
            message: Message text
            parse_mode: Parse mode
        """
        try:
            asyncio.run(self.send_message(message, parse_mode))
        except RuntimeError:
            # If event loop is already running, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.send_message(message, parse_mode))
            loop.close()
    
    def notify_trade(self, trade_info: dict):
        """
        Send trade notification
        
        Args:
            trade_info: Trade information dict
        """
        message = f"""
🤖 <b>TRADE EXECUTED</b>

📊 Symbol: <code>{trade_info.get('symbol')}</code>
{'📈' if trade_info.get('side') == 'LONG' else '📉'} Side: <b>{trade_info.get('side')}</b>
💰 Size: <code>{trade_info.get('amount'):.4f}</code>
💵 Entry: <code>${trade_info.get('entry_price'):.2f}</code>

🛑 Stop Loss: <code>${trade_info.get('stop_loss'):.2f}</code>
🎯 Take Profit: <code>${trade_info.get('take_profit'):.2f}</code>

📊 Confidence: <b>{trade_info.get('confidence', 0):.1%}</b>
🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        self.send_message_sync(message)
    
    def notify_signal(self, signal: dict):
        """
        Send signal notification
        
        Args:
            signal: Signal dict
        """
        emoji = '🟢' if signal['signal'] == 'BUY' else '🔴' if signal['signal'] == 'SELL' else '⚪'
        
        message = f"""
{emoji} <b>SIGNAL: {signal['signal']}</b>

📊 Confidence: <b>{signal.get('confidence', 0):.1%}</b>
🕐 Time: {datetime.now().strftime('%H:%M:%S')}
"""
        self.send_message_sync(message)
    
    def notify_pnl(self, pnl_info: dict):
        """
        Send PnL notification
        
        Args:
            pnl_info: PnL information dict
        """
        pnl = pnl_info.get('pnl', 0)
        emoji = '✅' if pnl >= 0 else '❌'
        
        message = f"""
{emoji} <b>POSITION CLOSED - {'PROFIT' if pnl >= 0 else 'LOSS'}</b>

📊 Symbol: <code>{pnl_info.get('symbol')}</code>
{'📈' if pnl_info.get('side') == 'LONG' else '📉'} Side: <b>{pnl_info.get('side')}</b>

💵 Entry: <code>${pnl_info.get('entry_price'):.2f}</code>
💵 Exit: <code>${pnl_info.get('exit_price'):.2f}</code>

💰 PnL: <b>${pnl:.2f}</b> ({pnl_info.get('pnl_percent', 0):+.2f}%)
⏱ Duration: {pnl_info.get('duration', 'N/A')}
"""
        self.send_message_sync(message)
    
    def notify_error(self, error: Exception, context: dict = None):
        """
        Send error notification
        
        Args:
            error: Exception object
            context: Additional context
        """
        message = f"""
⚠️ <b>ERROR OCCURRED</b>

🔴 Type: <code>{type(error).__name__}</code>
📝 Message: {str(error)}

🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        if context:
            message += f"\n📋 Context: <code>{context}</code>"
        
        self.send_message_sync(message)
    
    def notify_daily_summary(self, summary: dict):
        """
        Send daily summary notification
        
        Args:
            summary: Summary dict
        """
        win_rate = summary.get('win_rate', 0)
        pnl = summary.get('total_pnl', 0)
        emoji = '📈' if pnl >= 0 else '📉'
        
        message = f"""
{emoji} <b>DAILY SUMMARY</b>

📅 Date: {summary.get('date', datetime.now().date())}

📊 Trades: <b>{summary.get('total_trades', 0)}</b>
✅ Wins: <b>{summary.get('wins', 0)}</b>
❌ Losses: <b>{summary.get('losses', 0)}</b>
📈 Win Rate: <b>{win_rate:.1%}</b>

💰 Total PnL: <b>${pnl:+.2f}</b>
🔼 Best Trade: <code>${summary.get('best_trade', 0):.2f}</code>
🔽 Worst Trade: <code>${summary.get('worst_trade', 0):.2f}</code>

💵 Capital: <b>${summary.get('current_capital', 0):.2f}</b>
"""
        self.send_message_sync(message)
    
    def notify_start(self):
        """Send bot start notification"""
        message = f"""
🚀 <b>BOT STARTED</b>

🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
✅ Status: <b>Running</b>
"""
        self.send_message_sync(message)
    
    def notify_stop(self, reason: str = "User stopped"):
        """
        Send bot stop notification
        
        Args:
            reason: Stop reason
        """
        message = f"""
🛑 <b>BOT STOPPED</b>

📝 Reason: {reason}
🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        self.send_message_sync(message)


if __name__ == "__main__":
    # Test notifier
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    notifier = TelegramNotifier(
        bot_token=os.getenv('TELEGRAM_BOT_TOKEN', ''),
        chat_id=os.getenv('TELEGRAM_CHAT_ID', ''),
        enabled=True
    )
    
    # Test trade notification
    trade_info = {
        'symbol': 'SOL/USDT:USDT',
        'side': 'LONG',
        'amount': 0.5,
        'entry_price': 100.50,
        'stop_loss': 98.00,
        'take_profit': 104.00,
        'confidence': 0.75
    }
    notifier.notify_trade(trade_info)
    
    # Test signal notification
    signal = {
        'signal': 'BUY',
        'confidence': 0.68
    }
    notifier.notify_signal(signal)
    
    # Test PnL notification
    pnl_info = {
        'symbol': 'SOL/USDT:USDT',
        'side': 'LONG',
        'entry_price': 100.50,
        'exit_price': 102.30,
        'pnl': 9.00,
        'pnl_percent': 1.79,
        'duration': '15 minutes'
    }
    notifier.notify_pnl(pnl_info)
