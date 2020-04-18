# SierraOne
`SierraOne` is a simple shared reverse shell over Discord, based on [SierraTwo](https://github.com/berkgoksel/SierraTwo) that works over Slack. The logic is pretty much the same, however the Discord API is cleaner as well as easier to develop with. I find SierraOne to be more successful than It's peer.

# Why?
The idea is to have a shell the whole team can play around with during a CTF game. Also, we like using Discord as [@ExploitStudio](https://exploit.studio/). The traffic flows through Discord (and optionally, Mega Upload) therefore generating IoC's and rules for Sierra should be harder than your regular reverse shell. Although Sierra could be used for pentesting, I highly discourage you from doing so. Discord keeps record of all chat history which might lead to disclosure of confidential data. It is recommended to pack/crypt the binaries before use. 

## Usage
`SierraOne` only supports Python 3.x.

### Direct Usage
#### Windows
Not available. Instead, refer to [building](#building) to build an `.exe` for Windows.

#### Linux
Running SierraOne
```
$ sudo apt install python3-pip
$ pip3 install -r requirements.txt
$ python3 SierraOne.py
```

### Building
To build an executable:

```
$ sudo apt install python3-pip winbind wine winetricks
$ wget https://www.python.org/ftp/python/3.8.2/python-3.8.2-amd64.exe
$ wine python-3.8.2-amd64.exe
$ pip3 install -r requirements.txt
$ wine pip install -r wine_requirements.txt
$ python3 builder.py -o <TARGET SYSTEM>
```

#### **BE SURE TO ADD PYTHON TO PATH WHEN INSTALLING WITH WINE**

The following commands will setup Wine with 64 bit Python 3.8.2 on your system. `<TARGET SYSTEM>` can be either 
`Windows` or `Linux`. After building the executable, check the `dist` folder for your exectuable.

For example, running `python3 builder.py -o Linux` on a 64 bit Linux will generate a 64 bit executable. Same logic 
applies for `-o Windows`. If you want to generate a 32 bit executable, you'd have to install 32 bit Python instead of 
64 bit (on your Linux and/or Wine).

If built for Windows:
- The executable's name will be `msdtc.exe`
- Executable will automatically minimize and hide itself

If built for Linux:
- The executable's name will by `system`.

## Configuration
To use `SierraOne`, create a new server or be a part of a Discord server where you are an admin. Afterwards go to 
[Discord Developer Portal][Discord Developer Portal] and create a new application. In your application's settings, go 
to the `Bot` tab and turn your application into a bot. Then, go to the `OAuth` tab and tick `Bot` in `Scopes` and 
`Administrator` in `Bot Permissions`. Then, use the generated link to add the bot to your server.

Finally, copy `Token` in `Bot` tab of [Discord Developer Portal][Discord Developer Portal] and copy `Server ID` from 
`Widget` tab found on your Discord server's settings and paste the said info to their corresponding places `config.py`.

Optionally, you can integrate [Mega][Mega] in `config.py`, where the bot will upload files larger than 7.5 MB to your Mega 
account.

## Disclaimers
- This project is for educational purposes only. The developers and contributors are not responsible for any damage 
that may be caused by this program nor any consequences that may arise.
- By using this program you accept that the developers and contributors are not responsible if you violate 
[Discord's Terms of Service][Discord ToS], [Discord's API Terms of Service][Discord API ToS] and [Mega.nz's ToS][Mega ToS].
- With the current permissions of the app, `SierraOne` will have an admin access over your workspace.

[Discord Developer Portal]: https://discordapp.com/developers/applications
[Mega]:                     https://mega.nz
[Discord ToS]:              https://discordapp.com/terms
[Discord API ToS]:          https://discordapp.com/developers/docs/legal
[Mega ToS]:                 https://mega.nz/terms

## Acknowledgements:
- Shoutout to @Arszilla for helping out with development and testing.
