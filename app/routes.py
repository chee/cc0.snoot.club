from flask import render_template, flash, redirect, url_for, Response, request
from flask_login import current_user, login_user, login_required
from . import app
from . import db
from .forms import LoginForm, RegistrationForm, CollectionForm, PieceForm
from .models import CopyrightHolder, Collection, Piece
from .file import get_url_for, get_type_for
from slugify import slugify
from json import dumps as stringify_json

def render_json(thing):
        return Response(stringify_json(thing), mimetype="application/json")

def render_404():
         return Response("404", status=404)

@app.route('/')
def index():
        return render_template("index.html",
                               collections=Collection.query.all())

@app.route('/.json')
def index_json():
        s = lambda thing : thing.serialize()
        json = {
                'copyright_holders': list(map(s, CopyrightHolder.query.all())),
                'collections': list(map(s, Collection.query.all())),
                'pieces': list(map(s, Piece.query.all()))
        }
        return render_json(json)

@app.route('/logout/')
@app.route('/logout')
def logout():
        return render_template("base.html")

@app.route('/register/', methods=['GET', 'POST'])
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

@app.route('/login/', methods=['GET', 'POST'])
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
@app.route('/<username>/')
def copyright_holder(username):
        ch = CopyrightHolder.query.filter_by(username=username).first()
        if ch is None:
                return render_404()
        return render_template("copyright_holder.html",
                               copyright_holder=ch)

@app.route('/<username>/.json')
@app.route('/<username>.json')
def copyright_holder_json(username):
        ch = CopyrightHolder.query.filter_by(username=username).first()
        with_collections = request.args.get("collections")
        with_pieces = request.args.get("pieces")
        if ch is None:
                return render_json("{}")
        return render_json(ch.serialize(collections=with_collections or with_pieces,
                                        pieces=with_pieces))


@app.route('/<username>/new', methods=['GET', 'POST'])
@app.route('/<username>/new/', methods=['GET', 'POST'])
@login_required
def new_collection(username):
        ch = CopyrightHolder.query.filter_by(username=username).first()
        if ch is None:
                return render_404()
        if current_user.id != ch.id:
                flash("hey, that's not yours")
                return redirect(url_for('index'))
        form = CollectionForm()
        if form.validate_on_submit():
                slug = slugify(form.name.data)
                existing = Collection.query.filter_by(slug=slug).first()
                if existing is not None:
                        flash(f"that name would need the path {username}/{slug}, which is taken")
                        return redirect(url_for('new_collection',
                                                username=username))
                collection = Collection(name=form.name.data,
                                        description=form.description.data,
                                        slug=slug,
                                        copyright_holder_id=current_user.id)

                db.session.add(collection)
                db.session.commit()

                flash(f"{collection.name} created")
                return redirect(url_for('collection', username=username, slug=slug))
        return render_template('new_collection.html',
                               title="create new collection",
                               form=form)


@app.route('/<username>/<slug>')
@app.route('/<username>/<slug>/')
def collection(username, slug):
        ch = CopyrightHolder.query.filter_by(username=username).first()
        collection = ch.collections.filter_by(slug=slug).first()
        if collection is None:
                return render_404()
        return render_template("collection.html",
                               copyright_holder=ch,
                               collection=collection)

@app.route('/<username>/<slug>.json')
@app.route('/<username>/<slug>/.json')
def collection_json(username, slug):
        ch = CopyrightHolder.query.filter_by(username=username).first()
        collection = ch.collections.filter_by(slug=slug).first()
        with_copyright_holder = request.args.get("copyright_holder")
        with_pieces = request.args.get("pieces")
        if collection is None:
                return render_json("{}")
        return render_json(collection.serialize(
                copyright_holder=with_copyright_holder,
                pieces=with_pieces
        ))

@app.route('/<username>/<collection_slug>/<piece_slug>')
@app.route('/<username>/<collection_slug>/<piece_slug>/')
def piece(username, collection_slug, piece_slug):
        ch = CopyrightHolder.query.filter_by(username=username).first()
        collection = ch.collections.filter_by(slug=collection_slug).first()
        piece = collection.pieces.filter_by(slug=piece_slug).first()
        if piece is None:
                return render_404()
        return render_template("_piece.html",
                               copyright_holder=ch,
                               collection=collection,
                               piece=piece)

@app.route('/<username>/<collection_slug>/<piece_slug>.json')
@app.route('/<username>/<collection_slug>/<piece_slug>/.json')
def piece_json(username, collection_slug, piece_slug):
        ch = CopyrightHolder.query.filter_by(username=username).first()
        collection = ch.collections.filter_by(slug=collection_slug).first()
        piece = collection.pieces.filter_by(slug=piece_slug).first()
        with_copyright_holder = request.args.get("copyright_holder")
        with_collection = request.args.get("collection")
        return render_json(piece.serialize(
                copyright_holder=with_copyright_holder,
                collection=with_collection
        ))

@login_required
@app.route('/<username>/<slug>/new', methods=['GET', 'POST'])
@app.route('/<username>/<slug>/new/', methods=['GET', 'POST'])
def new_piece(username, slug):
        ch = CopyrightHolder.query.filter_by(username=username).first()
        if ch is None:
                return render_404()
        if current_user.id != ch.id:
                flash("hey, that's not yours")
                return redirect(url_for('index'))
        collection = Collection.query.filter_by(slug=slug).first()
        if collection is None:
                return render_404()
        form = PieceForm()
        if form.validate_on_submit():
                piece_slug = slugify(form.name.data)
                existing = Piece.query.filter_by(slug=piece_slug).first()
                if existing is not None:
                        flash(f"that name would need the path {username}/{slug}/{piece_slug}, which is taken")
                        return redirect(url_for('new_piece',
                                                username=username,
                                                slug=slug))
                file = form.file.data
                url = get_url_for(file,
                                  username=username,
                                  collection_slug=slug,
                                  piece_slug=piece_slug)
                type = get_type_for(file)
                piece = Piece(name=form.name.data,
                              description=form.description.data,
                              slug=piece_slug,
                              collection_id=collection.id,
                              type=type,
                              url=url)

                db.session.add(piece)
                db.session.commit()

                flash(f"{piece.name} created")
                return redirect(url_for('collection',
                                        username=username,
                                        slug=slug))
        return render_template('new_piece.html',
                               title=f"add to '{collection.name}'",
                               form=form)
