from conexion import ConexionDB

class DBClientes:
    def __init__(self, conexion):
        self.conexion = conexion

    def obtener_clientes(self):
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT c.id, c.rfc, c.nombre, c.apellido, c.email, c.telefono, c.direccion, c.puntos, u.username
                    FROM clientes c
                    LEFT JOIN usuarios u ON c.usuario_id = u.id
                    ORDER BY c.id
                """)
                return cursor.fetchall()
            except Exception as e:
                print(f"Error obteniendo clientes: {e}")
                return []
            finally:
                conn.close()
        return []

    def obtener_cliente(self, cliente_id):
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT c.id, c.rfc, c.nombre, c.apellido, c.email, c.telefono, c.direccion, c.puntos, u.username
                    FROM clientes c
                    LEFT JOIN usuarios u ON c.usuario_id = u.id
                    WHERE c.id = %s
                """, (cliente_id,))
                return cursor.fetchone()
            except Exception as e:
                print(f"Error obteniendo cliente: {e}")
                return None
            finally:
                conn.close()
        return None

    def crear_cliente(self, datos):
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Verificar que el RFC no exista
                cursor.execute("SELECT id FROM clientes WHERE rfc = %s", (datos['rfc'],))
                if cursor.fetchone():
                    return False, f"Ya existe un cliente con el RFC: {datos['rfc']}"
                
                cursor.execute("""
                    INSERT INTO clientes (rfc, nombre, apellido, email, telefono, direccion, puntos, usuario_id) 
                    VALUES (%s, %s, %s, %s, %s, %s, 0, %s)
                """, (datos['rfc'], datos['nombre'], datos['apellido'], datos['email'], 
                      datos['telefono'], datos['direccion'], datos['usuario_id']))
                conn.commit()
                return True, "Cliente creado exitosamente"
            except Exception as e:
                return False, f"Error creando cliente: {str(e)}"
            finally:
                conn.close()
        return False, "Error de conexión"

    def actualizar_cliente(self, cliente_id, datos):
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Verificar que el RFC no exista en otro cliente
                cursor.execute("SELECT id FROM clientes WHERE rfc = %s AND id != %s", (datos['rfc'], cliente_id))
                if cursor.fetchone():
                    return False, f"Ya existe otro cliente con el RFC: {datos['rfc']}"
                
                cursor.execute("""
                    UPDATE clientes 
                    SET rfc = %s, nombre = %s, apellido = %s, email = %s, telefono = %s, direccion = %s 
                    WHERE id = %s
                """, (datos['rfc'], datos['nombre'], datos['apellido'], datos['email'], 
                      datos['telefono'], datos['direccion'], cliente_id))
                conn.commit()
                return True, "Cliente actualizado exitosamente"
            except Exception as e:
                return False, f"Error actualizando cliente: {str(e)}"
            finally:
                conn.close()
        return False, "Error de conexión"

    def eliminar_cliente(self, cliente_id):
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Eliminamos físicamente el cliente
                cursor.execute("DELETE FROM clientes WHERE id = %s", (cliente_id,))
                
                # Reordenamos los IDs
                cursor.execute("SET @count = 0")
                cursor.execute("UPDATE clientes SET id = @count:= @count + 1 ORDER BY id")
                cursor.execute("ALTER TABLE clientes AUTO_INCREMENT = 1")
                
                conn.commit()
                return True, "Cliente eliminado y IDs reordenados exitosamente"
            except Exception as e:
                conn.rollback()
                return False, f"Error eliminando cliente: {str(e)}"
            finally:
                conn.close()
        return False, "Error de conexión"

    def actualizar_puntos(self, cliente_id, puntos):
        """Actualizar los puntos de un cliente"""
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("UPDATE clientes SET puntos = puntos + %s WHERE id = %s", (puntos, cliente_id))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error actualizando puntos: {e}")
                return False
            finally:
                conn.close()
        return False
    
    def canjear_puntos(self, cliente_id, puntos_a_descontar):
        """Descontar puntos cuando se canjean"""
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("UPDATE clientes SET puntos = puntos - %s WHERE id = %s", (puntos_a_descontar, cliente_id))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error canjeando puntos: {e}")
                return False
            finally:
                conn.close()
        return False