import discord
from discord.ext import commands
from concurrent.futures import ThreadPoolExecutor
import asyncio
import os
import json

from simple_client import SimpleClient

class UserInfo(commands.Cog):
    """Commands related to user lookup."""
    def __init__(self, bot):
        self.bot = bot
        creds = json.loads(os.getenv('simple_login'))
        self.sc = SimpleClient(creds[0],creds[1])



    async def async_get_uid(self, name):
        loop = asyncio.get_event_loop()
        searched_user, uid = await loop.run_in_executor(ThreadPoolExecutor(),
                                                        self.sc.get_uid, name)
        return searched_user, uid

    async def async_get_prof(self, uid):
        loop = asyncio.get_event_loop()
        prof = await loop.run_in_executor(ThreadPoolExecutor(),
                                                        self.sc.get_prof, uid)
        return prof

    async def async_get_location(self, uid):
        loop = asyncio.get_event_loop()
        place = await loop.run_in_executor(ThreadPoolExecutor(),
                                                        self.sc.get_location, uid)
        return place


    @commands.command(name='user', aliases=['u'])
    @commands.guild_only()
    async def detailed_userinfo(self, ctx, *, name):
        """Detailed user info"""
        await ctx.message.delete()

        if name[-1] == "_":
            uid = int(name[:-1])
        else:
            _, uid = await self.async_get_uid(name)
            if not uid:
                await ctx.send(f'{name} not found.')
                return
        prof = await self.async_get_prof(uid)

        if not prof:
            await ctx.send(f'Try again after few minutes.')
            return

        embed = discord.Embed(title=prof.username, colour=discord.Colour(0x3bbe65))

        embed.set_image(url=prof.img_url())
        embed.set_thumbnail(url=prof.img_url('head2.png'))
        embed.set_author(name="User Info")

        embed.add_field(name="Userid", value=f"{prof.uid}", inline=True)
        embed.add_field(name="Last active", value=prof.last_active(), inline=True)
        embed.add_field(name="Coins", value=f'{prof.coins():,}')
        embed.add_field(name="Bio", value=f"```{prof.bio()}```")

        await ctx.send(embed=embed)

    @commands.command(name='locate', aliases=['l'])
    @commands.guild_only()
    async def locate_user(self, ctx, *, name):
        """Locate user"""
        await ctx.message.delete()
        
        username, uid = await self.async_get_uid(name)
        if not uid:
            await ctx.send(f'{name} not found.')
            return
        place = await self.async_get_location(uid)

        embed = discord.Embed(title=username, colour=discord.Colour(0x3bbe65))
        embed.set_author(name="Locate")
        if place:
            embed.add_field(name="Userid", value=f"{place['located_uid']}", inline=False)
            embed.add_field(name="Place", value=f"{place['area']}", inline=True)
            if 'condo_owner_uid' in place:
                embed.add_field(name="Condo Owner ID", value=f"{place['condo_owner_uid']}", inline=True)
        else:
            embed.add_field(name="Status", value="Offline", inline=False)



        await ctx.send(embed=embed)






def setup(bot):
    bot.add_cog(UserInfo(bot))
