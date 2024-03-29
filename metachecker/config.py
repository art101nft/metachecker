from os import getenv
from dotenv import load_dotenv

load_dotenv()

# App
SECRET_KEY = getenv('SECRET_KEY', 'yyyyyyyyyyyyy')
DATA_FOLDER = getenv('DATA_FOLDER', '/path/to/uploads')
SERVER_NAME = getenv('SERVER_NAME', '127.0.0.1:5000')
IPFS_SERVER = getenv('IPFS_SERVER', 'http://127.0.0.1:8080')

# Cache
CACHE_HOST = getenv('CACHE_HOST', '127.0.0.1')
CACHE_PORT = getenv('CACHE_PORT', '6379')

# Logging
LOGGING_CONFIG = {
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'stream': 'ext://sys.stdout',
        },
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }
    },
    'loggers': {
        'gunicorn.error': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'gunicorn.access': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console'],
    }
}
