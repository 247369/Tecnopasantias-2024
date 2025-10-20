from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.order import Order
from models.material import Material
from utils.optimizer import optimize_cutting
import json

optimizer_bp = Blueprint('optimizer', __name__)

@optimizer_bp.route('/')
@login_required
def index():
    """Página principal del optimizador"""
    materiales = Material.query.filter_by(activo=True).all()
    return render_template('optimizer.html', materiales=materiales)


@optimizer_bp.route('/calculate', methods=['POST'])
@login_required
def calculate():
    """Calcular optimización de corte"""
    
    try:
        # Obtener datos del formulario
        material_id = request.form.get('material_id')
        piezas_json = request.form.get('piezas')  # JSON string
        
        if not material_id or not piezas_json:
            return jsonify({
                'success': False,
                'message': 'Faltan datos obligatorios'
            }), 400
        
        # Obtener material
        material = Material.query.get(material_id)
        if not material:
            return jsonify({
                'success': False,
                'message': 'Material no encontrado'
            }), 404
        
        # Parsear piezas requeridas
        try:
            piezas = json.loads(piezas_json)
        except:
            return jsonify({
                'success': False,
                'message': 'Formato de piezas inválido'
            }), 400
        
        # Validar piezas
        if not piezas or not isinstance(piezas, list):
            return jsonify({
                'success': False,
                'message': 'Debe especificar al menos una pieza'
            }), 400
        
        # Optimizar corte
        resultado = optimize_cutting(
            longitud_barra=material.longitud_disponible,
            piezas_requeridas=piezas
        )
        
        if not resultado['success']:
            return jsonify(resultado), 400
        
        return jsonify(resultado)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al calcular: {str(e)}'
        }), 500


@optimizer_bp.route('/save', methods=['POST'])
@login_required
def save_optimization():
    """Guardar resultado de optimización en un pedido"""
    
    if not current_user.es_admin():
        return jsonify({
            'success': False,
            'message': 'No tienes permisos para guardar optimizaciones'
        }), 403
    
    try:
        order_id = request.form.get('order_id')
        piezas_json = request.form.get('piezas')
        patron_json = request.form.get('patron')
        barras_utilizadas = request.form.get('barras_utilizadas')
        desperdicio_total = request.form.get('desperdicio_total')
        desperdicio_porcentaje = request.form.get('desperdicio_porcentaje')
        
        # Obtener pedido
        pedido = Order.query.get(order_id)
        if not pedido:
            return jsonify({
                'success': False,
                'message': 'Pedido no encontrado'
            }), 404
        
        # Actualizar pedido con resultados de optimización
        pedido.piezas_requeridas = piezas_json
        pedido.patron_corte = patron_json
        pedido.barras_utilizadas = int(barras_utilizadas)
        pedido.desperdicio_total = float(desperdicio_total)
        pedido.desperdicio_porcentaje = float(desperdicio_porcentaje)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Optimización guardada correctamente'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al guardar: {str(e)}'
        }), 500