from decouple import config

environment = config('ENVIRONMENT', cast=str)

match environment:
    case 'local':
        try:
            from .local import *
        except ImportError:
            pass
    case 'prod':
        try:
            from .prod import *
        except ImportError:
            pass
