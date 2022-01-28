# discoalia

DiscordでディスクオリアするためのBotです。

* AWS SAM CLI 
* python 3.8

Discordのアプリケーションコマンドは別で登録してください。 [Discord Developer Portal | Global Application Command](https://discord.com/developers/docs/interactions/application-commands#create-global-application-command)

[Slash CommandsでサーバレスなDiscordアプリを作る ｜ loop.run_forever()](https://note.sarisia.cc/entry/discord-slash-commands/) を参考にさせていただきました。

## Deploy to AWS

```
$ sam build
$ sam deploy --guided
```
