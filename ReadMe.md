# 🚀 Quick User Guide - Manifold Trading Bot

## ⚡ 5-Minute Quick Start

### Step 1: Get Your API Key (2 minutes)
1. Go to https://manifold.markets/profile
2. Click **"Edit"**
3. Scroll down to **"API Key"** section
4. Click **"Refresh"** to generate a key
5. **Copy** the key (you'll need it next)

### Step 2: Setup (2 minutes)
```bash
# 1. Download and extract the bot
cd manifold-mikhailtal-bot

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Create your configuration
cp .env.example .env

# 4. Edit .env and add your API key
# Open .env in a text editor and set:
# MANIFOLD_API_KEY=your_actual_key_here
```

### Step 3: Test (1 minute)
```bash
# Run a test to make sure everything works
python test_bot.py
```

**Expected:** `✓ All tests passed!`

### Step 4: First Run
```bash
# Run in dry-run mode (no real trades)
python src/main.py --dry-run --once
```

**Expected:** Bot analyzes markets, shows what it would trade

### Step 5: Go Live! 🎉
```bash
# Run for real (one cycle)
python src/main.py --once

# Or run continuously (24/7)
python src/main.py
```

**Done!** Your bot is now trading! 🚀

---

## 📖 User Guide

### Table of Contents
1. [What This Bot Does](#what-this-bot-does)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Bot](#running-the-bot)
5. [Monitoring](#monitoring)
6. [Customization](#customization)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 What This Bot Does

### Simple Explanation
This bot **automatically trades** on Manifold Markets (a prediction market platform). It:
- 🔍 **Finds** markets created by your target user
- 🧠 **Analyzes** each market using 5 AI strategies
- 💰 **Trades** when it finds good opportunities
- 📊 **Tracks** performance and learns over time
- 🔄 **Runs** 24/7 without human intervention

### The 5 Trading Strategies

**1. LLM Analyst** (Optional - requires paid API)
- Uses Claude AI to understand market questions
- Best for complex/semantic analysis
- Cost: ~$0.003-0.015 per market

**2. Momentum Trader** (Free)
- Follows trends in market probabilities
- "Buy what's going up"
- Works best with price history

**3. Contrarian** (Free)
- Bets against extreme probabilities
- "Sell when everyone's buying"
- Exploits overreactions

**4. Value Seeker** (Free)
- Finds mispriced markets
- "Buy low, sell high"
- Fundamental analysis

**5. Sentiment Analyzer** (Free)
- Reads comments and trading activity
- "Follow (or fade) the crowd"
- Social signals

**Result:** Bot combines all 5 opinions → makes optimal decision

---

## 💻 Installation

### Requirements
- **Python 3.8+** (Check: `python --version`)
- **Internet connection**
- **Manifold Markets account** (free)

### Windows Installation
```powershell
# 1. Clone or download repository
cd C:\Path\To\manifold-mikhailtal-bot

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get an error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 4. Install dependencies
pip install -r requirements.txt

# 5. Setup configuration
copy .env.example .env
notepad .env  # Add your API key
```

### Linux/Mac Installation
```bash
# 1. Clone or download repository
cd /path/to/manifold-mikhailtal-bot

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Setup configuration
cp .env.example .env
nano .env  # Add your API key
```

### Verify Installation
```bash
# Test that everything is installed
python test_bot.py
```

**Success:** `✓ All tests passed!`

---

## ⚙️ Configuration

### Essential Settings (.env file)

**Minimum Required:**
```dotenv
# REQUIRED - Get from https://manifold.markets/profile
MANIFOLD_API_KEY=your_actual_api_key_here

# Your bot's identity
BOT_USERNAME=MyBotName
TARGET_USER=MikhailTal
```

**Recommended Settings:**
```dotenv
# Trading parameters
MAX_BET_AMOUNT=100      # Maximum bet size (mana)
MIN_BET_AMOUNT=10       # Minimum bet size (mana)
MIN_EDGE=0.05           # Minimum 5% edge to trade
MAX_POSITIONS=20        # Maximum open positions

# Risk management
RISK_TOLERANCE=0.25     # Kelly Criterion fraction (0.25 = conservative)
KELLY_FRACTION=0.25
MAX_PORTFOLIO_RISK=0.30 # Max 30% of bankroll at risk

# Timing
TRADING_INTERVAL=300    # Check every 5 minutes
```

### Configuration Presets

**Conservative (Safe, Lower Returns):**
```dotenv
MIN_EDGE=0.08           # Require 8% edge
MAX_BET_AMOUNT=50       # Smaller bets
RISK_TOLERANCE=0.15     # Very cautious
MAX_PORTFOLIO_RISK=0.20
```

**Moderate (Balanced):**
```dotenv
MIN_EDGE=0.05           # Require 5% edge
MAX_BET_AMOUNT=100      # Standard bets
RISK_TOLERANCE=0.25     # Quarter Kelly
MAX_PORTFOLIO_RISK=0.30
```

**Aggressive (Higher Risk/Return):**
```dotenv
MIN_EDGE=0.03           # Require 3% edge
MAX_BET_AMOUNT=200      # Larger bets
RISK_TOLERANCE=0.35     # More aggressive
MAX_PORTFOLIO_RISK=0.40
```

### Optional: LLM Strategy

To enable Claude AI analysis:
```dotenv
# Get API key from https://console.anthropic.com/
ANTHROPIC_API_KEY=your_anthropic_key_here

# LLM settings
LLM_MODEL=claude-sonnet-4-20250514
LLM_MAX_TOKENS=1000
LLM_TEMPERATURE=0.7
```

**Note:** This costs money (~$0.003-0.015 per market). Bot works great without it!

---

## 🏃 Running the Bot

### Running Modes

**1. Dry Run (Test Mode - No Real Trades):**
```bash
# Test once without trading
python src/main.py --dry-run --once

# Test continuously without trading
python src/main.py --dry-run
```

**2. Live Trading (One Cycle):**
```bash
# Run once and exit
python src/main.py --once
```

**3. Continuous Trading (24/7):**
```bash
# Run forever (checks every 5 minutes)
python src/main.py
```

### Command Line Options

```bash
python src/main.py [options]

Options:
  --dry-run    Test mode - no real trades
  --once       Run one cycle then exit
  (no flags)   Run continuously
```

### Examples

```bash
# Test run (safe, see what it would do)
python src/main.py --dry-run --once

# Single real trading cycle
python src/main.py --once

# Run 24/7
python src/main.py

# Test continuously (no trades)
python src/main.py --dry-run
```

### Stopping the Bot

**Windows:**
- Press `Ctrl+C`

**Linux/Mac:**
- Press `Ctrl+C`

**As a Service:**
```bash
# If running as Windows service:
nssm stop TradingBot

# If running as Linux service:
sudo systemctl stop trading-bot
```

---

## 📊 Monitoring

### Real-Time Logs

**Watch logs while bot runs:**
```bash
# The bot prints everything to console
# You'll see:
# - Markets being analyzed
# - Trading signals generated
# - Trades executed
# - Performance updates
```

**Log file:**
```bash
# View log file
cat bot.log

# Watch log file in real-time
tail -f bot.log
```

### What You'll See

**Typical Output:**
```
2025-11-30 12:00:00 - INFO - Starting trading cycle
2025-11-30 12:00:01 - INFO - Found 13 markets by MikhailTal
2025-11-30 12:00:01 - INFO - 13 markets are open for trading
2025-11-30 12:00:02 - INFO - Current balance: 1,045M

2025-11-30 12:00:03 - INFO - Analyzing: Will X happen?...
2025-11-30 12:00:04 - INFO - ✓ Signal: YES @ 65% (confidence: 80%, strength: 0.75)
2025-11-30 12:00:04 - INFO - ✓ Bet size approved: 45M
2025-11-30 12:00:05 - INFO - ✓ Placed bet: YES 45M @ 40%

2025-11-30 12:00:10 - INFO - Trading cycle complete. Executed 3 trades.
```

### Check Performance

**View trade history:**
```bash
# On Windows:
type data\trades.json

# On Linux/Mac:
cat data/trades.json
```

**View performance metrics:**
```bash
# On Windows:
type data\performance.json

# On Linux/Mac:
cat data/performance.json
```

### Monitor on Manifold

Visit your bot's profile:
```
https://manifold.markets/[YOUR_BOT_USERNAME]
```

You'll see:
- All trades executed
- Current positions
- Win/loss record
- Balance history

---

## 🎨 Customization

### Adjusting Risk Tolerance

**More Conservative (Fewer Trades):**
```dotenv
MIN_EDGE=0.08           # Require 8% edge
MAX_BET_AMOUNT=50       # Smaller bets
RISK_TOLERANCE=0.15     # More cautious
```

**More Aggressive (More Trades):**
```dotenv
MIN_EDGE=0.02           # Only 2% edge needed
MAX_BET_AMOUNT=200      # Larger bets
RISK_TOLERANCE=0.35     # More aggressive
```

### Changing Target User

Trade on different user's markets:
```dotenv
# In .env file:
TARGET_USER=ManifoldMarkets    # Change to any username
```

### Multiple Bots

Run multiple bots simultaneously:
```bash
# Bot 1 - User A
BOT_USERNAME=Bot1
TARGET_USER=UserA
python src/main.py &

# Bot 2 - User B  
BOT_USERNAME=Bot2
TARGET_USER=UserB
python src/main.py &
```

### Adjusting Trading Frequency

```dotenv
# Check more often (may hit rate limits)
TRADING_INTERVAL=60     # Every 1 minute

# Check less often
TRADING_INTERVAL=600    # Every 10 minutes

# Default (recommended)
TRADING_INTERVAL=300    # Every 5 minutes
```

---

## 🔧 Troubleshooting

### Common Issues

#### Issue: "No module named 'anthropic'"
**Solution:**
```bash
pip install -r requirements.txt
```

#### Issue: "MANIFOLD_API_KEY is required"
**Solution:**
1. Check your `.env` file exists
2. Make sure `MANIFOLD_API_KEY=your_key` is set
3. Make sure there's no space before/after the key

#### Issue: "Invalid API key"
**Solution:**
1. Go to https://manifold.markets/profile
2. Click "Edit"
3. Generate a new API key
4. Copy it to your `.env` file

#### Issue: "No markets found"
**Solution:**
- Target user may have no open markets
- Try different user: `TARGET_USER=ManifoldMarkets`
- Or wait for target user to create markets

#### Issue: "No trades executed"
**Solution:**
This is normal! It means:
- No strong signals generated (bot being selective)
- Insufficient edge (markets fairly priced)
- Risk limits reached

**To see more trades:**
```dotenv
MIN_EDGE=0.02  # Lower from 0.05 to 0.02
```

#### Issue: Bot crashes/stops
**Solution:**
1. Check bot.log for errors
2. Verify internet connection
3. Check API key is valid
4. Run tests: `python test_bot.py`

#### Issue: "Permission denied" (Windows)
**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Getting Help

**1. Check Documentation:**
- README.md - Complete guide
- CLIENT_DOCUMENTATION.md - Detailed explanation
- TECHNICAL_SPECIFICATION.md - Technical details

**2. Run Diagnostics:**
```bash
# Test all components
python test_bot.py

# Verify file structure
python verify_structure.py

# Test configuration
python -c "from src.config import Config; print(Config.to_dict())"
```

**3. Check Logs:**
```bash
# View recent logs
tail -50 bot.log

# Search for errors
grep ERROR bot.log
```

---

## 📁 File Structure

```
manifold-mikhailtal-bot/
├── src/
│   ├── main.py              # Main bot controller
│   ├── config.py            # Configuration loader
│   ├── manifold_client.py   # API client
│   ├── ensemble.py          # Strategy combiner
│   ├── risk_manager.py      # Risk management
│   └── strategies/          # 5 trading strategies
├── data/
│   ├── trades.json          # Trade history
│   └── performance.json     # Performance metrics
├── tests/                   # Test files
├── .env                     # Your configuration (CREATE THIS)
├── .env.example             # Configuration template
├── requirements.txt         # Python dependencies
└── README.md               # Full documentation
```

---

## 🎯 Quick Reference

### Essential Commands
```bash
# Install
pip install -r requirements.txt

# Test
python test_bot.py

# Dry run (safe)
python src/main.py --dry-run --once

# Live trading (once)
python src/main.py --once

# Live trading (24/7)
python src/main.py

# Stop
Ctrl+C
```

### Essential Files
```bash
.env              # Your configuration (edit this)
bot.log           # Real-time logs
data/trades.json  # Trade history
data/performance.json  # Performance metrics
```

### Essential Settings
```dotenv
MANIFOLD_API_KEY=     # REQUIRED
BOT_USERNAME=         # Your bot name
TARGET_USER=          # User to trade on
MIN_EDGE=0.05         # Minimum edge (5%)
MAX_BET_AMOUNT=100    # Max bet size
RISK_TOLERANCE=0.25   # Kelly fraction
```

---

## 🚀 Next Steps

### After Installation

1. **Test Run:**
   ```bash
   python src/main.py --dry-run --once
   ```

2. **Review Output:**
   - Check what markets it found
   - See what signals were generated
   - Verify it's working correctly

3. **Adjust Settings:**
   - Edit `.env` file
   - Lower MIN_EDGE if you want more trades
   - Adjust MAX_BET_AMOUNT for bet sizes

4. **Go Live:**
   ```bash
   python src/main.py --once
   ```

5. **Monitor:**
   - Watch logs
   - Check Manifold profile
   - Review performance metrics

### For Production (24/7)

**Windows Service:**
```powershell
# Install NSSM
choco install nssm

# Create service
nssm install TradingBot "C:\path\to\venv\Scripts\python.exe" "src\main.py"

# Start service
nssm start TradingBot
```

**Linux Service:**
```bash
# Create service file
sudo nano /etc/systemd/system/trading-bot.service

# Enable and start
sudo systemctl enable trading-bot
sudo systemctl start trading-bot
```

---

## 📚 Additional Resources

### Documentation
- **README.md** - Complete documentation (8,200+ words)
- **QUICKSTART.md** - 5-minute setup
- **CLIENT_DOCUMENTATION.md** - How it works
- **TECHNICAL_SPECIFICATION.md** - Technical details
- **API_KEYS.md** - API key information
- **WINDOWS_GUIDE.md** - Windows-specific help

### Support
- Check `bot.log` for errors
- Run `python test_bot.py` for diagnostics
- Review troubleshooting section above
- Read documentation files

---

## ✅ Checklist

Before going live:

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with API key
- [ ] Tests pass (`python test_bot.py`)
- [ ] Dry run successful (`python src/main.py --dry-run --once`)
- [ ] Configuration reviewed and adjusted
- [ ] Understand risk settings
- [ ] Know how to stop the bot
- [ ] Know where logs are

---

## 🎉 You're Ready!

Your bot is:
- ✅ Installed and configured
- ✅ Tested and working
- ✅ Ready to trade

**Start trading:**
```bash
python src/main.py
```

**Good luck!**

---

**Version:** 1.0.4  
**Last Updated:** November 30, 2025