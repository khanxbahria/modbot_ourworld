import discord
from discord.ext import commands
import asyncio
import os
import json

from crasher_client import CrasherClient
from cooldown import Cooldown


class Crasher(commands.Cog):
    """Crasher commands."""
    def __init__(self, bot):
        self.bot = bot
        self.cooldown = Cooldown('crasher_cooldown')

        self.crash_uids = []
        # crasher_creds = [(f"r{i}@r.com", "password") for i in range(1,6)]

        crasher_creds = json.loads(os.getenv('crasher_logins'))
        self.crasher_clients = [CrasherClient(email, pwd, self.crash_uids) for email, pwd in crasher_creds.items()]
        # self.crasher_clients = [CrasherClient("teehee@nn.com", "password", self.crash_uids)]
        try:
            self.read_crash_list()
        except Exception as e:
            print("error reading crash list", e)

      
    def read_crash_list(self):
        with open('crash_list.json') as f:
            d = json.load(f)
        self.crash_uids = [(int(u),s) for u,s in d.items()]
        self.update_payload()

    def update_payload(self):
        for crasher_client in self.crasher_clients:
            crasher_client.update_payload()


    @commands.command(name='crash', aliases=['c'])
    @commands.guild_only()
    async def add_crash(self, ctx, *, name):
        """Crashes the user"""
        
        if name[-1] == "_":
            uid = int(name[:-1])
            searched_user = name
        else:
            user_info = self.bot.get_cog('UserInfo')
            try:
                searched_user, uid = await user_info.async_get_uid(name)
            except:
                await ctx.send(f'Try again after few minutes.')
                return
        if uid:
            d={}
            self.crash_uids.append((uid, searched_user))
            for uid, searched_user in self.crash_uids:
                d[uid] = searched_user
            
            with open('crash_list.json', 'w') as f:
                json.dump(d,f, indent=4)
            self.update_payload()
            embed = discord.Embed(title=f"Crashing\n{searched_user}  ```{uid}```", colour=discord.Colour(0xcc0000))
            # self.cooldown.add(ctx)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f'{name} not found.')

    @commands.command(name='stopcrash', aliases=['sc'])
    @commands.guild_only()
    async def stop_crash(self, ctx, *, name):
        """Stops crashing the user"""
        if not self.cooldown.is_whitelisted(ctx):
            return

        for uid, username in self.crash_uids[:]:
            if name.lower() == username.lower():
                self.crash_uids.remove((uid, username))
                self.update_payload()
                embed = discord.Embed(title=f"Stopped crashing\n{username}", colour=discord.Colour(0xf3ea00))
                # embed.set_author(name="Stopped crashing")
                await ctx.send(embed=embed)

    @commands.command(name='listcrash', aliases=['lc'])
    @commands.guild_only()
    async def list_crash(self, ctx):
        """Prints crashing list"""
        
        str_uids = [f"```{name}```" for uid, name in self.crash_uids]
        if str_uids:
            result = "".join(str_uids)
        else: result = "None"

        embed = discord.Embed(title=f"Crashing List\n", description=result, colour=discord.Colour(0x7289da))
        await ctx.send(embed=embed)




def setup(bot):
    bot.add_cog(Crasher(bot))
