from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import main_routes
    from app.routes import auth_routes
    
    app.register_blueprint(main_routes.bp)
    app.register_blueprint(auth_routes.bp)

    return app