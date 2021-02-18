import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv(dotenv_path='.env')



TOKEN = os.getenv('BOT_TOKEN')
bot = commands.Bot(command_prefix='!')
bot.remove_command('help')


my_cogs = ['cogs.user_info','cogs.crasher', 'cogs.gems']


for cog in my_cogs:
    bot.load_extension(cog)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="ourWorld die."))
    print(f"{bot.user} has connected to Discord.")

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="ModBot - Help", colour=discord.Colour(0x1e041f), description="ModBot is a basic ourWorld bot that features a collection of unpatched exploits in the game. The bot has its own accounts to interact with the game and it does not get linked with the target account in any way. The features provided here are only a Proof-of-Concept of unpatched glitches.")


    embed.add_field(inline=False,name="```!crash <ign>``` ```!c <ign>```", value="```Crashes user```")
    embed.add_field(inline=False,name="```!user <ign>``` ```!u <ign>```", value="``` View profiles of ourWorld accounts```")
    embed.add_field(inline=False,name="```!locate <ign>``` ```!l <ign>```", value=" ```Locate an ourWorld user```")

    await ctx.send(embed=embed)




bot.run(TOKEN)
