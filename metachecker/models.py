from uuid import uuid4
from datetime import datetime
from secrets import token_urlsafe

from flask_login import login_user
from sqlalchemy import inspect

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
    accesses = db.relationship('Access', back_populates='user')

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
        return self.admin

    def is_moderator(self):
        return self.moderator

    def get_id(self):
        return self.id

    def generate_nonce(self):
        return rand_id()

    def change_nonce(self):
        self.nonce = rand_id()
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
    metadata_uri = db.Column(db.String(100), unique=True, nullable=True)
    title = db.Column(db.String(50))
    secret_token = db.Column(db.String(50), default=token_urlsafe(8))
    start_token_id = db.Column(db.Integer)
    end_token_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='collections')
    accesses = db.relationship('Access', back_populates='collection')

    def as_dict(self):
        return {c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs}

    def user_can_access(self, user_id):
        if user_id == self.user_id or user_id in self.accesses:
            return True
        else:
            return False

    def __repr__(self):
        return str(f'collection-{self.id}')


class Access(db.Model):
    __tablename__ = 'access'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='accesses')
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.id'))
    collection = db.relationship('Collection', back_populates='accesses')

    def as_dict(self):
        return {c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs}

    def __repr__(self):
        return str(f'access-{self.id}')
