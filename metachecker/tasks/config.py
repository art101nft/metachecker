from huey import SqliteHuey

from metachecker.factory import create_app_huey
from metachecker import config


huey = SqliteHuey(filename=f'{config.DATA_FOLDER}/huey.db')

app = create_app_huey()
