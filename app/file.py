import mimetypes
from os.path import basename
from .config import Config
from werkzeug.utils import secure_filename
mimetypes.init()
import boto3

storage_endpoint = "https://eu-central-1.linodeobjects.com"
bucket_name = "cc0"
bucket_url = f"{storage_endpoint}/{bucket_name}"
storage = boto3.resource(
	's3',
	endpoint_url=storage_endpoint,
	region_name='eu-central-1',
	aws_access_key_id=Config.OBJECT_KEY_ID,
	aws_secret_access_key=Config.OBJECT_ACCESS_KEY
)
bucket = storage.Bucket(bucket_name)

def make_public(name):
	storage.Object(bucket_name, name).Acl().put(ACL='public-read')

def get_url_for(file, username, collection_slug, piece_slug):
	name = f'{username}-{collection_slug}-{piece_slug}-{secure_filename(basename(file.filename))}'
	bucket.upload_fileobj(file.stream, name)
	make_public(name)
	return f"{bucket_url}/{name}"

def get_type_for(file):
	return mimetypes.guess_type(file.filename)[0]
