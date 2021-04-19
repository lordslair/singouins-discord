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
