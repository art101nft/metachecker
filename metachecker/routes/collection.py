from os import path, remove
from secrets import token_urlsafe

from flask import Blueprint, render_template, flash
from flask import request, redirect, url_for
from flask_login import current_user

from metachecker.models import Collection
from metachecker.factory import db
from metachecker import config


bp = Blueprint('collection', 'collection')


@bp.route('/')
def index():
    collections = Collection.query.filter().order_by(Collection.create_date.desc())
    return render_template('index.html', collections=collections)


@bp.route('/new', methods=['GET', 'POST'])
def new():
    if not current_user.is_authenticated:
        flash('You need to connect your wallet first.', 'warning')
        return redirect(url_for('collection.index'))
    if request.method == 'POST':
        if not request.form.get('title'):
            flash('You need to specify a collection title.', 'warning')
            return redirect(url_for('collection.new'))
        if not request.form.get('metadata_uri').startswith('http'):
            flash('You need to specify a proper base metadata URI, ie, https://gateway.pinata.cloud/ipfs/xxxxxxxxxxx/', 'warning')
            return redirect(url_for('collection.new'))
        if not request.form.get('start_token_id').isnumeric():
            flash('You need to specify a valid starting token number, ie, 0 or 1', 'warning')
            return redirect(url_for('collection.new'))
        if not request.form.get('end_token_id').isnumeric():
            flash('You need to specify a valid ending token number, ie, 7777,10000,etc', 'warning')
            return redirect(url_for('collection.new'))
        c = Collection(
            title=request.form.get('title'),
            metadata_uri=request.form.get('metadata_uri'),
            start_token_id=request.form.get('start_token_id'),
            end_token_id=request.form.get('end_token_id'),
            user_id=current_user.id
        )
        db.session.add(c)
        db.session.commit()
        return redirect(url_for('collection.show', collection_id=c.id) + f'?secret_token={c.secret_token}')
    return render_template(
        'new.html'
    )


@bp.route('/collection/<collection_id>')
def show(collection_id):
    collection = Collection.query.filter(Collection.id == collection_id).first()
    if not collection:
        flash('That collection does not exist!', 'warning')
        return redirect(url_for('collection.index'))
    if request.args.get('secret_token') != collection.secret_token:
        flash('Invalid secret token to access the collection!', 'warning')
        return redirect(url_for('collection.index'))
    return render_template('collection.html', collection=collection)
