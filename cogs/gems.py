import discord
from discord.ext import commands
from concurrent.futures import ThreadPoolExecutor
import asyncio
from itertools import cycle
import os
from gempy import GemPY
from cooldown import Cooldown


class Gems(commands.Cog):
    """Commands to earn gems"""
    def __init__(self, bot):
        self.bot = bot
        self.current_users = []
        self.cooldown = Cooldown('gem_cooldown')

    def create_embed(self, title, msg):
        embed = discord.Embed(title=title, colour=discord.Colour(0x3bbe65),
                                description=msg)
        embed.set_author(name="GemPY")
        return embed


    async def async_get_gems(self, miner):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(ThreadPoolExecutor(), miner.get_gems)
        return

    @commands.command(name='gems', aliases=['g'])
    @commands.guild_only()
    async def get_gems(self, ctx, *, name):
        """Exploits Jungroup offers to get gems."""
        msg = self.cooldown.check(ctx)
        if msg:
            await ctx.send(msg)
            return

        user_info = self.bot.get_cog('UserInfo')
        try:
            username, uid = await user_info.async_get_uid(name)
        except:
            await ctx.send(f'Try again after few minutes.')
            return
        if not uid:
            await ctx.send(f'{name} not found.')
            return
        if uid in self.current_users:
            await ctx.send(f'Already running for {username}')
            return

        miner = GemPY(uid)
        self.current_users.append(uid)
        self.cooldown.add(ctx)
        await ctx.send(embed=self.create_embed(username, "```Collecting gems...```"))
        await self.async_get_gems(miner)
        self.current_users.remove(uid)
        if not miner.gems:
            self.cooldown.reset(ctx)
            await ctx.send(embed=self.create_embed(username, "```No offers available :(```"))
        else:
            await ctx.send(embed=self.create_embed(username, f"```Collected {miner.gems} gems!```"))


def setup(bot):
    bot.add_cog(Gems(bot))
