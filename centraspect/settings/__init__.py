from .base import *
import os


if os.environ.get("ENV_NAME") == 'Production':
    from .production import *
elif os.environ.get("ENV_NAME") == 'Staging':
    from .staging import *
elif os.environ.get('ENV_NAME') == 'Local':
    from .local import *
else:
    raise Exception('No environment name set. Please set ENV_NAME')
