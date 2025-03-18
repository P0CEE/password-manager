from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.')

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import user_routes
    app.register_blueprint(user_routes.bp)

    return app
