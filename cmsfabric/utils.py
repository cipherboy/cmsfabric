import random
from os.path import expanduser

def u_ri():
    return str(random.randint(100000000, 999999999))

def u_p(parts):
    return '/'.join(parts)

def u_c():
    return expanduser("~") + "/.cmsfabric.conf"
