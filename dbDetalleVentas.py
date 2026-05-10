from conexion import ConexionDB
from mysql.connector import Error

class DBDetaVenta:
    def __init__(self, conexion: ConexionDB):
        self. conexion = conexion