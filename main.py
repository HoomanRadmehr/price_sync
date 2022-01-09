from bot.market_maker import MarketMakerBot
import asyncio


pairs = ['BTC_IRT']
for pair in pairs:
    mm = MarketMakerBot(pair)
    mm.run()
    