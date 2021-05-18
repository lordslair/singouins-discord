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

from variables          import token, API_URL
from utils.messages     import *
from utils.requests     import *
from utils.pretty       import *

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
@client.command(name='ping', help='Gives you Discord bot latency')
async def ping(ctx):
    member       = ctx.message.author
    discordname  = member.name + '#' + member.discriminator

    print(f'{mynow()} [{ctx.message.channel}][{member}] !ping')
    await ctx.send(f'Pong! {round (client.latency * 1000)}ms ')

#
# Commands for Registration/Grant
#

# !register {user.mail}
@client.command(pass_context=True,name='register', help='Register a Discord user with a Singouins user')
async def register(ctx, usermail: str = None):
    member       = ctx.message.author
    discordname  = member.name + '#' + member.discriminator

    print(f'{mynow()} [{ctx.message.channel}][{member}] !register <usermail:{usermail}>')

    if usermail is None:
        print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Sent Helper')
        await ctx.message.author.send(msg_register_helper)
        return

    # Validate user association in DB
    validation = api_admin_user_validate(discordname, usermail)
    if validation:
        # Send registered DM to user
        answer = msg_register_ok.format(ctx.message.author)
        await ctx.message.author.send(answer)
        print(f'{mynow()} [{ctx.message.channel}][{member}] └──> DB validation successed')
    else:
        # Send failure DM to user
        await ctx.message.author.send(msg_register_ko)
        print(f'{mynow()} [{ctx.message.channel}][{member}] └──> DB validation failed')

# !grant
@client.command(pass_context=True,name='grant', help='Grant a Discord user basic roles')
async def register(ctx):
    member       = ctx.message.author
    discordname  = member.name + '#' + member.discriminator

    print(f'{mynow()} [{ctx.message.channel}][{member}] !grant')

    # Delete the command message sent by the user
    try:
        await ctx.message.delete()
    except:
        print(f'{mynow()} [{ctx.message.channel}][{member}] ├──> Message deletion failed')
    else:
        print(f'{mynow()} [{ctx.message.channel}][{member}] ├──> Message deleted')

    # Check if the command is used in a channel or a DM
    if isinstance(ctx.message.channel, discord.DMChannel):
        # In DM
        print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Sent Helper')
        msg_grant_helper  = ':information_source: `!grant` Command helper\n'
        msg_grant_helper += '`!grant` : Attribute more roles (**Use in channel**)\n'
        await ctx.message.author.send(msg_grant_helper)
        return
    else:
        # In a Channel
        pass

    user = api_admin_user(discordname)
    if user:
        # Fetch the Discord role
        try:
            role = discord.utils.get(member.guild.roles, name='Singouins')
        except Exception as e:
            # Something went wrong
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> get-role:Singouins Failed')
        else:
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> get-role:Singouins Successful')
        # Check role existence
        if role in member.roles:
            # Role already exists, do nothing
            print(f'{mynow()} [{ctx.message.channel}][{member}]     └──> add-role:Singouins already exists')
        else:
            # Apply role on user
            try:
                await ctx.message.author.add_roles(role)
            except Exception as e:
                print(f'{mynow()} [{ctx.message.channel}][{member}]     └──> add-role:Singouins Failed')
                # Send failure DM to user
                await ctx.message.author.send(':warning: Failed to add your future role:Singouins')
            else:
                print(f'{mynow()} [{ctx.message.channel}][{member}]     └──> add-role:Singouins Successed')
                # Send success DM to user
                await ctx.message.author.send(':ok: You have a new role:Singouins')

        # Apply Squad roles if needed
        guild = ctx.guild
        pcs   = api_admin_mypcs(discordname)
        if pcs:
            for pc in pcs:
                # Korp management
                korpid = pc['korp']
                # We need to skip pc when he is not in a korp
                if korpid is None:
                    continue
                # Add the korp role to the user
                print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Korp detected (korpid:{korpid})')
                try:
                    role = discord.utils.get(guild.roles, name=f'Korp-{korpid}')
                except:
                    print(f'{mynow()} [{ctx.message.channel}][{member}]    └──> get-role:Korp-{korpid} Failed')
                else:
                    print(f'{mynow()} [{ctx.message.channel}][{member}]    └──> get-role:Korp-{korpid} Successed')
                    if role in member.roles:
                        print(f'{mynow()} [{ctx.message.channel}][{member}]        └──> add-role:Korp-{korpid} already exists')
                    else:
                        try:
                            await ctx.author.add_roles(role)
                        except:
                            print(f'{mynow()} [{ctx.message.channel}][{member}]        └──> add-role:Korp-{korpid} Failed')
                        else:
                            print(f'{mynow()} [{ctx.message.channel}][{member}]        └──> add-role:Korp-{korpid} Successed')

                # Squad management
                squadid = pc['squad']
                # We need to skip pc when he is not in a squad
                if squadid is None:
                    continue
                # Add the squad role to the user
                print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Squad detected (squadid:{squadid})')
                try:
                    role = discord.utils.get(guild.roles, name=f'Squad-{squadid}')
                except:
                    print(f'{mynow()} [{ctx.message.channel}][{member}]    └──> get-role:Squad-{squadid} Failed')
                else:
                    print(f'{mynow()} [{ctx.message.channel}][{member}]    └──> get-role:Squad-{squadid} Successed')
                    if role in member.roles:
                        print(f'{mynow()} [{ctx.message.channel}][{member}]        └──> add-role:Squad-{squadid} already exists')
                    else:
                        try:
                            await ctx.author.add_roles(role)
                        except:
                            print(f'{mynow()} [{ctx.message.channel}][{member}]        └──> add-role:Squad-{squadid} Failed')
                        else:
                            print(f'{mynow()} [{ctx.message.channel}][{member}]        └──> add-role:Squad-{squadid} Successed')
    else:
        # Send failure DM to user
        await ctx.message.author.send(':warning: You need to be registered to use `!grant`')
        print(f'{mynow()} [{ctx.message.channel}][{member}] └──> User not found/registered')

#
# Commands for Admins
#
@client.command(pass_context=True,name='admin', help='Admin master-command [RESTRICTED]')
async def admin(ctx,*args):
    member       = ctx.message.author
    discordname  = member.name + '#' + member.discriminator
    adminrole    = discord.utils.get(member.guild.roles, name='Team')

    if adminrole not in ctx.author.roles:
        # This command is to be used only by Admin role
        print(f'{mynow()} [{ctx.message.channel}][{member}] !admin <{args}> [Unauthorized user]')

    # Channel and User are OK
    print(f'{mynow()} [{ctx.message.channel}][{member}] !admin <{args}>')

    if len(args) == 0:
        print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Args failure')
        await ctx.send('`!admin needs arguments`')
        return

    # PA commands
    if args[0] == 'pa':
        # We need exactly 4 args : !admin {pa} {action} {select} {pcid}
        if len(args) < 4:
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Args failure')
            await ctx.send('`!admin <pa> needs more arguments`')
            return

        action = args[1]
        select = args[2]
        pcid   = int(args[3])

        pc = api_admin_mypc('Wukong',pcid)
        if pc is None:
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Unknown creature')
            await ctx.send(f'`Unknown creature pcid:{pcid}`')
            return

        if action == 'reset':
            if select == 'all':
                api_admin_mypc_pa(discordname,pcid,16,8)
                await ctx.send(f'`Reset PA {select} done for pcid:{pc.id}`')
            elif select == 'red':
                api_admin_mypc_pa(discordname,pcid,16,None)
                await ctx.send(f'`Reset PA {select} done for pcid:{pc.id}`')
            elif select == 'blue':
                api_admin_mypc_pa(discordname,pcid,None,8)
                await ctx.send(f'`Reset PA {select} done for pcid:{pc.id}`')
        elif action == 'get':
            if select == 'all':
                payload = api_admin_mypc_pa(discordname,pcid,None,None)
                await ctx.send(pretty_pa(payload))
        elif action == 'help':
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Sent Helper')
            await ctx.send('`!admin pa {reset|get} {all|blue|red} {pcid}`')
    # Wallet commands
    elif args[0] == 'wallet':
        # We need exactly 4 args : !admin {wallet} {get} {all} {pcid}
        if len(args) < 4:
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Args failure')
            await ctx.send(f'`!admin <wallet> needs more arguments`')
            return

        action = args[1]
        select = args[2]
        pcid   = int(args[3])

        if action == 'get':
            if select == 'all':
                wallet = api_admin_mypc_wallet('Wukong',pcid)
                if wallet:
                    await ctx.send(pretty_wallet(payload))
        elif action == 'help':
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Sent Helper')
            await ctx.send('`!admin <wallet> {get} {all} {pcid}`')
    # Discord Commands
    elif args[0] == 'discord':
        # We need exactly 4 args : !admin {wallet} {get} {all} {pcid}
        if len(args) < 3:
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Args failure')
            await ctx.send(f'`!admin <discord> needs more arguments`')
            return

        action = args[1]

        try:
            amount = int(args[2])
        except:
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Amount:{args[2]} is not an integer')
            await ctx.send('`Amount given was not an integer`')
            return
        else:
            pass

        if action == 'delete':
            print(f'{mynow()} [{ctx.message.channel}][{member}] ├──> Messages deletion ({amount}) received')

            try:
                await ctx.channel.purge(limit=amount)
            except:
                print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Messages deletion ({amount}) failed')
            else:
                print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Messages deletion ({amount}) Successful')
        elif action == 'help':
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Sent Helper')
            await ctx.send('`!admin discord {delete} {integer}`')

#
# Commands for Singouins
#
# DM Only Commands
@client.command(pass_context=True,name='mysingouins', help='Display your Singouins')
async def mysingouins(ctx):
    member       = ctx.message.author
    discordname  = member.name + '#' + member.discriminator

    print(f'{mynow()} [{ctx.message.channel}][{member}] !mysingouins')

    # Check if the command is used in a channel or a DM
    if isinstance(ctx.message.channel, discord.DMChannel):
        # In DM
        pass
    else:
        # In a Channel
        # Delete the command message sent by the user
        try:
            await ctx.message.delete()
        except:
            pass
        else:
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Message deleted')
        return

    emojiM = discord.utils.get(client.emojis, name='statM')
    emojiR = discord.utils.get(client.emojis, name='statR')
    emojiV = discord.utils.get(client.emojis, name='statV')
    emojiG = discord.utils.get(client.emojis, name='statG')
    emojiP = discord.utils.get(client.emojis, name='statP')
    emojiB = discord.utils.get(client.emojis, name='statB')

    emojiRaceC = discord.utils.get(client.emojis, name='raceC')
    emojiRaceG = discord.utils.get(client.emojis, name='raceG')
    emojiRaceM = discord.utils.get(client.emojis, name='raceM')
    emojiRaceO = discord.utils.get(client.emojis, name='raceO')
    emojiRace = [emojiRaceC,
                 emojiRaceG,
                 emojiRaceM,
                 emojiRaceO]

    pcs = api_admin_mypcs(discordname)
    if pcs is None:
        await ctx.send(f'`No Singouin found in DB`')
        print(f'{mynow()} [{ctx.message.channel}][{member}] └──> No Singouin found in DB')
        return

    mydesc = ''
    for pc in pcs:
        emojiMyRace = emojiRace[pc['race'] - 1]
        mydesc += f"{emojiMyRace} [{pc['id']}] {pc['name']}\n"

    embed = discord.Embed(
        title = 'Mes Singouins:',
        description = mydesc,
        colour = discord.Colour.blue()
    )

    await ctx.send(embed=embed)

@client.command(pass_context=True,name='mysingouin', help='Display a Singouin infos')
async def mysingouin(ctx, action: str = None, pcid: int = None):
    member       = ctx.message.author
    discordname  = member.name + '#' + member.discriminator

    print(f'{mynow()} [{ctx.message.channel}][{member}] !mysingouin <{action}> <{pcid}>')

    if pcid is None or action is None:
        print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Sent Helper')
        await member.send(msg_mysingouin_helper)
        return

    # Check if the command is used in a channel or a DM
    if isinstance(ctx.message.channel, discord.DMChannel):
        # In DM
        pass
    else:
        # In a Channel
        # Delete the command message sent by the user
        try:
            await ctx.message.delete()
        except:
            pass
        else:
            print(f'{mynow()} [{ctx.message.channel}][{member}] ├──> Message deleted')

    if action == 'pa':
        pc = api_admin_mypc(discordname,pcid)
        if pc is None:
            await ctx.send(f'`Singouin not yours/not found in DB (pcid:{pcid})`')
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Singouin profile query failed')
            return
        else:
            print(f'{mynow()} [{ctx.message.channel}][{member}] ├──> Singouin profile query successed')

        payload = api_admin_mypc_pa(discordname,pcid,None,None)
        if payload is None:
            await ctx.send(f'`Singouin PA not found in DB (pcid:{pcid})`')
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Singouin PA query failed')
            return
        else:
            print(f'{mynow()} [{ctx.message.channel}][{member}] ├──> Singouin PA query successed')
            if isinstance(ctx.message.channel, discord.DMChannel):
                # If the member is in DM -> we send
                await member.send(pretty_pa(payload))
                print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Singouin PA sent')
            elif ctx.message.channel.name == f"Squad-{pc['squad']}".lower():
                # If the member is in his squad channel -> we send
                await ctx.send(pretty_pa(payload))
                print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Singouin PA sent')
            else:
                # We do nothing
                pass
    elif action == 'profile':
        pc = api_admin_mypc(discordname,pcid)
        if pc is None:
            await ctx.send(f'`Singouin not yours/not found in DB (pcid:{pcid})`')
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Singouin profile query failed')
            return
        else:
            print(f'{mynow()} [{ctx.message.channel}][{member}] ├──> Singouin profile query successed')

        embed = discord.Embed(
            title = f"[{pc['id']}] {pc['name']}\n",
            #description = 'Profil:',
            colour = discord.Colour.blue()
        )

        emojiM = discord.utils.get(client.emojis, name='statM')
        emojiR = discord.utils.get(client.emojis, name='statR')
        emojiV = discord.utils.get(client.emojis, name='statV')
        emojiG = discord.utils.get(client.emojis, name='statG')
        emojiP = discord.utils.get(client.emojis, name='statP')
        emojiB = discord.utils.get(client.emojis, name='statB')

        msg_stats = 'Stats:'
        msg_nbr   = 'Nbr:'
        embed.add_field(name=f'`{msg_stats: >9}`      {emojiM}      {emojiR}      {emojiV}      {emojiG}      {emojiP}      {emojiB}',
                        value=f"`{msg_nbr: >9}` `{pc['m']: >4}` `{pc['r']: >4}` `{pc['v']: >4}` `{pc['g']: >4}` `{pc['p']: >4}` `{pc['b']: >4}`",
                        inline = False)

        if isinstance(ctx.message.channel, discord.DMChannel):
            # If the member is in DM -> we send
            await member.send(embed=embed)
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Singouin ammo sent')
        elif ctx.message.channel.name == f"Squad-{pc['squad']}".lower():
            # If the member is in his squad channel -> we send
            await ctx.send(embed=embed)
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Singouin ammo sent')
        else:
            # We do nothing
            pass
    elif action == 'wallet':
        pc = api_admin_mypc(discordname,pcid)
        if pc is None:
            await ctx.send(f'`Singouin not yours/not found in DB (pcid:{pcid})`')
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Singouin profile query failed')
            return
        else:
            print(f'{mynow()} [{ctx.message.channel}][{member}] ├──> Singouin profile query successed')

        stuff = api_admin_mypc_wallet(discordname,pcid)
        if stuff is None:
            await ctx.send(f'`Singouin wallet not found in DB (pcid:{pcid})`')
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Singouin wallet query failed')
            return
        else:
            print(f'{mynow()} [{ctx.message.channel}][{member}] ├──> Singouin wallet query successed')

        embed = discord.Embed(
            title = f"[{pc['id']}] {pc['name']}\n",
            #description = 'Profil:',
            colour = discord.Colour.blue()
        )

        emojiShardL = discord.utils.get(client.emojis, name='shardL')
        emojiShardE = discord.utils.get(client.emojis, name='shardE')
        emojiShardR = discord.utils.get(client.emojis, name='shardR')
        emojiShardU = discord.utils.get(client.emojis, name='shardU')
        emojiShardC = discord.utils.get(client.emojis, name='shardC')
        emojiShardB = discord.utils.get(client.emojis, name='shardB')

        msg_shards = 'Shards:'
        msg_nbr    = 'Nbr:'
        name       = f'`{msg_shards: >9}`      '
        name      += f'{emojiShardL}      '
        name      += f'{emojiShardE}      '
        name      += f'{emojiShardR}      '
        name      += f'{emojiShardU}      '
        name      += f'{emojiShardC}      '
        name      += f'{emojiShardB}'
        value      = f'`{msg_nbr: >9}` '
        value     += f"`{stuff['wallet']['legendary']: >4}` "
        value     += f"`{stuff['wallet']['epic']: >4}` "
        value     += f"`{stuff['wallet']['rare']: >4}` "
        value     += f"`{stuff['wallet']['uncommon']: >4}` "
        value     += f"`{stuff['wallet']['common']: >4}` "
        value     += f"`{stuff['wallet']['broken']: >4}`"
        embed.add_field(name   = name,
                        value  = value,
                        inline = False)

        if isinstance(ctx.message.channel, discord.DMChannel):
            # If the member is in DM -> we send
            await member.send(embed=embed)
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Singouin ammo sent')
        elif ctx.message.channel.name == f"Squad-{pc['squad']}".lower():
            # If the member is in his squad channel -> we send
            await ctx.send(embed=embed)
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Singouin ammo sent')
        else:
            # We do nothing
            pass
    elif action == 'ammo':
        pc = api_admin_mypc(discordname,pcid)
        if pc is None:
            await ctx.send(f'`Singouin not yours/not found in DB (pcid:{pcid})`')
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Singouin profile query failed')
            return
        else:
            print(f'{mynow()} [{ctx.message.channel}][{member}] ├──> Singouin profile query successed')

        stuff = api_admin_mypc_wallet(discordname,pcid)
        if stuff is None:
            await ctx.send(f'`Singouin ammo not found in DB (pcid:{pcid})`')
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Singouin ammo query failed')
            return
        else:
            print(f'{mynow()} [{ctx.message.channel}][{member}] ├──> Singouin ammo query successed')

        embed = discord.Embed(
            title = f"[{pc['id']}] {pc['name']}\n",
            #description = 'Profil:',
            colour = discord.Colour.blue()
        )

        emojiAmmo22  = discord.utils.get(client.emojis, name='ammo22')
        emojiAmmo223 = discord.utils.get(client.emojis, name='ammo223')
        emojiAmmo311 = discord.utils.get(client.emojis, name='ammo311')
        emojiAmmo50  = discord.utils.get(client.emojis, name='ammo50')
        emojiAmmo55  = discord.utils.get(client.emojis, name='ammo55')
        emojiAmmoS   = discord.utils.get(client.emojis, name='ammoShell')

        msg_shards = 'Ammo:'
        msg_nbr    = 'Nbr:'
        name       = f'`{msg_shards: >9}`      '
        name      += f'{emojiAmmo22}      '
        name      += f'{emojiAmmo223}      '
        name      += f'{emojiAmmo311}      '
        name      += f'{emojiAmmo50}      '
        name      += f'{emojiAmmo55}      '
        name      += f'{emojiAmmoS}'
        value      = f'`{msg_nbr: >9}` '
        value     += f"`{stuff['wallet']['cal22']: >4}` "
        value     += f"`{stuff['wallet']['cal223']: >4}` "
        value     += f"`{stuff['wallet']['cal311']: >4}` "
        value     += f"`{stuff['wallet']['cal50']: >4}` "
        value     += f"`{stuff['wallet']['cal55']: >4}` "
        value     += f"`{stuff['wallet']['shell']: >4}`"
        embed.add_field(name   = name,
                        value  = value,
                        inline = False)

        emojiAmmoA   = discord.utils.get(client.emojis, name='ammoArrow')
        emojiAmmoB   = discord.utils.get(client.emojis, name='ammoBolt')
        emojiAmmoF   = discord.utils.get(client.emojis, name='ammoFuel')
        emojiAmmoG   = discord.utils.get(client.emojis, name='ammoGrenade')
        emojiAmmoR   = discord.utils.get(client.emojis, name='ammoRocket')

        emojiMoneyB  = discord.utils.get(client.emojis, name='moneyB')

        # Temporary
        stuff['wallet']['fuel']    = 0
        stuff['wallet']['grenade'] = 0
        stuff['wallet']['rocket']  = 0

        msg_shards = 'Specials:'
        msg_nbr    = 'Nbr:'
        name       = f'`{msg_shards: >9}`      '
        name      += f'{emojiAmmoA}      '
        name      += f'{emojiAmmoB}      '
        name      += f'{emojiAmmoF}      '
        name      += f'{emojiAmmoG}      '
        name      += f'{emojiAmmoR}      '
        name      += f'{emojiMoneyB}'
        value      = f'`{msg_nbr: >9}` '
        value     += f"`{stuff['wallet']['arrow']: >4}` "
        value     += f"`{stuff['wallet']['bolt']: >4}` "
        value     += f"`{stuff['wallet']['fuel']: >4}` "
        value     += f"`{stuff['wallet']['grenade']: >4}` "
        value     += f"`{stuff['wallet']['rocket']: >4}` "
        value     += f"`{stuff['wallet']['currency']: >4}`"
        embed.add_field(name   = name,
                        value  = value,
                        inline = False)

        if isinstance(ctx.message.channel, discord.DMChannel):
            # If the member is in DM -> we send
            await member.send(embed=embed)
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Singouin ammo sent')
        elif ctx.message.channel.name == f"Squad-{pc['squad']}".lower():
            # If the member is in his squad channel -> we send
            await ctx.send(embed=embed)
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Singouin ammo sent')
        else:
            # We do nothing
            pass

@client.event
async def on_member_join(member):
    await member.send(msg_welcome)

# Run Discord client
client.run(token)
