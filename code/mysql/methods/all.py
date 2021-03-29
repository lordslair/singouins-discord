# -*- coding: utf8 -*-

from ..session          import Session
from ..models           import User,Creature

def query_up():
    session = Session()

    try:
        result = session.query(User).first()
    except Exception as e:
        print(e)
    else:
        if result: return result
    finally:
        session.close()

def query_histo(arg):
    session = Session()

    try:
        if   arg == 'CreaturesLevel' or arg == 'CL':
            result = session.query(Creature.level).all()
        elif arg == 'CreaturesRace'  or arg == 'CR':
            result = session.query(Creature.race).all()
        else:
            result = None
    except Exception as e:
        print(e)
    else:
        if result: return result
    finally:
        session.close()
