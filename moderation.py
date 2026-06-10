import discord
from discord.ext import commands
from datetime import timedelta

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logging_cog = None

    async def cog_load(self):
        self.logging_cog = self.bot.get_cog("Logging")
        if not self.logging_cog:
            print("Logging cog not found. Moderation actions will not be logged.")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Kicks a member from the server."""
        await member.kick(reason=reason)
        await ctx.send(f'Member {member.mention} has been kicked. Reason: {reason}')
        if self.logging_cog: await self.logging_cog.log_moderation_action(ctx.guild, "Kick", ctx.author, member, reason=reason)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """Bans a member from the server."""
        await member.ban(reason=reason)
        await ctx.send(f'Member {member.mention} has been banned. Reason: {reason}')
        if self.logging_cog: await self.logging_cog.log_moderation_action(ctx.guild, "Ban", ctx.author, member, reason=reason)

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, minutes: int, *, reason=None):
        """Times out a member for a specified duration."""
        duration = timedelta(minutes=minutes)
        await member.timeout(duration, reason=reason)
        await ctx.send(f'Member {member.mention} has been timed out for {minutes} minutes. Reason: {reason}')
        if self.logging_cog: await self.logging_cog.log_moderation_action(ctx.guild, "Timeout", ctx.author, member, reason=reason, duration=f"{minutes} minutes")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        """Deletes a specified number of messages."""
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f'Deleted {len(deleted) - 1} messages.', delete_after=5)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, member: discord.Member, role: discord.Role):
        """Adds a role to a member."""
        await member.add_roles(role)
        await ctx.send(f'Added role {role.name} to {member.mention}')
        if self.logging_cog: await self.logging_cog.log_moderation_action(ctx.guild, "Add Role", ctx.author, member, reason=f"Added role {role.name}")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx, member: discord.Member, role: discord.Role):
        """Removes a role from a member."""
        await member.remove_roles(role)
        await ctx.send(f'Removed role {role.name} from {member.mention}')
        if self.logging_cog: await self.logging_cog.log_moderation_action(ctx.guild, "Remove Role", ctx.author, member, reason=f"Removed role {role.name}")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str):
        """Warns a member."""
        # In a real bot, you'd save this to a database
        await ctx.send(f'**Warning issued to {member.mention}**\nReason: {reason}')
        if self.logging_cog: await self.logging_cog.log_moderation_action(ctx.guild, "Warn", ctx.author, member, reason=reason)
        try:
            await member.send(f'You have been warned in {ctx.guild.name} for: {reason}')
        except discord.Forbidden:
            await ctx.send("Could not DM the user about the warning.")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
