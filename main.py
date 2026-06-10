import discord
from discord.ext import commands
import os
import asyncio

# Intents are required for advanced bots to track members and messages
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')
    # Load all cogs from the cogs folder
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'Loaded extension: {filename}')
            except Exception as e:
                print(f'Failed to load extension {filename}: {e}')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing a required argument. Please check the command usage. ({error})")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"Bad argument provided. Please check the argument types. ({error})")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("That command does not exist.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have the necessary permissions to run this command.")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send(f"I don't have the necessary permissions to perform this action. I need: {', '.join(error.missing_permissions)}")
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.send("This command cannot be used in private messages.")
    elif isinstance(error, commands.NotOwner):
        await ctx.send("This command can only be used by the bot owner.")
    else:
        print(f"Ignoring exception in command {ctx.command}:", error)
        await ctx.send("An unexpected error occurred while running this command.")

async def main():
    # Token should be provided via environment variable or a config file
    # For security, do not hardcode the token
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("Error: DISCORD_BOT_TOKEN environment variable not set.")
        return
    
    async with bot:
        await bot.start(token)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
