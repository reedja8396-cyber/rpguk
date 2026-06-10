import discord
from discord.ext import commands, tasks
import asyncio
import random

class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_giveaways = []
        self.check_giveaways.start()

    def cog_unload(self):
        self.check_giveaways.cancel()

    @tasks.loop(seconds=10.0)
    async def check_giveaways(self):
        now = discord.utils.utcnow()
        for giveaway in list(self.active_giveaways): # Iterate over a copy
            if now >= giveaway["end_time"]:
                self.active_giveaways.remove(giveaway)
                await self.end_giveaway(giveaway)

    @check_giveaways.before_loop
    async def before_check_giveaways(self):
        await self.bot.wait_until_ready()

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def gstart(self, ctx, duration: commands.TimedeltaConverter(default_unit="minutes"), winners: int, *, prize: str):
        """Starts a giveaway."""
        end_time = discord.utils.utcnow() + duration

        embed = discord.Embed(title=prize, description=f"React with 🎉 to enter!\nEnds: {discord.utils.format_dt(end_time, style=\'R\')}", color=discord.Color.green())
        embed.set_footer(text=f"Winners: {winners} | Hosted by: {ctx.author.display_name}")
        message = await ctx.send("🎉 **GIVEAWAY** 🎉", embed=embed)
        await message.add_reaction("🎉")

        self.active_giveaways.append({
            "message_id": message.id,
            "channel_id": ctx.channel.id,
            "guild_id": ctx.guild.id,
            "end_time": end_time,
            "winners": winners,
            "prize": prize,
            "host_id": ctx.author.id
        })
        await ctx.send(f"Giveaway for **{prize}** started! Ends in {duration}.")

    async def end_giveaway(self, giveaway_data):
        guild = self.bot.get_guild(giveaway_data["guild_id"])
        if not guild: return
        channel = guild.get_channel(giveaway_data["channel_id"])
        if not channel: return
        message = await channel.fetch_message(giveaway_data["message_id"])
        if not message: return

        users = [user async for user in message.reactions[0].users() if user != self.bot.user]

        if len(users) < giveaway_data["winners"]:
            await channel.send(f"Not enough participants for the giveaway of **{giveaway_data[\"prize\"]}**! ({len(users)} participants)")
            return
