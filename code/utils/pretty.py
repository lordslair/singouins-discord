# -*- coding: utf8 -*-

def pretty_pa(payload):

    redpaduration  = 3600
    redpamax       = 16
    redmaxttl      = redpaduration * redpamax

    bluepaduration = 3600
    bluepamax      = 8
    bluemaxttl     = bluepaduration * bluepamax

    redttl    = payload['pa']['red']['ttl']
    redpa     = int(round(((redmaxttl - abs(redttl))  / redpaduration)))
    redttnpa  = redttl % redpaduration
    redbar    = redpa*'🟥' + (redpamax-redpa)*'⬜'

    bluettl   = payload['pa']['blue']['ttl']
    bluepa    = int(round(((bluemaxttl - abs(bluettl))  / bluepaduration)))
    bluettnpa = bluettl % bluepaduration
    bluebar   = bluepa*'🟦' + (bluepamax-bluepa)*'⬜'

    rettext   = f"Creature : [{payload['pc']['id']}] {payload['pc']['name']}\n"
    rettext  += f"PA blue  : {bluebar}\n"
    rettext  += f"PA red   : {redbar}\n"

    return (f'```{rettext}```')


def pretty_wallet(payload):

    rettext   = f"Creature : [{payload['pc']['id']}] {payload['pc']['name']}\n"
    rettext  += f"Currency : {payload['wallet']['currency']}\n"
    rettext  += f'Shards\n'
    rettext  += f"    🟠 Legendary : {payload['wallet']['legendary']}\n"
    rettext  += f"    🟣 Epic      : {payload['wallet']['epic']}\n"
    rettext  += f"    🔵 Rare      : {payload['wallet']['rare']}\n"
    rettext  += f"    🟢 Uncommon  : {payload['wallet']['uncommon']}\n"
    rettext  += f"    ⚪ Common    : {payload['wallet']['common']}\n"
    rettext  += f"    🟤 Broken    : {payload['wallet']['broken']}\n"
    rettext  += f'Ammos\n'
    rettext  += f"    Arrows       : {payload['wallet']['arrow']}\n"
    rettext  += f"    Bolts        : {payload['wallet']['bolt']}\n"
    rettext  += f"    Shells       : {payload['wallet']['shell']}\n"
    rettext  += f"    Cal .22      : {payload['wallet']['cal22']}\n"
    rettext  += f"    Cal .223     : {payload['wallet']['cal223']}\n"
    rettext  += f"    Cal .311     : {payload['wallet']['cal311']}\n"
    rettext  += f"    Cal .50      : {payload['wallet']['cal50']}\n"
    rettext  += f"    Cal .55      : {payload['wallet']['cal55']}\n"

    return (f'```{rettext}```')
