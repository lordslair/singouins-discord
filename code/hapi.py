#!/usr/bin/env python3
# -*- coding: utf8 -*-

import re

from datetime           import datetime

# Shorted definition for actual now() with proper format
def mynow(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Log System imports
print(f'{mynow()} [BOT] System   imports [✓]')

import asyncio
import discord

from discord.ext        import commands

# Log Discord imports
print(f'{mynow()} [BOT] Discord  imports [✓]')

from variables          import token, PCS_URL
from utils.requests     import *
from utils.redis        import yqueue_get

# Log Internal imports
print(f'{mynow()} [BOT] Internal imports [✓]')

client = commands.Bot(command_prefix = '!')

# Welcome message in the logs on daemon start
print(f'{mynow()} [BOT] Daemon started   [✓]')
# Pre-flight check for API connection
if api_admin_up(): tick = '✓'
else             : tick = '✗'
print(f'{mynow()} [BOT] API connection   [{tick}] ({API_URL})')

@client.event
async def on_ready():
    channel = discord.utils.get(client.get_all_channels(), name='singouins')
    if channel:
        tick = '✓'
        #await channel.send(msg_ready)
    else: tick = '✗'
    print(f'{mynow()} [BOT] Discord ready    [{tick}]')

#
# Commands
#

# !ping
@client.command(name='hapi', help='Gives you Discord bot latency')
async def ping(ctx):
    member       = ctx.message.author
    discordname  = member.name + '#' + member.discriminator

    print(f'{mynow()} [{ctx.message.channel}][{member}] !ping')
    await ctx.send(f'Pong! {round (client.latency * 1000)}ms ')

#
# Tasks definition
#

async def yqueue_check(timer):
    while client.is_ready:
        # Opening Queue
        try:
            yqueue_name = 'discord'
            msgs        = yqueue_get(yqueue_name)
        except Exception as e:
            print(f'{mynow()} [BOT] Unable to retrieve data from yarqueue:{yqueue_name}')
        else:
            for msg in msgs:
                channel = discord.utils.get(client.get_all_channels(), name=msg['scope'].lower())
                if msg['embed']:
                    color_int  = msg['payload']['color_int']
                    path       = msg['payload']['path']
                    title      = msg['payload']['title']
                    item       = msg['payload']['item']
                    footer     = msg['payload']['footer']

                    answer = None
                    embed  = discord.Embed(color=color_int)
                    embed.set_thumbnail(url=f'{PCS_URL}{path}')
                    embed.add_field(name=title,
                                    value=item,
                                    inline=True)
                    embed.set_footer(text=footer)
                else:
                    answer = msg['payload']
                    embed  = None

                if channel:
                    try:
                        await channel.send(answer, embed=embed)
                    except Exception as e:
                        print(f'{mynow()} [{channel.name}] [BOT] ───> Send message to channel:{channel.name} failed')
                    else:
                        print(f'{mynow()} [{channel.name}] [BOT] ───> Send messag to channel:{channel.name} successed')

        await asyncio.sleep(timer)

async def squad_channel_cleanup(timer):
    while client.is_ready:
        for guild in client.guilds:
            for channel in guild.text_channels:
                m = re.search(r"^squad-(?P<squadid>\d+)", channel.name)
                if m is not None:
                    squadid = int(m.group('squadid'))
                    if api_admin_squad(squadid):
                        # The squad does exist in DB
                        pass
                    else:
                        # The squad does not exist in DB
                        print(f'{mynow()} [{channel.name}] [BOT] ───> Found Squad channel unused')
                        # We try to delete the unused channel
                        try:
                            await channel.delete()
                        except Exception as e:
                            print(f'{mynow()} [{channel.name}] [BOT]    └──> Squad channel deletion failed')
                        else:
                            print(f'{mynow()} [{channel.name}] [BOT]    └──> Squad channel deletion successed')
                        # We try to delete the unused role
                        try:
                            role = discord.utils.get(guild.roles, name=f'Squad-{squadid}')
                            if role:
                                await role.delete()
                        except Exception as e:
                            print(f'{mynow()} [{channel.name}] [BOT]    └──> Squad role deletion failed')
                        else:
                            print(f'{mynow()} [{channel.name}] [BOT]    └──> Squad role deletion successed')
        await asyncio.sleep(timer)

async def squad_channel_create(timer):
    while client.is_ready:
        for guild in client.guilds:
            admin_role = discord.utils.get(guild.roles, name='Team')
            category   = discord.utils.get(guild.categories, name='Squads')
            squads     = api_admin_squad(None)

            # We skip the loop if no squads are returned
            if squads is None:
                continue

            for squad in squads:
                channel_name = f"Squad-{squad['id']}".lower()
                channel      = discord.utils.get(client.get_all_channels(), name=channel_name)
                if channel:
                    # Squad channel already exists
                    pass
                else:
                    # Squad channel do not exists
                    print(f'{mynow()} [{channel_name}] [BOT] ───> Squad channel to add')

                    # Check role existence
                    if discord.utils.get(guild.roles, name=f"Squad-{squad['id']}"):
                        # Role already exists, do nothing
                        print(f"{mynow()} [{channel_name}] [BOT]    └──> Squad role already exists (squadid:{squad['id']})")
                    else:
                        # Role do not exist, create it
                        try:
                            squad_role = await guild.create_role(name=f"Squad-{squad['id']}",
                                                                 mentionable=True,
                                                                 permissions=discord.Permissions.none())
                        except:
                            print(f"{mynow()} [{channel_name}] [BOT]    └──> Squad role creation failed (squadid:{squad['id']})")
                        else:
                            print(f"{mynow()} [{channel_name}] [BOT]    └──> Squad role creation successed (squadid:{squad['id']})")

                    # Create channel
                    try:
                        squad_role = discord.utils.get(guild.roles, name=f"Squad-{squad['id']}")
                        overwrites    = {
                            guild.default_role: discord.PermissionOverwrite(read_messages=False),
                            guild.me: discord.PermissionOverwrite(read_messages=True),
                            admin_role: discord.PermissionOverwrite(read_messages=True),
                            squad_role: discord.PermissionOverwrite(read_messages=True)
                        }
                        mysquadchannel = await guild.create_text_channel(f"Squad-{squad['id']}",
                                                                         category=category,
                                                                         topic=f"Squad-{squad['id']} private channel",
                                                                         overwrites=overwrites)
                    except:
                        print(f"{mynow()} [{channel_name}] [BOT]    └──> Squad channel creation failed (Squads/squadid:{squad['id']})")
                    else:
                        print(f"{mynow()} [{channel_name}] [BOT]    └──> Squad channel creation successed (Squads/Squad-{squad['id']})")
        await asyncio.sleep(timer)

async def korp_channel_cleanup(timer):
    while client.is_ready:
        for guild in client.guilds:
            for channel in guild.text_channels:
                m = re.search(r"^korp-(?P<korpid>\d+)", channel.name)
                if m is not None:
                    korpid = int(m.group('korpid'))
                    if api_admin_korp(korpid):
                        # The korp does exist in DB
                        pass
                    else:
                        # The korp does not exist in DB
                        print(f'{mynow()} [{channel.name}] [BOT] ───> Found Korp channel unused')
                        # We try to delete the unused channel
                        try:
                            await channel.delete()
                        except Exception as e:
                            print(f'{mynow()} [{channel.name}] [BOT]    └──> Korp channel deletion failed')
                        else:
                            print(f'{mynow()} [{channel.name}] [BOT]    └──> Korp channel deletion successed')
                        # We try to delete the unused role
                        try:
                            role = discord.utils.get(guild.roles, name=f'Korp-{korpid}')
                            if role:
                                await role.delete()
                        except Exception as e:
                            print(f'{mynow()} [{channel.name}] [BOT]    └──> Korp role deletion failed')
                        else:
                            print(f'{mynow()} [{channel.name}] [BOT]    └──> Korp role deletion successed')
        await asyncio.sleep(timer)

async def korp_channel_create(timer):
    while client.is_ready:
        for guild in client.guilds:
            admin_role = discord.utils.get(guild.roles, name='Team')
            category   = discord.utils.get(guild.categories, name='Korps')
            korps      = api_admin_korps()

            # We skip the loop if no squads are returned
            if korps is None:
                continue

            for korp in korps:
                channel_name = f"Korp-{korp['id']}".lower()
                channel      = discord.utils.get(client.get_all_channels(), name=channel_name)
                if channel:
                    # Squad channel already exists
                    pass
                else:
                    # Squad channel do not exists
                    print(f'{mynow()} [{channel_name}] [BOT] ───> Korp channel to add')

                    # Check role existence
                    if discord.utils.get(guild.roles, name=f"Korp-{korp['id']}"):
                        # Role already exists, do nothing
                        print(f"{mynow()} [{channel_name}] [BOT]    └──> Korp role already exists (squadid:{korp['id']})")
                    else:
                        # Role do not exist, create it
                        try:
                            korp_role = await guild.create_role(name=f"Korp-{korp['id']}",
                                                                mentionable=True,
                                                                permissions=discord.Permissions.none())
                        except:
                            print(f"{mynow()} [{channel_name}] [BOT]    └──> Korp role creation failed (korpid:{korp['id']})")
                        else:
                            print(f"{mynow()} [{channel_name}] [BOT]    └──> Korp role creation successed (korpid:{korp['id']})")

                    # Create channel
                    try:
                        squad_role = discord.utils.get(guild.roles, name=f"Korp-{korp['id']}")
                        overwrites    = {
                            guild.default_role: discord.PermissionOverwrite(read_messages=False),
                            guild.me: discord.PermissionOverwrite(read_messages=True),
                            admin_role: discord.PermissionOverwrite(read_messages=True),
                            korp_role: discord.PermissionOverwrite(read_messages=True)
                        }
                        mykorpchannel = await guild.create_text_channel(f"Korp-{korp['id']}",
                                                                        category=category,
                                                                        topic=f"Korp-{korp['id']}:<{korp['name']}>",
                                                                        overwrites=overwrites)
                    except:
                        print(f"{mynow()} [{channel_name}] [BOT]    └──> Korp channel creation failed (Korps/korpid:{korp['id']})")
                    else:
                        print(f"{mynow()} [{channel_name}] [BOT]    └──> Korp channel creation successed (Korps/Korp-{korp['id']})")
        await asyncio.sleep(timer)

# 3600s Tasks (@Hourly)
client.loop.create_task(squad_channel_cleanup(3600))
client.loop.create_task(korp_channel_cleanup(3600))
# 300s Tasks (@5Minutes)
client.loop.create_task(squad_channel_create(300))
client.loop.create_task(korp_channel_create(300))
# 60s Tasks (@1Minute)
client.loop.create_task(yqueue_check(60))
# Run Discord client
client.run(token)
