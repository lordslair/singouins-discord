#!/usr/bin/env python3
# -*- coding: utf8 -*-

from datetime           import datetime,timedelta

# Shorted definition for actual now() with proper format
def mynow(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Log System imports
print(f'{mynow()} [BOT] System   imports [✓]')

import asyncio
import discord
import inspect

from discord.ext        import commands

# Log Discord imports
print(f'{mynow()} [BOT] Discord  imports [✓]')

from mysql.methods      import *
from mysql.utils        import redis
from variables          import token
from utils.messages     import *
from utils.histograms   import draw

from mysql.methods.fn_creature import fn_creature_get
from mysql.methods.fn_user     import fn_user_get_from_member

# Log Internal imports
print(f'{mynow()} [BOT] Internal imports [✓]')

client = commands.Bot(command_prefix = '!')

# Welcome message in the logs on daemon start
print(f'{mynow()} [BOT] Daemon started   [✓]')
# Pre-flight check for SQL connection
if query_up(): tick = '✓'
else         : tick = '✗'
print(f'{mynow()} [BOT] SQL connection   [{tick}]')

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
    user = query_user_validate(usermail,discordname)
    if user:
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
        await ctx.message.author.send(msg_grant_helper)
        return
    else:
        # In a Channel
        pass

    user = fn_user_get_from_member(member)
    if user:
        # Fetch the Discord role
        try:
            role = discord.utils.get(member.guild.roles, name='Singouins')
        except Exception as e:
            # Something went wrong
            print(f'{mynow()} [{ctx.message.channel}][{member}] ├──> Member get-role Failed')
        else:
            print(f'{mynow()} [{ctx.message.channel}][{member}] ├──> Member get-role Successful')

        # Check role existence
        if role in member.roles:
            # Role already exists, do nothing
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Member role already exists')
            return

        # Apply role on user
        try:
            await ctx.message.author.add_roles(role)
        except Exception as e:
            # Something went wrong during commit
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Member add-role Failed')
            # Send failure DM to user
            await ctx.message.author.send(msg_grant_ko)
        else:
            # Send success DM to user
            await ctx.message.author.send(msg_grant_ok)
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Member add-role Successful')
    else:
        # Send failure DM to user
        await ctx.message.author.send(msg_grant_ko)
        print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Query in DB Failed')

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
        print('{} [{}][{}] !admin <{}> [{}]'.format(mynow(),ctx.message.channel,member,args,'Unauthorized user'))

    # Channel and User are OK
    print('{} [{}][{}] !admin <{}>'.format(mynow(),ctx.message.channel,member,args))

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

        pc = fn_creature_get(None,pcid)[3]
        if pc is None:
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Unknown creature')
            await ctx.send(f'`Unknown creature pcid:{pcid}`')
            return

        if action == 'reset':
            if select == 'all':
                redis.reset_pa(pc,True,True)
                await ctx.send(f'`Reset PA {select} done for pcid:{pc.id}`')
            elif select == 'red':
                redis.reset_pa(pc,False,True)
                await ctx.send(f'`Reset PA {select} done for pcid:{pc.id}`')
            elif select == 'blue':
                redis.reset_pa(pc,True,False)
                await ctx.send(f'`Reset PA {select} done for pcid:{pc.id}`')
        elif action == 'get':
            if select == 'all':
                pa = redis.get_pa(pc)
                await ctx.send(pa)
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

        pc = fn_creature_get(None,pcid)[3]
        if pc is None:
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Unknown creature')
            await ctx.send(f'`Unknown creature pcid:{pcid}`')
            return

        if action == 'get':
            if select == 'all':
                wallet = query_wallet_get(pc)
                if wallet:
                    await ctx.send(wallet)
        elif action == 'help':
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Sent Helper')
            await ctx.send('`!admin <wallet> {get} {all} {pcid}`')
    # Histogram commands
    elif args[0] == 'histogram':
        # We need exactly 2 args : !admin {histogram} {CL|CR}
        if len(args) < 2:
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Args failure')
            await ctx.send('`!admin <histogram> needs more arguments`')
            return

        htype  = args[1]

        if htype == 'help':
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Sent Helper')
            await ctx.send('`!admin histogram {CL|CR}`')

        try:
            array  = query_histo(htype)
            answer = draw(array)
        except:
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Histogram creation failed')
        else:
            print(f'{mynow()} [{ctx.message.channel}][{member}] ├──> Histogram creation Successful')
            if answer:
                await ctx.send(answer)
                print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Histogram sent')
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

    print('{} [{}][{}] !mysingouins'.format(mynow(),ctx.message.channel,member))

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
            print('{} [{}][{}] └> Message deleted'.format(mynow(),ctx.message.channel,member))
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

    pcs = query_pcs_get(member)[3]
    if pcs is None:
        await ctx.send(f'`No Singouin found in DB`')

    mydesc = ''
    for pc in pcs:
        emojiMyRace = emojiRace[pc.race - 1]
        mydesc += f'{emojiMyRace} [{pc.id}] {pc.name}\n'

    embed = discord.Embed(
        title = 'Mes Singouins:',
        description = mydesc,
        colour = discord.Colour.blue()
    )

    await ctx.send(embed=embed)

@client.command(pass_context=True,name='mysingouin', help='Display a Singouin profile')
async def mysingouin(ctx, pcid: int = None):
    member       = ctx.message.author

    print('{} [{}][{}] !mysingouin <{}>'.format(mynow(),ctx.message.channel,member,pcid))

    if pcid is None:
        print('{} [{}][{}] └> Sent Helper'.format(mynow(),ctx.message.channel,member))
        await ctx.message.author.send(msg_mysingouin_helper)
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
            print('{} [{}][{}] └> Message deleted'.format(mynow(),ctx.message.channel,member))
        return

    pc = query_pc_get(pcid,member)[3]
    if pc is None:
        await ctx.send(f'`Singouin not yours/not found in DB (pcid:{pcid})`')
        return

    stuff = query_mypc_items_get(pcid,member)[3]
    if stuff is None:
        await ctx.send(f'`Singouin Stuff not found in DB (pcid:{pcid})`')
        return

    embed = discord.Embed(
        title = f'[{pc.id}] {pc.name}\n',
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
                    value=f'`{msg_nbr: >9}` `{pc.m: >4}` `{pc.r: >4}` `{pc.v: >4}` `{pc.g: >4}` `{pc.p: >4}` `{pc.b: >4}`',
                    inline = False)

    emojiShardL = discord.utils.get(client.emojis, name='shardL')
    emojiShardE = discord.utils.get(client.emojis, name='shardE')
    emojiShardR = discord.utils.get(client.emojis, name='shardR')
    emojiShardU = discord.utils.get(client.emojis, name='shardU')
    emojiShardC = discord.utils.get(client.emojis, name='shardC')
    emojiShardB = discord.utils.get(client.emojis, name='shardB')

    wallet     = stuff['wallet'][0]
    msg_shards = 'Shards:'
    msg_nbr    = 'Nbr:'
    embed.add_field(name=f'`{msg_shards: >9}`      {emojiShardL}      {emojiShardE}      {emojiShardR}      {emojiShardU}      {emojiShardC}      {emojiShardB}',
                    value=f'`{msg_nbr: >9}` `{wallet.legendary: >4}` `{wallet.epic: >4}` `{wallet.rare: >4}` `{wallet.uncommon: >4}` `{wallet.common: >4}` `{wallet.broken: >4}`',
                    inline = False)

    emojiAmmo22  = discord.utils.get(client.emojis, name='ammo22')
    emojiAmmo223 = discord.utils.get(client.emojis, name='ammo223')
    emojiAmmo311 = discord.utils.get(client.emojis, name='ammo311')
    emojiAmmo50  = discord.utils.get(client.emojis, name='ammo50')
    emojiAmmo55  = discord.utils.get(client.emojis, name='ammo55')
    emojiAmmoS   = discord.utils.get(client.emojis, name='ammoShell')

    msg_shards = 'Ammo:'
    msg_nbr    = 'Nbr:'
    embed.add_field(name=f'`{msg_shards: >9}`      {emojiAmmo22}      {emojiAmmo223}      {emojiAmmo311}      {emojiAmmo50}      {emojiAmmo55}      {emojiAmmoS}',
                    value=f'`{msg_nbr: >9}` `{wallet.cal22: >4}` `{wallet.cal223: >4}` `{wallet.cal311: >4}` `{wallet.cal50: >4}` `{wallet.cal55: >4}` `{wallet.shell: >4}`',
                    inline = False)

    emojiAmmoA   = discord.utils.get(client.emojis, name='ammoArrow')
    emojiAmmoB   = discord.utils.get(client.emojis, name='ammoBolt')
    emojiAmmoF   = discord.utils.get(client.emojis, name='ammoFuel')
    emojiAmmoG   = discord.utils.get(client.emojis, name='ammoGrenade')
    emojiAmmoR   = discord.utils.get(client.emojis, name='ammoRocket')

    emojiMoneyB  = discord.utils.get(client.emojis, name='moneyB')

    # Temporary
    wallet.fuel     = 0
    wallet.grenade  = 0
    wallet.rocket   = 0

    msg_shards = 'Specials:'
    msg_nbr    = 'Nbr:'
    embed.add_field(name=f'`{msg_shards: >9}`      {emojiAmmoA}      {emojiAmmoB}      {emojiAmmoF}      {emojiAmmoG}      {emojiAmmoR}      {emojiMoneyB}',
                    value=f'`{msg_nbr: >9}` `{wallet.arrow: >4}` `{wallet.bolt: >4}` `{wallet.fuel: >4}` `{wallet.grenade: >4}` `{wallet.rocket: >4}` `{wallet.currency: >4}`',
                    inline = False)

    await ctx.send(embed=embed)

# Channel only Commands
@client.command(pass_context=True,name='mysquads', help='Singouin Squad actions')
async def mysingouin(ctx, action: str = None):
    member       = ctx.message.author

    print(f'{mynow()} [{ctx.message.channel}][{member}] !mysquad <{action}>')

    # Delete the command message sent by the user
    try:
        await ctx.message.delete()
    except:
        print(f'{mynow()} [{ctx.message.channel}][{member}] ├──> Message deletion failed')
    else:
        print(f'{mynow()} [{ctx.message.channel}][{member}] ├──> Message deleted')

    if action is None:
        print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Sent Helper (action:{action})')
        await ctx.message.author.send(msg_mysquad_helper)
        return

    # Check if the command is used in a channel or a DM
    if isinstance(ctx.message.channel, discord.DMChannel):
        # In DM
        print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Sent Helper (Wrong channel)')
        await ctx.message.author.send(msg_mysquad_helper_dm)
        return
    else:
        # In a Channel
        pass

    if action == 'help':
        print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Sent Helper (action:{action})')
        await ctx.message.author.send(msg_mysquad_helper)
    if action == 'init':
        guild         = ctx.guild
        admin_role    = discord.utils.get(guild.roles, name='Team')
        category      = discord.utils.get(guild.categories, name='Squads')
        squads        = query_squads_get(member)
        overwrites    = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            admin_role: discord.PermissionOverwrite(read_messages=True)
        }

        if squads[3] is not None:
            print(f'{mynow()} [{ctx.message.channel}][{member}] ├──> Received Squads infos ({squads[3]})')
        else:
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Received no Squads infos ({squads[3]})')
            return

        squadlist = squads[3]['leader'] + squads[3]['member']
        squadset  = set(squadlist)

        for squadid in squadset:
            print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Squad detected (squadid:{squadid})')

            # Check channel existance
            if discord.utils.get(category.channels, name=f'Squad-{squadid}'.lower()):
                # Channel already exists, do nothing
                print(f'{mynow()} [{ctx.message.channel}][{member}]    ├──> Squad channel already exists (Squads/Squad-{squadid})')
            else:
                # Channel do not exist, create it
                try:
                    mysquadchannel = await guild.create_text_channel(f'Squad-{squadid}',
                                                                     category=category,
                                                                     topic=f'Squad-{squadid} private channel',
                                                                     overwrites=overwrites)
                except:
                    print(f'{mynow()} [{ctx.message.channel}][{member}]    ├──> Squad channel creation failed (squadid:{squadid})')
                else:
                    print(f'{mynow()} [{ctx.message.channel}][{member}]    ├──> Squad channel created (Squads/Squad-{squadid})')

            # Check role existence
            if discord.utils.get(guild.roles, name=f'Squad-{squadid}'):
                # Role already exists, do nothing
                print(f'{mynow()} [{ctx.message.channel}][{member}]    └──> Squad role already exists (squadid:{squadid})')
            else:
                # Role do not exist, create it
                try:
                    role = await guild.create_role(name=f'Squad-{squadid}',
                                                   mentionable=True,
                                                   permissions=discord.Permissions.none())
                except:
                    print(f'{mynow()} [{ctx.message.channel}][{member}]    └──> Squad role creation failed (squadid:{squadid})')
                else:
                    print(f'{mynow()} [{ctx.message.channel}][{member}]    └──> Squad role creation successed (squadid:{squadid})')

    elif action == 'grant':
        guild      = ctx.guild
        squads = query_squads_get(member)
        if squads[3] is not None:
            print(f'{mynow()} [{ctx.message.channel}][{member}] ├──> Received Squads infos ({squads[3]})')

            squadlist = squads[3]['leader'] + squads[3]['member']
            squadset  = set(squadlist)

            for squadid in squadset:
                print(f'{mynow()} [{ctx.message.channel}][{member}] └──> Squad detected (squadid:{squadid})')

                # Add the squad role to the user
                try:
                    squadrole = discord.utils.get(guild.roles, name=f'Squad-{squadid}')
                except:
                    print(f'{mynow()} [{ctx.message.channel}][{member}]    └──> Squad role not found (squadid:{squadid})')
                else:
                    if squadrole in member.roles:
                        print(f'{mynow()} [{ctx.message.channel}][{member}]    └──> Squad add-role already done (squadid:{squadid})')
                        return

                    try:
                        await ctx.author.add_roles(squadrole)
                    except:
                        print(f'{mynow()} [{ctx.message.channel}][{member}]    └──> Squad add-role failed (squadid:{squadid})')
                    else:
                        print(f'{mynow()} [{ctx.message.channel}][{member}]    └──> Squad add-role successed (squadid:{squadid})')

@client.event
async def on_member_join(member):
    await member.send(msg_welcome)

#
# Tasks definition
#

async def yqueue_check_60s():
    while client.is_ready:
        # Opening Queue
        try:
            yqueue_name = 'discord'
            msgs        = redis.yqueue_get(yqueue_name)
        except Exception as e:
            print(f'{mynow()} [BOT] Unable to retrieve data from yarqueue:{yqueue_name}')
        else:
            for msg in msgs:
                channel = discord.utils.get(client.get_all_channels(), name=msg['scope'].lower())
                if channel:
                    try:
                        await channel.send(msg['payload'])
                    except:
                        print(f'{mynow()} [{channel.name}][BOT] ───> Message from yarqueue:{yqueue_name}')
                    else:
                        print(f'{mynow()} [{channel.name}][BOT] ───> Message from yarqueue:{yqueue_name}')

        await asyncio.sleep(60) # task runs every 60 seconds / 1 minute

client.loop.create_task(yqueue_check_60s())
client.run(token)
