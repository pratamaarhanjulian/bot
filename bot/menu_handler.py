"""
Menu handler with inline keyboards
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import config
from database import get_user, get_user_stats

logger = logging.getLogger(__name__)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show main menu with inline keyboard.
    """
    try:
        menu_text = (
            "👑 <b>AUREA PRIME ELITE</b>\n"
            "Super AI Trading System\n\n"
            "Pilih menu:\n"
        )
        
        keyboard = [
            [InlineKeyboardButton("📊 Dashboard", callback_data='menu_dashboard')],
            [InlineKeyboardButton("📈 Sinyal Harian", callback_data='menu_signals')],
            [InlineKeyboardButton("💎 Upgrade Paket", callback_data='menu_upgrade')],
            [InlineKeyboardButton("⚙️ Settings", callback_data='menu_settings')],
            [InlineKeyboardButton("📖 Panduan", callback_data='menu_guide')],
            [InlineKeyboardButton("🎧 Support", callback_data='menu_support')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Check if it's a message or callback query
        if update.message:
            await update.message.reply_text(
                menu_text, 
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        elif update.callback_query:
            await update.callback_query.edit_message_text(
                menu_text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
    
    except Exception as e:
        logger.error(f"Error showing main menu: {e}")

async def show_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user dashboard with statistics."""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        user = get_user(user_id)
        stats = get_user_stats(user_id)
        
        # Format dashboard
        tier_emoji = {
            'FREE': '🆓',
            'PREMIUM': '💎',
            'SUPER': '⭐',
            'SUPREME': '👑'
        }
        
        mt5_status = "✅ Connected" if user['mt5_id'] else "❌ Not Connected"
        
        dashboard_text = (
            f"📊 <b>DASHBOARD</b>\n\n"
            f"<b>Status Akun:</b>\n"
            f"├ Tier: {tier_emoji.get(user['tier'], '🆓')} {user['tier']}\n"
            f"├ MT5: {mt5_status}\n"
            f"├ Token: {user['token'] or 'Belum ada'}\n"
            f"└ Quota: {user['signal_quota'] if user['signal_quota'] > 0 else 'Unlimited'}\n\n"
            f"<b>Stats Hari Ini:</b>\n"
            f"├ Sinyal: {stats['today']['count']}\n"
            f"└ Profit: ${stats['today']['profit']:.2f}\n\n"
            f"<b>Total Stats (30 hari):</b>\n"
            f"├ Total Trades: {stats['total_trades']}\n"
            f"├ Win Rate: {stats['win_rate']:.1f}%\n"
            f"├ Total Profit: ${stats['total_profit']:.2f}\n"
            f"└ Max Drawdown: ${stats['max_drawdown']:.2f}\n"
        )
        
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh", callback_data='menu_dashboard')],
            [InlineKeyboardButton("⬅️ Back", callback_data='menu_main')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            dashboard_text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    except Exception as e:
        logger.error(f"Error showing dashboard: {e}")

async def show_signals_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show signals menu based on user tier."""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        user = get_user(user_id)
        
        if user['tier'] == 'FREE':
            signals_text = (
                "📈 <b>SINYAL HARIAN</b>\n\n"
                f"Tier: 🆓 FREE\n"
                f"Quota: {user['signal_quota']}/5\n\n"
                "Klik tombol di bawah untuk request sinyal.\n"
                "Sinyal akan dikirim berdasarkan analisis 6 model AI.\n\n"
                "💎 Upgrade ke PREMIUM untuk:\n"
                "• Auto push sinyal\n"
                "• Unlimited quota\n"
                "• Higher lot size\n"
            )
            
            keyboard = [
                [InlineKeyboardButton("📊 Request Sinyal", callback_data='signal_request')],
                [InlineKeyboardButton("💎 Upgrade Now", callback_data='menu_upgrade')],
                [InlineKeyboardButton("⬅️ Back", callback_data='menu_main')]
            ]
        
        else:
            signals_text = (
                "📈 <b>SINYAL HARIAN</b>\n\n"
                f"Tier: {user['tier']}\n"
                f"Mode: {'Auto Execution' if user['tier'] in ['SUPER', 'SUPREME'] else 'Auto Push'}\n\n"
                "Sinyal otomatis akan dikirim ketika:\n"
                "✅ Confidence ≥ 85%\n"
                "✅ Market conditions optimal\n"
                "✅ Risk management terpenuhi\n\n"
                "Anda akan menerima notifikasi otomatis.\n"
            )
            
            keyboard = [
                [InlineKeyboardButton("📊 View History", callback_data='signal_history')],
                [InlineKeyboardButton("⬅️ Back", callback_data='menu_main')]
            ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            signals_text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    except Exception as e:
        logger.error(f"Error showing signals menu: {e}")

async def show_upgrade_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show upgrade packages menu."""
    try:
        query = update.callback_query
        await query.answer()
        
        upgrade_text = (
            "💎 <b>UPGRADE PAKET</b>\n\n"
            "Pilih paket trading:\n"
        )
        
        keyboard = [
            [InlineKeyboardButton("🥇 XAU Only", callback_data='upgrade_xau')],
            [InlineKeyboardButton("₿ BTC Only", callback_data='upgrade_btc')],
            [InlineKeyboardButton("🌟 All Pairs", callback_data='upgrade_all')],
            [InlineKeyboardButton("⭐ SUPER Package", callback_data='upgrade_super')],
            [InlineKeyboardButton("👑 SUPREME Package", callback_data='upgrade_supreme')],
            [InlineKeyboardButton("⬅️ Back", callback_data='menu_main')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            upgrade_text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    except Exception as e:
        logger.error(f"Error showing upgrade menu: {e}")

async def show_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show settings menu."""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        user = get_user(user_id)
        
        settings_text = (
            "⚙️ <b>SETTINGS</b>\n\n"
            f"<b>MT5 Account:</b> {user['mt5_id'] or 'Not Set'}\n"
            f"<b>Access Token:</b> {user['token'] or 'Not Set'}\n\n"
            "Untuk menggunakan auto-execution, Anda perlu:\n"
            "1. Install Expert Advisor (EA) di MT5\n"
            "2. Input token di EA settings\n"
            "3. Enable auto trading di MT5\n"
        )
        
        keyboard = [
            [InlineKeyboardButton("📥 Download EA", callback_data='settings_download_ea')],
            [InlineKeyboardButton("🔑 View Token", callback_data='settings_view_token')],
            [InlineKeyboardButton("📖 Setup Guide", callback_data='settings_guide')],
            [InlineKeyboardButton("⬅️ Back", callback_data='menu_main')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            settings_text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    except Exception as e:
        logger.error(f"Error showing settings menu: {e}")

async def show_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user guide."""
    try:
        query = update.callback_query
        await query.answer()
        
        guide_text = (
            "📖 <b>PANDUAN LENGKAP</b>\n\n"
            "<b>1. Cara Kerja Sistem:</b>\n"
            "   • 6 AI models menganalisis market 24/7\n"
            "   • Sinyal hanya dikirim jika confidence ≥ 85%\n"
            "   • Risk management otomatis (SL/TP adaptive)\n\n"
            "<b>2. Tier Levels:</b>\n"
            "   🆓 FREE: 5 sinyal manual/hari\n"
            "   💎 PREMIUM: Auto push unlimited\n"
            "   ⭐ SUPER: Auto execution dengan lot adaptif\n"
            "   👑 SUPREME: Ultra execution priority\n\n"
            "<b>3. Setup MT5:</b>\n"
            "   • Download EA dari Settings\n"
            "   • Copy ke folder Experts MT5\n"
            "   • Input token dari Settings\n"
            "   • Enable auto trading\n\n"
            "<b>4. Support:</b>\n"
            "   Hubungi admin untuk bantuan\n"
        )
        
        keyboard = [
            [InlineKeyboardButton("⬅️ Back", callback_data='menu_main')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            guide_text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    except Exception as e:
        logger.error(f"Error showing guide: {e}")

async def show_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show support information."""
    try:
        query = update.callback_query
        await query.answer()
        
        support_text = (
            "🎧 <b>CUSTOMER SUPPORT</b>\n\n"
            "Butuh bantuan? Hubungi kami:\n\n"
            "📱 Admin: @AureaPrimeAdmin\n"
            "💬 Group: @AureaPrimeGroup\n"
            "📧 Email: support@aureaprime.com\n\n"
            "<b>Jam Operasional:</b>\n"
            "Senin - Jumat: 08:00 - 20:00 WIB\n"
            "Sabtu: 08:00 - 16:00 WIB\n"
            "Minggu: Libur\n\n"
            "Response time: < 1 jam (jam kerja)\n"
        )
        
        keyboard = [
            [InlineKeyboardButton("💬 Contact Admin", url='https://t.me/AureaPrimeAdmin')],
            [InlineKeyboardButton("⬅️ Back", callback_data='menu_main')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            support_text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    except Exception as e:
        logger.error(f"Error showing support: {e}")

async def handle_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle all menu callback queries.
    """
    try:
        query = update.callback_query
        data = query.data
        
        # Route to appropriate handler
        if data == 'menu_main':
            await show_main_menu(update, context)
        elif data == 'menu_dashboard':
            await show_dashboard(update, context)
        elif data == 'menu_signals':
            await show_signals_menu(update, context)
        elif data == 'menu_upgrade':
            await show_upgrade_menu(update, context)
        elif data == 'menu_settings':
            await show_settings_menu(update, context)
        elif data == 'menu_guide':
            await show_guide(update, context)
        elif data == 'menu_support':
            await show_support(update, context)
        else:
            await query.answer("Feature coming soon!")
    
    except Exception as e:
        logger.error(f"Error handling menu callback: {e}")
