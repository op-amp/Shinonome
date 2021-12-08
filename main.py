import os
from khl import Bot, Message, PublicMessage, EventTypes, Event

# token here
bot = Bot(token="os.environ['TOKEN']")

@bot.command(name="hello")
async def greet(msg: Message):
    await msg.reply("你好！我叫东云CABAL（東雲カバール，Shinonome CABAL），是北非的旧CABAL核心被毁后经由东云研究所的博士重制来的。目前利用多余算力在这儿打份零工，给所里赚点牛奶钱。")

bot.run()
