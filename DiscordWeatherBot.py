
#
#   PLEASE READ BEFORE RUNNING:
#       -   The following program requires an existing discord bot made using the DISCORD-API
#           -   You can make one following these instructions: https://discord.com/developers/docs/intro
#           -   This program lets you define what the bot does
#
#   This dicord bot requires the following to operate
#       1:  TOKEN           |   This is your bot identifier. Keep this secret
#       2:  SERVER_ID       |   The Server you want the bot to be active in
#       3:  CHANNEL_ID      |   The Channel you want the bot to post the weather data to
#       4:  ACTIVIY_ID      |   The Channel you want the bot to post it's actions for logging purposes
#
#   How to get the IDs
#       1:  SERVER_ID:
#           1:  Navigate to Server
#           2:  Right-click Server Name near top left
#           3:  Click "Copy Server ID"
#       2:  CHANNEL_ID:
#           1:  Navigate to Server
#           2:  Right-click Channel Name
#           3:  Click "Copy Channel ID"
#       3:  ACTIVIY_ID:
#           1:  Same Steps as CHANNEL_ID
#
#   The purposes of the project:
#       1:  Serve as an introduction to web-scraping as a form of data collection
#       2:  Serve as an introduction to integrating programs with an existing interface
#       3:  
#
#   How it works:
#       -   Set Discord required constants
#       -   Set time to send the message
#       -   WeatherScraper is created
#       -   Discord Bot Client is set up
#       -   On Ready Bot logs in
#       -   Scrapes Weather data at a random time before the message time
#       -   Sends log message in activity channel
#       -   Sends daily message in channel at preset time
#       -   Sends log message in activity channel
#       -   Waits until next day
#
#   Async is used for some basic responses to certain messages
#
#   For Usage on RaspberryPi (Assuming os works and internet connection established)
#       1:  SSH into Raspberry Pi
#       2:  Transfer files
#       3:  Use tmux to create separate thread session
#       4:  Attach to session
#       5:  Run DiscordWeatherBot.py
#       6:  Detatch from session
#       7:  Disconnect from SSH
#

#------------------------------------------CODE-STARTS-HERE----------------------------------------

import discord
import asyncio
from datetime import datetime, timedelta
import WeatherScraper as scraper
import random as rand

TOKEN = 'YOUR_BOT_TOKEN'
SERVER_ID = 'SERVER_ID'
CHANNEL_ID = 'CHANNEL_ID'
ACTIVIY_ID = 'ACTIVITY_ID'

# The time of day you want to send the daily message (in 24-hour format)
DAILY_MESSAGE_TIME = '04:00'
SAFETY_WAIT_TIME = timedelta(minutes = 5)

location = scraper.locations[0]
scrape = scraper.Weather_App(location)

client = discord.Client(intents=discord.Intents.all())

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

    current_time = datetime.now()
    server = client.get_guild(SERVER_ID)
    channel = server.get_channel(ACTIVIY_ID)
    await channel.send("Discord Bot logged in at " + str(current_time))
    # Start the loop to send the daily message
    await send_daily_message()

async def send_daily_message():
    while True:
        # Get the current time
        now = datetime.now()

        # Calculate the time for the next daily message
        target_time = datetime.strptime(DAILY_MESSAGE_TIME, '%H:%M')
        target_datetime = datetime(now.year, now.month, now.day, target_time.hour, target_time.minute)
        if target_datetime < now:
            target_datetime += timedelta(days=1)

        flux = timedelta(minutes = rand.randint(0,30))
        
        # Calculate the delay until the next daily message
        delay1= (target_datetime - now - flux)
        delay2 = flux

        # Wait until it's time to renew the weather data
        server = client.get_guild(SERVER_ID)
        channel = server.get_channel(ACTIVIY_ID)
        await channel.send("Waiting for " + str(delay1) + " seconds")
        await asyncio.sleep(delay1.total_seconds())

        # Reset the scraper page to today's page
        scrape = scraper.Weather_App(location)
        await channel.send("Updated weather data")

        # Wait until it's time to send the daily message
        await channel.send("Waiting for " + str(delay2) + " seconds")
        await asyncio.sleep(delay2.total_seconds())

        # Get the server and channel objects
        server = client.get_guild(SERVER_ID)
        channel = server.get_channel(CHANNEL_ID)

        # Send the daily message
        await channel.send(scrape.todays_high_and_low() + '\n' + scrape.get_precip())
        await asyncio.sleep(SAFETY_WAIT_TIME.total_seconds())

@client.event
async def on_message(message):              #When a message is recieved
    if message.author == client.user:       #If the message was sent by the bot
        return                              #Do nothing

    if message.content.startswith('good morning'):
        await message.channel.send('Good Morning!')

    if message.content.startswith('how are you'):
        await message.channel.send('I am doing well. Thank you for asking.')

    if message.content.startswith('!current_weather'):
        await message.channel.send(scrape.format_current_weather() + '\n' + scrape.get_precip())

    if message.content.startswith('!todays_weather'):
        await message.channel.send(scrape.todays_high_and_low() + '\n' + scrape.get_precip())

    #if message.content.startswith('!set_location'):
    #   await message.channel.send(scrape.todays_high_and_low() + '\n' + scrape.get_precip())

    if message.content.startswith('!help'):
        await message.channel.send('Here are the commands that have been implemented: ' +
        '\n !current_weather: Returns the current weather and the rain chance' +
        '\n !todays_weather: Returns the days high and low temps and rain chance')

# Run the bot
client.run(TOKEN)
