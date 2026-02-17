from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# Global DB object
db = SQLAlchemy()
jwt = JWTManager()  
def create_app():
    app = Flask(__name__)
    app.config.from_object('backend.app.config.Config')

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    jwt.init_app(app)  


    # Import and register blueprints
    from backend.app.routes.job_routes import job_bp
    from backend.app.routes.reviewer_routes import reviewer_bp
    from backend.app.routes.auth_routes import auth_bp

    app.register_blueprint(job_bp)
    app.register_blueprint(reviewer_bp)
    app.register_blueprint(auth_bp)


    with app.app_context():
        from backend.app.models import User  
        db.create_all() 

    print(app.url_map)


    return app