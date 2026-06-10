import discord
from discord.ext import commands

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reaction_role_messages = {}

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def setup_reaction_role(self, ctx, message_id: int, emoji: str, role: discord.Role):
        """Sets up a reaction role on a specific message."""
        try:
            message = await ctx.fetch_message(message_id)
            await message.add_reaction(emoji)
            self.reaction_role_messages[str(message_id)] = {
                "emoji": emoji,
                "role_id": role.id,
                "guild_id": ctx.guild.id
            }
            await ctx.send(f"Reaction role set up for message {message_id}: {emoji} gives {role.name}")
        except discord.NotFound:
            await ctx.send("Message not found. Please ensure the message ID is correct and in this channel.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.guild_id is None: # DM reaction
            return
        
        if str(payload.message_id) in self.reaction_role_messages:
            data = self.reaction_role_messages[str(payload.message_id)]
            if str(payload.emoji) == data["emoji"]:
                guild = self.bot.get_guild(payload.guild_id)
                if guild is None: return
                
                role = guild.get_role(data["role_id"])
                if role is None: return
                
                member = guild.get_member(payload.user_id)
                if member is None: return
                
                if role not in member.roles:
                    await member.add_roles(role)
                    print(f"Added role {role.name} to {member.name}")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.guild_id is None: # DM reaction
            return

        if str(payload.message_id) in self.reaction_role_messages:
            data = self.reaction_role_messages[str(payload.message_id)]
            if str(payload.emoji) == data["emoji"]:
                guild = self.bot.get_guild(payload.guild_id)
                if guild is None: return
                
                role = guild.get_role(data["role_id"])
                if role is None: return
                
                member = guild.get_member(payload.user_id)
                if member is None: return
                
                if role in member.roles:
                    await member.remove_roles(role)
                    print(f"Removed role {role.name} from {member.name}")

async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))
