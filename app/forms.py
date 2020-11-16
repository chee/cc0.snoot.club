from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, URL
from .models import CopyrightHolder

class LoginForm(FlaskForm):
	name = StringField('username', validators=[DataRequired()])
	password = PasswordField('password', validators=[DataRequired()])
	remember = BooleanField('🍪')
	submit = SubmitField('login')

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
