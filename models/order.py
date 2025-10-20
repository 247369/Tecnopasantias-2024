from extensions import db
from datetime import datetime

class Order(db.Model):
    """Modelo de Pedido de corte"""
    
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Información del pedido
    numero_pedido = db.Column(db.String(50), unique=True, nullable=False)
    cliente = db.Column(db.String(150))
    descripcion = db.Column(db.Text)
    
    # Estado del pedido
    estado = db.Column(db.String(20), default='pendiente')
    
    # Prioridad
    prioridad = db.Column(db.String(20), default='normal')
    
    # Fechas
    fecha_solicitud = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_entrega_estimada = db.Column(db.DateTime)
    fecha_completado = db.Column(db.DateTime)
    
    # Relaciones (Foreign Keys)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    empleado_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Datos de corte
    piezas_requeridas = db.Column(db.Text)
    
    # Resultados de optimización
    barras_utilizadas = db.Column(db.Integer)
    desperdicio_total = db.Column(db.Float)
    desperdicio_porcentaje = db.Column(db.Float)
    patron_corte = db.Column(db.Text)
    
    # Notas
    notas = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Pedido {self.numero_pedido} - {self.estado}>'
    
    def puede_iniciar(self):
        return self.material_utilizado.tiene_stock() and self.estado == 'pendiente'
    
    def marcar_completado(self):
        self.estado = 'completado'
        self.fecha_completado = datetime.utcnow()
    
    def calcular_eficiencia(self):
        if self.desperdicio_porcentaje is not None:
            return 100 - self.desperdicio_porcentaje
        return None