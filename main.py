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

#stopLossPrice = 0.05
#takeProfitPrice = 0.2
#order = exchange.create_order("BTCUSDT", 'market', 'buy', 0.001)
#print(order)
#sl = exchange.create_order("BTCUSDT", 'market', 'sell', 0.001, None, {'stopPrice': stopLossPrice, "reduceOnly": True})
#print(sl)
#tp = exchange.create_order("BTCUSDT", 'market', 'sell', 0.001, None, {'stopPrice': takeProfitPrice, "reduceOnly": True})
#print(tp)

async def main(lastMsgId):
    buyPrice = 0
    qtyBrought = 0
    sellPrice = 0
    takeProfitPrice = 999999
    while True:
        # Get the ticker for BTCUSDT
        ticker = exchange.fetch_ticker('BTC/USDT')
        # Get the current price of BTCUSDT
        btcCurrentPrice = ticker['close']

        # Print the price
        # print(btcCurrentPrice)
        # Read the last msg that TradingView Alert sent to the TelegramBot via WebHook
        last_messages = await client(GetHistoryRequest(
            peer=bot_id,
            limit=2,
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
        print("Buy Price : " + str(buyPrice) + " Current Price: " + str(btcCurrentPrice))

        tolerance = timedelta(minutes=1)
        if getCurrent - tolerance <= msgDateTime <= getCurrent + tolerance:
            # print('The times are within the tolerance interval')
            # print(str(lastMsgId) + " : " + str(msgId))
            if lastMsgId != msgId:
                lastMsgId = msgId
                if "BTCUSDT" in signalMsg:
                    if "buy" in signalMsg:
                        order = exchange.create_order("BTCUSDT", 'market', 'buy', getQty, None)
                        buyPrice = round(float(order["info"]["fills"][0]["price"]),2)
                        # qtyBrought = int(order["info"]["origQty"])
                        # takeProfitPrice = buyPrice * 0.01 + buyPrice
                        print("Buying " +  str(getQty) + " @ " + str(buyPrice) + " BTCUSDT: " + str(order))
                        await client.send_message(bot_id, 'Brought ' +  str(getQty) + " @ " + str(buyPrice))
                    if "sell" in signalMsg:
                        order = exchange.create_order("BTCUSDT", 'market', 'sell', getQty, None)
                        sellPrice = round(float(order["info"]["fills"][0]["price"]),2)
                        print("Selling " +  str(getQty) + " @ " + str(sellPrice) + " BTCUSDT: " + str(order))
                        await client.send_message(bot_id, 'Sold ' +  str(getQty) + " @ " + str(sellPrice))
        
        # if btcCurrentPrice < takeProfitPrice and takeProfitPrice != 999999:
        #     order = exchange.create_order("BTCUSDT", 'market', 'sell', qtyBrought, None)
        #     currentPrice = round(float(order["info"]["fills"][0]["price"]),2)
        #     await client.send_message(bot_id, 'Took profit on ' +  str(qtyBrought) + " @ " + str(currentPrice))

        await asyncio.sleep(0.2)


with client:
    client.loop.run_until_complete(main(lastMsgId))
