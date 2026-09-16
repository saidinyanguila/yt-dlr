from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '1234567890'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

    db.init_app(app)

    from .routes.views import views
    from .routes.auth import auth
    from .routes.library import library

    app.register_blueprint(views, url_prefix = "/")
    app.register_blueprint(auth, url_prefix = "/account")
    app.register_blueprint(library, url_prefix = "/library")

    from .models.models import User
        
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all() 
        print('Created database')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.sign_in'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
    