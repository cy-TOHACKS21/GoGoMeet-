import discord 
import os
from discord.ext import commands


# Retrieving bot token
fin = open('Saved/Keys.txt')
lines = list(map(lambda x: x.strip(), fin.readlines()))
fin.close()

token = lines[1]

# Bot setup
bot = commands.Bot(command_prefix = '-')
bot.remove_command('help')


# On ready event
@bot.event
async def on_ready():
    print('Status: Online') 
    activity = discord.Activity(name = 'Finding Meetings!', type = discord.ActivityType.playing)
    return await bot.change_presence(activity = activity)

# Kill command
@bot.command(aliases = ['exit'])
async def kill(ctx):
    if ctx.message.author.id == 665442546188681217:
        await ctx.send('**Status:** Offline**')
        await bot.logout()
    else:
        await ctx.send("Sorry, but you're not the bot owner.")

# Turn cog online
@bot.command(aliases = ['cogon'])
async def cog_online(ctx, extension):
    if ctx.message.author.id == 665442546188681217:
        bot.load_extension(f'Cogs.{extension}')
        await ctx.send(f':white_check_mark: **{extension}** loaded.')
    else:
        await ctx.send("Sorry, but you're not the bot owner.")

# Turn cog offline
@bot.command(aliases = ['cogoff'])
async def cog_offline(ctx, extension):
    if ctx.message.author.id == 665442546188681217:
        bot.unload_extension (f'Cogs.{extension}')
        await ctx.send(f':x: **{extension}** unloaded.')
    else:
        await ctx.send("Sorry, but you're not the bot owner.")

# Cogs
for filename in os.listdir('./Cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'Cogs.{filename[:-3]}')


# Run
bot.run(token)


