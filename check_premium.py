import os
import json



def is_premium(ctx):
    whitelist = json.loads(os.getenv('whitelist_discord'))
    for e in whitelist:
        if e == ctx.author.id:
            return True
        if e == ctx.message.channel.id:
            return True
        if e == ctx.message.guild.id:
            return True
        if e in [role.id for role in ctx.author.roles]:
            return True
    return False

