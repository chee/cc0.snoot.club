from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, URL
from werkzeug.utils import secure_filename
from .models import CopyrightHolder

class LoginForm(FlaskForm):
	name = StringField('username', validators=[DataRequired()])
	password = PasswordField('password', validators=[DataRequired()])
	remember = BooleanField('🍪')
	submit = SubmitField('login')

class CollectionForm(FlaskForm):
	name = StringField('name', validators=[DataRequired()])
	description = StringField('description', validators=[DataRequired()])
	submit = SubmitField('make')

class PieceForm(FlaskForm):
	name = StringField('name', validators=[DataRequired()])
	description = StringField('description', validators=[DataRequired()])
	file = FileField('file', validators=[FileRequired()])
	submit = SubmitField('save')

class RegistrationForm(FlaskForm):
	name = StringField('username', validators=[DataRequired()])
	password = PasswordField('password', validators=[DataRequired()])
	legal_name = StringField('legal name', validators=[DataRequired()])
	website = StringField('website url', validators=[DataRequired(), URL()])
	submit = SubmitField('register')

	def validate_name(self, username):
		user = CopyrightHolder.query.filter_by(username=username.data).first()

		if user is not None or user in ["login", "register", "logout"]:
			raise ValidationError('sorry, username in use')
