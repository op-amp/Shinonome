from khl import Bot, Message, MessageTypes, Event, EventTypes
from khl.card import CardMessage, Card, Module, Element, Types as CardTypes
from itertools import cycle
import re
import os

bot = Bot(token=os.environ['TOKEN'])
status = cycle([{
	'name': "命令与征服",
	'icon': "https://media.contentapi.ea.com/content/dam/gin/images/2018/05/command-and-conquer-keyart.jpg.adapt.crop1x1.767p.jpg"
}, {
	'name': "日常",
	'icon': "http://www.shinonome-lab.com/goods/img/LACM-4823L.jpg"
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
	print("机器人已{1}，当前身份：{0}".format(identity, availability))

@bot.command(name="hello")
async def greet(msg: Message):
    await msg.ctx.channel.send('''你好！我叫東雲CABAL（東雲カバール，Shinonome CABAL），是北非的旧CABAL核心被毁后经由东云研究所的博士重制而来的。目前利用多余算力在这儿打份零工，给所里赚点牛奶钱。''')

@bot.command(name="prefix")
async def change_prefix(msg: Message, symbol: str = '/'):
	if symbol in {'!', '$', '%', '.', '/', '>'}:
		bot.command.update_prefixes(symbol)
		await msg.reply("机器人命令的前缀已被更改为：「{0}」".format(symbol))
	else:
		await msg.reply("请在「!」「$」「%」「.」「/」「>」中指定新前缀")

@bot.command(name="card")
async def send_card(msg: Message, *contents: str):
	if not len(contents):
		content = '''[{"type":"card","theme":"primary","size":"lg","modules":[{"type":"section","text":{"type":"plain-text","content":"東雲CABAL机器人为您生成的演示卡片消息。"}}]}]'''
	else:
		raw = ''.join(contents)
		pattern = re.compile(r'[][}{,:]+')
		sep = pattern.findall(raw)
		prop = pattern.split(raw)
		content = sep[0]
		for i in range(1, len(sep)):
			content += '"' + prop[i] + '"' + sep[i]
	await msg.ctx.channel.send(content, type=MessageTypes.CARD)

@bot.command(name="assign")
async def offer_role(msg: Message, role: str = ''):
	await msg.ctx.channel.send(CardMessage(
		Card(
			Module.Header("开始聊天"),
			Module.Divider(),
			Module.Section(
				Element.Text('''本服务器内默认角色无法发言。如果您已**阅读并同意**上述服务器规定，请*点击按钮*''', type=CardTypes.Text.KMD)
			),
			Module.ActionGroup(
				Element.Button("获取发言权限", value="code=" + os.environ['CODE'] + "|role=" + role)
			),
			theme=CardTypes.Theme.NONE
		)
	) if role else "请指定需为用户添加的角色")

@bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
async def assign_role(b: Bot, event: Event):
	values = event.body['value'].split('|')
	v = dict(values[i].split('=') for i in range(0, len(values)) if '=' in values[i])
	if ('role' in v) and ('code' in v) and (v['code'] == os.environ['CODE']):
		g = (await b.list_guild())[0]
		u = await b.fetch_user(event.body['user_id'])
		await g.grant_role(u, v['role'])

bot.command.update_prefixes('>')
bot.run()
