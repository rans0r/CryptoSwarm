# 🐝 CryptoSwarm

Local automated crypto trading server with AI-interpreted rules and evolutionary bot swarms.

## Overview

CryptoSwarm is a powerful local automated crypto trading server that enables you to:

- **Manage multiple trading bots** with natural-language rules
- **AI-powered rule interpretation** via xAI or OpenAI API
- **Kraken exchange integration** via CCXT library
- **Evolutionary swarm algorithms** for strategy optimization
- **Track performance, trades, and logs** in real-time
- **Simple web UI** for viewing and managing bots

## Features

### 🤖 AI-Powered Trading Rules
Write trading rules in plain English. The system uses OpenAI or xAI (X.AI) to interpret your natural language rules into executable trading strategies.

**Example:** "Buy BTC when the price drops below $40,000 and sell when it rises above $45,000"

### 🔄 Kraken Exchange Integration
Direct integration with Kraken exchange using the CCXT library for:
- Real-time market data
- Order execution (buy/sell)
- Balance tracking
- Trade history

### 🧬 Evolutionary Swarm Intelligence
Bots compete in pools where:
- Best performing bots survive
- Strategies mutate and evolve
- Crossover combines successful traits
- Fee-aware fitness calculations
- Automatic strategy optimization

### 📊 Comprehensive Tracking
- Bot performance metrics (win rate, P&L, fitness scores)
- Complete trade history with fees
- Detailed activity logs
- Pool statistics and evolution history

### 🔐 Security & Privacy
- Everything runs locally on your machine
- Your API keys never leave your server
- JWT-based authentication
- SQLite database for data persistence

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Kraken account with API keys (optional, for live trading)
- OpenAI or xAI API key (for AI rule interpretation)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/rans0r/CryptoSwarm.git
cd CryptoSwarm
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env file with your API keys
```

4. **Run the application**
```bash
python main.py
```

The server will start on `http://localhost:8000`

### Configuration

Edit the `.env` file with your settings:

```env
# AI API Keys (choose one or both)
OPENAI_API_KEY=your-openai-api-key
XAI_API_KEY=your-xai-api-key
DEFAULT_AI_PROVIDER=openai  # or "xai"

# Kraken Exchange API
KRAKEN_API_KEY=your-kraken-api-key
KRAKEN_API_SECRET=your-kraken-secret
KRAKEN_TESTNET=true  # Set to false for live trading

# Security
SECRET_KEY=change-this-to-a-random-secret-key

# Trading Configuration
MAX_BOTS=100
MAX_POSITION_SIZE=1000.0
```

## Usage

### Web Interface

1. **Home Page**: Visit `http://localhost:8000` for an overview
2. **Dashboard**: Go to `http://localhost:8000/dashboard` to view bots and trades
3. **API Documentation**: Access interactive docs at `http://localhost:8000/docs`

### API Authentication

1. **Get access token**:
```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

Default credentials:
- Username: `admin`
- Password: `admin123`

**⚠️ Change the default password in production!**

2. **Use the token** in subsequent requests:
```bash
curl -X GET "http://localhost:8000/bots/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Creating a Trading Bot

```bash
curl -X POST "http://localhost:8000/bots/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "BTC Scalper",
    "description": "Quick BTC trades on small movements",
    "natural_language_rule": "Buy BTC/USD when price drops 2% below the 1-hour moving average, sell when it rises 2% above"
  }'
```

The AI will interpret this rule and create an executable trading strategy.

### Managing Bots

- **List all bots**: `GET /bots/`
- **Get bot details**: `GET /bots/{bot_id}`
- **Update bot**: `PUT /bots/{bot_id}`
- **Delete bot**: `DELETE /bots/{bot_id}`
- **Reinterpret rule**: `POST /bots/{bot_id}/reinterpret`

### Viewing Trades

- **List all trades**: `GET /trades/`
- **Get trade details**: `GET /trades/{trade_id}`
- **Bot statistics**: `GET /trades/bot/{bot_id}/stats`

### Evolutionary Swarm

1. **Create a swarm pool**:
```bash
curl -X POST "http://localhost:8000/swarm/pools" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alpha Pool",
    "description": "Competitive bot pool for BTC strategies",
    "max_bots": 20,
    "selection_pressure": 0.5
  }'
```

2. **Trigger evolution**:
```bash
curl -X POST "http://localhost:8000/swarm/pools/{pool_id}/evolve" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

This will:
- Evaluate all bots in the pool
- Eliminate poor performers
- Create mutations of successful bots
- Perform crossover between top performers

## Project Structure

```
CryptoSwarm/
├── app/
│   ├── __init__.py
│   ├── database.py              # Database setup and session management
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py            # SQLAlchemy models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── bots.py              # Bot management endpoints
│   │   ├── trades.py            # Trade history endpoints
│   │   ├── logs.py              # Log viewing endpoints
│   │   └── swarm.py             # Swarm pool endpoints
│   └── utils/
│       ├── __init__.py
│       ├── auth.py              # Authentication utilities
│       ├── ai_interpreter.py    # AI rule interpretation
│       ├── kraken.py            # Kraken/CCXT integration
│       └── evolution.py         # Evolutionary algorithms
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── templates/
│   ├── index.html               # Home page
│   └── dashboard.html           # Dashboard page
├── config.py                    # Application configuration
├── main.py                      # FastAPI application entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── .gitignore
├── LICENSE
└── README.md
```

## API Endpoints

### Authentication
- `POST /auth/token` - Get access token
- `POST /auth/register` - Register new user
- `GET /auth/me` - Get current user info

### Bots
- `GET /bots/` - List all bots
- `POST /bots/` - Create new bot
- `GET /bots/{id}` - Get bot details
- `PUT /bots/{id}` - Update bot
- `DELETE /bots/{id}` - Delete bot
- `POST /bots/{id}/reinterpret` - Reinterpret bot rule

### Trades
- `GET /trades/` - List all trades
- `GET /trades/{id}` - Get trade details
- `GET /trades/bot/{bot_id}/stats` - Get bot statistics

### Logs
- `GET /logs/` - List bot logs
- `GET /logs/{id}` - Get log details

### Swarm
- `GET /swarm/pools` - List swarm pools
- `POST /swarm/pools` - Create swarm pool
- `GET /swarm/pools/{id}` - Get pool details
- `POST /swarm/pools/{id}/evolve` - Trigger evolution

### System
- `GET /health` - Health check
- `GET /status` - System status

## Development

### Running in Development Mode

```bash
# Enable debug mode in .env
DEBUG=true

# Run with auto-reload
python main.py
```

### Running Tests

```bash
pytest
```

### Code Style

```bash
# Format code
black .

# Lint code
flake8 .
```

## Safety & Best Practices

⚠️ **Important Security Notes:**

1. **Never commit your `.env` file** - It contains sensitive API keys
2. **Change default credentials** - The admin/admin123 combo is for initial setup only
3. **Start with testnet** - Use Kraken's testnet before live trading
4. **Test with small amounts** - When going live, start with minimal position sizes
5. **Monitor closely** - Always watch your bots, especially initially
6. **Set limits** - Configure `MAX_POSITION_SIZE` and other safety limits
7. **Backup your database** - Regularly backup `cryptoswarm.db`

## Troubleshooting

### Database Issues
If you encounter database errors, try:
```bash
rm cryptoswarm.db
python main.py  # Will recreate the database
```

### API Connection Issues
- Verify your API keys are correct in `.env`
- Check that Kraken API keys have proper permissions
- For xAI, ensure you're using the correct base URL

### AI Interpretation Issues
- Ensure your AI API key is valid and has credits
- Try rephrasing your trading rule more clearly
- Check the `/bots/{id}` endpoint to see the interpreted rule

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

**This software is for educational and research purposes only.**

Trading cryptocurrencies carries significant risk. CryptoSwarm is provided "as is" without any warranties. The authors are not responsible for any financial losses incurred through the use of this software.

Always:
- Do your own research
- Start with paper trading or testnet
- Never trade more than you can afford to lose
- Understand the strategies you're deploying

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check the API documentation at `/docs`
- Review the code and inline documentation

---

**Happy Trading! 🚀**
