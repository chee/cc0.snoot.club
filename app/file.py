import mimetypes
from os.path import join, basename, dirname
from werkzeug.utils import secure_filename
from slugify import slugify
mimetypes.init()

def get_url_for(file, username, collection_slug, piece_slug):
	name = f'{username}-{collection_slug}-{piece_slug}-{secure_filename(basename(file.filename))}'
	path = join(dirname(__file__), "static", name)
	file.save(path)

	return f"/static/{name}"

def get_type_for(file):
	return mimetypes.guess_type(file.filename)[0]
