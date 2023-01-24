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
api_id = os.environ.get("TELEGRAMAPPID")
api_hash = os.environ.get("TELEGRAMHASHID")

# balance = exchange.fetch_balance(params={'type': 'spot'})
# print(balance)

# Create a TelegramClient using your API ID and API hash
client = TelegramClient('danielTeleSession', api_id, api_hash).start()
lastMsgId = 0

# TradingView Alert is sent to this Telegram Bot via WebHook.
bot_id=5685940104

# Get Signal's Purchase Quantity
def getQuantity(signalMsg):
    match = re.search("@ (.+?) filled", signalMsg)
    if match:
        qty = match.group(1)
        return qty

# Get Current Position
def getCurrPosition(signalMsg):
    position = abs(float(signalMsg.split(" ")[-1]))
    return position

async def main(lastMsgId):

    while True:
        # Read the last msg that TradingView Alert sent to the TelegramBot via WebHook
        last_messages = await client(GetHistoryRequest(
            peer=bot_id,
            limit=1,
            offset_date=None,
            offset_id=0,
            max_id=0,
            min_id=0,
            add_offset=0,
            hash=0
        ))

        signalMsg = last_messages.messages[0].message
        msgId = last_messages.messages[0].id
        msgDateTime = last_messages.messages[0].date.astimezone(gmt8).replace(tzinfo=None)
        getCurrent = datetime.utcnow().replace(microsecond=0).astimezone(gmt8).replace(tzinfo=None)
        getQty = getQuantity(signalMsg)
        getCurrPos = getCurrPosition(signalMsg)

        # print(str(msgDateTime))
        # print(str(getCurrent))
        # print(str(getQty) + " : " + str(getCurrPos))
        # print(str(msgId) + " : " + signalMsg)

        tolerance = timedelta(minutes=1)
        if getCurrent - tolerance <= msgDateTime <= getCurrent + tolerance:
            # print('The times are within the tolerance interval')
            # print(str(lastMsgId) + " : " + str(msgId))
            if lastMsgId != msgId:
                lastMsgId = msgId
                if "BTCUSDT" in signalMsg:
                    if "buy" in signalMsg:
                        order = exchange.create_order("BTCUSDT", 'market', 'buy', getQty, None)
                        print("Buying " +  str(getQty) + "BTCUSDT: " + str(order))
                    if "sell" in signalMsg:
                        order = exchange.create_order("BTCUSDT", 'market', 'sell', getQty, None)
                        print("Selling " +  str(getQty) + "BTCUSDT: " + str(order))



        await asyncio.sleep(1)


with client:
    client.loop.run_until_complete(main(lastMsgId))