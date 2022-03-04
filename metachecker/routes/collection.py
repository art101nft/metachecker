from os import path, remove
from secrets import token_urlsafe

from flask import Blueprint, render_template, flash
from flask import request, redirect, url_for
from flask_login import current_user

from metachecker.models import Collection, User
from metachecker.factory import db
from metachecker import config


bp = Blueprint('collection', 'collection')


@bp.route('/')
def index():
    if current_user.is_anonymous:
        collections = None
    else:
        collections = Collection.query.filter(
            User.id == current_user.id
        ).order_by(Collection.create_date.desc()).all()
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
        return redirect(url_for('collection.show', collection_id=c.id))
    return render_template(
        'new.html'
    )


@bp.route('/collection/<collection_id>')
def show(collection_id):
    amt = 20
    page = 1
    _page = request.args.get('page')
    if _page and _page.isnumeric() and int(_page) > 0:
        page = int(_page)
    collection = Collection.query.filter(Collection.id == collection_id).first()
    if not collection:
        flash('That collection does not exist!', 'warning')
        return redirect(url_for('collection.index'))
    if current_user.is_anonymous:
        flash('Must be authenticated.', 'warning')
        return redirect(url_for('collection.index'))
    if not collection.user_can_access(current_user.id):
        flash('You are not allowed to access that collection.', 'warning')
        return redirect(url_for('collection.index'))
    end_token = page * amt
    start_token = end_token - amt
    tokens = [i for i in range(start_token, end_token + 1) if i >= collection.start_token_id and i <= collection.end_token_id]
    return render_template(
        'collection.html',
        collection=collection,
        tokens=tokens,
        page=page
    )
