from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user
from . import app
from . import db
from .forms import LoginForm, RegistrationForm
from .models import CopyrightHolder, Collection, Piece

from os import scandir
from os.path import join, dirname

@app.route('/')
def index():
	return render_template("index.html",
			       collections=Collection.query.all())

@app.route('/logout')
def logout():
	return render_template("base.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		ch = CopyrightHolder(
			username=form.name.data,
			legal_name=form.legal_name.data
		)
		ch.set_password(form.password.data)
		db.session.add(ch)
		db.session.commit()
		flash(f"{ch} created")
		return redirect(url_for('index'))
	return render_template('register.html', title="make user", form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		copyright_holder = CopyrightHolder.query.filter_by(username=form.name.data).first()
		if copyright_holder is None or not copyright_holder.check_password(form.password.data):
			flash('bad name or wrong pass')
			return redirect(url_for('login'))
		login_user(copyright_holder, remember=form.remember.data)
		return redirect(url_for('index'))
	return render_template('login.html', title="login", form=form)

@app.route('/<username>')
def copyright_holder(username):
	ch = CopyrightHolder.query.filter_by(username=username).first()
	if ch is None:
		return "404"
	return render_template("copyright_holder.html",
			       copyright_holder=ch)

@app.route('/<username>/new')
def new_collection(username):
	return render_template("base.html")


@app.route('/<username>/<slug>')
def collection(username, slug):
	collection = Collection.query.filter_by(slug=slug).first()
	if collection is None:
		return "404"
	return render_template("collection.html",
			       copyright_holder=collection)

@app.route('/<username>/<slug>/new')
def new_piece(username, slug):
	return render_template("base.html")
