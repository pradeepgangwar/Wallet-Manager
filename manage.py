from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import os

app = Flask(__name__)

from app import app,Base
app.config.from_object(os.environ['APP_SETTINGS'])

with app.app_context():
  from database_setup import *

migrate = Migrate(app,Base)
manager = Manager(app)

manager.add_command('Base', MigrateCommand)

if __name__ == '__main__':
	manager.run()