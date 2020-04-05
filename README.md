# SierraTwo
`SierraOne` is a simple shared reverse shell over Discord.

## Usage
`SierraOne` only supports Python 3.x.

### Windows
```
$ pip install -r requirements.txt
$ python SierraOne.py
```

### Linux
```
$ sudo apt install python3-pip
$ pip3 install -r requirements.txt
$ python3 SierraOne.py
```

## Configuration
To use `SierraOne`, create a new server or be a part of a Discord server where you are an admin. Afterwards go to [Discord Developer Portal] and create a new application. In your application's settings, go to the `Bot` tab and turn your application into a bot. Then, go to the `OAuth` tab and tick `Bot` in `Scopes` and `Administrator` in `Bot Permissions`. Then, use the generated link to add the bot to your server.

Finally, copy `Token` in `Bot` tab of [Discord Developer Portal] and copy `Server ID` from `Widget` tab found on your Discord server's settings and paste the said info to their corresponding places `config.yaml`.

[Discord Developer Portal]: https://discordapp.com/developers/applications