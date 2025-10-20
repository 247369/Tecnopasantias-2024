from flask_mail import Message
from app import mail
from flask import render_template

def enviar_notificacion_pedido(destinatario, pedido, tipo='creado'):
    """
    Envía notificación por email sobre un pedido
    
    Args:
        destinatario (str): Email del destinatario
        pedido (Order): Objeto pedido
        tipo (str): Tipo de notificación ('creado', 'asignado', 'completado')
    """
    
    asuntos = {
        'creado': f'Nuevo Pedido Creado: {pedido.numero_pedido}',
        'asignado': f'Pedido Asignado: {pedido.numero_pedido}',
        'completado': f'Pedido Completado: {pedido.numero_pedido}'
    }
    
    try:
        msg = Message(
            subject=asuntos.get(tipo, 'Notificación de Pedido'),
            recipients=[destinatario]
        )
        
        # Puedes crear templates HTML para los emails
        msg.body = f"""
        Hola,
        
        El pedido {pedido.numero_pedido} ha sido {tipo}.
        
        Cliente: {pedido.cliente or 'N/A'}
        Estado: {pedido.estado}
        Prioridad: {pedido.prioridad}
        
        Por favor revisa el sistema PLECORMET para más detalles.
        
        Saludos,
        Sistema PLECORMET
        """
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error al enviar email: {str(e)}")
        return False