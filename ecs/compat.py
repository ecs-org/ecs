from uuid import uuid4

def gen_uuid():
    return uuid4().get_hex()
