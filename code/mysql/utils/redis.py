# -*- coding: utf8 -*-

import json
import redis
import yarqueue

from datetime  import datetime

from variables import (REDIS_PORT,
                       REDIS_HOST,
                       REDIS_DB_NAME)

r = redis.StrictRedis(host     = REDIS_HOST,
                      port     = REDIS_PORT,
                      db       = REDIS_DB_NAME,
                      encoding = 'utf-8')

redpaduration  = 3600
redpamax       = 16
redmaxttl      = redpaduration * redpamax

bluepaduration = 3600
bluepamax      = 8
bluemaxttl     = bluepaduration * bluepamax

#
# Queries: PA
#

def get_pa(pc):

    redkey    = f'red:{pc.id}'
    redttl    = r.ttl(redkey)
    redpa     = int(round(((redmaxttl - abs(redttl))  / redpaduration)))
    redttnpa  = r.ttl(redkey) % redpaduration
    redbar    = redpa*'🟥' + (redpamax-redpa)*'⬜'

    bluekey   = f'blue:{pc.id}'
    bluettl   = r.ttl(bluekey)
    bluepa    = int(round(((bluemaxttl - abs(bluettl))  / bluepaduration)))
    bluettnpa = r.ttl(bluekey) % bluepaduration
    bluebar   = bluepa*'🟦' + (bluepamax-bluepa)*'⬜'

    rettext   = f'Creature : [{pc.id}] {pc.name}\n'
    rettext  += f'PA blue  : {bluebar}\n'
    rettext  += f'PA red   : {redbar}\n'
    return (f'```{rettext}```')

def reset_pa(pc,blue,red):

    if red:
        r.set(f'red:{pc.id}','red',ex=1)
    if blue:
        r.set(f'blue:{pc.id}','blue',ex=1)

#
# Queries: Queues
#

def yqueue_get(yqueue_name):
    # Opening Queue
    try:
        yqueue = yarqueue.Queue(name=yqueue_name, redis=r)
    except:
        print(f'Connection to yarqueue:{yqueue_name} [KO]')
    else:
        pass

    # Get data from Queue
    try:
        msgs = []
        for msg in yqueue:
            msgs.append(json.loads(msg))
    except:
        print(f'Failed to get messages from yarqueue:{yqueue_name} [KO]')
    else:
        return msgs
