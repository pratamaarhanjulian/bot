"""
Main Telegram Bot implementation
"""

import logging
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

import config
from database import setup_database, create_user, get_user, user_exists
from bot.menu_handler import (
    show_main_menu, handle_menu_callback,
    show_dashboard, show_signals_menu, show_upgrade_menu,
    show_settings_menu, show_guide, show_support
)
from bot.admin_panel import (
    admin_command, admin_password_handler, handle_admin_callback
)
from bot.user_menu import (
    handle_payment_flow, PAYMENT_STATES
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /start command.
    Creates new user if not exists and shows main menu.
    """
    try:
        user_id = update.effective_user.id
        username = update.effective_user.username
        
        # Check if user exists
        if not user_exists(user_id):
            # Create new user with FREE tier
            create_user(user_id, username, 'FREE')
            logger.info(f"New user created: {user_id} (@{username})")
            
            # Welcome message
            welcome_text = (
                "🎉 <b>Selamat Datang di AUREA PRIME ELITE!</b>\n\n"
                "Super AI Trading System dengan 6 model AI terintegrasi:\n"
                "✅ LSTM Neural Network\n"
                "✅ Transformer Model\n"
                "✅ CNN-LSTM Hybrid\n"
                "✅ XGBoost Algorithm\n"
                "✅ DQN Reinforcement Learning\n"
                "✅ PPO Reinforcement Learning\n\n"
                "🆓 Tier FREE: 5 sinyal manual per hari\n"
                "💎 Upgrade untuk mendapatkan:\n"
                "   • Auto signal push\n"
                "   • Auto execution\n"
                "   • Unlimited quota\n"
                "   • Priority support\n\n"
                "Silakan pilih menu di bawah 👇"
            )
            
            await update.message.reply_text(welcome_text, parse_mode='HTML')
        
        # Show main menu
        await show_main_menu(update, context)
    
    except Exception as e:
        logger.error(f"Error in start_command: {e}")
        await update.message.reply_text(
            "❌ Terjadi kesalahan. Silakan coba lagi."
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = (
        "<b>📖 PANDUAN PENGGUNAAN</b>\n\n"
        "<b>Commands:</b>\n"
        "/start - Tampilkan menu utama\n"
        "/help - Tampilkan panduan ini\n"
        "/admin - Panel admin (khusus admin)\n\n"
        "<b>Fitur:</b>\n"
        "📊 Dashboard - Lihat statistik trading\n"
        "📈 Sinyal Harian - Dapatkan sinyal trading\n"
        "💎 Upgrade Paket - Tingkatkan tier akun\n"
        "⚙️ Settings - Pengaturan MT5 dan token\n"
        "📖 Panduan - Tutorial lengkap\n"
        "🎧 Support - Hubungi customer service\n\n"
        "<b>Tier Levels:</b>\n"
        "🆓 FREE - 5 sinyal/hari (manual request)\n"
        "💎 PREMIUM - Auto push sinyal\n"
        "⭐ SUPER - Auto execution\n"
        "👑 SUPREME - Ultra execution\n"
    )
    
    await update.message.reply_text(help_text, parse_mode='HTML')

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}")
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Terjadi kesalahan. Silakan coba lagi atau hubungi support."
            )
    except Exception as e:
        logger.error(f"Error in error_handler: {e}")

def main():
    """Start the bot."""
    try:
        # Initialize database
        setup_database()
        
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        
        # Create application
        application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
        
        # Register handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("admin", admin_command))
        
        # Payment conversation handler
        payment_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(handle_payment_flow, 
                                              pattern='^payment_')],
            states=PAYMENT_STATES,
            fallbacks=[CommandHandler("start", start_command)]
        )
        application.add_handler(payment_conv)
        
        # Callback query handlers
        application.add_handler(CallbackQueryHandler(handle_admin_callback, 
                                                    pattern='^admin_'))
        application.add_handler(CallbackQueryHandler(handle_menu_callback))
        
        # Message handler for admin password
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,
                                              admin_password_handler))
        
        # Error handler
        application.add_error_handler(error_handler)
        
        logger.info("🚀 Bot started successfully!")
        print("=" * 60)
        print("  AUREA PRIME ELITE - Bot Running")
        print("=" * 60)
        print(f"  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Start bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
