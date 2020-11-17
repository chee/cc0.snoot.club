import os
basedir = os.path.abspath(os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv()

class Config(object):
	SECRET_KEY = os.environ.get('CC0_SECRET_KEY')
	SQLALCHEMY_DATABASE_URI = os.environ.get("CC0_SQLALCHEMY_DATABASE_URI") or f"sqlite:///{os.path.join(basedir, 'app.db')}"
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	OBJECT_KEY_ID = os.environ.get('CC0_OBJECT_KEY_ID')
	OBJECT_ACCESS_KEY = os.environ.get('CC0_OBJECT_ACCESS_KEY')
