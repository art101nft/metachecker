from math import ceil

from flask import Blueprint, render_template, flash
from flask import request, redirect, url_for
from flask_login import current_user
from web3.auto import w3

from metachecker.models import Collection, User, Token, Access
from metachecker.tasks.metadata import fetch_collection_metadata
from metachecker.factory import db
from metachecker import config


bp = Blueprint('collection', 'collection')


@bp.route('/')
def index():
    if current_user.is_anonymous:
        collections = None
    else:
        collections = Collection.query.filter().order_by(Collection.create_date.desc()).all()
        collections = [i for i in collections if i.user_can_access(current_user.id)]
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
        metadata_uri = request.form.get('metadata_uri')
        if not metadata_uri.endswith('/'):
            metadata_uri = metadata_uri + '/'
        c = Collection(
            title=request.form.get('title'),
            metadata_uri=metadata_uri,
            start_token_id=request.form.get('start_token_id'),
            end_token_id=request.form.get('end_token_id'),
            user_id=current_user.id
        )
        db.session.add(c)
        db.session.commit()
        fetch_collection_metadata.schedule([c.id], delay=3)
        return redirect(url_for('collection.show', collection_id=c.id))
    return render_template(
        'new.html'
    )


@bp.route('/collection/<collection_id>')
def show(collection_id):
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
    return render_template(
        'collection.html',
        collection=collection
    )

@bp.route('/collection/<collection_id>/add_collaborator')
def add_collaborator(collection_id):
    collection = Collection.query.filter(Collection.id == collection_id).first()
    if not collection:
        flash('That collection does not exist!', 'warning')
        return redirect(url_for('collection.index'))
    if current_user.is_anonymous:
        flash('Must be authenticated.', 'warning')
        return redirect(url_for('collection.show', collection_id=collection.id))
    if not collection.user_id == current_user.id:
        flash('Must be the owner of the collection to add collaborators.', 'warning')
        return redirect(url_for('collection.show', collection_id=collection.id))
    address = request.args.get('address')
    if address:
        address = address.lower()
        if w3.isAddress(address):
            if collection.user.public_address == address:
                flash('Cannot add that collaborator, they own the collection.', 'warning')
            else:
                exists = Access.query.filter(Access.public_address == address).first()
                if exists:
                    flash('Collaborator already added.', 'warning')
                else:
                    a = Access(
                        public_address=address,
                        collection_id=collection.id
                    )
                    db.session.add(a)
                    db.session.commit()
                    flash(f'Collaborator {address} added!', 'success')
        else:
            flash('Invalid ETH address provided.', 'error')
    return redirect(url_for('collection.show', collection_id=collection.id))

@bp.route('/collection/<collection_id>/<token_id>')
def show_token(collection_id, token_id):
    prev, next = None, None
    collection = Collection.query.get(collection_id)
    if not collection:
        flash('That collection does not exist!', 'warning')
        return redirect(url_for('collection.index'))
    token = Token.query.filter(
        Token.token_id == token_id,
        Token.collection_id == collection_id
    ).first()
    if not token:
        flash('That token does not exist for that collection!', 'warning')
        return redirect(url_for('collection.show', collection_id=collection_id))
    if current_user.is_anonymous:
        flash('Must be authenticated.', 'warning')
        return redirect(url_for('collection.index'))
    if not collection.user_can_access(current_user.id):
        flash('You are not allowed to access that collection.', 'warning')
        return redirect(url_for('collection.index'))

    _show = request.args.get('show')
    rejected, approved, all = False, False, False
    if _show == 'rejected':
        rejected = True
    elif _show == 'approved':
        approved = True
    else:
        all = True
    tokens = collection.get_tokens(rejected=rejected, approved=approved, all=all).all()
    index = tokens.index(token)
    if index + 1 < len(tokens):
        next = tokens[index + 1]
    if index > 0:
        prev = tokens[index - 1]
    return render_template(
        'token.html',
        token=token,
        prev=prev,
        next=next
    )

@bp.route('/collection/<collection_id>/<token_id>/<action>')
def update_token(collection_id, token_id, action):
    collection = Collection.query.get(collection_id)
    if not collection:
        flash('That collection does not exist!', 'warning')
        return redirect(url_for('collection.index'))
    token = Token.query.filter(
        Token.token_id == token_id,
        Token.collection_id == collection_id
    ).first()
    if not token:
        flash('That token does not exist for that collection!', 'warning')
        return redirect(url_for('collection.show', collection_id=collection_id))
    if current_user.is_anonymous:
        flash('Must be authenticated.', 'warning')
        return redirect(url_for('collection.index'))
    if not collection.user_can_access(current_user.id):
        flash('You are not allowed to access that collection.', 'warning')
        return redirect(url_for('collection.index'))
    if action == 'approve':
        token.rejected = False
        token.approved = True
        token.reject_reason = None
        db.session.commit()
        flash(f'Token was approved!', 'success')
    elif action == 'reject':
        if not request.args.get('reason'):
            flash('You need to specify a reason for rejection.', 'warning')
            return redirect(url_for('collection.show_token', collection_id=collection_id, token_id=token.token_id))
        token.rejected = True
        token.approved = False
        token.reject_reason = request.args.get('reason')
        db.session.commit()
        flash(f'Token was rejected!', 'error')
    else:
        flash('Unknown action.', 'warning')
    next = collection.get_tokens().first()
    return redirect(url_for('collection.show_token', collection_id=collection_id, token_id=next.token_id))
