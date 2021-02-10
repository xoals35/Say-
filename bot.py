import discord
from discord.ext import commands
import asyncio
import datetime
import random
import time
import sys
import json
import os
import discord as d
from discord.ext import commands, tasks
from discord.voice_client import VoiceClient
import youtube_dl
from bs4 import BeautifulSoup
import aiohttp

from random import choice

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
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
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




client = commands.Bot(command_prefix=">")

status = ['Jamming out to music!', 'Eating!', 'Sleeping!']
queue = []

@client.event
async def on_ready(): #봇이 준비되었을때 뭐라고하기
    user = len(client.users)
    server = len(client.guilds)
    message = [">관리자,>유저 한개만 쳐보세요!",  str(user) + "유저와 함께해요!", str(server) + "개의 서버에 세이봇이 같이운영해요!"]
    while True:
        await client.change_presence(status=discord.Status.online, activity=discord.Game(message[0]))
        message.append(message.pop(0))
        await asyncio.sleep(4)



@client.command()
async def 안녕(ctx):
	await ctx.send("그래 안녕!")

@client.command()
async def 핑(ctx):
    await ctx.send(f'퐁! {round(client.latency * 1000)}ms')

@client.command(aliases=['청소'])
@commands.has_permissions(administrator=True)
async def clear(ctx, l: int = 50):
   c = await ctx.channel.purge(limit=l)
   await ctx.send(f"`{len(c)}` 개의 메세지를 삭제했습니다.", delete_after=3)
   


@client.command()
async def 밴(ctx, user: discord.User):
	guild = ctx.guild
	mbed = discord.Embed(
		title = '처리 완료',
		description = f"{user}님이 밴을 당하셨어요!"
	)
	if ctx.author.guild_permissions.ban_members:
		await ctx.send(embed=mbed)
		await guild.ban(user=user)

@client.command()
async def 언밴(ctx, user: discord.User):
	guild = ctx.guild
	mbed = discord.Embed(
		title = '처리완료',
		description = f"{user}님을 언밴 했어요!"
	)
	if ctx.author.guild_permissions.ban_members:
		await ctx.send(embed=mbed)
		await guild.unban(user=user)

@client.command()
@commands.has_permissions(kick_members=True)
async def 킥(ctx, member: discord.member, *, reason=None):
	await member.kick(reason=reason)
	await ctx.send(f"{member}님을 킥했어요!")

@client.command(name="뮤트")
@commands.has_permissions(manage_messages=True)
async def mute(ctx , member: discord.Member, *, reason=None):
	guild = ctx.guild
	mutedRole = discord.utils.get(guild.roles, name="Muted")

	if not mutedRole:
		mutedRole = await guild.create_role(name="Muted")

		for channel in guild.channels:
			await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True, read_messages=False)

	await member.add_roles(mutedRole, reason=reason)
	await ctx.send(f"뮤트 {member.mention} 사유: {reason}으로 뮤트를 먹으셨습니다.")
	await member.send(f"뮤트 {member.mention} 사유: {reason}으로 뮤트를 먹으셨습니다.")


@client.command(name="언뮤트")
@commands.has_permissions(manage_messages=True)
async def unmute(ctx, member: discord.Member):
	mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")

	
			

	await member.remove_roles(mutedRole)
	await ctx.send(f"언뮤트 {member.mention}님이 언뮤트를 당하셨습니다.")
	await member.send(f"언뮤트 {member.mention}님이  언뮤트를 당하셨습니다.")


@client.command()
async def 관리자(ctx):
	em = discord.Embed(title = "관리자 명령어", description = "밑에 도움말을 보세요!")

	em.add_field(name = "관리자 명령어", value = "킥,밴,뮤트,언뮤트,언밴이 있습니다. ")
	em.add_field(name = "킥", value = "유저를 킥할수 있습니다.")
	em.add_field(name = "밴", value = "유저를 밴 할수있습니다.")
	em.add_field(name = "언벤", value = "유저를 언밴 할수있습니다.")
	em.add_field(name = "뮤트", value = "유저를 뮤트!")
	em.add_field(name = "언뮤트", value = "유저를 언뮤트") 

	await ctx.send(embed = em)

@client.command()
async def 유저(ctx):
	em = discord.Embed(title = "유저들이 쓸수있는 명령어", description = "밑에 도움말을 보세요!")

	em.add_field(name = "청소", value = "채팅을 청소 할수있습니다.")
	em.add_field(name = "핑", value = "봇의 응답핑을 확인 가능합니다.")


	await ctx.send(embed = em)




 
@client.command()
async def poll(ctx,*,message):
    emb=discord.Embed(title="투표", description=f"투표내용:{message}")
    msg=await ctx.channel.send(embed=emb)
    
    await msg.add_reaction('👍')            
    await msg.add_reaction('👎')

                 
@client.command()
@commands.has_role("Owner")
async def 경품(ctx, mins : int, * , prize: str):
	embed = discord.Embed(title = "상품!", description = f"{prize}", color = ctx.author.color)

	end = datetime.datetime.utcnow() + datetime.timedelta(seconds = mins*60)

	embed.add_field(name = "종료 시간:", value = f"{end} UTC")
	embed.set_footer(text = f"지금부터 {mins}분 후 Emds")

	my_msg = await ctx.send(embed = embed)

	await my_msg.add_reaction("🎉")

@client.command()
async def 리로드(ctx, extension):
    client.load_extension(f"cogs.{extension}")
    await ctx.send(f"Loaded extension: {extension}.")

@client.command()
async def 언로드(ctx, extension):
    client.unload_extension(f"cogs.{extension}")
    await ctx.send(f"Unloaded extension: {extension}.")

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")

@client.command()
async def 채널제거(ctx, channel: d.TextChannel):
	mbed = d.Embed(
		title = '완료!',
		description = f'{channel}이라는 채널을 삭제했습니다.',
	)
	if ctx.author.guild_permissions.manage_channels:
		await ctx.send(embed=mbed)
		await channel.delete()


@client.command()
async def 채널생성(ctx, channelName):
	guild = ctx.guild

	mbed = d.Embed(
		title = '완료!',
		description = "{}이라는 채널을 성공적으로 생성되었습니다.".format(channelName)
	)
	if ctx.author.guild_permissions.manage_channels:
		await guild.create_text_channel(name='{}'.format(channelName))
		await ctx.send(embed=mbed)
		
		
@client.command()
async def 따라해(ctx, *, text):
    await ctx.send(text)





@client.command()
async def dm(ctx, user: discord.User, *, msg):
	await ctx.send('전송을 완료했습니다.')
	await user.send(f'보낸사람:세이봇 \n내용:{msg}')

@client.command()
async def 서버정보(ctx):
    name = str(ctx.guild.name)
    description = str(ctx.guild.description)

    owner = str(ctx.guild.owner)
    id = str(ctx.guild.id)
    region = str(ctx.guild.region)
    memberCount = str(ctx.guild.member_count)

    icon = str(ctx.guild.icon_url)

    embed = discord.Embed(
        title=name + "서버정보",
        description=description,
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=icon)
    embed.add_field(name="서버 소유자", value=owner, inline=True)
    embed.add_field(name="서버 아이디", value=id, inline=True)
    embed.add_field(name="부위", value=region, inline=True)
    embed.add_field(name="멤버 수", value=memberCount, inline=True)

    await ctx.send(embed=embed)





client.run('봇토큰')