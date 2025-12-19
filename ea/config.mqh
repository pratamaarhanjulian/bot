//+------------------------------------------------------------------+
//|                                                       config.mqh  |
//|                               Aurea Prime Elite Configuration     |
//+------------------------------------------------------------------+

// Version info
#define EA_NAME     "Aurea Prime Elite"
#define EA_VERSION  "1.00"
#define EA_AUTHOR   "Aurea Prime Team"

// Default settings
#define DEFAULT_SERVER_IP    "127.0.0.1"
#define DEFAULT_SERVER_PORT  8080
#define DEFAULT_MAGIC        20231217

// Trading parameters
#define MIN_LOT    0.01
#define MAX_LOT    10.0
#define LOT_STEP   0.01

// Risk parameters
#define MAX_RISK_PERCENT     2.0    // Maximum risk per trade
#define MIN_CONFIDENCE       85.0   // Minimum confidence to trade

// Timing
#define REQUEST_INTERVAL     60     // Seconds between signal requests
#define CONNECTION_TIMEOUT   30     // Seconds before connection timeout

// Colors for visualization
#define COLOR_BUY_SIGNAL     clrLime
#define COLOR_SELL_SIGNAL    clrRed
#define COLOR_PREDICTION     clrYellow
#define COLOR_CONFIDENCE     clrAqua

//+------------------------------------------------------------------+
