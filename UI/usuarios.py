import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox, simpledialog
from DB.dbUsuario import DBUsuario
from conexion import ConexionDB

class UsuariosUI:
    def __init__(self, parent, usuario_actual=None):
        self.parent = parent
        self.usuario_actual = usuario_actual
        self.con = ConexionDB()
        self.db = DBUsuario(self.con)
        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Verificar permisos - solo admin puede gestionar usuarios
        if not usuario_actual or usuario_actual.get('rol') != 'admin':
            ctk.CTkLabel(self.frame, text="Acceso denegado: Solo administradores pueden gestionar usuarios",
                font=("Courier New", 14), text_color='red').pack(expand=True)
            return

        self.var_id = ctk.StringVar()
        self.var_username = ctk.StringVar()
        self.var_password = ctk.StringVar()
        self.var_nombre = ctk.StringVar()
        self.var_apellido = ctk.StringVar()
        self.var_email = ctk.StringVar()
        self.var_telefono = ctk.StringVar()
        self.var_rfc = ctk.StringVar()
        self.var_rol = ctk.StringVar(value="cajero")

        self.build_ui()
        self.configurar_estilo_treeview()
        self.cargar_usuarios()
        self.set_estado("inicio")

    def configurar_estilo_treeview(self):
        """Configurar estilo oscuro para Treeview"""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("Treeview",
            background="#2b2b2b",
            foreground="white",
            fieldbackground="#2b2b2b",
            borderwidth=0,
            rowheight=30,
            font=('Sans', 11)
        )
        
        style.configure("Treeview.Heading",
            background="#1f1f1f",
            foreground="white",
            borderwidth=1,
            relief="flat",
            font=('Sans', 12, 'bold')
        )
        
        style.map('Treeview',
            background=[('selected', '#1f6aa5')],
            foreground=[('selected', 'white')]
        )

    def build_ui(self):
        main_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        main_frame.pack(fill='both', expand=True)

        # Formulario
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.pack(fill='x', padx=10, pady=10)

        # Título
        title_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        title_container.pack(fill='x', padx=15, pady=(15, 10))
        
        ctk.CTkLabel(
            title_container, 
            text="👥 Gestión de Usuarios", 
            font=("Sans", 20, "bold")
        ).pack(side='left')

        # Campos del formulario
        fields_frame = ctk.CTkFrame(form_frame)
        fields_frame.pack(fill='x', padx=15, pady=10)

        # Fila 1: Username y RFC
        ctk.CTkLabel(fields_frame, text="Username:", font=("Sans", 12, "bold")).grid(
            row=0, column=0, sticky='w', padx=(10, 5), pady=8
        )
        self.entry_username = ctk.CTkEntry(fields_frame, textvariable=self.var_username, width=240, height=35)
        self.entry_username.grid(row=0, column=1, padx=5, pady=8)

        ctk.CTkLabel(fields_frame, text="🆔 RFC:", font=("Sans", 12, "bold")).grid(
            row=0, column=2, sticky='w', padx=(15, 5), pady=8
        )
        self.entry_rfc = ctk.CTkEntry(
            fields_frame, 
            textvariable=self.var_rfc, 
            width=240, 
            height=35,
            placeholder_text="XAXX010101XXX"
        )
        self.entry_rfc.grid(row=0, column=3, padx=5, pady=8)

        # Fila 2: Nombre y Apellido
        ctk.CTkLabel(fields_frame, text="Nombre:", font=("Sans", 12, "bold")).grid(
            row=1, column=0, sticky='w', padx=(10, 5), pady=8
        )
        self.entry_nombre = ctk.CTkEntry(fields_frame, textvariable=self.var_nombre, width=240, height=35)
        self.entry_nombre.grid(row=1, column=1, padx=5, pady=8)

        ctk.CTkLabel(fields_frame, text="Apellido:", font=("Sans", 12, "bold")).grid(
            row=1, column=2, sticky='w', padx=(15, 5), pady=8
        )
        self.entry_apellido = ctk.CTkEntry(fields_frame, textvariable=self.var_apellido, width=240, height=35)
        self.entry_apellido.grid(row=1, column=3, padx=5, pady=8)

        # Fila 3: Email y Teléfono
        ctk.CTkLabel(fields_frame, text="📧 Email:", font=("Sans", 12, "bold")).grid(
            row=2, column=0, sticky='w', padx=(10, 5), pady=8
        )
        self.entry_email = ctk.CTkEntry(fields_frame, textvariable=self.var_email, width=240, height=35)
        self.entry_email.grid(row=2, column=1, padx=5, pady=8)

        ctk.CTkLabel(fields_frame, text="📞 Teléfono:", font=("Sans", 12, "bold")).grid(
            row=2, column=2, sticky='w', padx=(15, 5), pady=8
        )
        self.entry_telefono = ctk.CTkEntry(fields_frame, textvariable=self.var_telefono, width=240, height=35)
        self.entry_telefono.grid(row=2, column=3, padx=5, pady=8)

        # Fila 4: Password y Rol
        ctk.CTkLabel(fields_frame, text="Password:", font=("Sans", 12, "bold")).grid(
            row=3, column=0, sticky='w', padx=(10, 5), pady=8
        )
        self.entry_password = ctk.CTkEntry(
            fields_frame, 
            textvariable=self.var_password, 
            show="*", 
            width=240, 
            height=35,
            placeholder_text="Dejar vacío para no cambiar"
        )
        self.entry_password.grid(row=3, column=1, padx=5, pady=8)

        ctk.CTkLabel(fields_frame, text="Rol:", font=("Sans", 12, "bold")).grid(
            row=3, column=2, sticky='w', padx=(15, 5), pady=8
        )
        self.combo_rol = ctk.CTkComboBox(
            fields_frame, 
            variable=self.var_rol, 
            values=["admin", "gerente", "cajero"], 
            width=240,
            height=35
        )
        self.combo_rol.grid(row=3, column=3, padx=5, pady=8)

        # Botones en una sola fila
        buttons_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        buttons_frame.pack(fill='x', padx=15, pady=(5, 15))

        self.btn_nuevo = ctk.CTkButton(
            buttons_frame, 
            text="➕ Nuevo", 
            command=self.nuevo_usuario, 
            width=110,
            height=38,
            font=("Sans", 13, "bold")
        )
        self.btn_nuevo.pack(side='left', padx=5)
        
        self.btn_guardar = ctk.CTkButton(
            buttons_frame, 
            text="💾 Guardar", 
            command=self.guardar_usuario, 
            width=110,
            height=38,
            font=("Sans", 13, "bold"),
            fg_color="#4caf50",
            hover_color="#45a049"
        )
        self.btn_guardar.pack(side='left', padx=5)
        
        self.btn_cancelar = ctk.CTkButton(
            buttons_frame, 
            text="❌ Cancelar", 
            command=self.cancelar_edicion, 
            width=110,
            height=38,
            font=("Sans", 13, "bold"),
            fg_color="#757575",
            hover_color="#616161"
        )
        self.btn_cancelar.pack(side='left', padx=5)

        self.btn_editar = ctk.CTkButton(
            buttons_frame, 
            text="✏️ Editar", 
            command=self.editar_usuario, 
            width=110,
            height=38,
            font=("Sans", 13, "bold")
        )
        self.btn_editar.pack(side='left', padx=5)
        
        self.btn_eliminar = ctk.CTkButton(
            buttons_frame, 
            text="🗑️ Eliminar", 
            command=self.eliminar_usuario, 
            width=110,
            height=38,
            font=("Sans", 13, "bold"),
            fg_color="#d13438", 
            hover_color="#a42c2f"
        )
        self.btn_eliminar.pack(side='left', padx=5)

        ctk.CTkButton(
            buttons_frame, 
            text="🔄 Actualizar", 
            command=self.cargar_usuarios, 
            width=110,
            height=38,
            font=("Sans", 13, "bold")
        ).pack(side='right', padx=5)

        # Lista de usuarios
        list_frame = ctk.CTkFrame(main_frame)
        list_frame.pack(fill='both', expand=True, padx=10, pady=(5, 10))

        # Header de lista con buscador
        list_header = ctk.CTkFrame(list_frame, fg_color="transparent")
        list_header.pack(fill='x', padx=10, pady=(10, 5))
        
        ctk.CTkLabel(
            list_header, 
            text="📋 Lista de Usuarios", 
            font=("Sans", 14, "bold")
        ).pack(side='left')
        
        self.entry_buscar = ctk.CTkEntry(
            list_header,
            width=300,
            height=35,
            placeholder_text="🔍 Buscar usuario..."
        )
        self.entry_buscar.pack(side='right', padx=5)
        self.entry_buscar.bind('<KeyRelease>', lambda e: self.buscar_usuario())

        # Treeview
        columns = ('ID', 'Username', 'RFC', 'Nombre', 'Apellido', 'Email', 'Teléfono', 'Rol')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        self.tree.heading('ID', text='ID')
        self.tree.column('ID', width=50, anchor='center')
        
        self.tree.heading('Username', text='Username')
        self.tree.column('Username', width=120)
        
        self.tree.heading('RFC', text='RFC')
        self.tree.column('RFC', width=130, anchor='center')
        
        self.tree.heading('Nombre', text='Nombre')
        self.tree.column('Nombre', width=120)
        
        self.tree.heading('Apellido', text='Apellido')
        self.tree.column('Apellido', width=120)
        
        self.tree.heading('Email', text='Email')
        self.tree.column('Email', width=180)
        
        self.tree.heading('Teléfono', text='Teléfono')
        self.tree.column('Teléfono', width=100, anchor='center')
        
        self.tree.heading('Rol', text='Rol')
        self.tree.column('Rol', width=100, anchor='center')

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=(0, 10))
        scrollbar.pack(side='right', fill='y', pady=(0, 10))
        
        self.tree.bind('<<TreeviewSelect>>', self.seleccionar_usuario)

    def set_estado(self, estado):
        """Controlar el estado de los campos según la acción"""
        if estado == "nuevo":
            self.limpiar_formulario()
            # Habilitar campos
            self.entry_username.configure(state='normal')
            self.entry_rfc.configure(state='normal')
            self.entry_nombre.configure(state='normal')
            self.entry_apellido.configure(state='normal')
            self.entry_email.configure(state='normal')
            self.entry_telefono.configure(state='normal')
            self.entry_password.configure(state='normal')
            self.combo_rol.configure(state='normal')
            
        elif estado == "edicion":
            # Habilitar campos para edición
            self.entry_username.configure(state='normal')
            self.entry_rfc.configure(state='normal')
            self.entry_nombre.configure(state='normal')
            self.entry_apellido.configure(state='normal')
            self.entry_email.configure(state='normal')
            self.entry_telefono.configure(state='normal')
            self.entry_password.configure(state='normal')
            self.combo_rol.configure(state='normal')
            
        elif estado == "inicio":
            self.limpiar_formulario()
            # Deshabilitar campos
            self.entry_username.configure(state='disabled')
            self.entry_rfc.configure(state='disabled')
            self.entry_nombre.configure(state='disabled')
            self.entry_apellido.configure(state='disabled')
            self.entry_email.configure(state='disabled')
            self.entry_telefono.configure(state='disabled')
            self.entry_password.configure(state='disabled')
            self.combo_rol.configure(state='disabled')

    def limpiar_formulario(self):
        self.var_id.set("")
        self.var_username.set("")
        self.var_password.set("")
        self.var_nombre.set("")
        self.var_apellido.set("")
        self.var_email.set("")
        self.var_telefono.set("")
        self.var_rfc.set("")
        self.var_rol.set("cajero")

    def buscar_usuario(self):
        """Buscar usuario en tiempo real"""
        busqueda = self.entry_buscar.get().lower()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        usuarios = self.db.obtener_usuarios()
        for usuario in usuarios:
            if (busqueda in str(usuario[1]).lower() or  # Username
                busqueda in str(usuario[2]).lower() or  # RFC
                busqueda in str(usuario[3]).lower() or  # Nombre
                busqueda in str(usuario[5]).lower() or  # Email
                busqueda == ""):
                self.tree.insert('', 'end', values=usuario)

    def cargar_usuarios(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        usuarios = self.db.obtener_usuarios()
        for usuario in usuarios:
            self.tree.insert('', 'end', values=usuario)

    def seleccionar_usuario(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            values = item['values']
            if values:
                self.var_id.set(values[0])
                self.var_username.set(values[1])
                self.var_rfc.set(values[2])
                self.var_nombre.set(values[3])
                self.var_apellido.set(values[4])
                self.var_email.set(values[5])
                self.var_telefono.set(values[6])
                self.var_rol.set(values[7])
                self.var_password.set("")  # No mostrar password

    def nuevo_usuario(self):
        self.set_estado("nuevo")

    def guardar_usuario(self):
        if not self.validar_formulario():
            return

        datos = {
            'username': self.var_username.get().strip(),
            'rfc': self.var_rfc.get().strip().upper(),
            'nombre': self.var_nombre.get().strip(),
            'apellido': self.var_apellido.get().strip(),
            'email': self.var_email.get().strip(),
            'telefono': self.var_telefono.get().strip(),
            'rol': self.var_rol.get()
        }

        # Solo incluir password si se está creando nuevo usuario o se cambió
        if self.var_password.get().strip():
            datos['password'] = self.var_password.get().strip()

        if self.var_id.get():
            # Editar
            ok, msg = self.db.actualizar_usuario(self.var_id.get(), datos)
        else:
            # Nuevo
            if 'password' not in datos:
                messagebox.showwarning("Validación", "El password es obligatorio para nuevos usuarios")
                return
            ok, msg = self.db.crear_usuario(datos)

        if ok:
            messagebox.showinfo("✅ Éxito", msg)
            self.cargar_usuarios()
            self.set_estado("inicio")
        else:
            messagebox.showerror("❌ Error", msg)

    def editar_usuario(self):
        if not self.var_id.get():
            messagebox.showwarning("Advertencia", "Seleccione un usuario para editar")
            return
        
        self.set_estado("edicion")

    def eliminar_usuario(self):
        if not self.var_id.get():
            messagebox.showwarning("Advertencia", "Seleccione un usuario para eliminar")
            return

        # No permitir eliminar el propio usuario
        if self.var_id.get() == str(self.usuario_actual.get('id')):
            messagebox.showwarning("Advertencia", "No puede eliminar su propio usuario")
            return

        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar al usuario {self.var_nombre.get()} {self.var_apellido.get()}?"):
            ok, msg = self.db.eliminar_usuario(self.var_id.get())
            if ok:
                messagebox.showinfo("✅ Éxito", msg)
                self.cargar_usuarios()
                self.set_estado("inicio")
            else:
                messagebox.showerror("❌ Error", msg)

    def cancelar_edicion(self):
        self.set_estado("inicio")

    def validar_formulario(self):
        if not self.var_username.get().strip():
            messagebox.showwarning("Validación", "El username es obligatorio")
            return False
        
        # Validar RFC
        rfc = self.var_rfc.get().strip()
        if not rfc:
            messagebox.showwarning("Validación", "El RFC es obligatorio")
            return False
        if len(rfc) < 12 or len(rfc) > 13:
            messagebox.showwarning("Validación", "El RFC debe tener 12 o 13 caracteres")
            return False
        
        if not self.var_nombre.get().strip():
            messagebox.showwarning("Validación", "El nombre es obligatorio")
            return False
        if not self.var_email.get().strip():
            messagebox.showwarning("Validación", "El email es obligatorio")
            return False
        return True
