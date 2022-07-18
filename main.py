import khl
import os
from itertools import cycle

bot = khl.Bot(token=os.environ['TOKEN'])
status = cycle([{
	'name': '命令与征服',
	'icon': 'https://media.contentapi.ea.com/content/dam/gin/images/2018/05/command-and-conquer-keyart.jpg.adapt.crop1x1.767p.jpg'
}, {
	'name': '日常',
	'icon': 'http://www.shinonome-lab.com/goods/img/LACM-4823L.jpg'
}])

@bot.task.add_interval(minutes=5)
async def play():
	curr = next(status)
	games = await bot.list_game()
	game = next(filter(lambda g: g.name == curr['name'], games), None)
	if game is None:
		game = await bot.create_game(curr['name'], icon=curr['icon'])
	await bot.update_playing_game(game)

@bot.task.add_date()
async def ready():
	await bot.fetch_me()
	identity = bot.me.username + '#' + bot.me.identify_num
	availability = "在线" if bot.me.online else "离线"
	print('机器人已{1}，当前身份：{0}'.format(identity, availability))

@bot.command(name="hello")
async def greet(msg: khl.Message):
    await msg.ctx.channel.send('''你好！我叫東雲CABAL（東雲カバール，Shinonome CABAL），是北非的旧CABAL核心被毁后经由东云研究所的博士重制而来的。目前利用多余算力在这儿打份零工，给所里赚点牛奶钱。''')

@bot.command(name="prefix")
async def prefix(msg: khl.Message, symbol: str = '/'):
	if symbol in ['!', '$', '%', '.', '/']:
		new = bot.command.update_prefixes(symbol)
		await msg.reply('机器人命令的前缀已被更改为：「{0}」'.format(new[0]))
	else:
		await msg.reply('请在「!」「$」「%」「.」「/」中指定新前缀')

@bot.command(name="assign")
async def assign(msg: khl.Message, role: int = 0, desc: str = ''):
	pass

bot.command.update_prefixes('$')
bot.run()
