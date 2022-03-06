from huey import RedisHuey

from metachecker.factory import create_app_huey
from metachecker import config


huey = RedisHuey(
    host=config.CACHE_HOST,
    port=config.CACHE_PORT
)

app = create_app_huey()
