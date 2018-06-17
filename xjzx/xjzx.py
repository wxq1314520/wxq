from flask import Flask,render_template

from flask_script import Manager

from app import create_app
app=Flask(__name__)
from config import DevelopConfig
app=create_app(DevelopConfig)
manager=Manager(app)

from models import db
db.init_app(app)
from flask_migrate import Migrate,MigrateCommand
Migrate(app,db)
manager.add_command('db',MigrateCommand)
# @app.route('/')
# def index():
#     return render_template('news/index.html')
# @app.route('/user')
# def user():
#     return render_template('news/user.html')
from super_command import CreateAdminCommand
manager.add_command('admin',CreateAdminCommand())
if __name__ == '__main__':
    manager.run()
