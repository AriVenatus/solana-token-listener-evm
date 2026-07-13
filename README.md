# Solana Token Listener Bot 🚀

A Telegram bot that helps you monitor Solana and EVM tokens from source chats and track their market performance.

## 🌟 Features

- Monitor specific users in Telegram chats for token mentions
- Forward token contract addresses to your target chat
- Track market cap and price multiples
- Detailed feed showing all monitored messages
- User-friendly setup and configuration
- Choose which blockchain to monitor — Solana or an EVM chain (Robinhood Chain and others)

## ⛓️ Supported Chains

The first time you run the bot, you'll be asked which blockchain to monitor.
This choice is saved and can be changed later from the main menu
("Change Blockchain"):

- **Solana** (default, original behavior)
- **Robinhood Chain** — Robinhood's EVM Layer 2 (chain ID 4663)
- **Ethereum**
- **Base**
- **Arbitrum One**
- **BNB Chain**
- **Custom EVM chain** — enter your own name/chain ID/explorer/DexScreener slug

Switching chains changes how contract addresses are recognized (Solana
base58 vs. EVM `0x...` addresses), how market cap is looked up (Jupiter +
Solana RPC for Solana; DexScreener for EVM chains), and **which bot found
tokens are forwarded to** — Solana addresses always go to
`TARGET_CHAT_SOLANA`, and EVM addresses (regardless of which EVM chain is
selected) always go to `TARGET_CHAT_EVM`. When you switch chains, you'll be
offered the option to clear your tracked-token history, since old entries
won't resolve on the new chain.

## 📋 Prerequisites

Before you start, you'll need:
1. Python 3.8 or higher installed on your computer
2. A Telegram account
3. Your Telegram API credentials (we'll help you get these!)

## 🔧 Initial Setup

### Step 1: Get Your Telegram API Credentials
1. Visit https://my.telegram.org/auth
2. Log in with your phone number
3. Click on "API development tools"
4. Create a new application (any name and short name will work)
5. Save your `api_id` and `api_hash` - you'll need these later!

### Step 2: Install Python Dependencies
1. Open a terminal/command prompt
2. Navigate to the bot's directory
3. Run this command:
```bash
pip install -r requirements.txt
```

### Step 3: Set Up Environment Variables
1. Find the `.env.sample` file in the project
2. Make a copy and rename it to `.env`
3. Open `.env` and fill in your details:
```
API_ID=your_api_id_here
API_HASH=your_api_hash_here
TARGET_CHAT_SOLANA=your_solana_trading_bot_here
TARGET_CHAT_EVM=your_evm_trading_bot_here
TRACKING_CHAT=your_tracking_chat_here
```
You need both trading bots set up even if you only plan to use one chain
right now — this lets you switch between Solana and EVM later (via
"Change Blockchain") without editing `.env` again.

## 🚀 Running the Bot

1. Open a terminal/command prompt
2. Navigate to the bot's directory
3. Run:
```bash
python main.py
```

4. On first run:
   - You'll be asked to enter your phone number
   - Telegram will send you a code - enter it when prompted
   - The bot will save your session for future use

## 📱 Basic Commands

When the bot is running, you can use these commands:
- `add` - Add new chats to monitor
- `list` - Show all monitored chats
- `remove` - Remove chats from monitoring
- `feed` - Toggle detailed message feed
- `stats` - Show bot statistics
- `tokens` - Manage tracked tokens
- `stop` - Stop the bot

## 🔍 How It Works

### 1. Source Chat Monitoring
- The bot watches messages in your chosen source chats
- What it looks for depends on the active chain (see "Supported Chains" above):
  - **Solana**: base58 addresses, DexScreener/Birdeye/Solscan/Jupiter/pump.fun/gmgn links
  - **EVM chains**: `0x...` addresses, DexScreener links, and your configured chain's block explorer links

### 2. User Filtering
- For each source chat, you can choose specific users to monitor
- Only messages from these users will be processed
- Other users' messages will be ignored

### 3. Token Forwarding
- When a valid contract address is found, it's forwarded to the bot for the
  active chain — `TARGET_CHAT_SOLANA` for Solana, `TARGET_CHAT_EVM` for any
  EVM chain
- Each token is only forwarded once to avoid duplicates
- The bot maintains a list of processed tokens

### 4. Market Cap Tracking
- The bot tracks market cap for forwarded tokens
- Solana: Jupiter API, with GeckoTerminal as backup
- EVM chains: DexScreener, with GeckoTerminal as an optional backup where supported
- You'll get notifications when tokens hit significant multiples (2x, 3x, etc.)

### 5. Detailed Feed
- See every message the bot processes in real-time
- Know exactly why messages are forwarded or filtered
- Track user activity and token discoveries

## ⚙️ Advanced Configuration

### Changing the Monitored Blockchain
1. From the main menu, choose **"Change Blockchain"**
2. Pick Solana, a preset EVM chain (Robinhood Chain, Ethereum, Base,
   Arbitrum One, BNB Chain), or enter a custom EVM chain
3. Optionally clear existing tracked-token history when switching

### Managing User Filters
1. Use the `add` command to select chats
2. For each chat, you can:
   - Choose specific users to monitor
   - Monitor all users
   - Remove existing filters

### Token Management
1. Use the `tokens` command to:
   - View all tracked tokens
   - Remove specific tokens
   - Clear all tracking data

## 🆘 Troubleshooting

### Common Issues:

1. **Bot won't connect:**
   - Check your internet connection
   - Verify API credentials in .env file
   - Ensure your Telegram session is valid

2. **Messages not forwarding:**
   - Confirm source chat configuration
   - Check user filters
   - Verify `TARGET_CHAT_SOLANA`/`TARGET_CHAT_EVM` in `.env` — make sure the
     one matching your active chain (check "View Current Settings") is set correctly

3. **Market cap not updating:**
   - Check your internet connection
   - Verify the token contract is valid
   - Wait a few minutes and try again

### Need Help?
- Check the detailed logs in the `logs` directory
- Look for error messages in the console
- Make sure all configuration files exist

## 🔐 Security Notes

- Never share your `session_string` or `.env` file
- Keep your API credentials private
- Don't run multiple instances of the bot with the same session

## 📝 Files You Should Know About

- `.env` - Your private configuration
- `sol_listener_config.json` - Bot settings, filters, and active chain
- `processed_tokens_solana.json` / `processed_tokens_evm.json` - List of processed tokens, one file per chain
- `tracked_tokens_solana.json` / `tracked_tokens_evm.json` - Current token tracking data, one file per chain
- `sold_tokens_solana.json` / `sold_tokens_evm.json` - Sold-token history, one file per chain

## 🔄 Updating the Bot

To update to the latest version:
1. Save your `.env` file
2. Pull the latest changes:
```bash
git pull
```
3. Restore your `.env` file if needed
4. Restart the bot

## 💡 Tips

1. Start with one or two source chats until you're comfortable
2. Use the detailed feed to understand what the bot is doing
3. Regularly check your tracked tokens
4. Back up your configuration files
5. Monitor the bot's performance and adjust filters as needed

Need more help? Feel free to reach out!
  