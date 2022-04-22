import requests
from flask import Blueprint, render_template
from flask import redirect, url_for
from flask_login import logout_user, login_required

from metachecker import config


bp = Blueprint('meta', 'meta')


@bp.route('/about')
def about():
    return render_template('about.html')


@bp.route('/disconnect')
def disconnect():
    logout_user()
    return redirect(url_for('collection.index'))

@bp.route('/ipfs/<path:path>')
@login_required
def load_ipfs(path):
    ipfs_uri = f'{config.IPFS_SERVER}/ipfs/{path}'
    res = requests.get(ipfs_uri, timeout=60)
    return res.content
