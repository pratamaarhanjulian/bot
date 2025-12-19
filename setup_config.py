import os
import getpass
import sys

def main():
    """
    Interactive wizard to setup configuration.
    Asks for 3 inputs and generates config.py file.
    """
    print("=" * 60)
    print("  AUREA PRIME ELITE - Configuration Setup")
    print("=" * 60)
    print()
    
    # Input 1: Telegram Bot Token
    print("1. Telegram Bot Token")
    print("   Get from: @BotFather on Telegram")
    bot_token = input("   Enter Bot Token: ").strip()
    
    if not bot_token:
        print("❌ Bot Token cannot be empty!")
        sys.exit(1)
    
    print("✅ Bot Token saved\n")
    
    # Input 2: Admin Chat ID
    print("2. Admin Chat ID")
    print("   Get from: @userinfobot on Telegram")
    admin_id = input("   Enter Admin Chat ID: ").strip()
    
    if not admin_id:
        print("❌ Admin Chat ID cannot be empty!")
        sys.exit(1)
    
    print("✅ Admin Chat ID saved\n")
    
    # Input 3: OpenRouter API Key
    print("3. OpenRouter API Key")
    print("   Get from: https://openrouter.ai")
    api_key = input("   Enter API Key: ").strip()
    
    if not api_key:
        print("❌ API Key cannot be empty!")
        sys.exit(1)
    
    print("✅ API Key saved\n")
    
    # Generate config.py
    config_content = f'''"""
Auto-generated configuration file.
DO NOT COMMIT THIS FILE!
"""

TELEGRAM_BOT_TOKEN = "{bot_token}"
ADMIN_CHAT_ID = "{admin_id}"
OPENROUTER_API_KEY = "{api_key}"

# Database
DATABASE_PATH = "database/aurea_prime.db"

# WebSocket Server
WEBSOCKET_HOST = "127.0.0.1"
WEBSOCKET_PORT = 8080

# Admin Password
ADMIN_PASSWORD = "oncoy"

# Confidence Threshold
MIN_CONFIDENCE = 85.0

# Pricing (in IDR thousands)
PRICING = {{
    "XAU": {{
        "1M": 49,
        "3M": 119,
        "6M": 299,
        "12M": 499,
        "LIFETIME": 999
    }},
    "BTC": {{
        "1M": 39,
        "3M": 99,
        "6M": 179,
        "12M": 319,
        "LIFETIME": 799
    }},
    "ALL": {{
        "1M": 99,
        "3M": 219,
        "6M": 389,
        "12M": 699,
        "LIFETIME": 1499
    }},
    "SUPER_MULTIPLIER": 1.6,
    "SUPREME_PRICE": 2999
}}

# Tier Quotas
TIER_QUOTAS = {{
    "FREE": 5,
    "PREMIUM": -1,  # Unlimited
    "SUPER": -1,
    "SUPREME": -1
}}

# Lot Sizes
LOT_SIZES = {{
    "FREE": 0.01,
    "PREMIUM": {{
        "min": 0.02,
        "max": 0.05
    }},
    "SUPER": {{
        "min": 0.05,
        "max": 0.10
    }},
    "SUPREME": {{
        "min": 0.05,
        "max": 0.10
    }}
}}
'''
    
    with open("config.py", "w") as f:
        f.write(config_content)
    
    print("=" * 60)
    print("✅ Configuration file created successfully!")
    print("   File: config.py")
    print("=" * 60)
    print()
    print("⚠️  IMPORTANT: Never commit config.py to git!")
    print()

if __name__ == "__main__":
    main()
