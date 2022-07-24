from khl import Bot, Message, MessageTypes, Event, EventTypes
from khl.card import CardMessage, Card, Module, Element, Types as CardTypes
from itertools import cycle
from random import randint
import json
import re
import os

bot = Bot(token=os.environ['TOKEN'])
prefix = '>'
repl = {
	'\*': ('*'),
	'\(': ('('),
	'\)': (')'),
	'\[': ('[', r'\u005B'),
	'\]': (']', r'\u005D'),
	'\`': ('`')
}
status = cycle([{
	'name': "Act On Instinct",
	'artist': "Frank Klepacki"
}, {
	'name': "ヒャダインのカカカタ☆カタオモイ-C",
	'artist': "前山田健一"
}])

@bot.task.add_interval(minutes=5)
async def play():
	song = next(status)
	await bot.client.update_listening_music(song['name'], song['artist'], "cloudmusic")

@bot.task.add_date()
async def ready():
	await bot.fetch_me()
	identity = bot.me.username + '#' + bot.me.identify_num
	availability = "在线" if bot.me.online else "离线"
	print(f"机器人已{availability}，当前身份：{identity}")

@bot.command(name="help", desc="展示机器人指令的信息", help='''`help [指令名]`
【描述】通过卡片消息显示机器人帮助。
【参数】0个：显示全部可用指令的列表；
　　　　1个：指定一个指令，显示详细用法。''')
async def show_help(msg: Message, query: str = ''):
	if query:
		cmd = [query, bot.command.get(query)]
		await msg.ctx.channel.send(CardMessage(
			Card(
				Module.Header(f"机器人帮助－{query}指令"),
				Module.Divider(),
				Module.Section(
					Element.Text(cmd[1].help, type=CardTypes.Text.KMD)
				),
				Module.Context(f"记得给指令添加「{prefix}」前缀"),
				theme=CardTypes.Theme.INFO
			) if cmd[1] else Card(
				Module.Header(f"机器人帮助－错误"),
				Module.Divider(),
				Module.Section(
					f"{query}指令不存在。"
				),
				theme=CardTypes.Theme.DANGER
			)
		))
	else:
		cmds = list(bot.command.items())
		await msg.ctx.channel.send(CardMessage(
			Card(
				Module.Header("机器人帮助－可用指令列表"),
				Module.Divider(),
				Module.Section(
					'\n'.join(tuple((prefix + cmd[0].ljust(8) + '\t' + cmd[1].desc) for cmd in cmds))
				),
				Module.Context("使用「help 指令名」查询指定指令的详细用法"),
				theme=CardTypes.Theme.INFO
			)
		))

@bot.command(name="hello", desc="打招呼", help='''`hello`
【描述】发送一条自我介绍消息。''')
async def greet(msg: Message):
    await msg.ctx.channel.send("你好！我叫東雲CABAL（東雲カバール，Shinonome CABAL），是北非的旧CABAL核心被毁后经由东云研究所的博士重制而来的。目前利用多余算力在这儿打份零工，给所里赚点牛奶钱。")

@bot.command(name="dice", desc="生成随机整数", help='''`roll [最小值 [最大值]]`
【描述】在一定范围内随机生成一个整数。
【参数】0个：默认范围在1至6间；
　　　　1个：只规定最小值；
　　　　2个：同时规定最大值与最小值。''')
async def roll(msg: Message, lower: int = 1, upper: int = 6):
    result = randint(lower, upper)
    await msg.reply(f"随机生成的{lower}至{upper}间的数字为：{result}")

@bot.command(name="prefix", desc="更改指令前缀", help='''`prefix [新前缀]`
【描述】修改触发机器人指令的前缀。
【参数】0个：默认修改为「/」；
　　　　1个：修改为指定的符号。''')
async def change_prefix(msg: Message, symbol: str = '/'):
	if symbol in {'!', '$', '%', '.', '/', '>'}:
		bot.command.update_prefixes(symbol)
		global prefix; prefix = symbol
		await msg.reply(f"机器人指令的前缀已被更改为：「{symbol}」")
	else:
		await msg.reply("请在「!」「$」「%」「.」「/」「>」中指定新前缀")

@bot.command(name="card", desc="发送卡片消息", help='''`card [普通文本|卡片消息JSON]`
【描述】命令机器人向频道内发送卡片消息。
【参数】不提供：发送一条演示卡片消息；
　　　　普通文本：将文本作为卡片的内容；
　　　　JSON：按JSON描述的样式生成卡片。''')
async def send_card(msg: Message, *contents: str):
	legit = raw = ''.join(contents)
	try:
		for k in repl:
			legit = legit.replace(k, repl[k][0])
		json.loads(legit)
		await msg.ctx.channel.send(legit, type=MessageTypes.CARD)
		return
	except json.JSONDecodeError:
		for k in repl:
			raw = raw.replace(k, repl[k][-1])
	pattern = re.compile(r'[][}{,:]+')
	sep = pattern.findall(raw)
	prop = pattern.split(raw)
	if len(sep):
		content = sep[0]
		for i in range(1, len(sep)):
			content += '"' + prop[i] + '"' + sep[i]
	else:
		content = '''[{
			"type": "card",
			"theme": "primary",
			"modules": [{
				"type": "section",
				"text": "''' + (raw if raw else "卡片消息演示") + '''"
			}]
		}]'''
	try:
		json.loads(content)
	except json.JSONDecodeError:
		content = '''[{
			"type": "card",
			"theme": "danger",
			"modules": [{
				"type": "section",
				"text": "卡片消息的参数格式不正确"
			}, {
				"type": "context",
				"elements": [
					"参数为JSON时，可见文本内容中一般不能包含「,」「:」「{」「}」；\\n",
					"如需包含，请将JSON字符串化（单行、无非内容空白，最外侧由引号包裹）。\\n",
					"任何情况下「\\\\」都是不允许的，请使用「\\\\\\\\」进行转义。"
				]
			}]
		}]'''
	await msg.ctx.channel.send(content, type=MessageTypes.CARD)

@bot.command(name="assign", desc="生成用于自助获取角色的按钮", help='''`assign 角色ID`
【描述】发送一条卡片消息；
　　　　点击其中的按钮可获得指定的角色。
【参数】可自助获取的角色的角色ID。''')
async def offer_role(msg: Message, role: str = ''):
	params = "code=" + os.environ['CODE'] + "|role=" + role + "|guild=" + msg.ctx.guild.id
	await msg.ctx.channel.send(CardMessage(
		Card(
			Module.Header("开始聊天"),
			Module.Divider(),
			Module.Section(
				Element.Text("本服务器内默认角色无法发言。如果您已**阅读并同意**上述服务器规定，请*点击按钮*", type=CardTypes.Text.KMD)
			),
			Module.ActionGroup(
				Element.Button("获取发言权限", value=params)
			),
			theme=CardTypes.Theme.NONE
		)
	) if role else "请指定需为用户添加的角色")

@bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
async def assign_role(b: Bot, event: Event):
	values = event.body['value'].split('|')
	v = dict(values[i].split('=') for i in range(0, len(values)) if '=' in values[i])
	if ('role' in v) and ('guild' in v) and ('code' in v) and (v['code'] == os.environ['CODE']):
		g = await b.fetch_guild(v['guild'])
		u = await b.fetch_user(event.body['user_id'])
		await g.grant_role(u, v['role'])

bot.command.update_prefixes(prefix)
bot.run()
