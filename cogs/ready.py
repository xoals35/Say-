import discord
from discord.ext import commands
import asyncio
from urllib import request


class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"ready.py 에서 봇을 켰습니다.")
        

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong!")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            embed=discord.Embed(title=f'환영합니다!',description=f'{member.mention}님이  {member.guild}에 들어오셨습니다. 환영합니다 ! \n현재 서버 인원수: {str(len(member.guild.members))}명',color=embedcolor)
            embed.set_footer(text="환영메시지를 받고싶지 않으시면 봇이 이 채널을 못보게 해주세요")
            embed.set_thumbnail(url=member.avatar_url)
            await member.guild.system_channel.send(embed=embed)
        except:
            pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        try:
            embed=discord.Embed(title=f'안녕히 가세요',description=f'{member.mention}님이  나가셨습니다. 안녕히 가세요 \n현재 서버 인원수: {str(len(member.guild.members))}명',color=embederrorcolor)
            embed.set_footer(text="환영메시지를 받고싶지 않으시면 봇이 이 채널을 못보게 해주세요")
            embed.set_thumbnail(url=member.avatar_url)
            await member.guild.system_channel.send(embed=embed)
        except:
            pass

   
def setup(bot):
    bot.add_cog(Test(bot))