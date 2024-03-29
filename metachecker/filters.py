from flask import Blueprint
from arrow import get as arrow_get
from urllib.parse import urlencode

from metachecker import config


bp = Blueprint('filters', 'filters')


@bp.app_template_filter('shorten_address')
def shorten_address(a):
    _p = a[0:6]
    _s = a[-4:]
    return f'{_p}...{_s}'


@bp.app_template_filter('humanize')
def humanize(d):
    if not d:
        return 'never'
    return arrow_get(d).humanize()

@bp.app_template_filter('convert_ipfs_uri')
def convert_ipfs_uri(u):
    ipfs = u.split('ipfs://')[1]
    return f'https://gateway.pinata.cloud/ipfs/{ipfs}'

@bp.app_template_filter("fix_args")
def trim_arg(all_args):
    d = all_args.to_dict()
    if d:
        return '?' + urlencode(d)
    else:
        return ''
