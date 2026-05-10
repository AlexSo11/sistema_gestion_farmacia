import customtkinter as ctk
from tkinter import ttk, messagebox
from dbArticulos import DBArticulos
from conexion import ConexionDB

class ArticulosUI:
    def __init__(self, parent, usuario_actual=None):
        self.parent = parent
        self.usuario_actual = usuario_actual
        self.con = ConexionDB()
        self.db = DBArticulos(self.con)
        
        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Verificar permisos
        self.solo_lectura = usuario_actual and usuario_actual.get('rol') == 'cajero'
        
        if not usuario_actual:
            ctk.CTkLabel(
                self.frame, 
                text="⚠️ Acceso denegado",
                font=("Sans", 14), 
                text_color='red'
            ).pack(expand=True)
            return

        self.var_id = ctk.StringVar()
        self.var_codigo = ctk.StringVar()
        self.var_nombre = ctk.StringVar()
        self.var_descripcion = ctk.StringVar()
        self.var_precio = ctk.StringVar(value="0.0")
        self.var_stock = ctk.StringVar(value="0")
        self.var_categoria = ctk.StringVar(value="Medicamentos")
        self.var_es_promocion = ctk.BooleanVar(value=False)
        
        # Categorías de farmacia
        self.categorias = [
            "Medicamentos",
            "Cuidado Personal",
            "Suplementos",
            "Herbolaria",
            "Promociones",
            "Dermatología",
            "Ortopedia"
        ]

        self.configurar_estilo_treeview()
        self.build_ui()
        self.cargar_articulos()
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
            text="💊 Gestión de Artículos", 
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

        # Fila 1: Código y Nombre
        ctk.CTkLabel(fields_frame, text="🔢 Código:", font=("Sans", 12, "bold")).grid(
            row=0, column=0, sticky='w', padx=5, pady=8
        )
        self.entry_codigo = ctk.CTkEntry(fields_frame, textvariable=self.var_codigo, width=180, height=35)
        self.entry_codigo.grid(row=0, column=1, padx=5, pady=8)

        ctk.CTkLabel(fields_frame, text="📦 Nombre:", font=("Sans", 12, "bold")).grid(
            row=0, column=2, sticky='w', padx=5, pady=8
        )
        self.entry_nombre = ctk.CTkEntry(fields_frame, textvariable=self.var_nombre, width=300, height=35)
        self.entry_nombre.grid(row=0, column=3, padx=5, pady=8)

        # Fila 2: Descripción
        ctk.CTkLabel(fields_frame, text="📝 Descripción:", font=("Sans", 12, "bold")).grid(
            row=1, column=0, sticky='w', padx=5, pady=8
        )
        self.entry_descripcion = ctk.CTkEntry(fields_frame, textvariable=self.var_descripcion, width=680, height=35)
        self.entry_descripcion.grid(row=1, column=1, columnspan=3, padx=5, pady=8, sticky='ew')

        # Fila 3: Precio, Stock, Categoría
        ctk.CTkLabel(fields_frame, text="💰 Precio:", font=("Sans", 12, "bold")).grid(
            row=2, column=0, sticky='w', padx=5, pady=8
        )
        self.entry_precio = ctk.CTkEntry(fields_frame, textvariable=self.var_precio, width=140, height=35)
        self.entry_precio.grid(row=2, column=1, padx=5, pady=8, sticky='w')

        ctk.CTkLabel(fields_frame, text="📊 Stock:", font=("Sans", 12, "bold")).grid(
            row=2, column=2, sticky='w', padx=5, pady=8
        )
        self.entry_stock = ctk.CTkEntry(fields_frame, textvariable=self.var_stock, width=100, height=35)
        self.entry_stock.grid(row=2, column=3, padx=5, pady=8, sticky='w')

        # Fila 4: Categoría y Promoción
        ctk.CTkLabel(fields_frame, text="🏷️ Categoría:", font=("Sans", 12, "bold")).grid(
            row=3, column=0, sticky='w', padx=5, pady=8
        )
        self.combo_categoria = ctk.CTkComboBox(
            fields_frame,
            variable=self.var_categoria,
            values=self.categorias,
            width=200,
            height=35
        )
        self.combo_categoria.grid(row=3, column=1, padx=5, pady=8, sticky='w')

        self.check_promocion = ctk.CTkCheckBox(
            fields_frame,
            text="⭐ Es artículo en promoción (canjeable por 50 puntos)",
            variable=self.var_es_promocion,
            font=("Sans", 12, "bold")
        )
        self.check_promocion.grid(row=3, column=2, columnspan=2, padx=5, pady=8, sticky='w')

        # Botones
        if not self.solo_lectura:
            buttons_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
            buttons_frame.pack(fill='x', padx=15, pady=(5, 15))

            self.btn_nuevo = ctk.CTkButton(
                buttons_frame, 
                text="➕ Nuevo", 
                command=self.nuevo_articulo, 
                width=120,
                height=38,
                font=("Sans", 13, "bold")
            )
            self.btn_nuevo.pack(side='left', padx=5)
            
            self.btn_guardar = ctk.CTkButton(
                buttons_frame, 
                text="💾 Guardar", 
                command=self.guardar_articulo, 
                width=120,
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
                width=120,
                height=38,
                font=("Sans", 13, "bold"),
                fg_color="#757575",
                hover_color="#616161"
            )
            self.btn_cancelar.pack(side='left', padx=5)

        # Lista de artículos
        list_frame = ctk.CTkFrame(main_frame)
        list_frame.pack(fill='both', expand=True, padx=10, pady=(5, 10))

        # Header de lista
        list_header = ctk.CTkFrame(list_frame, fg_color="transparent")
        list_header.pack(fill='x', padx=10, pady=(10, 5))
        
        ctk.CTkLabel(
            list_header, 
            text="📋 Lista de Artículos", 
            font=("Sans", 14, "bold")
        ).pack(side='left')
        
        # Búsqueda
        self.entry_buscar = ctk.CTkEntry(
            list_header,
            width=300,
            height=35,
            placeholder_text="🔍 Buscar artículo..."
        )
        self.entry_buscar.pack(side='right', padx=5)
        self.entry_buscar.bind('<KeyRelease>', lambda e: self.buscar_articulo())

        # Treeview
        columns = ('ID', 'Código', 'Nombre', 'Descripción', 'Precio', 'Stock', 'Categoría', 'Promoción')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        self.tree.heading('ID', text='ID')
        self.tree.column('ID', width=50, anchor='center')
        
        self.tree.heading('Código', text='Código')
        self.tree.column('Código', width=100, anchor='center')
        
        self.tree.heading('Nombre', text='Nombre')
        self.tree.column('Nombre', width=200)
        
        self.tree.heading('Descripción', text='Descripción')
        self.tree.column('Descripción', width=250)
        
        self.tree.heading('Precio', text='Precio')
        self.tree.column('Precio', width=100, anchor='e')
        
        self.tree.heading('Stock', text='Stock')
        self.tree.column('Stock', width=80, anchor='center')
        
        self.tree.heading('Categoría', text='Categoría')
        self.tree.column('Categoría', width=120, anchor='center')
        
        self.tree.heading('Promoción', text='Promoción')
        self.tree.column('Promoción', width=100, anchor='center')

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=(0, 10))
        scrollbar.pack(side='right', fill='y', pady=(0, 10))
        
        self.tree.bind('<<TreeviewSelect>>', self.seleccionar_articulo)

        # Botones de acción
        action_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        action_frame.pack(fill='x', padx=10, pady=(0, 10))

        if not self.solo_lectura:
            self.btn_editar = ctk.CTkButton(
                action_frame, 
                text="✏️ Editar", 
                command=self.editar_articulo, 
                width=110,
                height=38,
                font=("Sans", 12, "bold")
            )
            self.btn_editar.pack(side='left', padx=5)
            
            self.btn_eliminar = ctk.CTkButton(
                action_frame, 
                text="🗑️ Eliminar", 
                command=self.eliminar_articulo, 
                width=110,
                height=38,
                font=("Sans", 12, "bold"),
                fg_color="#d13438", 
                hover_color="#a42c2f"
            )
            self.btn_eliminar.pack(side='left', padx=5)
        
        ctk.CTkButton(
            action_frame, 
            text="🔄 Actualizar", 
            command=self.cargar_articulos, 
            width=110,
            height=38,
            font=("Sans", 12, "bold")
        ).pack(side='right', padx=5)

    def set_estado(self, estado):
        """Controlar el estado de los campos según la acción"""
        if estado == "nuevo":
            self.limpiar_formulario()
            # Habilitar campos
            self.entry_codigo.configure(state='normal')
            self.entry_nombre.configure(state='normal')
            self.entry_descripcion.configure(state='normal')
            self.entry_precio.configure(state='normal')
            self.entry_stock.configure(state='normal')
            self.combo_categoria.configure(state='normal')
            self.check_promocion.configure(state='normal')
            
        elif estado == "edicion":
            # Habilitar campos para edición
            self.entry_codigo.configure(state='normal')
            self.entry_nombre.configure(state='normal')
            self.entry_descripcion.configure(state='normal')
            self.entry_precio.configure(state='normal')
            self.entry_stock.configure(state='normal')
            self.combo_categoria.configure(state='normal')
            self.check_promocion.configure(state='normal')
            
        elif estado == "inicio":
            self.limpiar_formulario()
            # Deshabilitar campos
            if not self.solo_lectura:
                self.entry_codigo.configure(state='disabled')
                self.entry_nombre.configure(state='disabled')
                self.entry_descripcion.configure(state='disabled')
                self.entry_precio.configure(state='disabled')
                self.entry_stock.configure(state='disabled')
                self.combo_categoria.configure(state='disabled')
                self.check_promocion.configure(state='disabled')

    def limpiar_formulario(self):
        self.var_id.set("")
        self.var_codigo.set("")
        self.var_nombre.set("")
        self.var_descripcion.set("")
        self.var_precio.set("0.0")
        self.var_stock.set("0")
        self.var_categoria.set("Medicamentos")
        self.var_es_promocion.set(False)

    def buscar_articulo(self):
        """Buscar artículo en tiempo real"""
        busqueda = self.entry_buscar.get().lower()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        articulos = self.db.obtener_articulos()
        for articulo in articulos:
            if (busqueda in str(articulo[1]).lower() or  # Código
                busqueda in str(articulo[2]).lower() or  # Nombre
                busqueda in str(articulo[6]).lower() or  # Categoría
                busqueda == ""):
                # Formatear promoción
                es_promo = "⭐ SÍ" if articulo[7] else "No"
                valores = list(articulo[:7]) + [es_promo]
                valores[4] = f"${articulo[4]:,.2f}"  # Formatear precio
                self.tree.insert('', 'end', values=valores)

    def cargar_articulos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        articulos = self.db.obtener_articulos()
        for articulo in articulos:
            # Formatear promoción
            es_promo = "⭐ SÍ" if articulo[7] else "No"
            valores = list(articulo[:7]) + [es_promo]
            valores[4] = f"${articulo[4]:,.2f}"  # Formatear precio
            self.tree.insert('', 'end', values=valores)

    def seleccionar_articulo(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            values = item['values']
            if values:
                self.var_id.set(values[0])
                self.var_codigo.set(values[1])
                self.var_nombre.set(values[2])
                self.var_descripcion.set(values[3])
                # Limpiar formato de precio
                precio_str = str(values[4]).replace('$', '').replace(',', '')
                self.var_precio.set(precio_str)
                self.var_stock.set(str(values[5]))
                self.var_categoria.set(values[6] if len(values) > 6 else "Medicamentos")
                # Convertir promoción
                es_promo = values[7] if len(values) > 7 else "No"
                self.var_es_promocion.set(es_promo == "⭐ SÍ")

    def nuevo_articulo(self):
        if self.solo_lectura:
            messagebox.showwarning("Permiso denegado", "Solo lectura para cajeros")
            return
        self.set_estado("nuevo")

    def guardar_articulo(self):
        if self.solo_lectura:
            messagebox.showwarning("Permiso denegado", "Solo lectura para cajeros")
            return

        if not self.validar_formulario():
            return

        try:
            precio = float(self.var_precio.get())
            stock = int(self.var_stock.get())
        except ValueError:
            messagebox.showerror("Error", "Precio y Stock deben ser números válidos")
            return

        datos = {
            'codigo': self.var_codigo.get().strip(),
            'nombre': self.var_nombre.get().strip(),
            'descripcion': self.var_descripcion.get().strip(),
            'precio': precio,
            'stock': stock,
            'categoria': self.var_categoria.get(),
            'es_promocion': 1 if self.var_es_promocion.get() else 0
        }

        if self.var_id.get():
            # Editar
            ok, msg = self.db.actualizar_articulo(self.var_id.get(), datos)
        else:
            # Nuevo
            ok, msg = self.db.crear_articulo(datos)

        if ok:
            messagebox.showinfo("✅ Éxito", msg)
            self.cargar_articulos()
            self.set_estado("inicio")
        else:
            messagebox.showerror("❌ Error", msg)

    def editar_articulo(self):
        if self.solo_lectura:
            messagebox.showwarning("Permiso denegado", "Solo lectura para cajeros")
            return
            
        if not self.var_id.get():
            messagebox.showwarning("Advertencia", "Seleccione un artículo para editar")
            return
        
        self.set_estado("edicion")

    def eliminar_articulo(self):
        if self.solo_lectura:
            messagebox.showwarning("Permiso denegado", "Solo lectura para cajeros")
            return
            
        if not self.var_id.get():
            messagebox.showwarning("Advertencia", "Seleccione un artículo para eliminar")
            return

        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar el artículo {self.var_nombre.get()}?"):
            ok, msg = self.db.eliminar_articulo(self.var_id.get())
            if ok:
                messagebox.showinfo("✅ Éxito", msg)
                self.cargar_articulos()
                self.set_estado("inicio")
            else:
                messagebox.showerror("❌ Error", msg)

    def cancelar_edicion(self):
        self.set_estado("inicio")

    def validar_formulario(self):
        if not self.var_codigo.get().strip():
            messagebox.showwarning("Validación", "El código es obligatorio")
            return False
        if not self.var_nombre.get().strip():
            messagebox.showwarning("Validación", "El nombre es obligatorio")
            return False
        try:
            precio = float(self.var_precio.get())
            if precio <= 0:
                messagebox.showwarning("Validación", "El precio debe ser mayor a 0")
                return False
        except ValueError:
            messagebox.showwarning("Validación", "El precio debe ser un número válido")
            return False
        
        try:
            stock = int(self.var_stock.get())
            if stock < 0:
                messagebox.showwarning("Validación", "El stock no puede ser negativo")
                return False
        except ValueError:
            messagebox.showwarning("Validación", "El stock debe ser un número entero válido")
            return False
        
        return True