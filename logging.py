import discord
from discord.ext import commands

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = None # This should be set by a command or config

    async def get_log_channel(self, guild):
        if self.log_channel_id:
            return guild.get_channel(self.log_channel_id)
        return None

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def setlogchannel(self, ctx, channel: discord.TextChannel):
        """Sets the channel for moderation logs."""
        self.log_channel_id = channel.id
        await ctx.send(f"Log channel set to {channel.mention}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        log_channel = await self.get_log_channel(member.guild)
        if log_channel:
            embed = discord.Embed(title="Member Joined", description=f"{member.mention} ({member}) has joined the server.", color=discord.Color.green())
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            embed.set_footer(text=f"ID: {member.id}")
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        log_channel = await self.get_log_channel(member.guild)
        if log_channel:
            embed = discord.Embed(title="Member Left", description=f"{member.mention} ({member}) has left the server.", color=discord.Color.red())
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            embed.set_footer(text=f"ID: {member.id}")
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or not message.guild: return
        log_channel = await self.get_log_channel(message.guild)
        if log_channel:
            embed = discord.Embed(title="Message Deleted", color=discord.Color.orange())
            embed.add_field(name="Author", value=message.author.mention, inline=True)
            embed.add_field(name="Channel", value=message.channel.mention, inline=True)
            embed.add_field(name="Content", value=message.content or "(No content)", inline=False)
            embed.set_footer(text=f"Message ID: {message.id} | Author ID: {message.author.id}")
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or not before.guild or before.content == after.content: return
        log_channel = await self.get_log_channel(before.guild)
        if log_channel:
            embed = discord.Embed(title="Message Edited", color=discord.Color.blue())
            embed.add_field(name="Author", value=before.author.mention, inline=True)
            embed.add_field(name="Channel", value=before.channel.mention, inline=True)
            embed.add_field(name="Before", value=before.content or "(No content)", inline=False)
            embed.add_field(name="After", value=after.content or "(No content)", inline=False)
            embed.set_footer(text=f"Message ID: {before.id} | Author ID: {before.author.id}")
            await log_channel.send(embed=embed)

    # Custom logging for moderation actions (will be called from moderation cog)
    async def log_moderation_action(self, guild, action_type, moderator, target, reason=None, duration=None):
        log_channel = await self.get_log_channel(guild)
        if log_channel:
            embed = discord.Embed(title=f"{action_type} Action", color=discord.Color.red())
            embed.add_field(name="Moderator", value=moderator.mention, inline=True)
            embed.add_field(name="Target", value=target.mention, inline=True)
            if reason: embed.add_field(name="Reason", value=reason, inline=False)
            if duration: embed.add_field(name="Duration", value=duration, inline=True)
            embed.set_footer(text=f"Moderator ID: {moderator.id} | Target ID: {target.id}")
            await log_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Logging(bot))
