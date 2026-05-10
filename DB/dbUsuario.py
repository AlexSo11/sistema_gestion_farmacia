from conexion import ConexionDB

class DBUsuario:
    def __init__(self, conexion):
        self.conexion = conexion

    def autenticar(self, username, password):
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Consulta simplificada y directa usando 'password'
                query = "SELECT id, username, nombre, apellido, email, rol FROM usuarios WHERE username = %s AND password = %s"
                cursor.execute(query, (username, password))
                
                usuario = cursor.fetchone()
                if usuario:
                    print(f"Login exitoso para usuario: {username}")
                    return True, {
                        'id': usuario[0],
                        'username': usuario[1],
                        'nombre': usuario[2],
                        'apellido': usuario[3],
                        'email': usuario[4],
                        'rol': usuario[5]
                    }
                else:
                    print(f"Login fallido - Usuario: {username}")
                    # Debug: Verificar si el usuario existe
                    cursor.execute("SELECT username, password FROM usuarios WHERE username = %s", (username,))
                    debug_user = cursor.fetchone()
                    if debug_user:
                        print(f"Usuario encontrado. Password en BD: '{debug_user[1]}', Password ingresado: '{password}'")
                    else:
                        print(f"Usuario '{username}' no existe en la base de datos")
                    return False, "Usuario o contraseña incorrectos"
                    
            except Exception as e:
                print(f"Error detallado en autenticación: {str(e)}")
                return False, f"Error en autenticación: {str(e)}"
            finally:
                conn.close()
        return False, "Error de conexión"

    def buscar_usuario_por_username(self, username):
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
                return cursor.fetchone() is not None
            except Exception as e:
                print(f"Error buscando usuario: {e}")
                return False
            finally:
                conn.close()
        return False

    def crear_usuario(self, username, password, nombre, apellido="", email="", telefono="", rol="cajero"):
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Verificar que email no exista
                if email:
                    cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
                    if cursor.fetchone():
                        return False, f"Ya existe un usuario con el email: {email}"
                
                # Verificar que teléfono no exista
                if telefono:
                    cursor.execute("SELECT id FROM usuarios WHERE telefono = %s", (telefono,))
                    if cursor.fetchone():
                        return False, f"Ya existe un usuario con el teléfono: {telefono}"
                
                cursor.execute("""
                    INSERT INTO usuarios (username, password, nombre, apellido, email, telefono, rol) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (username, password, nombre, apellido, email, telefono, rol))
                conn.commit()
                return True, "Usuario creado exitosamente"
            except Exception as e:
                return False, f"Error creando usuario: {str(e)}"
            finally:
                conn.close()
        return False, "Error de conexión"

    def obtener_usuarios(self):
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id, username, nombre, apellido, email, telefono, rol, fecha_creacion FROM usuarios ORDER BY id")
                return cursor.fetchall()
            except Exception as e:
                print(f"Error obteniendo usuarios: {e}")
                return []
            finally:
                conn.close()
        return []

    def actualizar_usuario(self, usuario_id, datos):
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Construir query dinámicamente
                set_clause = []
                params = []
                
                for key, value in datos.items():
                    if key == 'password' and value:  # Solo actualizar password si no está vacío
                        set_clause.append("password = %s")
                        params.append(value)
                    elif key != 'password':  # Para otros campos
                        set_clause.append(f"{key} = %s")
                        params.append(value)
                
                if not set_clause:
                    return False, "No hay datos para actualizar"
                
                query = f"UPDATE usuarios SET {', '.join(set_clause)} WHERE id = %s"
                params.append(usuario_id)
                
                cursor.execute(query, params)
                conn.commit()
                return True, "Usuario actualizado exitosamente"
            except Exception as e:
                return False, f"Error actualizando usuario: {str(e)}"
            finally:
                conn.close()
        return False, "Error de conexión"

    def eliminar_usuario(self, usuario_id):
        conn = self.conexion.obtener_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Eliminamos físicamente el usuario
                cursor.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
                
                # Luego reordenamos los IDs
                cursor.execute("SET @count = 0")
                cursor.execute("UPDATE usuarios SET id = @count:= @count + 1 ORDER BY id")
                cursor.execute("ALTER TABLE usuarios AUTO_INCREMENT = 1")
                
                conn.commit()
                return True, "Usuario eliminado y IDs reordenados exitosamente"
            except Exception as e:
                conn.rollback()
                return False, f"Error eliminando usuario: {str(e)}"
            finally:
                conn.close()
        return False, "Error de conexión"