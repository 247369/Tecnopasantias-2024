"""
Algoritmo de optimización de corte usando First Fit Decreasing (FFD)
"""

def optimize_cutting(longitud_barra, piezas_requeridas, margen_corte=3):
    """
    Optimiza el corte de piezas en barras usando el algoritmo First Fit Decreasing
    
    Args:
        longitud_barra (float): Longitud de la barra disponible en mm
        piezas_requeridas (list): Lista de diccionarios con 'longitud' y 'cantidad'
                                  Ejemplo: [{"longitud": 1500, "cantidad": 10}, ...]
        margen_corte (float): Margen de corte en mm (desperdicio por corte)
    
    Returns:
        dict: Resultado de la optimización con patrón de corte y estadísticas
    """
    
    try:
        # Validar entrada
        if longitud_barra <= 0:
            return {
                'success': False,
                'message': 'La longitud de la barra debe ser mayor a 0'
            }
        
        # Expandir piezas según cantidad
        lista_piezas = []
        for pieza in piezas_requeridas:
            longitud = float(pieza.get('longitud', 0))
            cantidad = int(pieza.get('cantidad', 0))
            
            # Validar pieza
            if longitud <= 0 or cantidad <= 0:
                continue
            
            if longitud > longitud_barra:
                return {
                    'success': False,
                    'message': f'La pieza de {longitud}mm excede la longitud de la barra ({longitud_barra}mm)'
                }
            
            # Añadir cada pieza individualmente
            for _ in range(cantidad):
                lista_piezas.append(longitud)
        
        if not lista_piezas:
            return {
                'success': False,
                'message': 'No hay piezas válidas para optimizar'
            }
        
        # Ordenar piezas de mayor a menor (Decreasing en FFD)
        lista_piezas.sort(reverse=True)
        
        # Inicializar barras
        barras = []  # Lista de barras, cada una es un dict con 'piezas' y 'espacio_restante'
        
        # Algoritmo First Fit Decreasing
        for pieza in lista_piezas:
            colocada = False
            
            # Intentar colocar en una barra existente
            for barra in barras:
                espacio_necesario = pieza + margen_corte
                
                if barra['espacio_restante'] >= espacio_necesario:
                    barra['piezas'].append(pieza)
                    barra['espacio_restante'] -= espacio_necesario
                    colocada = True
                    break
            
            # Si no cabe en ninguna barra, crear nueva barra
            if not colocada:
                nueva_barra = {
                    'piezas': [pieza],
                    'espacio_restante': longitud_barra - pieza - margen_corte
                }
                barras.append(nueva_barra)
        
        # Calcular estadísticas
        total_piezas = len(lista_piezas)
        barras_utilizadas = len(barras)
        
        # Calcular desperdicio
        desperdicio_total = sum(barra['espacio_restante'] for barra in barras)
        material_total_usado = barras_utilizadas * longitud_barra
        material_util = sum(lista_piezas) + (total_piezas * margen_corte)
        desperdicio_porcentaje = (desperdicio_total / material_total_usado) * 100 if material_total_usado > 0 else 0
        
        # Preparar patrón de corte detallado
        patron_corte = []
        for i, barra in enumerate(barras, 1):
            patron_corte.append({
                'numero_barra': i,
                'piezas': barra['piezas'],
                'cantidad_piezas': len(barra['piezas']),
                'longitud_utilizada': sum(barra['piezas']) + (len(barra['piezas']) * margen_corte),
                'desperdicio': barra['espacio_restante']
            })
        
        # Calcular eficiencia
        eficiencia = 100 - desperdicio_porcentaje
        
        return {
            'success': True,
            'barras_utilizadas': barras_utilizadas,
            'total_piezas': total_piezas,
            'desperdicio_total': round(desperdicio_total, 2),
            'desperdicio_porcentaje': round(desperdicio_porcentaje, 2),
            'eficiencia': round(eficiencia, 2),
            'material_total': material_total_usado,
            'material_util': round(material_util, 2),
            'patron_corte': patron_corte,
            'longitud_barra': longitud_barra,
            'margen_corte': margen_corte
        }
    
    except Exception as e:
        return {
            'success': False,
            'message': f'Error en la optimización: {str(e)}'
        }


def calcular_costo_desperdicio(desperdicio_mm, precio_por_mm):
    """
    Calcula el costo del material desperdiciado
    
    Args:
        desperdicio_mm (float): Desperdicio total en mm
        precio_por_mm (float): Precio por milímetro del material
    
    Returns:
        float: Costo del desperdicio
    """
    return desperdicio_mm * precio_por_mm