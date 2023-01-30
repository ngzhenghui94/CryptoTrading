import ccxt
import os, time, sys, re
from datetime import datetime, timedelta, timezone
from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetHistoryRequest
from os.path import join, dirname
from dotenv import load_dotenv
import asyncio

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
gmt8 = timezone(timedelta(hours=8))

exchange = ccxt.binance()
exchange.apiKey = os.environ.get("CXAPIKEY")
exchange.secret = os.environ.get("CXSECRETKEY")
exchange.enableRateLimit = True
api_id = os.environ.get("TELEGRAMAPPID")
api_hash = os.environ.get("TELEGRAMHASHID")
exchange.load_markets()

balance = exchange.fetch_balance(params={'type': 'spot'})