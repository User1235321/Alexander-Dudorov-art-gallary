import os
from flask import Flask
from flaskr.db_project import db
from flask_jwt_extended import JWTManager
from datetime import timedelta
from dotenv import load_dotenv
from flask_mail import Mail
from .mail_service import init_mail_service

mail=Mail()
load_dotenv()

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///example.db'),
                        SQLALCHEMY_TRACK_MODIFICATIONS=False,
                        JWT_SECRET_KEY=os.environ.get('JWT_SECRET', 'default-secret-key'),
                        JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=1),
                        JWT_BLACKLIST_ENABLED = True,

                        MAIL_SERVER='smtp.gmail.com',
                        MAIL_PORT=587,
                        MAIL_USE_TLS=True,
                        MAIL_USERNAME=os.getenv('GMAIL_USER'),
                        MAIL_PASSWORD=os.getenv('GMAIL_APP_PASSWORD'),
                        MAIL_DEFAULT_SENDER=os.getenv('GMAIL_USER')
                        )
init_mail_service(app)
db.init_app(app)

jwt = JWTManager(app)

with app.app_context():
    db.create_all()

try:
    os.makedirs(app.instance_path)
except OSError:
    pass

from . import content
from . import user
from . import admin_panel

from .db_project import User
app.register_blueprint(content.bp)
app.register_blueprint(user.auth_bp)
app.register_blueprint(admin_panel.art_bp)


with app.app_context():
    db.create_all()
    #db.session.query(User).delete()
    if not User.query.filter_by(username='admin').first():
        new_admin = User(
            username='admin',
            email='admin@gmail.com',
            role='artist',
        )
        new_admin.set_password('12345')
        db.session.add(new_admin)
        db.session.commit()




