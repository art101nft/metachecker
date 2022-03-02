from logging.config import dictConfig

from metachecker.factory import create_app
from metachecker import config


app = create_app()

dictConfig(config.LOGGING_CONFIG)

if __name__ == '__main__':
    app.run()
