from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.order import Order
from models.material import Material
from models.user import User
from datetime import datetime
import json

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal - Vista según rol"""
    
    if current_user.es_admin():
        # Admin ve todos los pedidos
        pedidos_pendientes = Order.query.filter_by(estado='pendiente').count()
        pedidos_en_proceso = Order.query.filter_by(estado='en_proceso').count()
        pedidos_completados = Order.query.filter_by(estado='completado').count()
        
        # Últimos pedidos
        ultimos_pedidos = Order.query.order_by(Order.fecha_solicitud.desc()).limit(10).all()
        
        # Materiales con stock bajo
        materiales_bajo_stock = Material.query.filter(
            Material.cantidad_stock <= Material.stock_minimo,
            Material.activo == True
        ).all()
        
        return render_template('dashboard_admin.html',
                             pedidos_pendientes=pedidos_pendientes,
                             pedidos_en_proceso=pedidos_en_proceso,
                             pedidos_completados=pedidos_completados,
                             ultimos_pedidos=ultimos_pedidos,
                             materiales_bajo_stock=materiales_bajo_stock)
    else:
        # Empleado ve solo sus pedidos asignados
        mis_pedidos = Order.query.filter_by(empleado_id=current_user.id).order_by(
            Order.fecha_solicitud.desc()
        ).all()
        
        return render_template('dashboard_empleado.html', mis_pedidos=mis_pedidos)


@orders_bp.route('/list')
@login_required
def list_orders():
    """Lista de pedidos"""
    
    # Filtros
    estado = request.args.get('estado', 'todos')
    
    if current_user.es_admin():
        query = Order.query
    else:
        # Empleados solo ven sus pedidos
        query = Order.query.filter_by(empleado_id=current_user.id)
    
    if estado != 'todos':
        query = query.filter_by(estado=estado)
    
    pedidos = query.order_by(Order.fecha_solicitud.desc()).all()
    
    return render_template('orders_list.html', pedidos=pedidos, estado_filtro=estado)


@orders_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_order():
    """Crear nuevo pedido"""
    
    # Solo administradores pueden crear pedidos
    if not current_user.es_admin():
        flash('No tienes permisos para crear pedidos.', 'danger')
        return redirect(url_for('orders.dashboard'))
    
    if request.method == 'POST':
        # Obtener datos del formulario
        numero_pedido = request.form.get('numero_pedido')
        cliente = request.form.get('cliente')
        descripcion = request.form.get('descripcion')
        material_id = request.form.get('material_id')
        empleado_id = request.form.get('empleado_id')
        prioridad = request.form.get('prioridad', 'normal')
        fecha_entrega = request.form.get('fecha_entrega')
        
        # Validaciones
        if not all([numero_pedido, material_id]):
            flash('Por favor completa los campos obligatorios.', 'warning')
            return redirect(url_for('orders.create_order'))
        
        # Verificar que el número de pedido no exista
        if Order.query.filter_by(numero_pedido=numero_pedido).first():
            flash('El número de pedido ya existe.', 'danger')
            return redirect(url_for('orders.create_order'))
        
        # Crear pedido
        nuevo_pedido = Order(
            numero_pedido=numero_pedido,
            cliente=cliente,
            descripcion=descripcion,
            material_id=material_id,
            empleado_id=empleado_id if empleado_id else None,
            prioridad=prioridad,
            fecha_entrega_estimada=datetime.strptime(fecha_entrega, '%Y-%m-%d') if fecha_entrega else None
        )
        
        db.session.add(nuevo_pedido)
        db.session.commit()
        
        flash(f'Pedido {numero_pedido} creado exitosamente.', 'success')
        return redirect(url_for('orders.view_order', order_id=nuevo_pedido.id))
    
    # GET: Mostrar formulario
    materiales = Material.query.filter_by(activo=True).all()
    empleados = User.query.filter_by(rol='empleado', activo=True).all()
    
    return render_template('order_create.html', materiales=materiales, empleados=empleados)


@orders_bp.route('/<int:order_id>')
@login_required
def view_order(order_id):
    """Ver detalles de un pedido"""
    
    pedido = Order.query.get_or_404(order_id)
    
    # Verificar permisos
    if not current_user.es_admin() and pedido.empleado_id != current_user.id:
        flash('No tienes permisos para ver este pedido.', 'danger')
        return redirect(url_for('orders.dashboard'))
    
    # Parsear piezas requeridas si existen
    piezas = []
    if pedido.piezas_requeridas:
        try:
            piezas = json.loads(pedido.piezas_requeridas)
        except:
            piezas = []
    
    # Parsear patrón de corte si existe
    patron = None
    if pedido.patron_corte:
        try:
            patron = json.loads(pedido.patron_corte)
        except:
            patron = None
    
    return render_template('order_detail.html', pedido=pedido, piezas=piezas, patron=patron)


@orders_bp.route('/<int:order_id>/update-status', methods=['POST'])
@login_required
def update_status(order_id):
    """Actualizar estado del pedido"""
    
    pedido = Order.query.get_or_404(order_id)
    
    # Verificar permisos
    if not current_user.es_admin() and pedido.empleado_id != current_user.id:
        return jsonify({'success': False, 'message': 'No tienes permisos'}), 403
    
    nuevo_estado = request.form.get('estado')
    
    if nuevo_estado not in ['pendiente', 'en_proceso', 'completado', 'cancelado']:
        return jsonify({'success': False, 'message': 'Estado inválido'}), 400
    
    pedido.estado = nuevo_estado
    
    if nuevo_estado == 'completado':
        pedido.fecha_completado = datetime.utcnow()
    
    db.session.commit()
    
    flash(f'Estado del pedido actualizado a: {nuevo_estado}', 'success')
    return redirect(url_for('orders.view_order', order_id=order_id))


@orders_bp.route('/<int:order_id>/delete', methods=['POST'])
@login_required
def delete_order(order_id):
    """Eliminar pedido (solo admin)"""
    
    if not current_user.es_admin():
        flash('No tienes permisos para eliminar pedidos.', 'danger')
        return redirect(url_for('orders.dashboard'))
    
    pedido = Order.query.get_or_404(order_id)
    
    db.session.delete(pedido)
    db.session.commit()
    
    flash(f'Pedido {pedido.numero_pedido} eliminado correctamente.', 'success')
    return redirect(url_for('orders.list_orders'))


@orders_bp.route('/materials')
@login_required
def list_materials():
    """Lista de materiales"""
    
    materiales = Material.query.filter_by(activo=True).all()
    return render_template('materials_list.html', materiales=materiales)


@orders_bp.route('/materials/create', methods=['GET', 'POST'])
@login_required
def create_material():
    """Crear nuevo material (solo admin)"""
    
    if not current_user.es_admin():
        flash('No tienes permisos para agregar materiales.', 'danger')
        return redirect(url_for('orders.dashboard'))
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        tipo = request.form.get('tipo')
        material = request.form.get('material')
        longitud_disponible = request.form.get('longitud_disponible')
        diametro_espesor = request.form.get('diametro_espesor')
        cantidad_stock = request.form.get('cantidad_stock')
        stock_minimo = request.form.get('stock_minimo', 5)
        precio_unitario = request.form.get('precio_unitario')
        
        # Validaciones
        if not all([nombre, tipo, longitud_disponible]):
            flash('Por favor completa los campos obligatorios.', 'warning')
            return render_template('material_create.html')
        
        # Crear material
        nuevo_material = Material(
            nombre=nombre,
            tipo=tipo,
            material=material,
            longitud_disponible=float(longitud_disponible),
            diametro_espesor=float(diametro_espesor) if diametro_espesor else None,
            cantidad_stock=int(cantidad_stock) if cantidad_stock else 0,
            stock_minimo=int(stock_minimo),
            precio_unitario=float(precio_unitario) if precio_unitario else None
        )
        
        db.session.add(nuevo_material)
        db.session.commit()
        
        flash(f'Material {nombre} creado exitosamente.', 'success')
        return redirect(url_for('orders.list_materials'))
    
    return render_template('material_create.html')
    