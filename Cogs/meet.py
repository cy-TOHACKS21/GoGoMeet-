import discord
import asyncio
import datetime
from discord.ext import commands
import os
import requests
import json
import pandas as pd
import re
from datetime import datetime, timedelta


# Retrieving Distance Matrix API key
fin = open('Saved/Keys.txt')
lines = list(map(lambda x: x.strip(), fin.readlines()))
fin.close()

API_KEY = lines[3]


class Meet_Cog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Meet: Online')

    @commands.command(aliases = ['gogomeet'])
    async def meet(self, ctx):

        # Basic wait_for message check
        def check(answer: discord.Message): 
            return answer.channel == ctx.channel and answer.author.id == ctx.author.id

        # Prompt user for origin locations
        origin_message = await ctx.send('**Enter origin locations (separate by |): **')
        try:
            origin_wait = await self.bot.wait_for('message', timeout = 180, check = check)
            origin = origin_wait.content.replace(' ', '+').split('|')
            origin = '|'.join(list(map(lambda x: x.strip(), origin)))
            await origin_wait.delete()
            await origin_message.delete()
        except asyncio.TimeoutError:
            await origin_message.delete()
            await ctx.send('Timed out.')
            return

        # Prompt user for destination location
        destination_message = await ctx.send('**Enter destination location: **')
        try:
            destination_wait = await self.bot.wait_for('message', timeout = 180, check = check)
            destination = destination_wait.content.replace(' ', '+')
            await destination_wait.delete()
            await destination_message.delete()
        except asyncio.TimeoutError:
            await destination_message.delete()
            await ctx.send('Timed out.')
            return

        # Prompt user for arrival time
        arrival_message = await ctx.send('**Enter arrival time (YYYY-MM-DD HH:MM:SS): **')
        try:
            arrival_wait = await self.bot.wait_for('message', timeout = 180, check = check)
            arrival_time = arrival_wait.content
            arrival_time = datetime.strptime(arrival_time, '%Y-%m-%d %H:%M:%S')
            await arrival_wait.delete()
            await arrival_message.delete()
        except asyncio.TimeoutError:
            await arrival_message.delete()
            await ctx.send('Timed out.')
            return

        # Get current time
        current_time = datetime.now().replace(microsecond = 0)
        
        # API call using given parameters
        url = f'https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin}&destinations={destination}&key={API_KEY}'
        request = requests.get(url)
        result = json.loads(request.text)

        # Retrieve full addresses for origins and destination
        origin_addresses = result['origin_addresses']
        dest_address = result['destination_addresses'][0]

        # Initialize variables for loop
        d = {}
        day_amount = sec_amount = min_amount = hour_amount = week_amount = 0
        count = 0

        # Loop through each origin address
        for i in origin_addresses:
            # Retrieve distance and duration between origin and destination
            distance = result['rows'][count]['elements'][0]['distance']['text']
            duration = result['rows'][count]['elements'][0]['duration']['text']

            # Parse string to create timedelta object
            time_split = re.findall('[^ ]+ [^ ]+', duration)
            for j in time_split:
                if 'day' in j:
                    day_amount = int(j.split()[0])
                elif 'sec' in j:
                    sec_amount = int(j.split()[0])
                elif 'min' in j:
                    min_amount = int(j.split()[0])
                elif 'hour' in j:
                    hour_amount = int(j.split()[0])
                elif 'week' in j:
                    week_amount = int(j.split()[0])

            # Create timedelta object and calculate departure time
            time_delta = timedelta(weeks = week_amount, days = day_amount, hours = hour_amount, minutes = min_amount, seconds = sec_amount)
            departure_time = arrival_time - time_delta

            if len(i) > 35:
                i = i[:35] + '...'

            # Add info to dictionary
            d[i] = [distance, duration, departure_time]
            count += 1

        # Create dataframe
        df = pd.DataFrame(d, index = ['Distance:', 'Duration:', 'Departure Time:'])

        # Creating results embed
        embed = discord.Embed(title = 'GoGoMeet!', colour = discord.Colour(0xefe61))
        embed.description = 'Meet up with friends without the hassle of waiting!'
        embed.set_thumbnail(url = 'https://imgur.com/jVdMcwL.png')

        embed.add_field(name = 'Current Time:', value = current_time, inline = False)
        embed.add_field(name = 'Arrival Time:', value = arrival_time, inline = False)
        embed.add_field(name = 'Destination:', value = dest_address, inline = False)

        embed.set_footer(text = 'GoGoMeet!', icon_url = 'https://imgur.com/jVdMcwL.png')
        embed.timestamp = datetime.utcnow()

        await ctx.send(embed = embed)
        await ctx.send(f'```{df}```')


def setup(bot):
    bot.add_cog(Meet_Cog(bot))
