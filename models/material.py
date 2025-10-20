from extensions import db
from datetime import datetime

class Material(db.Model):
    """Modelo de Material disponible en inventario"""
    
    __tablename__ = 'materials'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Información del material
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    material = db.Column(db.String(50))
    
    # Dimensiones
    longitud_disponible = db.Column(db.Float, nullable=False)
    diametro_espesor = db.Column(db.Float)
    
    # Inventario
    cantidad_stock = db.Column(db.Integer, default=0)
    stock_minimo = db.Column(db.Integer, default=5)
    
    # Costos
    precio_unitario = db.Column(db.Float)
    
    # Estado
    activo = db.Column(db.Boolean, default=True)
    
    # Timestamps
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    pedidos = db.relationship('Order', backref='material_utilizado', lazy=True)
    
    def __repr__(self):
        return f'<Material {self.nombre} - {self.longitud_disponible}mm>'
    
    def stock_bajo(self):
        return self.cantidad_stock <= self.stock_minimo
    
    def tiene_stock(self):
        return self.cantidad_stock > 0