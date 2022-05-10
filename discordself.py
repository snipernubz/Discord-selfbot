import discord
from discord.ext import commands
import logging
#import asyncio
import urllib.request
import mimetypes
import os.path
import json
import youtube_dl


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

logging.basicConfig(level=logging.INFO)

def guess_type_of(link, strict=True):
    link_type, _ = mimetypes.guess_type(link)
    if link_type is None and strict:
        u = urllib.urlopen(link)
        link_type = u.headers.gettype() # or using: u.info().gettype()
    return link_type

@client.event
async def on_ready():
	print(f'We have logged in as {client.user}')

	#client.load_extension('./cogs/voice')
	#print("loaded Music extension")

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

#voice stuff

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def play(self, ctx, *, query):
        """Plays a file from the local filesystem"""

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)

        await ctx.send(f'Now playing: {query}')

    @commands.command()
    async def yt(self, ctx, *, url):
        """Plays from a url (almost anything youtube_dl supports)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

        await ctx.send(f'Now playing: {player.title}')

    @commands.command()
    async def stream(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

        await ctx.send(f'Now playing: {player.title}')

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @play.before_invoke
    @yt.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


#client.add_cog(Music(client))
client.run(token, bot=False)

