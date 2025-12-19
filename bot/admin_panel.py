"""
Admin panel with password protection
"""

import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import config
from database import (
    get_pending_payments, get_payment, update_payment_status,
    create_token, get_all_tokens, get_all_users, update_user_tier
)

logger = logging.getLogger(__name__)

# Store admin authentication state
admin_authenticated = {}

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /admin command with password protection.
    """
    try:
        user_id = update.effective_user.id
        
        # Check if already authenticated
        if admin_authenticated.get(user_id):
            await show_admin_panel(update, context)
        else:
            # Request password
            context.user_data['awaiting_admin_password'] = True
            await update.message.reply_text(
                "🔐 <b>Admin Authentication</b>\n\n"
                "Please enter admin password:",
                parse_mode='HTML'
            )
    
    except Exception as e:
        logger.error(f"Error in admin_command: {e}")

async def admin_password_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle admin password input.
    """
    try:
        # Check if we're waiting for admin password
        if not context.user_data.get('awaiting_admin_password'):
            return
        
        user_id = update.effective_user.id
        password = update.message.text.strip()
        
        # Verify password using constant-time comparison
        import hmac
        expected = config.ADMIN_PASSWORD.encode('utf-8')
        provided = password.encode('utf-8')
        
        if hmac.compare_digest(expected, provided):
            admin_authenticated[user_id] = True
            context.user_data['awaiting_admin_password'] = False
            
            # Delete password message for security
            try:
                await update.message.delete()
            except:
                pass
            
            await update.message.reply_text(
                "✅ Authentication successful!\n"
                "Loading admin panel..."
            )
            
            # Show admin panel
            await show_admin_panel(update, context)
        
        else:
            await update.message.reply_text(
                "❌ Invalid password!\n"
                "Try again with /admin"
            )
            context.user_data['awaiting_admin_password'] = False
    
    except Exception as e:
        logger.error(f"Error in admin_password_handler: {e}")

async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show admin panel main menu.
    """
    try:
        # Get statistics
        all_users = get_all_users()
        pending_payments = get_pending_payments()
        
        # Count users by tier
        tier_counts = {
            'FREE': 0,
            'PREMIUM': 0,
            'SUPER': 0,
            'SUPREME': 0
        }
        for user in all_users:
            tier = user.get('tier', 'FREE')
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        admin_text = (
            "👑 <b>ADMIN PANEL</b>\n"
            "Aurea Prime Elite\n\n"
            f"<b>System Stats:</b>\n"
            f"├ Total Users: {len(all_users)}\n"
            f"├ FREE: {tier_counts['FREE']}\n"
            f"├ PREMIUM: {tier_counts['PREMIUM']}\n"
            f"├ SUPER: {tier_counts['SUPER']}\n"
            f"└ SUPREME: {tier_counts['SUPREME']}\n\n"
            f"<b>Pending Actions:</b>\n"
            f"└ Payment Verifications: {len(pending_payments)}\n"
        )
        
        keyboard = [
            [InlineKeyboardButton(f"💳 Verify Payments ({len(pending_payments)})", 
                                 callback_data='admin_payments')],
            [InlineKeyboardButton("🔑 Generate Token", 
                                 callback_data='admin_generate_token')],
            [InlineKeyboardButton("📊 View Tokens", 
                                 callback_data='admin_view_tokens')],
            [InlineKeyboardButton("📢 Broadcast Message", 
                                 callback_data='admin_broadcast')],
            [InlineKeyboardButton("📈 System Stats", 
                                 callback_data='admin_stats')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Check if it's message or callback
        if update.message:
            await update.message.reply_text(
                admin_text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        elif update.callback_query:
            await update.callback_query.edit_message_text(
                admin_text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
    
    except Exception as e:
        logger.error(f"Error showing admin panel: {e}")

async def show_pending_payments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show pending payment verifications.
    """
    try:
        query = update.callback_query
        await query.answer()
        
        payments = get_pending_payments()
        
        if not payments:
            await query.edit_message_text(
                "✅ No pending payments!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("⬅️ Back", callback_data='admin_main')
                ]])
            )
            return
        
        # Show first payment
        payment = payments[0]
        
        payment_text = (
            f"💳 <b>PAYMENT VERIFICATION</b>\n\n"
            f"<b>Payment ID:</b> {payment['id']}\n"
            f"<b>User:</b> @{payment.get('username', 'Unknown')} ({payment['user_id']})\n"
            f"<b>Package:</b> {payment['package']}\n"
            f"<b>Duration:</b> {payment['duration']}\n"
            f"<b>Amount:</b> Rp {payment['amount']}.000\n"
            f"<b>Date:</b> {payment['created_at']}\n\n"
            f"<b>Proof:</b> Check image below\n"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Approve", 
                                   callback_data=f'admin_approve_{payment["id"]}'),
                InlineKeyboardButton("❌ Reject", 
                                   callback_data=f'admin_reject_{payment["id"]}')
            ],
            [InlineKeyboardButton("⏭️ Next", callback_data='admin_payments')],
            [InlineKeyboardButton("⬅️ Back", callback_data='admin_main')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send payment proof image
        await query.message.reply_photo(
            photo=payment['proof_url'],
            caption=payment_text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        
        # Delete previous message
        try:
            await query.message.delete()
        except:
            pass
    
    except Exception as e:
        logger.error(f"Error showing pending payments: {e}")

async def approve_payment(update: Update, context: ContextTypes.DEFAULT_TYPE, payment_id: int):
    """
    Approve a payment and generate token.
    """
    try:
        query = update.callback_query
        
        # Get payment info
        payment = get_payment(payment_id)
        if not payment:
            await query.answer("Payment not found!")
            return
        
        # Update payment status
        update_payment_status(payment_id, 'APPROVED')
        
        # Generate token
        from datetime import timedelta
        duration_map = {
            '1M': 30,
            '3M': 90,
            '6M': 180,
            '12M': 365,
            'LIFETIME': 3650
        }
        days = duration_map.get(payment['duration'], 30)
        expired_at = datetime.now() + timedelta(days=days)
        
        # Determine tier from package
        tier = 'PREMIUM'
        if payment['package'] == 'SUPER':
            tier = 'SUPER'
        elif payment['package'] == 'SUPREME':
            tier = 'SUPREME'
        
        # Create token (MT5 ID will be set by user later)
        token = create_token('PENDING', tier, expired_at)
        
        if token:
            # Update user tier
            update_user_tier(payment['user_id'], tier, token, '', expired_at)
            
            # Notify user
            try:
                await context.bot.send_message(
                    chat_id=payment['user_id'],
                    text=(
                        f"✅ <b>Payment Approved!</b>\n\n"
                        f"Package: {payment['package']}\n"
                        f"Duration: {payment['duration']}\n"
                        f"Tier: {tier}\n\n"
                        f"🔑 <b>Your Token:</b> <code>{token}</code>\n\n"
                        f"Silakan input token ini di EA MT5 Anda.\n"
                        f"Expired: {expired_at.strftime('%Y-%m-%d')}"
                    ),
                    parse_mode='HTML'
                )
            except:
                pass
            
            await query.answer("✅ Payment approved!")
            await query.edit_message_caption(
                caption=f"✅ Approved!\n\nToken: {token}\nUser will be notified.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("⬅️ Back", callback_data='admin_main')
                ]])
            )
        else:
            await query.answer("❌ Failed to generate token!")
    
    except Exception as e:
        logger.error(f"Error approving payment: {e}")

async def reject_payment(update: Update, context: ContextTypes.DEFAULT_TYPE, payment_id: int):
    """
    Reject a payment.
    """
    try:
        query = update.callback_query
        
        # Get payment info
        payment = get_payment(payment_id)
        if not payment:
            await query.answer("Payment not found!")
            return
        
        # Update payment status
        update_payment_status(payment_id, 'REJECTED')
        
        # Notify user
        try:
            await context.bot.send_message(
                chat_id=payment['user_id'],
                text=(
                    "❌ <b>Payment Rejected</b>\n\n"
                    "Maaf, pembayaran Anda tidak dapat diverifikasi.\n"
                    "Silakan hubungi admin untuk informasi lebih lanjut."
                ),
                parse_mode='HTML'
            )
        except:
            pass
        
        await query.answer("❌ Payment rejected!")
        await query.edit_message_caption(
            caption="❌ Rejected!\nUser will be notified.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("⬅️ Back", callback_data='admin_main')
            ]])
        )
    
    except Exception as e:
        logger.error(f"Error rejecting payment: {e}")

async def show_tokens(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show all generated tokens.
    """
    try:
        query = update.callback_query
        await query.answer()
        
        tokens = get_all_tokens()
        
        if not tokens:
            tokens_text = "No tokens generated yet."
        else:
            tokens_text = "<b>🔑 GENERATED TOKENS</b>\n\n"
            for token in tokens[:10]:  # Show last 10
                tokens_text += (
                    f"Token: <code>{token['token']}</code>\n"
                    f"MT5: {token['mt5_id']}\n"
                    f"Tier: {token['tier']}\n"
                    f"Expires: {token['expired_at']}\n\n"
                )
        
        keyboard = [
            [InlineKeyboardButton("⬅️ Back", callback_data='admin_main')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            tokens_text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    except Exception as e:
        logger.error(f"Error showing tokens: {e}")

async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle admin panel callbacks.
    """
    try:
        query = update.callback_query
        data = query.data
        
        # Check authentication
        user_id = update.effective_user.id
        if not admin_authenticated.get(user_id):
            await query.answer("❌ Authentication required!")
            return
        
        # Route to handler
        if data == 'admin_main':
            await show_admin_panel(update, context)
        elif data == 'admin_payments':
            await show_pending_payments(update, context)
        elif data.startswith('admin_approve_'):
            payment_id = int(data.split('_')[2])
            await approve_payment(update, context, payment_id)
        elif data.startswith('admin_reject_'):
            payment_id = int(data.split('_')[2])
            await reject_payment(update, context, payment_id)
        elif data == 'admin_view_tokens':
            await show_tokens(update, context)
        else:
            await query.answer("Feature coming soon!")
    
    except Exception as e:
        logger.error(f"Error handling admin callback: {e}")
