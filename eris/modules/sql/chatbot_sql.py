import threading

from sqlalchemy import Column, String

from eris.modules.sql import BASE, SESSION


class erischats(BASE):
    __tablename__ = "eris_chats"
    chat_id = Column(String(14), primary_key=True)

    def __init__(self, chat_id):
        self.chat_id = chat_id


erischats.__table__.create(checkfirst=True)
INSERTION_LOCK = threading.RLock()


def is_eris(chat_id):
    try:
        chat = SESSION.query(erischats).get(str(chat_id))
        return bool(chat)
    finally:
        SESSION.close()


def set_eris(chat_id):
    with INSERTION_LOCK:
        erischat = SESSION.query(erischats).get(str(chat_id))
        if not erischat:
            erischat = erischats(str(chat_id))
        SESSION.add(erischat)
        SESSION.commit()


def rem_eris(chat_id):
    with INSERTION_LOCK:
        erischat = SESSION.query(erischats).get(str(chat_id))
        if erischat:
            SESSION.delete(erischat)
        SESSION.commit()