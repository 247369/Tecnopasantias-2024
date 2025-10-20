"""
Script para inicializar la base de datos con datos de prueba
"""
from app import create_app, db, bcrypt
from datetime import datetime, timedelta

def init_database():
    """Inicializa la base de datos con datos de prueba"""
    
    app = create_app('development')
    
    with app.app_context():
        # Importar modelos dentro del contexto
        from models.user import User
        from models.material import Material
        from models.order import Order
        
        # Eliminar todas las tablas existentes
        print("Eliminando tablas existentes...")
        db.drop_all()
        
        # Crear todas las tablas
        print("Creando tablas...")
        db.create_all()
        
        # Crear usuario administrador
        print("Creando usuario administrador...")
        admin = User(
            username='admin',
            email='admin@plecormet.com',
            password_hash=bcrypt.generate_password_hash('admin123').decode('utf-8'),
            nombre_completo='Administrador del Sistema',
            rol='admin',
            activo=True
        )
        db.session.add(admin)
        
        # Crear usuario empleado
        print("Creando usuario empleado...")
        empleado = User(
            username='empleado1',
            email='empleado1@plecormet.com',
            password_hash=bcrypt.generate_password_hash('empleado123').decode('utf-8'),
            nombre_completo='Juan Pérez',
            rol='empleado',
            activo=True
        )
        db.session.add(empleado)
        
        # Crear materiales de ejemplo
        print("Creando materiales...")
        materiales = [
            Material(
                nombre='Barra de Acero Redonda SAE 1020',
                tipo='Redondo',
                material='Acero SAE 1020',
                longitud_disponible=6000,  # 6 metros
                diametro_espesor=25.4,  # 1 pulgada
                cantidad_stock=50,
                stock_minimo=10,
                precio_unitario=1250.00,
                activo=True
            ),
            Material(
                nombre='Perfil L de Aluminio',
                tipo='Perfil L',
                material='Aluminio 6061',
                longitud_disponible=6000,
                diametro_espesor=3.0,  # 3mm de espesor
                cantidad_stock=30,
                stock_minimo=8,
                precio_unitario=890.00,
                activo=True
            ),
            Material(
                nombre='Tubo Cuadrado de Acero',
                tipo='Tubo Cuadrado',
                material='Acero estructural',
                longitud_disponible=6000,
                diametro_espesor=2.5,
                cantidad_stock=25,
                stock_minimo=5,
                precio_unitario=1450.00,
                activo=True
            ),
            Material(
                nombre='Barra Cuadrada de Acero',
                tipo='Cuadrado',
                material='Acero 1045',
                longitud_disponible=3000,  # 3 metros
                diametro_espesor=50.0,  # 50mm
                cantidad_stock=8,
                stock_minimo=5,
                precio_unitario=2100.00,
                activo=True
            ),
            Material(
                nombre='Perfil T de Aluminio',
                tipo='Perfil T',
                material='Aluminio 6063',
                longitud_disponible=6000,
                diametro_espesor=2.0,
                cantidad_stock=4,  # Stock bajo para prueba de alerta
                stock_minimo=10,
                precio_unitario=950.00,
                activo=True
            )
        ]
        
        for material in materiales:
            db.session.add(material)
        
        db.session.commit()
        
        # Crear pedidos de ejemplo
        print("Creando pedidos de ejemplo...")
        pedidos = [
            Order(
                numero_pedido='PED-2024-001',
                cliente='Metalúrgica ABC S.A.',
                descripcion='Cortes para estructura de soporte',
                estado='pendiente',
                prioridad='alta',
                material_id=1,
                empleado_id=empleado.id,
                fecha_solicitud=datetime.utcnow() - timedelta(days=2),
                fecha_entrega_estimada=datetime.utcnow() + timedelta(days=5)
            ),
            Order(
                numero_pedido='PED-2024-002',
                cliente='Construcciones XYZ',
                descripcion='Cortes para marcos de ventanas',
                estado='en_proceso',
                prioridad='normal',
                material_id=2,
                empleado_id=empleado.id,
                fecha_solicitud=datetime.utcnow() - timedelta(days=5),
                fecha_entrega_estimada=datetime.utcnow() + timedelta(days=2)
            ),
            Order(
                numero_pedido='PED-2024-003',
                cliente='Industrias DEF',
                descripcion='Tubos para estructura de muebles',
                estado='completado',
                prioridad='baja',
                material_id=3,
                empleado_id=empleado.id,
                fecha_solicitud=datetime.utcnow() - timedelta(days=10),
                fecha_entrega_estimada=datetime.utcnow() - timedelta(days=3),
                fecha_completado=datetime.utcnow() - timedelta(days=2),
                barras_utilizadas=5,
                desperdicio_total=450.5,
                desperdicio_porcentaje=7.5
            ),
            Order(
                numero_pedido='PED-2024-004',
                cliente='Taller Mecánico GHI',
                descripcion='Ejes para maquinaria',
                estado='pendiente',
                prioridad='urgente',
                material_id=1,
                fecha_solicitud=datetime.utcnow(),
                fecha_entrega_estimada=datetime.utcnow() + timedelta(days=1)
            )
        ]
        
        for pedido in pedidos:
            db.session.add(pedido)
        
        db.session.commit()
        
        print("\n" + "="*60)
        print("✅ Base de datos inicializada correctamente!")
        print("="*60)
        print("\n📋 USUARIOS CREADOS:")
        print("-" * 60)
        print(f"👤 Administrador:")
        print(f"   Usuario: admin")
        print(f"   Contraseña: admin123")
        print(f"   Email: admin@plecormet.com")
        print()
        print(f"👤 Empleado:")
        print(f"   Usuario: empleado1")
        print(f"   Contraseña: empleado123")
        print(f"   Email: empleado1@plecormet.com")
        print("-" * 60)
        print(f"\n📦 MATERIALES: {len(materiales)} creados")
        print(f"📄 PEDIDOS: {len(pedidos)} creados")
        print("\n🚀 Ya puedes iniciar la aplicación con: python app.py")
        print("="*60)

if __name__ == '__main__':
    init_database()