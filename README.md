## About
Python based Crypto trading bot that uses CCXT library to buy and sell Cryptocurrency by reading "Signals" from Telegram Channel/Bot.

Uses TradingView Alerts that sends buy/sell notification to my webhook server (see the forked implementation: https://github.com/ngzhenghui94/TradingViewAlert) which forwards the TradingView Alerts -> Webhook Server -> my Telegram Bot.

Rename .exampleenv -> .env and fill in the Crypto Exchange's API key, secrets. Get your Telegram APP ID and HASH ID from my.telegram.org/auth