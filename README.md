# AnonymousChat
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)  
Discord上で5ch-likeな匿名チャットを動かすBot   
   
   
    
## Description  

ユーザー毎に専用チャンネルを割り当て、メッセージの送信をwebhookで置き換える事でアカウント情報を隠したままDiscordのチャットを利用できるようにします  

また、これによりメンションが出来なくなります。その代わりにチャットID(bot側で任意に変更可能)へのメンションが使えるようになっています 

`get_message_numbered`を書けばメッセージ番号でのメンションも出来るようになります。又、アンカー(">>")で引用も可能になります 
  
  
  
## Description about bot_template_basic.py
anonchatモジュールの利用例です    

- システムチャンネルの設定及びその利用   
    - anonc_system_channel_info に渡したdictの各項目と合致するチャンネルがあれば取得し設定。無ければ自動生成
    - 標準の`system_channel`(サーバー作成時自動生成される`general`)利用の可否
    - 設定した`system_channel`は`anonc_guild.anonc_system_{channel.name}_channel`でアクセス出来ます
    - メッセージ受信イベントは`on_message_at_{channel.name}_channel`
- `on_anonc_`類のイベントの利用例
- `get_message_numbered`の実装例
- チャットID更新の例
   
   
## Requirement
discord.py rewrite


## Deploy to Heroku

[![Heroku Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy?template=https://github.com/watosar/AnonymousChat)   
↑のボタンを押せばherokuにデプロイ出来ます。(アカウントの新規作成又は事前のログインが必要)   



## Author

Discord: nekojyarasi#9236   
Twitter: [@d7iy_l](https://twitter.com/d7iy_l)

