from extensions import db  # CAMBIO AQUÍ - antes era "from app import db"
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    """Modelo de Usuario"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    nombre_completo = db.Column(db.String(150))
    
    # Rol: 'admin' o 'empleado'
    rol = db.Column(db.String(20), nullable=False, default='empleado')
    
    # Estado
    activo = db.Column(db.Boolean, default=True)
    
    # Timestamps
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    ultima_conexion = db.Column(db.DateTime)
    
    # Relaciones
    pedidos_asignados = db.relationship('Order', backref='empleado_asignado', lazy=True)
    
    def __repr__(self):
        return f'<Usuario {self.username}>'
    
    def es_admin(self):
        return self.rol == 'admin'