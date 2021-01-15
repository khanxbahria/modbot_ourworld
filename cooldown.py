import os
import time
import json

class Cooldown:
    def __init__(self, cooldown_env):
        self.dict = {}
        self.cooldown_env = cooldown_env

    def add(self,ctx):
        if not self.is_whitelisted(ctx):
            self.dict[ctx.message.author.id] = time.time()

    def check(self,ctx):
        start_time = self.dict.get(ctx.message.author.id)


        duration = int(os.getenv(self.cooldown_env))
        if self.is_whitelisted(ctx):
            duration = 0
        elif not self.is_premium(ctx):
            msg = "This command is only available for server boosters!"
            return msg
        if not start_time:
            return False
        finish_time = start_time + duration
        time_now = time.time()
        if time_now < finish_time:
            retry_after = finish_time-time_now
            m, s = divmod(int(retry_after), 60)
            h, m = divmod(m, 60)
            msg = f'This command is on {h:d}h {m:02d}m {s:02d}s cooldown!'

            return msg
        else:
            return False


    def reset(self,ctx):
        try:
            del self.dict[ctx.message.author.id]
        except:pass



    def is_whitelisted(self,ctx):
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

    def is_premium(self,ctx):
        whitelist = json.loads(os.getenv('booster_discord'))
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

