"""
⠀⠀⠀⠀⠀⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢰⣿⡿⠗⠀⠠⠄⡀⠀⠀⠀⠀
⠀⠀⠀⠀⡜⠁⠀⠀⠀⠀⠀⠈⠑⢶⣶⡄
⢀⣶⣦⣸⠀⢼⣟⡇⠀⠀⢀⣀⠀⠘⡿⠃
⠀⢿⣿⣿⣄⠒⠀⠠⢶⡂⢫⣿⢇⢀⠃⠀
⠀⠈⠻⣿⣿⣿⣶⣤⣀⣀⣀⣂⡠⠊⠀⠀
⠀⠀⠀⠃⠀⠀⠉⠙⠛⠿⣿⣿⣧⠀⠀⠀
⠀⠀⠘⡀⠀⠀⠀⠀⠀⠀⠘⣿⣿⡇⠀⠀
⠀⠀⠀⣷⣄⡀⠀⠀⠀⢀⣴⡟⠿⠃⠀⠀
⠀⠀⠀⢻⣿⣿⠉⠉⢹⣿⣿⠁⠀⠀⠀⠀
⠀⠀⠀⠀⠉⠁⠀⠀⠀⠉⠁

Desarrollo AlexWhite USER GIT AlexSo11
"""
import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
import platform
import os

from conexion import ConexionDB
from usuarios import UsuariosUI
from dbUsuario import DBUsuario
from clientes import ClientesUI
from ventas import VentasUI
from detalle_venta import DetaVentaUI
from articulos import ArticulosUI
from almacen import AlmacenUI
from compras import ComprasUI

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Configurar fuentes según sistema operativo
if platform.system() == "Windows":
    FONT_FAMILY = "Segoe UI"
elif platform.system() == "Darwin":  # macOS
    FONT_FAMILY = "SF Pro Display"
else:  # Linux
    FONT_FAMILY = "Sans"

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'farmacia_qci'
}

class App: 
    def __init__(self, root):
        self.root = root
        self.root.title("Farmacia QCI - Login")
        self.root.geometry("450x500")
        self.root.resizable(False, False)
        
        # Centrar ventana
        self.center_window(450, 500)

        self.con = ConexionDB(**DB_CONFIG)
        self.db = DBUsuario(self.con)
        self.usuario_actual = None
        self.build_login()
    
    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def build_login(self):
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Configurar geometría para login
        self.root.geometry("450x500")
        self.root.resizable(True, True)
        self.center_window(450, 500)
        
        # Frame principal
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Logo/Título
        title_frame = ctk.CTkFrame(main_frame, fg_color="#346081", corner_radius=15)
        title_frame.pack(fill='x', pady=(0, 30))
        
        ctk.CTkLabel(
            title_frame, 
            text="🏥 Farmacia QCI", 
            font=(FONT_FAMILY, 32, "bold"),
            text_color="white"
        ).pack(pady=20)
        
        ctk.CTkLabel(
            title_frame, 
            text="Sistema de Gestión", 
            font=(FONT_FAMILY, 14),
            text_color="white"
        ).pack(pady=(0, 15))
        
        # Frame de formulario
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.pack(fill='both', expand=True, pady=10)
        
        # Usuario
        ctk.CTkLabel(
            form_frame, 
            text="Usuario:", 
            font=("Arial", 14, "bold")
        ).pack(anchor='w', padx=20, pady=(30, 5))
        
        self.entry_user = ctk.CTkEntry(
            form_frame, 
            width=330, 
            height=45,
            font=("Arial", 13),
            placeholder_text="Ingrese su usuario"
        )
        self.entry_user.pack(padx=20, pady=(0, 15))
        
        # Contraseña
        ctk.CTkLabel(
            form_frame, 
            text="Contraseña:", 
            font=("Arial", 14, "bold")
        ).pack(anchor='w', padx=20, pady=(10, 5))
        
        self.entry_pass = ctk.CTkEntry(
            form_frame, 
            show="●", 
            width=330, 
            height=45,
            font=("Arial", 13),
            placeholder_text="Ingrese su contraseña"
        )
        self.entry_pass.pack(padx=20, pady=(0, 25))
        
        # Botón de login
        ctk.CTkButton(
            form_frame, 
            text="Iniciar Sesión", 
            command=self.login, 
            width=330, 
            height=45,
            font=("Arial", 15, "bold"),
            fg_color="#30658d",
            hover_color="#204563"
        ).pack(padx=20, pady=(10, 30))
        
        # Enter para login
        self.entry_pass.bind('<Return>', lambda e: self.login())
        self.entry_user.bind('<Return>', lambda e: self.entry_pass.focus())
    
    def login(self):
        u = self.entry_user.get().strip()
        p = self.entry_pass.get().strip()
        if not u or not p:
            messagebox.showwarning("Validación", "Introduce usuario y contraseña.")
            return
        ok, resp = self.db.autenticar(u, p)
        if ok:
            self.usuario_actual = resp
            self.build_menu()
        else:
            messagebox.showerror("Error", resp)
    
    def build_menu(self):
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()

        # Configurar ventana para menú principal
        self.root.geometry("1400x850")
        self.root.resizable(True, True)
        self.center_window(1400, 850)

        # Menú superior
        menubar = tk.Menu(self.root, bg="#2b2b2b", fg="white", activebackground="#3c4242")
        self.root.config(menu=menubar)
        
        menu_archivo = tk.Menu(menubar, tearoff=0, bg="#5a5a5a", fg="white")
        menubar.add_cascade(label="Archivo", menu=menu_archivo)
        menu_archivo.add_command(label="Cerrar sesión", command=self.cerrar_sesion)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.root.quit)

        # Frame principal con sidebar
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.pack(fill='both', expand=True)

        # Sidebar
        sidebar = ctk.CTkFrame(main_container, width=250, corner_radius=0, fg_color="#585B66")
        sidebar.pack(side='left', fill='y', padx=0, pady=0)
        sidebar.pack_propagate(False)
        
        # Info usuario en sidebar
        user_info_frame = ctk.CTkFrame(sidebar, fg_color="#484B53", corner_radius=10)
        user_info_frame.pack(fill='x', padx=10, pady=20)
        
        ctk.CTkLabel(
            user_info_frame, 
            text="👤", 
            font=("Arial", 40)
        ).pack(pady=(15, 5))
        
        ctk.CTkLabel(
            user_info_frame, 
            text=self.usuario_actual.get('nombre'), 
            font=("Arial", 16, "bold")
        ).pack(pady=5)
        
        ctk.CTkLabel(
            user_info_frame, 
            text=f"Rol: {self.usuario_actual.get('rol').title()}", 
            font=("Arial", 12),
            text_color="#000000"
        ).pack(pady=(0, 15))

        # Contenedor de pestañas
        content_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        content_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        # Crear CTkTabview en lugar de ttk.Notebook
        self.tabview = ctk.CTkTabview(content_frame, corner_radius=10)
        self.tabview.pack(fill='both', expand=True)

        # Asignar pestañas según rol
        if self.usuario_actual.get('rol') == 'admin':
            tab_usuarios = self.tabview.add("👥 Usuarios")
            UsuariosUI(tab_usuarios, self.usuario_actual)
        
        if self.usuario_actual.get('rol') in ['admin', 'gerente', 'cajero']:
            tab_clientes = self.tabview.add("👥 Clientes")
            ClientesUI(tab_clientes, self.usuario_actual)

        if self.usuario_actual.get('rol') in ['admin', 'gerente', 'cajero']:
            tab_ventas = self.tabview.add("💰 Ventas")
            VentasUI(tab_ventas, self.usuario_actual)

        if self.usuario_actual.get('rol') in ['admin', 'gerente']:
            tab_detalle_ventas = self.tabview.add("📋 Detalle Ventas")
            DetaVentaUI(tab_detalle_ventas, self.usuario_actual)
        
        if self.usuario_actual.get('rol') in ['admin', 'gerente', 'cajero']:
            tab_articulos = self.tabview.add("💊 Artículos")
            ArticulosUI(tab_articulos, self.usuario_actual)
        
        if self.usuario_actual.get('rol') in ['admin', 'gerente']:
            tab_almacen = self.tabview.add("📦 Almacén")
            AlmacenUI(tab_almacen, self.usuario_actual)
        
        if self.usuario_actual.get('rol') in ['admin', 'gerente']:
            tab_compras = self.tabview.add("🛒 Compras")
            ComprasUI(tab_compras, self.usuario_actual)

    def cerrar_sesion(self):
        self.usuario_actual = None
        self.build_login()
    
def main():
    root = ctk.CTk()
    app = App(root)
    root.mainloop()
    
if __name__ == "__main__":
    main()
