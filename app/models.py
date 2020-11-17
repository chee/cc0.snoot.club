from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db
from . import login

@login.user_loader
def load_user(id):
	return CopyrightHolder.query.get(int(id))

class CopyrightHolder(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(128), index=True, unique=True)
	legal_name = db.Column(db.String(128), index=True)
	password_hash = db.Column(db.String(128))
	email = db.Column(db.String(128), index=True, unique=True)
	website = db.Column(db.String(256), index=True, unique=True)
	collections = db.relationship('Collection', backref='copyright_holder', lazy='dynamic')

	def __repr__(self):
		return f'<CopyrightHolder {self.username} ("{self.legal_name}" <{self.email}>)>'

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)
	def check_password(self, password):
		return check_password_hash(self.password_hash, password)
	def is_admin(self):
		return self.id == 1
	def serialize(self, collections=False, pieces=False):
		return {
			'id': self.id,
			'username': self.username,
			'legal_name': self.legal_name,
			'email': self.email,
			'website': self.website,
			'collections': list(map(
				lambda c : c.serialize(copyright_holder=False, pieces=pieces) if collections else c.id,
				self.collections.all()
			))
		}

class Collection(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(128), index=True)
	description = db.Column(db.String(256))
	slug = db.Column(db.String(128), index=True)
	copyright_holder_id = db.Column(db.Integer, db.ForeignKey('copyright_holder.id'))
	pieces = db.relationship('Piece', backref='collection', lazy='dynamic')
	def __repr__(self):
		return f'<Collection {self.name}>'
	def serialize(self, copyright_holder=False, pieces=False):
		return {
			'id': self.id,
			'name': self.name,
			'description': self.description,
			'slug': self.slug,
			'copyright_holder': self.copyright_holder.serialize(collections=False, pieces=False) if copyright_holder else self.copyright_holder_id,
			'pieces': list(map(
				lambda c : c.serialize(copyright_holder=False, collection=False) if pieces else c.id,
				self.pieces.all()
			))
		}

class Piece(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(128), index=True)
	slug = db.Column(db.String(128), index=True)
	description = db.Column(db.String(256))
	url = db.Column(db.String(256))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	type = db.Column(db.String(10), index=True)
	collection_id = db.Column(db.Integer, db.ForeignKey('collection.id'))
	def __repr__(self):
		return f'<Piece {self.name}>'
	def serialize(self, copyright_holder=False, collection=False):
		return {
			'id': self.id,
			'name': self.name,
			'description': self.description,
			'slug': self.slug,
			'url': self.url,
			'timestamp': str(self.timestamp),
			'copyright_holder': self.collection.copyright_holder.serialze() if copyright_holder else self.collection_id,
			'collection': self.collection.serialize() if collection else self.collection_id
		}
