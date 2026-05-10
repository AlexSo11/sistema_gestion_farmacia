from conexion import ConexionDB
import datetime

class DBCompras:
    def __init__(self, conexion):
        self.conexion = conexion

    def generar_folio_automatico(self):
        """Genera un folio automático en formato COMP-YYYYMMDD-001"""
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                fecha_actual = datetime.datetime.now().strftime('%Y%m%d')
                
                # Buscar el último folio del día
                cursor.execute("""
                    SELECT folio FROM compras 
                    WHERE folio LIKE %s 
                    ORDER BY id DESC LIMIT 1
                """, (f'COMP-{fecha_actual}-%',))
                
                ultimo_folio = cursor.fetchone()
                
                if ultimo_folio:
                    # Extraer el número consecutivo y incrementarlo
                    ultimo_numero = int(ultimo_folio[0].split('-')[-1])
                    nuevo_numero = ultimo_numero + 1
                else:
                    # Primer folio del día
                    nuevo_numero = 1
                
                folio = f"COMP-{fecha_actual}-{nuevo_numero:03d}"
                return folio
                
            except Exception as e:
                print(f"Error generando folio automático: {e}")
                # Folio de respaldo
                return f"COMP-{fecha_actual}-001"
            finally:
                conn.close()
        return "COMP-ERROR"

    def obtener_compras(self):
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT c.id, c.folio, c.total, c.fecha, c.estado
                    FROM compras c 
                    ORDER BY c.fecha DESC, c.id DESC
                """)
                return cursor.fetchall()
            except Exception as e:
                print(f"Error obteniendo compras: {e}")
                return []
            finally:
                conn.close()
        return []

    def crear_compra(self, datos_compra):
        """
        Crea una nueva compra en la base de datos
        datos_compra: dict con keys: fecha, total, usuario_id
        """
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Generar folio automático
                folio = self.generar_folio_automatico()
                
                # Insertar compra principal
                cursor.execute("""
                    INSERT INTO compras (folio, fecha, total, usuario_id, estado) 
                    VALUES (%s, %s, %s, %s, %s, 'ACTIVA')
                """, (
                    folio,
                    datos_compra['fecha'],
                    datos_compra['total'],
                    datos_compra['usuario_id']
                ))
                
                compra_id = cursor.lastrowid
                conn.commit()
                return compra_id, folio  # Retornar tanto ID como folio
                
            except Exception as e:
                conn.rollback()
                print(f"Error creando compra: {e}")
                return None, None
            finally:
                conn.close()
        return None, None

    def crear_detalle_compra(self, datos_detalle):
        """
        Crea un detalle de compra
        datos_detalle: dict con keys: compra_id, articulo_id, articulo_codigo, cantidad, precio_unitario, subtotal
        """
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO detalle_compras 
                    (compra_id, articulo_id, articulo_codigo, cantidad, precio_unitario, subtotal) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    datos_detalle['compra_id'],
                    datos_detalle['articulo_id'],
                    datos_detalle['articulo_codigo'],
                    datos_detalle['cantidad'],
                    datos_detalle['precio_unitario'],
                    datos_detalle['subtotal']
                ))
                
                conn.commit()
                return True
                
            except Exception as e:
                conn.rollback()
                print(f"Error creando detalle compra: {e}")
                return False
            finally:
                conn.close()
        return False

    def obtener_detalles_compra(self, compra_id):
        """Obtiene los detalles de una compra específica"""
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT dc.id, dc.articulo_codigo, a.nombre, dc.cantidad, 
                           dc.precio_unitario, dc.subtotal
                    FROM detalle_compras dc
                    LEFT JOIN articulos a ON dc.articulo_id = a.id
                    WHERE dc.compra_id = %s
                """, (compra_id,))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error obteniendo detalles compra: {e}")
                return []
            finally:
                conn.close()
        return []

    def eliminar_compra(self, compra_id):
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Primero obtener los detalles para revertir el stock
                cursor.execute("""
                    SELECT articulo_id, cantidad 
                    FROM detalle_compras 
                    WHERE compra_id = %s
                """, (compra_id,))
                detalles = cursor.fetchall()
                
                # Revertir stock de cada artículo
                for detalle in detalles:
                    articulo_id, cantidad = detalle
                    cursor.execute("""
                        UPDATE articulos 
                        SET stock = stock - %s 
                        WHERE id = %s AND stock >= %s
                    """, (cantidad, articulo_id, cantidad))
                
                # Eliminar detalles de la compra
                cursor.execute("DELETE FROM detalle_compras WHERE compra_id = %s", (compra_id,))
                
                # Eliminar la compra principal
                cursor.execute("DELETE FROM compras WHERE id = %s", (compra_id,))
                
                conn.commit()
                return True, "Compra eliminada exitosamente"
                
            except Exception as e:
                conn.rollback()
                return False, f"Error eliminando compra: {str(e)}"
            finally:
                conn.close()
        return False, "Error de conexión"

    def obtener_compra_por_id(self, compra_id):
        """Obtener una compra específica por ID"""
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, folio, total, fecha, estado, usuario_id
                    FROM compras 
                    WHERE id = %s
                """, (compra_id,))
                return cursor.fetchone()
            except Exception as e:
                print(f"Error obteniendo compra: {e}")
                return None
            finally:
                conn.close()
        return None

    def verificar_folio_existente(self, folio):
        """Verifica si un folio ya existe en la base de datos"""
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM compras WHERE folio = %s", (folio,))
                return cursor.fetchone() is not None
            except Exception as e:
                print(f"Error verificando folio: {e}")
                return True  # Por seguridad, asumir que existe si hay error
            finally:
                conn.close()
        return True

    def obtener_compras_por_fecha(self, fecha_inicio, fecha_fin):
        """Obtiene compras dentro de un rango de fechas"""
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT c.id, c.folio, c.total, c.fecha, c.estado,
                           u.nombre as usuario_nombre
                    FROM compras c 
                    LEFT JOIN usuarios u ON c.usuario_id = u.id
                    WHERE c.fecha BETWEEN %s AND %s
                    ORDER BY c.fecha DESC, c.id DESC
                """, (fecha_inicio, fecha_fin))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error obteniendo compras por fecha: {e}")
                return []
            finally:
                conn.close()
        return []

    def obtener_total_compras(self):
        """Obtiene el total de compras registradas"""
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) as total FROM compras WHERE estado = 'ACTIVA'")
                result = cursor.fetchone()
                return result[0] if result else 0
            except Exception as e:
                print(f"Error obteniendo total compras: {e}")
                return 0
            finally:
                conn.close()
        return 0