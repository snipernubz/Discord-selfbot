import discord
from discord.ext import commands
import logging
#import asyncio
import urllib.request
import mimetypes
import os.path
import json

with open('config.json', 'r') as configfile:
	config = json.load(configfile)
	token = config["token"]
	prefix = config["prefix"]
	replacer = config["replacer"]
	localpath = config["localpath"]
	musicpath = config["musicpath"]
	print(config)

guildIdList = []
guildNames = []
guildDict = {}
channelIds = []
channelNameList = []
musicList = []
acceptedFormats = ['.txt', '.json', '.py']
client = commands.Bot(command_prefix=prefix, self_bot=True)
#client.remove_command('help')

#logging.basicConfig(level=logging.INFO)

def guess_type_of(link, strict=True):
    link_type, _ = mimetypes.guess_type(link)
    if link_type is None and strict:
        u = urllib.urlopen(link)
        link_type = u.headers.gettype() # or using: u.info().gettype()
    return link_type

@client.event
async def on_ready():
	print(f'We have logged in as {client.user}')

	client.load_extension('./cogs/voice')
	print("loaded Music extension")

	for x in range(0,len(client.guilds)):
		guildNames.append(str(client.guilds[x]))
	for guild in client.guilds:
		guildIdList.append(guild.id)
	for x in range(0,len(client.guilds)):
		guildNames.append(str(client.guilds[x]))
	for guild in client.guilds:
		guildIdList.append(guild.id)
	for x in range(0, len(guildIdList)):
		print(f'GuildDict: x = {x}')
		guildDict[str(client.guilds[x])] = guildIdList[x]
	for x in os.listdir(musicpath):
		if x.endswith(".mp3"):
			musicList.append(x)
	print(guildIdList)
	print(guildNames)
	print(guildDict)
	print(channelIds)
	print(channelNameList)

@client.command()
async def ping(ctx):
	await ctx.send(f"Pong! {round(client.latency *1000)}ms")
	print(ctx)
@client.command(name='get-guilds')
async def get_guilds(ctx):
	await ctx.send(guildDict)
	
@client.command(name='get-music')
async def get_music(ctx, path=musicpath):
	if path == musicpath:
		await ctx.send(musicList)
	else:
		for x in os.listdir(path):
			if x.endswith(".mp3"):
				await ctx.send(x)
@client.command()
async def send(ctx, guildval, channel, filename, path=localpath):
	print('SEND: called')
	sendingchanneltemp = ''
	sendingguild = client.get_guild(int(guildval))
	sendingpath = path
	sendingfilecomb = path + '/' + filename
	sendingfiledata = ''
	urlfile = ''
	print(f'SEND: guilval type = {type(guildval)}')
	print(f'SEND: channel type = {type(channel)}')
	print(f'SEND: guildval = {guildval}')
	print(f'SEND: channel = {channel}')
	
	if guildval == int:
		print('SEND: testing if guild is an id')
		if guildIdList.count(guildval) == 0:
			await ctx.send('client not in specified guild')
			print(f'SEND: not in guild with id: {guildval}')
			
	if guildval == str:
		print('SEND: testing if guild is str')
		if guildNames.count(guildval) == 0:
			await ctx.send('client not in specified guild')
			print(f'SEND: client not in guild named {guildval}')
			
	if channel == int:
		print('SEND: testing if channel is a id')
		if channelIds.count(channel) == 0:
			await ctx.send(f'channel id not found for any channel in guild: {sendingguild}') 
			print(f'SEND: no channel with id {channel} exists in guild: {guildval}')
			sendingchanneltemp = channel
			print(f'sendingchanneltemp = {sendingchanneltemp}')

	if channel == str:
		print('SEND: testing if channel is a name')
		if channelNameList.count(channel) == 0:
			await ctx.send(f'channel name not found for any channel in guild:{guildval}')
			print(f'SEND: no channel with name {channel} exists in guild: {guildval}')
			channelgetname = discord.utils.get(ctx.sendingguild.channels, name=str(channel))
			sendingchanneltemp = channelgetname.id
			print(f'tempchannel = {sendingchanneltemp}')

	print(f'SEND: sendingguild = {sendingguild}')
	print(f'SEND: sendingchanneltemp = {sendingchanneltemp}')
	print(f'SEND: sendingchanneltemp int = {sendingchanneltemp}')
	sendingchannel = sendingguild.get_channel(int(channel))
	print(f'SEND: sendingchannel = {sendingchannel}')
	if urlfile == '':
		with open(sendingfilecomb) as textfile:
			await ctx.send(f'Sending file: {filename} to Guild: {guildval} to channel: {sendingchannel}')
			uncleandata = textfile.readlines()
			print(f'SEND: sending {len(uncleandata)} lines')
			for x in range(0,len(uncleandata)):
				print(f'SEND: sending line number {x}')
				cleandata = uncleandata[x].replace("\r", "").replace("\n", str(replacer))
				await sendingchannel.send(str(cleandata))
@send.error
async def send_error(ctx, error):
	if isinstance(error, commands.MissingPermissions):
		errormsg = "You are missing the required permissions to run this command!"
	elif isinstance(error, commands.MissingRequiredArgument):
		errormsg = f"Missing a required argument: {error}"
	elif isinstance(error, commands.ConversionError):
		errormsg = str(error)
	else:
		errormsg = "Oh no! Something went wrong while running the command!"
	await ctx.send(errormsg, delete_after=15)
	await ctx.send(str(error), delete_after=20)
	print(error)


client.run(token, bot=False)

