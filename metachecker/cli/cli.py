import requests
from flask import Blueprint
from secrets import token_urlsafe
from datetime import datetime

from metachecker.factory import db
from metachecker.models import Collection, User
from metachecker import config


bp = Blueprint('cli', 'cli', cli_group=None)


@bp.cli.command('init')
def init():
    db.create_all()
