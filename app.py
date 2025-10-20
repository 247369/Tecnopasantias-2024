from flask import Flask, redirect, url_for
from config import config
from extensions import db, login_manager, bcrypt, mail

def create_app(config_name='default'):
    """Factory pattern para crear la aplicación"""
    
    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones con la app
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    
    # User loader para Flask-Login
    from models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Registrar blueprints
    from routes.auth import auth_bp
    from routes.orders import orders_bp
    from routes.optimizer import optimizer_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(orders_bp, url_prefix='/orders')
    app.register_blueprint(optimizer_bp, url_prefix='/optimizer')
    
    # Ruta principal
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
    
    # Crear tablas si no existen
    with app.app_context():
        db.create_all()
    
    return app


if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, host='0.0.0.0', port=5000)