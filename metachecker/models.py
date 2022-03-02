from uuid import uuid4
from datetime import datetime
from secrets import token_urlsafe

from flask_login import login_user
from sqlalchemy import inspect

from metachecker.factory import db
from metachecker import config


def rand_id():
    return uuid4().hex


class Moderator(db.Model):
    __tablename__ = 'moderators'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='moderator')

    def __rep__(self):
        return self.user.handle


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    register_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_date = db.Column(db.DateTime, nullable=True)
    public_address = db.Column(db.String(180))
    nonce = db.Column(db.String(180), default=rand_id())
    nonce_date = db.Column(db.DateTime, default=datetime.utcnow)
    moderator = db.relationship('Moderator', back_populates='user')
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
        return self.admin

    def is_moderator(self):
        return len(self.moderator) > 0

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

    id = db.Column(db.String(80), default=rand_id, primary_key=True)
    create_date = db.Column(db.DateTime, default=datetime.utcnow)
    metadata_uri = db.Column(db.String(100), unique=True, nullable=True)
    title = db.Column(db.String(50))
    secret_token = db.Column(db.String(50), default=token_urlsafe(8))
    # synced = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='collections')

    def as_dict(self):
        return {c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs}

    def __repr__(self):
        return str(f'collection-{self.id}')
