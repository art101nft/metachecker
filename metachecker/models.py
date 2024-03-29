import json
from uuid import uuid4
from datetime import datetime

from flask_login import login_user
from sqlalchemy import inspect
from slugify import slugify

from metachecker.factory import db
from metachecker import config


def rand_id():
    return uuid4().hex


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    register_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_date = db.Column(db.DateTime, nullable=True)
    public_address = db.Column(db.String(180))
    nonce = db.Column(db.String(180), default=rand_id())
    nonce_date = db.Column(db.DateTime, default=datetime.utcnow)
    moderator = db.Column(db.Boolean, default=False)
    collections = db.relationship('Collection', back_populates='user')

    def as_dict(self):
        return {c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs if c.key != 'nonce'}

    def __repr__(self):
        return str(self.handle)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_admin(self):
        return self.moderator

    def get_id(self):
        return self.id

    def generate_nonce(self):
        return rand_id()[0:8]

    def change_nonce(self):
        self.nonce = self.generate_nonce()
        self.nonce_date = datetime.utcnow()
        db.session.commit()

    def login(self):
        self.change_nonce()
        self.last_login_date = datetime.utcnow()
        login_user(self)
        db.session.commit()


class Collection(db.Model):
    __tablename__ = 'collections'

    id = db.Column(db.Integer, primary_key=True)
    create_date = db.Column(db.DateTime, default=datetime.utcnow)
    metadata_uri = db.Column(db.String(100))
    title = db.Column(db.String(50))
    start_token_id = db.Column(db.Integer)
    end_token_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='collections')
    accesses = db.relationship('Access', back_populates='collection')
    tokens = db.relationship('Token', back_populates='collection')

    def as_dict(self):
        return {c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs}

    def user_can_access(self, user_id):
        exists = User.query.get(user_id)
        if exists:
            collaborators = [i.public_address for i in self.accesses]
            if user_id == self.user_id or exists.public_address in collaborators:
                return True
            else:
                return False
        else:
            return False

    def get_metadata_folder(self):
        collection_folder = f'{self.id}-{slugify(self.metadata_uri)}'
        return f'{config.DATA_FOLDER}/json/{collection_folder}'

    def is_sync_completed(self):
        tokens = Token.query.filter(
            Token.collection_id == self.id
        ).count()
        return tokens == len(range(self.start_token_id, self.end_token_id + 1))

    def get_tokens(self, approved=False, rejected=False, all=False, start=0, end=0):
        # By default return unreviewed tokens
        if all:
            return Token.query.filter(
                Token.collection_id == self.id
            ).order_by(Token.create_date.asc())
        if end:
            return Token.query.filter(
                Token.collection_id == self.id,
                Token.token_id >= start,
                Token.token_id < end
            ).order_by(Token.create_date.asc())
        return Token.query.filter(
            Token.collection_id == self.id,
            Token.approved == approved,
            Token.rejected == rejected
        ).order_by(Token.create_date.asc())

    def __repr__(self):
        return str(f'collection-{self.id}')


class Token(db.Model):
    __tablename__ = 'tokens'

    id = db.Column(db.Integer, primary_key=True)
    create_date = db.Column(db.DateTime, default=datetime.utcnow)
    token_id = db.Column(db.Integer)
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.id'))
    collection = db.relationship('Collection', back_populates='tokens')
    approved = db.Column(db.Boolean, default=False)
    rejected = db.Column(db.Boolean, default=False)
    reject_reason = db.Column(db.String(200), nullable=True)

    def as_dict(self):
        return {c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs}

    def get_metadata_path(self):
        return f'{self.collection.get_metadata_folder()}/{self.token_id}.json'

    def get_metadata_dict(self):
        with open(self.get_metadata_path(), 'r') as f:
            return json.loads(f.read())

    def set_metadata_dict(self, data):
        with open(self.get_metadata_path(), 'w') as f:
            f.write(json.dumps(data))

    def __repr__(self):
        return str(f'token-{self.id}')


class Access(db.Model):
    __tablename__ = 'access'

    id = db.Column(db.Integer, primary_key=True)
    public_address = db.Column(db.String(180))
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.id'))
    collection = db.relationship('Collection', back_populates='accesses')

    def as_dict(self):
        return {c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs}

    def __repr__(self):
        return str(f'access-{self.id}')
