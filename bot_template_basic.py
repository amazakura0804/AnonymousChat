# -*- coding: utf-8 -*-

import anonchat
import discord
import asyncio
import logging
import json
from collections import namedtuple
from textwrap import dedent
import os
from io import BytesIO
import html
import typing

asyncio.set_event_loop(asyncio.new_event_loop())
logging.basicConfig(level=logging.INFO)

token = os.environ['token']

welcome_message = '''
{member.mention}
WELCOME !!
This is Anonymous Chat by nekojyarasi#9236
https://github.com/watosar/AnonymousChat


・機能概要
ユーザーが使用可能な機能は以下の2つです。
①@ID 又は @番号 でそのメンバーにメンション
②>>番号 でメッセージ引用
有効なメンションでは ＠ 及び >> が送信時に絵文字に置き換えられます。
これは可読性の向上を意図したもので、ユーザー側からこの絵文字を使用する事は出来ません。

ユーザーにはそれぞれ専用のチャンネルが割り当てられており、その内部ではメッセージがそのユーザーに対して調整されます。具体的には以下の3項目です。
①ユーザー自身のメッセージの送信者アイコンにユーザーのものと同一のものを使用
②ID を YOU として表示
③@ID 又は @番号 によるメンションをそのユーザーへのものに変換

'''

MessageMimic = namedtuple('MessageMimic', ('content', 'author', 'created_at'))
UserMimic = namedtuple('UserMimic', ('name', ))


client = anonchat.AnoncBaseClient(
    max_messages = 100,
    use_default_system_channel=True,
    anonc_system_channels_info=[
      {
        'name': name,
        'topic': 'for AnonyousChatBot'
      } for name in ['count', 'history', 'timer']
    ],
    nsfw=True,
    with_role=True,
    show_chat_id=True,
    anonc_default_name='名無し'
)


async def update_presence() -> None:
    game = discord.Game(name=f'{len(client.anonc_guild.anonc_chat_channels)}人')
    print(f'now anonc have {len(client.anonc_guild.anonc_chat_channels)}members')
    await client.change_presence(activity=game) 
    
    
async def send_to_bot_owner(content) -> None:
    print(content)
    try:
        await client.bot_owner.send(content)
    except discord.errors.Forbidden as e:
        print('Exception', e)


def message_to_html_style(message) -> str:
    msg = webhook_info_message_to_message_obj(message)
    return dedent(f'''\
    <p class="author"><font>{msg.author.name}</font>&nbsp;&nbsp;<font>{str(msg.created_at).split('.')[0]}</font></p>
    <p class="content">{html.escape(msg.content).replace(chr(10),'<br>')}</p>''')
    

async def make_history_html_file() -> typing.Optional[discord.File]:
    channel = client.anonc_guild.anonc_system_history_channel
    messages = []
    history_to = None
    msg = None
    async for msg in channel.history(limit=1000):
        if not history_to:
            history_to = str(msg.created_at.date())
        messages.append(message_to_html_style(msg))
    else:
        if not msg:
            return None
        history_from = str(msg.created_at.date())
    base = ''
    with open('./data/history-template.html', encoding='utf-8') as f:
        base = f.read()
    f = discord.File(
        BytesIO(
            bytearray(
                base.replace(
                    '{history_from}', history_from
                ).replace(
                    '{history_to}', history_to
                ).replace(
                    '{messages}', ''.join(reversed(messages)).replace(
                        ':msg_anchor:', '>>'
                    ).replace(
                        ':at_sign:', '@'
                    )
                ),
                'utf-8'
            )
        ),
        filename='history.html'
    )
    return f
     

@client.event
async def on_anonc_ready() -> None:
    await update_presence()
    await send_to_bot_owner('I’m ready')
    print('member guilds')
    for g in client.guilds:
        print(f'{g.name}:{len(g.members)}members')
        if g == client.anonc_guild.anonc_system_guild and client.bot_owner not in g.members:
            invite = (await g.invites())[0]
            print(f'you should join here {invite}')
    #print(f'guild base name is {client.anonc_guild.base_name}')


@client.event
async def init_anonc_count() -> int:
    ch = client.anonc_guild.anonc_system_count_channel
    async for m in ch.history(limit=1):
        return int(m.content)
    else:
        return 0
        

@client.event
async def on_anonc_count_update(value: int) -> None:
    await client.anonc_guild.anonc_system_count_channel.send(value)
        
  
@client.event
async def on_anonc_message(anonc_message: anonchat.message.AnoncMessage) -> None:
    # await run_public_command(message)
    msg_data = anonc_message.to_dict()
    data = json.dumps(msg_data ,ensure_ascii=False)
    if len(data)>2000:
        msg_data.pop('embeds')
        data = json.dumps(msg_data ,ensure_ascii=False)
        new_len = len(data)
        if new_len>2000:
            msg_data['content']=msg_data['content'][:2000-new_len]
            data = json.dumps(msg_data ,ensure_ascii=False)
    await client.anonc_guild.anonc_system_history_channel.send(data)
  
  
@client.event
async def on_direct_message(message: discord.Message) -> None:
    if message.author == client.user:
        return
    if message.author != client.bot_owner:
        await send_to_bot_owner(f'__message from {message.author}:{message.author.mention}__\n{message.content}')
    if message.content == 'close':
        await client.logout()
        client.loop.close()
    elif message.content == 'reset':
        print('reset anonc')
        await client.on_ready()
    elif message.content == 'enable owner authority':
        for g in client.guilds:
            member = g.get_member(message.author.id)
            if member.top_role.name == 'bot owner':
                continue
            
            await member.add_roles(next(i for i in member.guild.roles if i.name=='bot owner'))
            client.anonc_guild.get_anonc_chat_channel_from_user(member).anonc_id = 'owner'
  
  
@client.event
async def on_message_at_timer_channel(message: discord.Message) -> None:
    print(f'reset anonc id : {message.content}')
    await client.anonc_guild.reset_all_anonc_id()
    await send_to_bot_owner('anonc id reseted')
    

@client.event
async def on_message_at_general_channel(message: discord.Message) -> None:
    if message.author == client.user:
        return
    content = message.content
    print('general :', content)
    if content == 'change id present':
        client.show_chat_id = not client.show_chat_id
        await message.channel.send(f'now show chat id is {client.show_chat_id}')
    elif content == 'close':
        await client.logout()
        client.loop.close()
    elif message.content == 'reset':
        print('reset anonc')
        await client.on_ready()
    elif content == 'history':
        await message.channel.send(file=await make_history_html_file())
    elif content == 'disable owner authority':
        await message.author.edit(roles=[])
        ch = client.anonc_guild.get_anonc_chat_channel_from_user(message.author)
        ch.anonc_id = ch.topic
    elif content == 'disable use_role option':
        await client.anonc_guild.disable_use_role()
    elif content == 'enable use_role option':
        await client.anonc_guild.enable_use_role()
        
        
@client.event
async def on_anonc_member_guild_created(guild: discord.Guild) -> None:
    print('new guild created', guild)
    msg = await guild.system_channel.send('hello')
    invite = await msg.channel.create_invite()
    await send_to_bot_owner(f'registered new server : {invite.url}')
    anonc_system_guild = client.anonc_guild.anonc_system_guild
    if anonc_system_guild:
        await anonc_system_guild.system_channel.send(f'registered new server : {invite.url}')
    elif guild.name.split('-')[-1] == '0':
        await guild.system_channel.send(f'registered new server : {invite.url}')
        
        
@client.event
async def on_anonc_member_join(anonc_chat_channel: anonchat.channel.AnoncChannel) -> None:
    message = await anonc_chat_channel.send(welcome_message.format(member=anonc_chat_channel.anonc_member))
    await message.pin()
    await update_presence()
    f = await make_history_html_file()
    if f:
        await anonc_chat_channel.send('here is this chat log', file=f)
        

@client.event
async def on_anonc_member_removed(member: discord.Member) -> None:
    print(f'{member} removed')
    await update_presence()
  
  
def webhook_info_message_to_message_obj(message: discord.Message) -> MessageMimic:
    try:
        info_dict = json.loads(message.content)
    except Exception as e:
        print(e)
        print(message.content)
        info_dict = {'content':'ERROR','username':'ERROR'}
        
    msg = MessageMimic(
        content=info_dict['content'],
        author=UserMimic(name=info_dict['username']),
        created_at=message.created_at
    )
    return msg
 
 
@client.event
async def get_message_numbered(num: int) -> MessageMimic:
    channel = client.anonc_guild.anonc_system_history_channel
    loop_limit = client.anonc_count - num
    async for message in channel.history(limit=loop_limit):
        pass
    msg = webhook_info_message_to_message_obj(message)
    if int(msg.author.name.split(':')[0]) == num:
        return msg
    logging.error(f'expect numbered-{num} but found\n```\n{message.author.name}\n{message.content}```')


@client.event
async def _is_message_for_chat(msg):
    if not await anonchat.AnoncBaseClient._is_message_for_chat(client, msg):
        return False
        
    if any(r.name=='Muted' for r in msg.author.roles):
        print('muted', msg.author)
        return False
        
    return True

client.run(token)

