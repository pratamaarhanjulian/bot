# 👑 Aurea Prime Elite - AI Trading System

Super AI Trading System berbasis 6 model AI dengan integrasi Telegram Bot dan MetaTrader 5.

## 🌟 Features

### 6 AI Models Ensemble
- **LSTM Neural Network** - Deep learning untuk time series prediction
- **Transformer Model** - Multi-head attention mechanism
- **CNN-LSTM Hybrid** - Convolutional + LSTM untuk feature extraction
- **XGBoost** - Gradient boosting untuk robust predictions
- **DQN Agent** - Deep Q-Network untuk entry/exit optimization
- **PPO Agent** - Proximal Policy Optimization untuk adaptive trading

### Tier Levels
- 🆓 **FREE** - 5 sinyal manual per hari
- 💎 **PREMIUM** - Auto push sinyal unlimited
- ⭐ **SUPER** - Auto execution dengan lot adaptif
- 👑 **SUPREME** - Ultra execution priority dengan all pairs

### Key Features
- ✅ Confidence threshold 85% (hanya trade jika prediksi sangat akurat)
- ✅ Adaptive Stop Loss & Take Profit (berdasarkan ATR & confidence)
- ✅ Risk-based lot calculation
- ✅ WebSocket integration dengan MT5
- ✅ Real-time signal generation
- ✅ Online learning & model updates
- ✅ Payment system terintegrasi
- ✅ Admin panel untuk verifikasi

## 📦 Installation

### Requirements
- Windows 10/11
- Python 3.9 atau lebih tinggi
- MetaTrader 5
- Telegram Bot Token (dari @BotFather)
- Admin Chat ID (dari @userinfobot)
- OpenRouter API Key (dari openrouter.ai)

### Quick Start

1. **Clone repository**
```bash
git clone https://github.com/pratamaarhanjulian/bot.git
cd bot
```

2. **Run setup**
```bash
setup.bat
```

Setup akan:
- Install Python dependencies
- Create virtual environment
- Setup database
- Run configuration wizard

3. **Configure sistem**

Saat setup, Anda akan diminta 3 input:
- Telegram Bot Token
- Admin Chat ID
- OpenRouter API Key

4. **Start sistem**
```bash
start.bat
```

## 📁 Project Structure

```
/
├── setup.bat                  # Windows installer
├── start.bat                  # Start script
├── config.py                  # Auto-generated config
├── requirements.txt           # Dependencies
├── setup_config.py            # Setup wizard
│
├── bot/                       # Telegram Bot
│   ├── telegram_bot.py        # Main bot
│   ├── menu_handler.py        # Menu & buttons
│   ├── admin_panel.py         # Admin functions
│   └── user_menu.py           # User interface
│
├── engine/                    # AI Engine
│   ├── ml_engine.py           # Main ML engine
│   ├── lstm_model.py          # LSTM
│   ├── transformer_model.py   # Transformer
│   ├── cnn_lstm_model.py      # CNN-LSTM
│   ├── xgboost_model.py       # XGBoost
│   ├── dqn_agent.py           # DQN RL
│   ├── ppo_agent.py           # PPO RL
│   ├── ensemble.py            # Ensemble predictor
│   ├── learning_engine.py     # Training
│   └── trade_manager.py       # Trade management
│
├── mt5/                       # MT5 Integration
│   ├── websocket_server.py    # WebSocket server
│   ├── mt5_connector.py       # OHLC receiver
│   └── signal_sender.py       # Signal sender
│
├── data/                      # Data Management
│   ├── downloader.py          # Data downloader
│   ├── preprocessor.py        # Feature engineering
│   └── storage.py             # Data storage
│
├── database/                  # Database
│   ├── schema.sql             # DB schema
│   ├── setup_db.py            # DB initialization
│   ├── user_db.py             # User management
│   ├── token_db.py            # Token system
│   ├── payment_db.py          # Payment tracking
│   └── trade_db.py            # Trade history
│
├── payment/                   # Payment System
│   ├── invoice.py             # Invoice generator
│   └── verifier.py            # Payment verifier
│
├── ea/                        # Expert Advisor
│   ├── AureaPrime.mq5         # Main EA
│   └── config.mqh             # EA config
│
└── models/                    # Trained models
    └── .gitkeep
```

## 🤖 Telegram Bot Usage

### User Commands
- `/start` - Tampilkan main menu
- `/help` - Panduan penggunaan

### Admin Commands
- `/admin` - Access admin panel (password: "oncoy")

### Main Menu
```
👑 AUREA PRIME ELITE
Super AI Trading System

┌─────────────────────┐
│ 📊 Dashboard        │
│ 📈 Sinyal Harian    │
│ 💎 Upgrade Paket    │
│ ⚙️ Settings         │
│ 📖 Panduan          │
│ 🎧 Support          │
└─────────────────────┘
```

## 💎 Pricing

### XAU Only
- 1 Month: Rp 49.000
- 3 Months: Rp 119.000
- 6 Months: Rp 299.000
- 12 Months: Rp 499.000
- Lifetime: Rp 999.000

### BTC Only
- 1 Month: Rp 39.000
- 3 Months: Rp 99.000
- 6 Months: Rp 179.000
- 12 Months: Rp 319.000
- Lifetime: Rp 799.000

### All Pairs
- 1 Month: Rp 99.000
- 3 Months: Rp 219.000
- 6 Months: Rp 389.000
- 12 Months: Rp 699.000
- Lifetime: Rp 1.499.000

### SUPER Package
Premium × 1.6 (with auto-execution)

### SUPREME Package
Rp 2.999.000 (one-time, all features)

## 🔧 MT5 Setup

1. **Copy EA to MT5**
```
Copy ea/AureaPrime.mq5 to:
C:\Users\[User]\AppData\Roaming\MetaQuotes\Terminal\[ID]\MQL5\Experts\
```

2. **Compile EA**
- Open MetaEditor
- Open AureaPrime.mq5
- Press F7 to compile

3. **Configure EA**
- Drag EA to chart
- Input your token from Settings
- Set ServerIP (default: 127.0.0.1)
- Enable AutoExecution if desired
- Enable algo trading in MT5

## 🌐 WebSocket Server

WebSocket server runs on port 8080 and handles:
- Token validation
- OHLC data receiving
- Signal generation
- Real-time communication with EA

Start WebSocket server:
```python
python mt5/websocket_server.py
```

## 📊 AI Model Details

### Ensemble Weights
- LSTM: 25%
- Transformer: 20%
- CNN-LSTM: 20%
- XGBoost: 15%
- DQN: 10%
- PPO: 10%

### Confidence Calculation
Berdasarkan agreement antar model. Hanya trade jika confidence ≥ 85%.

### Trade Management
- **Entry**: Dari prediction[0]
- **SL**: ATR × multiplier (adaptive)
- **TP**: SL × RR ratio (2:1 hingga 3:1)
- **Lot**: Risk-based (0.01 - 0.10)

## 🔐 Security

- Admin password: "oncoy" (hardcoded)
- Token validation strict
- Database dengan proper indexes
- No sensitive data in logs
- config.py not committed to git

## 📝 Database Schema

### Users Table
- user_id (PRIMARY KEY)
- username
- tier (FREE/PREMIUM/SUPER/SUPREME)
- mt5_id
- token
- signal_quota
- expired_at
- created_at

### Tokens Table
- token (PRIMARY KEY)
- mt5_id
- tier
- expired_at
- created_at

### Payments Table
- id (PRIMARY KEY)
- user_id
- package
- duration
- amount
- proof_url
- status
- verified_at
- created_at

### Signals Table
- id (PRIMARY KEY)
- user_id
- pair
- action
- entry, sl, tp, lot
- confidence
- predictions (JSON)
- tier
- created_at

### Executions Table
- id (PRIMARY KEY)
- user_id
- mt5_id
- signal_id
- pair, action
- entry, exit, lot
- profit, result
- tier
- executed_at, closed_at

## 🧪 Testing

1. Database creation
```python
python database/setup_db.py
```

2. Bot testing
```bash
python bot/telegram_bot.py
```

3. WebSocket testing
```bash
python mt5/websocket_server.py
```

## 📚 Training Models

Train initial models with historical data:
```python
from data import DataDownloader, DataPreprocessor
from engine import LearningEngine

# Download 25 years data
downloader = DataDownloader()
data = downloader.download_all_pairs(years=25)

# Preprocess
preprocessor = DataPreprocessor()
X_train, X_val, y_train, y_val = preprocessor.preprocess_pipeline(data['XAUUSD'])

# Train models
learning = LearningEngine()
learning.train_initial_models(X_train, y_train, X_val, y_val)
```

## 🔄 Online Learning

Models automatically update setiap 24 jam dengan data trading terbaru.

## 📞 Support

- Telegram: @AureaPrimeAdmin
- Group: @AureaPrimeGroup
- Email: support@aureaprime.com

## 📄 License

Copyright © 2024 Aurea Prime Elite. All rights reserved.

## ⚠️ Disclaimer

Trading involves risk. Past performance does not guarantee future results. Use at your own risk.