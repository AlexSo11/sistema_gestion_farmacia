import customtkinter as ctk
from tkinter import ttk, messagebox
from dbClientes import DBClientes
from conexion import ConexionDB

class ClientesUI:
    def __init__(self, parent, usuario_actual=None):
        self.parent = parent
        self.usuario_actual = usuario_actual
        self.con = ConexionDB()
        self.db = DBClientes(self.con)
        
        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Verificar permisos - cajeros solo pueden leer
        self.solo_lectura = usuario_actual and usuario_actual.get('rol') == 'cajero'
        
        if not usuario_actual:
            ctk.CTkLabel(
                self.frame, 
                text="⚠️ Acceso denegado",
                font=("Sans", 16, "bold"), 
                text_color='#ff4444'
            ).pack(expand=True)
            return

        self.var_id = ctk.StringVar()
        self.var_rfc = ctk.StringVar()
        self.var_nombre = ctk.StringVar()
        self.var_apellido = ctk.StringVar()
        self.var_email = ctk.StringVar()
        self.var_telefono = ctk.StringVar()
        self.var_direccion = ctk.StringVar()
        self.var_puntos = ctk.IntVar(value=0)
        self.var_usuario_registro = ctk.StringVar()

        self.configurar_estilo_treeview()
        self.build_ui()
        self.cargar_clientes()
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
            text="👥 Gestión de Clientes", 
            font=("Sans", 20, "bold")
        ).pack(side='left')
        
        if self.solo_lectura:
            ctk.CTkLabel(
                title_container,
                text="📖 SOLO LECTURA",
                font=("Sans", 11, "bold"),
                text_color="#ff9800"
            ).pack(side='right')

        # Campos del formulario
        fields_frame = ctk.CTkFrame(form_frame)
        fields_frame.pack(fill='x', padx=15, pady=10)

        # Fila 0: Usuario que registró y Puntos (DESHABILITADOS)
        ctk.CTkLabel(fields_frame, text="👤 Registrado por:", font=("Sans", 12, "bold")).grid(
            row=0, column=0, sticky='w', padx=(10, 5), pady=8
        )
        self.entry_usuario_registro = ctk.CTkEntry(
            fields_frame, 
            textvariable=self.var_usuario_registro, 
            width=240, 
            height=35,
            state='disabled',
            fg_color="#3a3a3a"
        )
        self.entry_usuario_registro.grid(row=0, column=1, padx=5, pady=8)

        ctk.CTkLabel(fields_frame, text="⭐ Puntos:", font=("Sans", 12, "bold")).grid(
            row=0, column=2, sticky='w', padx=(15, 5), pady=8
        )
        self.entry_puntos = ctk.CTkEntry(
            fields_frame, 
            textvariable=self.var_puntos, 
            width=240, 
            height=35,
            state='disabled',
            fg_color="#3a3a3a"
        )
        self.entry_puntos.grid(row=0, column=3, padx=5, pady=8)

        # Fila 1: RFC
        ctk.CTkLabel(fields_frame, text="🆔 RFC:", font=("Sans", 12, "bold")).grid(
            row=1, column=0, sticky='w', padx=(10, 5), pady=8
        )
        self.entry_rfc = ctk.CTkEntry(
            fields_frame, 
            textvariable=self.var_rfc, 
            width=240, 
            height=35,
            placeholder_text="XAXX010101XXX"
        )
        self.entry_rfc.grid(row=1, column=1, padx=5, pady=8)

        # Fila 2: Nombre y Apellido
        ctk.CTkLabel(fields_frame, text="Nombre:", font=("Sans", 12, "bold")).grid(
            row=2, column=0, sticky='w', padx=(10, 5), pady=8
        )
        self.entry_nombre = ctk.CTkEntry(
            fields_frame, 
            textvariable=self.var_nombre, 
            width=240, 
            height=35
        )
        self.entry_nombre.grid(row=2, column=1, padx=5, pady=8)

        ctk.CTkLabel(fields_frame, text="Apellido:", font=("Sans", 12, "bold")).grid(
            row=2, column=2, sticky='w', padx=(15, 5), pady=8
        )
        self.entry_apellido = ctk.CTkEntry(
            fields_frame, 
            textvariable=self.var_apellido, 
            width=240, 
            height=35
        )
        self.entry_apellido.grid(row=2, column=3, padx=5, pady=8)

        # Fila 3: Email y Teléfono
        ctk.CTkLabel(fields_frame, text="📧 Email:", font=("Sans", 12, "bold")).grid(
            row=3, column=0, sticky='w', padx=(10, 5), pady=8
        )
        self.entry_email = ctk.CTkEntry(
            fields_frame, 
            textvariable=self.var_email, 
            width=240, 
            height=35
        )
        self.entry_email.grid(row=3, column=1, padx=5, pady=8)

        ctk.CTkLabel(fields_frame, text="📞 Teléfono:", font=("Sans", 12, "bold")).grid(
            row=3, column=2, sticky='w', padx=(15, 5), pady=8
        )
        self.entry_telefono = ctk.CTkEntry(
            fields_frame, 
            textvariable=self.var_telefono, 
            width=240, 
            height=35
        )
        self.entry_telefono.grid(row=3, column=3, padx=5, pady=8)

        # Fila 4: Dirección (span completo)
        ctk.CTkLabel(fields_frame, text="📍 Dirección:", font=("Sans", 12, "bold")).grid(
            row=4, column=0, sticky='w', padx=(10, 5), pady=8
        )
        self.entry_direccion = ctk.CTkEntry(
            fields_frame, 
            textvariable=self.var_direccion, 
            width=740, 
            height=35
        )
        self.entry_direccion.grid(row=4, column=1, columnspan=3, padx=5, pady=8, sticky='ew')

        # Botones en una sola fila
        if not self.solo_lectura:
            buttons_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
            buttons_frame.pack(fill='x', padx=15, pady=(5, 15))

            self.btn_nuevo = ctk.CTkButton(
                buttons_frame, 
                text="➕ Nuevo", 
                command=self.nuevo_cliente, 
                width=110,
                height=38,
                font=("Sans", 13, "bold")
            )
            self.btn_nuevo.pack(side='left', padx=5)
            
            self.btn_guardar = ctk.CTkButton(
                buttons_frame, 
                text="💾 Guardar", 
                command=self.guardar_cliente, 
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
                command=self.editar_cliente, 
                width=110,
                height=38,
                font=("Sans", 13, "bold")
            )
            self.btn_editar.pack(side='left', padx=5)
            
            self.btn_eliminar = ctk.CTkButton(
                buttons_frame, 
                text="🗑️ Eliminar", 
                command=self.eliminar_cliente, 
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
                command=self.cargar_clientes, 
                width=110,
                height=38,
                font=("Sans", 13, "bold")
            ).pack(side='left', padx=5)
            
            # Buscador
            self.entry_buscar = ctk.CTkEntry(
                buttons_frame,
                width=300,
                height=38,
                placeholder_text="🔍 Buscar cliente por RFC, nombre..."
            )
            self.entry_buscar.pack(side='right', padx=5)
            self.entry_buscar.bind('<KeyRelease>', lambda e: self.buscar_cliente())

        # Lista de clientes
        list_frame = ctk.CTkFrame(main_frame)
        list_frame.pack(fill='both', expand=True, padx=10, pady=(5, 10))

        # Header de lista
        list_header = ctk.CTkFrame(list_frame, fg_color="transparent")
        list_header.pack(fill='x', padx=10, pady=(10, 5))
        
        ctk.CTkLabel(
            list_header, 
            text="📋 Lista de Clientes", 
            font=("Sans", 14, "bold")
        ).pack(side='left')

        # Treeview - CORREGIDO: orden correcto de columnas
        columns = ('ID', 'RFC', 'Nombre', 'Apellido', 'Email', 'Teléfono', 'Puntos', 'Usuario')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        self.tree.heading('ID', text='ID')
        self.tree.column('ID', width=50, anchor='center')
        
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
        
        self.tree.heading('Puntos', text='⭐ Puntos')
        self.tree.column('Puntos', width=80, anchor='center')
        
        self.tree.heading('Usuario', text='Registrado por')
        self.tree.column('Usuario', width=120, anchor='center')

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=(0, 10))
        scrollbar.pack(side='right', fill='y', pady=(0, 10))
        
        self.tree.bind('<<TreeviewSelect>>', self.seleccionar_cliente)

    def set_estado(self, estado):
        """Controlar el estado de los campos según la acción"""
        if estado == "nuevo":
            self.limpiar_formulario()
            # Habilitar campos editables
            self.entry_rfc.configure(state='normal')
            self.entry_nombre.configure(state='normal')
            self.entry_apellido.configure(state='normal')
            self.entry_email.configure(state='normal')
            self.entry_telefono.configure(state='normal')
            self.entry_direccion.configure(state='normal')
            
            # Establecer usuario que registra
            self.var_usuario_registro.set(self.usuario_actual.get('username'))
            
        elif estado == "edicion":
            # Habilitar campos editables
            self.entry_rfc.configure(state='normal')
            self.entry_nombre.configure(state='normal')
            self.entry_apellido.configure(state='normal')
            self.entry_email.configure(state='normal')
            self.entry_telefono.configure(state='normal')
            self.entry_direccion.configure(state='normal')
            
        elif estado == "inicio":
            self.limpiar_formulario()
            # Deshabilitar campos
            if not self.solo_lectura:
                self.entry_rfc.configure(state='disabled')
                self.entry_nombre.configure(state='disabled')
                self.entry_apellido.configure(state='disabled')
                self.entry_email.configure(state='disabled')
                self.entry_telefono.configure(state='disabled')
                self.entry_direccion.configure(state='disabled')

    def limpiar_formulario(self):
        self.var_id.set("")
        self.var_rfc.set("")
        self.var_nombre.set("")
        self.var_apellido.set("")
        self.var_email.set("")
        self.var_telefono.set("")
        self.var_direccion.set("")
        self.var_puntos.set(0)
        self.var_usuario_registro.set("")

    def buscar_cliente(self):
        """Buscar cliente en tiempo real"""
        busqueda = self.entry_buscar.get().lower()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        clientes = self.db.obtener_clientes()
        for cliente in clientes:
            if (busqueda in str(cliente[1]).lower() or  # RFC
                busqueda in str(cliente[2]).lower() or  # Nombre
                busqueda in str(cliente[3]).lower() or  # Apellido
                busqueda in str(cliente[4]).lower() or  # Email
                busqueda == ""):
                self.tree.insert('', 'end', values=cliente)

    def cargar_clientes(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        clientes = self.db.obtener_clientes()
        for cliente in clientes:
            self.tree.insert('', 'end', values=cliente)

    def seleccionar_cliente(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            values = item['values']
            if values:
                self.var_id.set(values[0])
                self.var_rfc.set(values[1])
                self.var_nombre.set(values[2])
                self.var_apellido.set(values[3])
                self.var_email.set(values[4])
                self.var_telefono.set(values[5])
                self.var_puntos.set(values[6] if len(values) > 6 else 0)
                self.var_usuario_registro.set(values[7] if len(values) > 7 else "")

    def nuevo_cliente(self):
        if self.solo_lectura:
            messagebox.showwarning("Permiso denegado", "Solo lectura para cajeros")
            return
        self.set_estado("nuevo")

    def guardar_cliente(self):
        if self.solo_lectura:
            messagebox.showwarning("Permiso denegado", "Solo lectura para cajeros")
            return

        if not self.validar_formulario():
            return

        datos = {
            'rfc': self.var_rfc.get().strip().upper(),
            'nombre': self.var_nombre.get().strip(),
            'apellido': self.var_apellido.get().strip(),
            'email': self.var_email.get().strip(),
            'telefono': self.var_telefono.get().strip(),
            'direccion': self.var_direccion.get().strip(),
            'usuario_id': self.usuario_actual.get('id')
        }

        if self.var_id.get():
            # Editar
            ok, msg = self.db.actualizar_cliente(self.var_id.get(), datos)
        else:
            # Nuevo
            ok, msg = self.db.crear_cliente(datos)

        if ok:
            messagebox.showinfo("✅ Éxito", msg)
            self.cargar_clientes()
            self.set_estado("inicio")
        else:
            messagebox.showerror("❌ Error", msg)

    def editar_cliente(self):
        if self.solo_lectura:
            messagebox.showwarning("Permiso denegado", "Solo lectura para cajeros")
            return
            
        if not self.var_id.get():
            messagebox.showwarning("Advertencia", "Seleccione un cliente para editar")
            return
        
        self.set_estado("edicion")

    def eliminar_cliente(self):
        if self.solo_lectura:
            messagebox.showwarning("Permiso denegado", "Solo lectura para cajeros")
            return
            
        if not self.var_id.get():
            messagebox.showwarning("Advertencia", "Seleccione un cliente para eliminar")
            return

        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar al cliente {self.var_nombre.get()} {self.var_apellido.get()}?"):
            ok, msg = self.db.eliminar_cliente(self.var_id.get())
            if ok:
                messagebox.showinfo("✅ Éxito", msg)
                self.cargar_clientes()
                self.set_estado("inicio")
            else:
                messagebox.showerror("❌ Error", msg)

    def cancelar_edicion(self):
        self.set_estado("inicio")

    def validar_formulario(self):
        # Validar RFC
        rfc = self.var_rfc.get().strip()
        if not rfc:
            messagebox.showwarning("Validación", "El RFC es obligatorio")
            return False
        if len(rfc) < 12 or len(rfc) > 13:
            messagebox.showwarning("Validación", "El RFC debe tener 12 o 13 caracteres")
            return False
        
        # Validar nombre
        if not self.var_nombre.get().strip():
            messagebox.showwarning("Validación", "El nombre es obligatorio")
            return False
        
        # Validar apellido
        if not self.var_apellido.get().strip():
            messagebox.showwarning("Validación", "El apellido es obligatorio")
            return False
        
        return True