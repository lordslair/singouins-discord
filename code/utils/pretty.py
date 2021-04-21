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
