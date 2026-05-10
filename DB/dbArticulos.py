from conexion import ConexionDB

class DBArticulos:
    def __init__(self, conexion):
        self.conexion = conexion

    def obtener_articulos(self):
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id, codigo, nombre, descripcion, precio, stock, categoria, es_promocion FROM articulos ORDER BY id")
                return cursor.fetchall()
            except Exception as e:
                print(f"Error obteniendo artículos: {e}")
                return []
            finally:
                conn.close()
        return []

    def obtener_articulo(self, articulo_id):
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id, codigo, nombre, descripcion, precio, stock, categoria, es_promocion FROM articulos WHERE id = %s", (articulo_id,))
                return cursor.fetchone()
            except Exception as e:
                print(f"Error obteniendo artículo: {e}")
                return None
            finally:
                conn.close()
        return None
    
    def obtener_articulos_promocion(self):
        """Obtener solo artículos en promoción"""
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id, codigo, nombre, descripcion, precio, stock, categoria FROM articulos WHERE es_promocion = 1 ORDER BY nombre")
                return cursor.fetchall()
            except Exception as e:
                print(f"Error obteniendo artículos en promoción: {e}")
                return []
            finally:
                conn.close()
        return []

    def crear_articulo(self, datos):
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO articulos (codigo, nombre, descripcion, precio, stock, categoria, es_promocion) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (datos['codigo'], datos['nombre'], datos['descripcion'], datos['precio'], 
                      datos['stock'], datos['categoria'], datos.get('es_promocion', 0)))
                conn.commit()
                return True, "Artículo creado exitosamente"
            except Exception as e:
                return False, f"Error creando artículo: {str(e)}"
            finally:
                conn.close()
        return False, "Error de conexión"

    def actualizar_articulo(self, articulo_id, datos):
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE articulos 
                    SET codigo = %s, nombre = %s, descripcion = %s, precio = %s, stock = %s, categoria = %s, es_promocion = %s
                    WHERE id = %s
                """, (datos['codigo'], datos['nombre'], datos['descripcion'], datos['precio'], 
                      datos['stock'], datos['categoria'], datos.get('es_promocion', 0), articulo_id))
                conn.commit()
                return True, "Artículo actualizado exitosamente"
            except Exception as e:
                return False, f"Error actualizando artículo: {str(e)}"
            finally:
                conn.close()
        return False, "Error de conexión"

    def eliminar_articulo(self, articulo_id):
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Eliminamos físicamente el artículo
                cursor.execute("DELETE FROM articulos WHERE id = %s", (articulo_id,))
                
                # Reordenamos los IDs
                cursor.execute("SET @count = 0")
                cursor.execute("UPDATE articulos SET id = @count:= @count + 1 ORDER BY id")
                cursor.execute("ALTER TABLE articulos AUTO_INCREMENT = 1")
                
                conn.commit()
                return True, "Artículo eliminado y IDs reordenados exitosamente"
            except Exception as e:
                conn.rollback()
                return False, f"Error eliminando artículo: {str(e)}"
            finally:
                conn.close()
        return False, "Error de conexión"

    def actualizar_stock(self, articulo_id, cantidad):
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("UPDATE articulos SET stock = stock + %s WHERE id = %s", (cantidad, articulo_id))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error actualizando stock: {e}")
                return False
            finally:
                conn.close()
        return False