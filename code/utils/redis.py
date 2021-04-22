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
