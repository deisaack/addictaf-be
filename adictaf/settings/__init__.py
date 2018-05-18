from decouple import config

DEBUG=config('DEBUG', False,  cast=bool)

if DEBUG:
    from . development import *
else:
    from . production import *
