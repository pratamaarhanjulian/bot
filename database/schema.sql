-- Aurea Prime Elite Database Schema

CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    tier VARCHAR(20) DEFAULT 'FREE',
    mt5_id VARCHAR(50),
    token VARCHAR(8),
    signal_quota INTEGER DEFAULT 5,
    expired_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tokens (
    token VARCHAR(8) PRIMARY KEY,
    mt5_id VARCHAR(50) UNIQUE,
    tier VARCHAR(20),
    expired_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id BIGINT,
    package VARCHAR(50),
    duration VARCHAR(20),
    amount INTEGER,
    proof_url TEXT,
    status VARCHAR(20) DEFAULT 'PENDING',
    verified_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id BIGINT,
    pair VARCHAR(20),
    action VARCHAR(10),
    entry DECIMAL(10,5),
    sl DECIMAL(10,5),
    tp DECIMAL(10,5),
    lot DECIMAL(5,2),
    confidence DECIMAL(5,2),
    predictions TEXT,
    tier VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id BIGINT,
    mt5_id VARCHAR(50),
    signal_id INTEGER,
    pair VARCHAR(20),
    action VARCHAR(10),
    entry DECIMAL(10,5),
    exit DECIMAL(10,5),
    lot DECIMAL(5,2),
    profit DECIMAL(10,2),
    result VARCHAR(10),
    tier VARCHAR(20),
    executed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    closed_at DATETIME
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_tier ON users(tier);
CREATE INDEX IF NOT EXISTS idx_users_token ON users(token);
CREATE INDEX IF NOT EXISTS idx_tokens_mt5 ON tokens(mt5_id);
CREATE INDEX IF NOT EXISTS idx_payments_user ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_signals_user ON signals(user_id);
CREATE INDEX IF NOT EXISTS idx_signals_created ON signals(created_at);
CREATE INDEX IF NOT EXISTS idx_executions_user ON executions(user_id);
CREATE INDEX IF NOT EXISTS idx_executions_mt5 ON executions(mt5_id);
