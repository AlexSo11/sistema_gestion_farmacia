from conexion import ConexionDB

class DBVentas:
    def __init__(self, conexion):
        self.conexion = conexion

    def obtener_ventas(self):
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT v.id, CONCAT(c.nombre, ' ', c.apellido), v.total, v.puntos_ganados, v.fecha_venta, v.estado 
                    FROM ventas v 
                    JOIN clientes c ON v.cliente_id = c.id 
                    ORDER BY v.id DESC
                """)
                return cursor.fetchall()
            except Exception as e:
                print(f"Error obteniendo ventas: {e}")
                return []
            finally:
                conn.close()
        return []

    def obtener_detalles_venta(self, venta_id):
        """Obtener los detalles de una venta específica CON CÓDIGO"""
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT articulo_codigo, articulo_nombre, cantidad, precio_unitario, subtotal, es_promocion
                    FROM detalle_ventas 
                    WHERE venta_id = %s
                    ORDER BY id
                """, (venta_id,))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error obteniendo detalles de venta: {e}")
                return []
            finally:
                conn.close()
        return []

    def crear_venta(self, datos):
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Obtener nombre del cliente
                cursor.execute("SELECT nombre, apellido FROM clientes WHERE id = %s", (datos['cliente_id'],))
                cliente = cursor.fetchone()
                cliente_nombre = f"{cliente[0]} {cliente[1]}" if cliente else "Cliente Desconocido"
                
                cursor.execute("""
                    INSERT INTO ventas (cliente_id, cliente_nombre, total, puntos_ganados, fecha_venta, usuario_id) 
                    VALUES (%s, %s, %s, %s, CURDATE(), %s)
                """, (datos['cliente_id'], cliente_nombre, datos['total'], datos.get('puntos_ganados', 0), datos['usuario_id']))
                
                venta_id = cursor.lastrowid
                conn.commit()
                return venta_id
            except Exception as e:
                conn.rollback()
                print(f"Error creando venta: {e}")
                return None
            finally:
                conn.close()
        return None

    def crear_detalle_venta(self, datos):
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Obtener nombre del artículo si no viene
                if not datos.get('articulo_nombre'):
                    cursor.execute("SELECT nombre, codigo FROM articulos WHERE id = %s", (datos['articulo_id'],))
                    articulo = cursor.fetchone()
                    articulo_nombre = articulo[0] if articulo else "Artículo Desconocido"
                    articulo_codigo = articulo[1] if articulo else "N/A"
                else:
                    articulo_nombre = datos['articulo_nombre']
                    articulo_codigo = datos.get('articulo_codigo', 'N/A')
                
                cursor.execute("""
                    INSERT INTO detalle_ventas (venta_id, articulo_id, articulo_codigo, articulo_nombre, cantidad, precio_unitario, subtotal, es_promocion) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (datos['venta_id'], datos['articulo_id'], articulo_codigo, articulo_nombre, 
                      datos['cantidad'], datos['precio_unitario'], datos['subtotal'], 
                      datos.get('es_promocion', False)))
                
                conn.commit()
                return True
            except Exception as e:
                conn.rollback()
                print(f"Error creando detalle venta: {e}")
                return False
            finally:
                conn.close()
        return False

    def eliminar_venta(self, venta_id):
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Obtener info de la venta para revertir puntos
                cursor.execute("SELECT cliente_id, puntos_ganados FROM ventas WHERE id = %s", (venta_id,))
                venta_info = cursor.fetchone()
                
                # Obtener detalles para revertir el stock
                cursor.execute("SELECT articulo_id, cantidad, es_promocion FROM detalle_ventas WHERE venta_id = %s", (venta_id,))
                detalles = cursor.fetchall()
                
                # Revertir el stock de cada artículo (excepto promociones)
                for detalle in detalles:
                    if not detalle[2]:  # No es promoción
                        cursor.execute("UPDATE articulos SET stock = stock + %s WHERE id = %s", (detalle[1], detalle[0]))
                
                # Revertir puntos del cliente
                if venta_info:
                    cursor.execute("UPDATE clientes SET puntos = puntos - %s WHERE id = %s", 
                                 (venta_info[1], venta_info[0]))
                    
                    # Si había promoción, devolver los 50 puntos
                    tiene_promocion = any(d[2] for d in detalles)
                    if tiene_promocion:
                        cursor.execute("UPDATE clientes SET puntos = puntos + 50 WHERE id = %s", 
                                     (venta_info[0],))
                
                # Eliminamos los detalles primero (por la clave foránea)
                cursor.execute("DELETE FROM detalle_ventas WHERE venta_id = %s", (venta_id,))
                
                # Luego eliminamos la venta
                cursor.execute("DELETE FROM ventas WHERE id = %s", (venta_id,))
                
                # Reordenamos los IDs de ventas
                cursor.execute("SET @count = 0")
                cursor.execute("UPDATE ventas SET id = @count:= @count + 1 ORDER BY id")
                cursor.execute("ALTER TABLE ventas AUTO_INCREMENT = 1")
                
                # Reordenamos los IDs de detalle_ventas
                cursor.execute("SET @count = 0")
                cursor.execute("UPDATE detalle_ventas SET id = @count:= @count + 1 ORDER BY id")
                cursor.execute("ALTER TABLE detalle_ventas AUTO_INCREMENT = 1")
                
                conn.commit()
                return True, "Venta eliminada y IDs reordenados exitosamente"
            except Exception as e:
                conn.rollback()
                return False, f"Error eliminando venta: {str(e)}"
            finally:
                conn.close()
        return False, "Error de conexión"