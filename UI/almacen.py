import customtkinter as ctk
from tkinter import ttk, messagebox
from DB.dbArticulos import DBArticulos
from conexion import ConexionDB
from datetime import datetime

class AlmacenUI:
    def __init__(self, parent, usuario_actual=None):
        self.parent = parent
        self.usuario_actual = usuario_actual
        self.con = ConexionDB()
        self.db = DBArticulos(self.con)
        
        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Verificar permisos
        if not usuario_actual or usuario_actual.get('rol') not in ['admin', 'gerente']:
            ctk.CTkLabel(
                self.frame, 
                text="⚠️ Acceso denegado: Solo administradores y gerentes",
                font=("Arial", 16, "bold"), 
                text_color='#ff4444'
            ).pack(expand=True)
            return

        self.filtro_categoria = ctk.StringVar(value="Todas")
        self.filtro_stock = ctk.StringVar(value="Todos")
        
        self.build_ui()
        self.configurar_estilo_treeview()
        self.cargar_inventario()

    def configurar_estilo_treeview(self):
        """Configurar estilo oscuro para Treeview"""
        style = ttk.Style()
        
        # Configurar tema base
        style.theme_use('clam')
        
        # Colores del Treeview
        style.configure("Treeview",
            background="#2b2b2b",           # Fondo de las filas
            foreground="white",               # Texto
            fieldbackground="#2b2b2b",      # Fondo del campo
            borderwidth=0,
            font=('Sans', 11)
        )
        
        # Colores de los encabezados
        style.configure("Treeview.Heading",
            background="#1f1f1f",            # Fondo del header
            foreground="white",                # Texto del header
            borderwidth=1,
            relief="flat",
            font=('Sans', 12, 'bold')
        )
        
        # Color cuando se pasa el mouse (hover)
        style.map('Treeview',
            background=[('selected', '#1f6aa5')],  # Color al seleccionar
            foreground=[('selected', 'white')]
        )
        
        # Eliminar las líneas del Treeview
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])

    def build_ui(self):
        main_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        main_frame.pack(fill='both', expand=True)

        # Header con título y estadísticas
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill='x', padx=10, pady=(10, 5))

        # Título
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side='left', padx=10, pady=10)
        
        ctk.CTkLabel(
            title_frame, 
            text="📦 Almacén - Inventario de Farmacia", 
            font=("Arial", 20, "bold")
        ).pack(anchor='w')
        
        ctk.CTkLabel(
            title_frame, 
            text=f"Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
            font=("Arial", 11),
            text_color="gray"
        ).pack(anchor='w')

        # Estadísticas
        stats_frame = ctk.CTkFrame(header_frame, fg_color="#2b2b2b", corner_radius=10)
        stats_frame.pack(side='right', padx=10, pady=5)
        
        self.lbl_total_productos = ctk.CTkLabel(
            stats_frame, 
            text="Total Productos: 0", 
            font=("Arial", 12, "bold")
        )
        self.lbl_total_productos.pack(side='left', padx=15, pady=8)
        
        self.lbl_stock_bajo = ctk.CTkLabel(
            stats_frame, 
            text="Stock Bajo: 0", 
            font=("Arial", 12, "bold"),
            text_color="#ff9800"
        )
        self.lbl_stock_bajo.pack(side='left', padx=15, pady=8)
        
        self.lbl_sin_stock = ctk.CTkLabel(
            stats_frame, 
            text="Sin Stock: 0", 
            font=("Arial", 12, "bold"),
            text_color="#f44336"
        )
        self.lbl_sin_stock.pack(side='left', padx=15, pady=8)

        # Filtros
        filtros_frame = ctk.CTkFrame(main_frame)
        filtros_frame.pack(fill='x', padx=10, pady=5)

        # Búsqueda
        ctk.CTkLabel(filtros_frame, text="🔍 Buscar:", font=("Arial", 12, "bold")).pack(side='left', padx=(10, 5), pady=10)
        
        self.entry_buscar = ctk.CTkEntry(
            filtros_frame, 
            width=300, 
            height=35,
            placeholder_text="Buscar por código o nombre..."
        )
        self.entry_buscar.pack(side='left', padx=5, pady=10)
        self.entry_buscar.bind('<KeyRelease>', lambda e: self.filtrar_inventario())

        # Filtro por categoría - CATEGORÍAS COMPLETAS
        ctk.CTkLabel(filtros_frame, text="Categoría:", font=("Arial", 12, "bold")).pack(side='left', padx=(20, 5), pady=10)
        
        self.combo_categoria = ctk.CTkComboBox(
            filtros_frame,
            variable=self.filtro_categoria,
            values=["Todas", "Medicamentos", "Cuidado Personal", "Suplementos", "Herbolaria", "Promociones", "Dermatología", "Ortopedia", "Belleza", "Salud", "Maternidad", "Equipo Médico", "Otros"],
            width=180,
            height=35,
            command=lambda e: self.filtrar_inventario()
        )
        self.combo_categoria.pack(side='left', padx=5, pady=10)

        # Filtro por stock
        ctk.CTkLabel(filtros_frame, text="Stock:", font=("Arial", 12, "bold")).pack(side='left', padx=(20, 5), pady=10)
        
        self.combo_stock = ctk.CTkComboBox(
            filtros_frame,
            variable=self.filtro_stock,
            values=["Todos", "En Stock", "Stock Bajo (<20)", "Sin Stock"],
            width=180,
            height=35,
            command=lambda e: self.filtrar_inventario()
        )
        self.combo_stock.pack(side='left', padx=5, pady=10)

        # Botón actualizar
        ctk.CTkButton(
            filtros_frame,
            text="🔄 Actualizar",
            command=self.cargar_inventario,
            width=120,
            height=35
        ).pack(side='right', padx=10, pady=10)

        # Tabla de inventario
        tabla_frame = ctk.CTkFrame(main_frame)
        tabla_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Crear Treeview con estilo mejorado
        style = ttk.Style()
        style.configure("Treeview", rowheight=30, font=('Arial', 11))
        style.configure("Treeview.Heading", font=('Arial', 12, 'bold'))

        columns = ('Código', 'Nombre', 'Descripción', 'Precio', 'Stock', 'Categoría', 'Estado')
        self.tree = ttk.Treeview(
            tabla_frame, 
            columns=columns, 
            show='headings', 
            height=20
        )
        
        # Configurar columnas
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
        self.tree.column('Categoría', width=150, anchor='center')
        
        self.tree.heading('Estado', text='Estado')
        self.tree.column('Estado', width=120, anchor='center')

        # Scrollbars
        scrollbar_y = ttk.Scrollbar(tabla_frame, orient='vertical', command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(tabla_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        self.tree.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=10)
        scrollbar_y.pack(side='right', fill='y', pady=10)
        scrollbar_x.pack(side='bottom', fill='x', padx=10)

        # Configurar tags para colores
        self.tree.tag_configure('sin_stock', background="#862d3b")
        self.tree.tag_configure('stock_bajo', background="#a57b38")
        self.tree.tag_configure('stock_ok', background="#477a4b")

        # Frame de acciones
        acciones_frame = ctk.CTkFrame(main_frame)
        acciones_frame.pack(fill='x', padx=10, pady=(5, 10))

        ctk.CTkButton(
            acciones_frame,
            text="📊 Exportar Reporte",
            command=self.exportar_reporte,
            width=150,
            height=40
        ).pack(side='left', padx=10, pady=10)
        
        ctk.CTkButton(
            acciones_frame,
            text="⚠️ Ver Alertas de Stock",
            command=self.ver_alertas_stock,
            width=180,
            height=40,
            fg_color="#ff9800",
            hover_color="#f57c00"
        ).pack(side='left', padx=5, pady=10)

    def cargar_inventario(self):
        """Cargar todos los artículos del inventario"""
        try:
            # Limpiar árbol
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Obtener artículos
            articulos = self.db.obtener_articulos()
            
            total_productos = len(articulos)
            stock_bajo = 0
            sin_stock = 0
            
            for articulo in articulos:
                # articulo = (id, codigo, nombre, descripcion, precio, stock, categoria)
                codigo = articulo[1]
                nombre = articulo[2]
                descripcion = articulo[3] if articulo[3] else "N/A"
                precio = f"${articulo[4]:,.2f}"
                stock = articulo[5]
                categoria = articulo[6] if articulo[6] else "Sin categoría"
                
                # Determinar estado
                if stock == 0:
                    estado = "❌ Sin Stock"
                    tag = 'sin_stock'
                    sin_stock += 1
                elif stock < 20:
                    estado = "⚠️ Stock Bajo"
                    tag = 'stock_bajo'
                    stock_bajo += 1
                else:
                    estado = "✅ Disponible"
                    tag = 'stock_ok'
                
                self.tree.insert(
                    '', 
                    'end', 
                    values=(codigo, nombre, descripcion, precio, stock, categoria, estado),
                    tags=(tag,)
                )
            
            # Actualizar estadísticas
            self.lbl_total_productos.configure(text=f"Total Productos: {total_productos}")
            self.lbl_stock_bajo.configure(text=f"Stock Bajo: {stock_bajo}")
            self.lbl_sin_stock.configure(text=f"Sin Stock: {sin_stock}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando inventario: {str(e)}")

    def filtrar_inventario(self):
        """Filtrar inventario según búsqueda y filtros"""
        busqueda = self.entry_buscar.get().lower()
        categoria = self.filtro_categoria.get()
        filtro_stock = self.filtro_stock.get()
        
        # Limpiar árbol
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener artículos
        articulos = self.db.obtener_articulos()
        
        total_productos = len(articulos)
        stock_bajo = 0
        sin_stock = 0
        
        for articulo in articulos:
            codigo = articulo[1]
            nombre = articulo[2]
            descripcion = articulo[3] if articulo[3] else "N/A"
            precio = f"${articulo[4]:,.2f}"
            stock = articulo[5]
            cat = articulo[6] if articulo[6] else "Sin categoría"
            
            # Aplicar filtros
            # Filtro de búsqueda
            if busqueda and busqueda not in codigo.lower() and busqueda not in nombre.lower():
                continue
            
            # Filtro de categoría
            if categoria != "Todas" and cat != categoria:
                continue
            
            # Filtro de stock
            if filtro_stock == "En Stock" and stock <= 0:
                continue
            elif filtro_stock == "Stock Bajo (<20)" and (stock >= 20 or stock == 0):
                continue
            elif filtro_stock == "Sin Stock" and stock > 0:
                continue
            
            # Determinar estado
            if stock == 0:
                estado = "❌ Sin Stock"
                tag = 'sin_stock'
                sin_stock += 1
            elif stock < 20:
                estado = "⚠️ Stock Bajo"
                tag = 'stock_bajo'
                stock_bajo += 1
            else:
                estado = "✅ Disponible"
                tag = 'stock_ok'
            
            self.tree.insert(
                '', 
                'end', 
                values=(codigo, nombre, descripcion, precio, stock, cat, estado),
                tags=(tag,)
            )
        
        # Actualizar estadísticas con los artículos filtrados
        self.lbl_total_productos.configure(text=f"Total Productos: {total_productos}")
        self.lbl_stock_bajo.configure(text=f"Stock Bajo: {stock_bajo}")
        self.lbl_sin_stock.configure(text=f"Sin Stock: {sin_stock}")

    def ver_alertas_stock(self):
        """Mostrar ventana con alertas de stock"""
        alertas_window = ctk.CTkToplevel(self.parent)
        alertas_window.title("⚠️ Alertas de Stock")
        alertas_window.geometry("800x600")
        
        # Centrar ventana
        alertas_window.update_idletasks()
        x = (alertas_window.winfo_screenwidth() - 800) // 2
        y = (alertas_window.winfo_screenheight() - 600) // 2
        alertas_window.geometry(f"800x600+{x}+{y}")
        
        # Título
        ctk.CTkLabel(
            alertas_window, 
            text="⚠️ Productos que requieren atención", 
            font=("Arial", 18, "bold")
        ).pack(pady=20)
        
        # Frame para tabla
        tabla_frame = ctk.CTkFrame(alertas_window)
        tabla_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Treeview
        columns = ('Código', 'Nombre', 'Stock Actual', 'Estado')
        tree_alertas = ttk.Treeview(
            tabla_frame, 
            columns=columns, 
            show='headings', 
            height=15
        )
        
        for col in columns:
            tree_alertas.heading(col, text=col)
        
        tree_alertas.column('Código', width=100, anchor='center')
        tree_alertas.column('Nombre', width=300)
        tree_alertas.column('Stock Actual', width=150, anchor='center')
        tree_alertas.column('Estado', width=200, anchor='center')
        
        # Configurar tags
        tree_alertas.tag_configure('sin_stock', background='#ffebee')
        tree_alertas.tag_configure('stock_bajo', background='#fff3e0')
        
        scrollbar = ttk.Scrollbar(tabla_frame, orient='vertical', command=tree_alertas.yview)
        tree_alertas.configure(yscrollcommand=scrollbar.set)
        
        tree_alertas.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)
        
        # Cargar datos
        articulos = self.db.obtener_articulos()
        alertas_count = 0
        
        for articulo in articulos:
            stock = articulo[5]
            if stock < 20:
                codigo = articulo[1]
                nombre = articulo[2]
                
                if stock == 0:
                    estado = "❌ URGENTE: Sin Stock"
                    tag = 'sin_stock'
                else:
                    estado = "⚠️ Stock Bajo"
                    tag = 'stock_bajo'
                
                tree_alertas.insert(
                    '', 
                    'end', 
                    values=(codigo, nombre, stock, estado),
                    tags=(tag,)
                )
                alertas_count += 1
        
        if alertas_count == 0:
            ctk.CTkLabel(
                tabla_frame,
                text="✅ No hay alertas de stock",
                font=("Arial", 14),
                text_color="#4caf50"
            ).pack(expand=True)
        
        # Botón cerrar
        ctk.CTkButton(
            alertas_window,
            text="Cerrar",
            command=alertas_window.destroy,
            width=150,
            height=40
        ).pack(pady=(0, 20))

    def exportar_reporte(self):
        """Exportar reporte de inventario"""
        try:
            from datetime import datetime
            
            filename = f"inventario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("REPORTE DE INVENTARIO - FARMACIA QCI\n")
                f.write(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write("="*80 + "\n\n")
                
                articulos = self.db.obtener_articulos()
                
                f.write(f"Total de productos: {len(articulos)}\n\n")
                
                f.write(f"{'Código':<15} {'Nombre':<30} {'Stock':<10} {'Precio':<15} {'Estado':<20}\n")
                f.write("-"*80 + "\n")
                
                for articulo in articulos:
                    codigo = articulo[1]
                    nombre = articulo[2][:28]
                    stock = articulo[5]
                    precio = f"${articulo[4]:,.2f}"
                    
                    if stock == 0:
                        estado = "Sin Stock"
                    elif stock < 20:
                        estado = "Stock Bajo"
                    else:
                        estado = "Disponible"
                    
                    f.write(f"{codigo:<15} {nombre:<30} {stock:<10} {precio:<15} {estado:<20}\n")
            
            messagebox.showinfo("✅ Éxito", f"Reporte exportado: {filename}")
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error exportando reporte: {str(e)}")
