"""
User menu and payment flow
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

import config
from database import create_payment, get_user

logger = logging.getLogger(__name__)

# Payment conversation states
PACKAGE_SELECT, DURATION_SELECT, PROOF_UPLOAD = range(3)

PAYMENT_STATES = {
    PACKAGE_SELECT: [],
    DURATION_SELECT: [],
    PROOF_UPLOAD: []
}

async def handle_payment_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle payment flow starting from upgrade menu.
    """
    try:
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        # Parse package type
        if data == 'upgrade_xau':
            context.user_data['package'] = 'XAU'
            package_name = '🥇 XAU Only'
            prices = config.PRICING['XAU']
        elif data == 'upgrade_btc':
            context.user_data['package'] = 'BTC'
            package_name = '₿ BTC Only'
            prices = config.PRICING['BTC']
        elif data == 'upgrade_all':
            context.user_data['package'] = 'ALL'
            package_name = '🌟 All Pairs'
            prices = config.PRICING['ALL']
        elif data == 'upgrade_super':
            await show_super_package(update, context)
            return
        elif data == 'upgrade_supreme':
            await show_supreme_package(update, context)
            return
        else:
            return
        
        # Show duration selection
        duration_text = (
            f"<b>{package_name}</b>\n\n"
            "Pilih durasi:\n"
        )
        
        keyboard = []
        for duration, price in prices.items():
            keyboard.append([
                InlineKeyboardButton(
                    f"{duration} - Rp {price}.000",
                    callback_data=f'payment_duration_{duration}_{price}'
                )
            ])
        
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data='menu_upgrade')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            duration_text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        
        return DURATION_SELECT
    
    except Exception as e:
        logger.error(f"Error in payment flow: {e}")

async def show_super_package(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show SUPER package options (Premium × 1.6).
    """
    try:
        query = update.callback_query
        
        super_text = (
            "⭐ <b>SUPER PACKAGE</b>\n\n"
            "Premium features + Auto Execution:\n"
            "✅ Auto signal push\n"
            "✅ Auto trade execution\n"
            "✅ Adaptive lot size (0.05-0.10)\n"
            "✅ Priority processing\n\n"
            "Pilih pair:\n"
        )
        
        keyboard = [
            [InlineKeyboardButton("🥇 SUPER XAU", callback_data='payment_super_xau')],
            [InlineKeyboardButton("₿ SUPER BTC", callback_data='payment_super_btc')],
            [InlineKeyboardButton("🌟 SUPER All Pairs", callback_data='payment_super_all')],
            [InlineKeyboardButton("⬅️ Back", callback_data='menu_upgrade')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            super_text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    except Exception as e:
        logger.error(f"Error showing super package: {e}")

async def show_supreme_package(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show SUPREME package (fixed price).
    """
    try:
        query = update.callback_query
        
        supreme_text = (
            "👑 <b>SUPREME PACKAGE</b>\n\n"
            "Ultimate trading experience:\n"
            "✅ All SUPER features\n"
            "✅ Ultra priority execution\n"
            "✅ All pairs included\n"
            "✅ Lifetime updates\n"
            "✅ VIP support\n\n"
            f"Price: Rp {config.PRICING['SUPREME_PRICE']}.000\n"
            "(One-time payment)\n"
        )
        
        keyboard = [
            [InlineKeyboardButton(
                f"💎 Buy SUPREME - Rp {config.PRICING['SUPREME_PRICE']}.000",
                callback_data='payment_supreme_buy'
            )],
            [InlineKeyboardButton("⬅️ Back", callback_data='menu_upgrade')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            supreme_text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    except Exception as e:
        logger.error(f"Error showing supreme package: {e}")

async def request_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Request payment proof upload.
    """
    try:
        query = update.callback_query
        await query.answer()
        
        # Extract duration and price from callback data
        data = query.data
        
        if 'payment_duration_' in data:
            parts = data.split('_')
            duration = parts[2]
            price = parts[3]
            package = context.user_data.get('package', 'PREMIUM')
        
        elif 'payment_supreme_buy' in data:
            duration = 'LIFETIME'
            price = config.PRICING['SUPREME_PRICE']
            package = 'SUPREME'
        
        else:
            return
        
        # Store payment info
        context.user_data['duration'] = duration
        context.user_data['price'] = price
        context.user_data['package'] = package
        
        payment_text = (
            "💳 <b>PAYMENT INFORMATION</b>\n\n"
            f"Package: {package}\n"
            f"Duration: {duration}\n"
            f"Amount: Rp {price}.000\n\n"
            "<b>Bank Transfer:</b>\n"
            "BCA: 1234567890\n"
            "a.n. Aurea Prime Elite\n\n"
            "Setelah transfer, upload bukti pembayaran (screenshot).\n"
            "Admin akan verifikasi dalam 1x24 jam.\n"
        )
        
        await query.edit_message_text(
            payment_text,
            parse_mode='HTML'
        )
        
        await query.message.reply_text(
            "📤 Silakan upload bukti pembayaran (gambar):"
        )
        
        return PROOF_UPLOAD
    
    except Exception as e:
        logger.error(f"Error requesting payment proof: {e}")

async def handle_proof_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle payment proof image upload.
    """
    try:
        user_id = update.effective_user.id
        
        # Get photo
        if not update.message.photo:
            await update.message.reply_text(
                "❌ Please upload an image!"
            )
            return PROOF_UPLOAD
        
        # Get largest photo
        photo = update.message.photo[-1]
        file = await photo.get_file()
        
        # Get payment info
        package = context.user_data.get('package')
        duration = context.user_data.get('duration')
        price = context.user_data.get('price')
        
        # Save to database
        payment_id = create_payment(
            user_id=user_id,
            package=package,
            duration=duration,
            amount=int(price),
            proof_url=file.file_path
        )
        
        if payment_id:
            await update.message.reply_text(
                "✅ <b>Payment Submitted!</b>\n\n"
                f"Payment ID: #{payment_id}\n"
                "Status: Pending Verification\n\n"
                "Admin akan verifikasi pembayaran Anda.\n"
                "Anda akan menerima notifikasi setelah diverifikasi.\n\n"
                "Terima kasih! 🙏",
                parse_mode='HTML'
            )
            
            # Notify admin
            try:
                await context.bot.send_message(
                    chat_id=config.ADMIN_CHAT_ID,
                    text=(
                        f"💳 <b>New Payment</b>\n\n"
                        f"ID: #{payment_id}\n"
                        f"User: @{update.effective_user.username}\n"
                        f"Package: {package}\n"
                        f"Duration: {duration}\n"
                        f"Amount: Rp {price}.000\n\n"
                        "Use /admin to verify"
                    ),
                    parse_mode='HTML'
                )
            except:
                pass
        else:
            await update.message.reply_text(
                "❌ Failed to submit payment. Please try again."
            )
        
        # Clear user data
        context.user_data.clear()
        
        return ConversationHandler.END
    
    except Exception as e:
        logger.error(f"Error handling proof upload: {e}")
        return ConversationHandler.END
