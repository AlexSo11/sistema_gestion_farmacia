import customtkinter as ctk
from tkinter import ttk, messagebox
from DB.dbVentas import DBVentas
from conexion import ConexionDB

class DetaVentaUI:
    def __init__(self, parent, usuario_actual=None):
        self.parent = parent
        self.usuario_actual = usuario_actual
        self.con = ConexionDB()
        self.db = DBVentas(self.con)
        
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

        self.venta_seleccionada = None
        self.build_ui()
        self.configurar_estilo_treeview()
        self.cargar_ventas()

    def configurar_estilo_treeview(self):
        """Configurar estilo oscuro para Treeview"""
        style = ttk.Style()
        
        # Configurar tema base
        style.theme_use('clam')
        
        # Colores del Treeview
        style.configure("Treeview",
            background="#2b2b2b",
            foreground="white",
            fieldbackground="#2b2b2b",
            borderwidth=0,
            font=('Sans', 11)
        )
        
        # Colores de los encabezados
        style.configure("Treeview.Heading",
            background="#1f1f1f",
            foreground="white",
            borderwidth=1,
            relief="flat",
            font=('Sans', 12, 'bold')
        )
        
        # Color cuando se pasa el mouse (hover)
        style.map('Treeview',
            background=[('selected', '#1f6aa5')],
            foreground=[('selected', 'white')]
        )
        
        # Eliminar las líneas del Treeview
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])

    def build_ui(self):
        # Frame principal con dos secciones
        main_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        main_frame.pack(fill='both', expand=True)

        # Sección superior: Lista de ventas
        ventas_frame = ctk.CTkFrame(main_frame)
        ventas_frame.pack(fill='both', expand=True, padx=10, pady=(10, 5))

        # Título
        header_frame = ctk.CTkFrame(ventas_frame, fg_color="transparent")
        header_frame.pack(fill='x', padx=10, pady=10)
        
        ctk.CTkLabel(
            header_frame, 
            text="📋 Historial de Ventas", 
            font=("Sans", 16, "bold")
        ).pack(side='left')
        
        ctk.CTkButton(
            header_frame, 
            text="🔄 Actualizar", 
            command=self.cargar_ventas, 
            width=120,
            height=35
        ).pack(side='right', padx=5)

        # Treeview de ventas - COLUMNAS CORREGIDAS
        columns_ventas = ('ID', 'Cliente', 'Total', 'Puntos', 'Fecha', 'Estado')
        self.tree_ventas = ttk.Treeview(ventas_frame, columns=columns_ventas, show='headings', height=8)
        
        # Configurar encabezados
        self.tree_ventas.heading('ID', text='ID')
        self.tree_ventas.column('ID', width=60, anchor='center')
        
        self.tree_ventas.heading('Cliente', text='Cliente')
        self.tree_ventas.column('Cliente', width=200)
        
        self.tree_ventas.heading('Total', text='Total')
        self.tree_ventas.column('Total', width=120, anchor='e')
        
        self.tree_ventas.heading('Puntos', text='⭐ Puntos')
        self.tree_ventas.column('Puntos', width=100, anchor='center')
        
        self.tree_ventas.heading('Fecha', text='Fecha')
        self.tree_ventas.column('Fecha', width=120, anchor='center')
        
        self.tree_ventas.heading('Estado', text='Estado')
        self.tree_ventas.column('Estado', width=120, anchor='center')

        # Scrollbar para treeview de ventas
        scrollbar_ventas = ttk.Scrollbar(ventas_frame, orient='vertical', command=self.tree_ventas.yview)
        self.tree_ventas.configure(yscrollcommand=scrollbar_ventas.set)

        self.tree_ventas.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=(0, 10))
        scrollbar_ventas.pack(side='right', fill='y', pady=(0, 10))

        # Enlazar evento de selección
        self.tree_ventas.bind('<<TreeviewSelect>>', self.seleccionar_venta)

        # Sección inferior: Detalles de la venta seleccionada
        detalles_frame = ctk.CTkFrame(main_frame)
        detalles_frame.pack(fill='both', expand=True, padx=10, pady=(5, 10))

        # Título de detalles
        det_header_frame = ctk.CTkFrame(detalles_frame, fg_color="transparent")
        det_header_frame.pack(fill='x', padx=10, pady=10)
        
        self.lbl_detalle_titulo = ctk.CTkLabel(
            det_header_frame, 
            text="📦 Detalles de Venta - Seleccione una venta", 
            font=("Sans", 14, "bold")
        )
        self.lbl_detalle_titulo.pack(side='left')

        # Treeview de artículos de la venta - COLUMNAS CORREGIDAS
        columns_detalles = ('Código', 'Artículo', 'Cantidad', 'Precio Unit.', 'Subtotal')
        self.tree_detalles = ttk.Treeview(detalles_frame, columns=columns_detalles, show='headings', height=6)
        
        # Configurar encabezados de detalles
        self.tree_detalles.heading('Código', text='Código')
        self.tree_detalles.column('Código', width=100, anchor='center')
        
        self.tree_detalles.heading('Artículo', text='Artículo')
        self.tree_detalles.column('Artículo', width=250)
        
        self.tree_detalles.heading('Cantidad', text='Cantidad')
        self.tree_detalles.column('Cantidad', width=100, anchor='center')
        
        self.tree_detalles.heading('Precio Unit.', text='Precio Unitario')
        self.tree_detalles.column('Precio Unit.', width=120, anchor='e')
        
        self.tree_detalles.heading('Subtotal', text='Subtotal')
        self.tree_detalles.column('Subtotal', width=120, anchor='e')

        # Scrollbar para treeview de detalles
        scrollbar_detalles = ttk.Scrollbar(detalles_frame, orient='vertical', command=self.tree_detalles.yview)
        self.tree_detalles.configure(yscrollcommand=scrollbar_detalles.set)

        self.tree_detalles.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=(0, 10))
        scrollbar_detalles.pack(side='right', fill='y', pady=(0, 10))

        # Información adicional de la venta
        self.info_frame = ctk.CTkFrame(detalles_frame, fg_color="#2b2b2b", corner_radius=10)
        self.info_frame.pack(fill='x', padx=10, pady=10)

        self.lbl_info_venta = ctk.CTkLabel(
            self.info_frame,
            text="Seleccione una venta para ver los detalles",
            font=("Sans", 12),
            wraplength=400
        )
        self.lbl_info_venta.pack(padx=10, pady=10)

    def cargar_ventas(self):
        try:
            # Limpiar treeview
            for item in self.tree_ventas.get_children():
                self.tree_ventas.delete(item)
            
            # Obtener ventas de la base de datos
            ventas = self.db.obtener_ventas()
            
            # Insertar datos en el treeview
            for venta in ventas:
                venta_list = list(venta)
                # Formatear total como moneda
                if len(venta_list) > 2:
                    venta_list[2] = f"${float(venta[2]):,.2f}"
                
                self.tree_ventas.insert('', 'end', values=tuple(venta_list))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando ventas: {str(e)}")

    def seleccionar_venta(self, event):
        try:
            # Obtener venta seleccionada
            seleccion = self.tree_ventas.selection()
            if not seleccion:
                return
                
            item = self.tree_ventas.item(seleccion[0])
            valores = item['values']
            
            if not valores:
                return
                
            self.venta_seleccionada = valores[0]  # ID de la venta
            
            # Actualizar título
            self.lbl_detalle_titulo.configure(
                text=f"📦 Detalles de Venta ID: {self.venta_seleccionada}"
            )
            
            # Cargar detalles de la venta
            self.cargar_detalles_venta(self.venta_seleccionada)
            
            # Mostrar información adicional
            self.mostrar_info_venta(valores)
            
        except Exception as e:
            print(f"Error seleccionando venta: {e}")

    def cargar_detalles_venta(self, venta_id):
        try:
            # Limpiar treeview de detalles
            for item in self.tree_detalles.get_children():
                self.tree_detalles.delete(item)
            
            # Obtener detalles de la venta
            detalles = self.db.obtener_detalles_venta(venta_id)
            
            # Insertar en el treeview
            for detalle in detalles:
                detalle_list = list(detalle)
                
                # Formatear precios como moneda
                if len(detalle_list) > 3:
                    detalle_list[3] = f"${float(detalle[3]):.2f}"
                if len(detalle_list) > 4:
                    detalle_list[4] = f"${float(detalle[4]):.2f}"
                
                # Marcar promociones
                if len(detalle_list) > 5 and detalle[5]:  # es_promocion
                    detalle_list[1] += " 🎁"
                
                self.tree_detalles.insert('', 'end', values=tuple(detalle_list))
                
        except Exception as e:
            print(f"Error cargando detalles: {e}")

    def mostrar_info_venta(self, venta_info):
        try:
            if len(venta_info) >= 6:
                info_text = (
                    f"👤 Cliente: {venta_info[1]}\n"
                    f"💰 Total: {venta_info[2]}\n"
                    f"⭐ Puntos: {venta_info[3]}\n"
                    f"📅 Fecha: {venta_info[4]}\n"
                    f"📊 Estado: {venta_info[5]}"
                )
                self.lbl_info_venta.configure(text=info_text)
        except Exception as e:
            print(f"Error mostrando info: {e}")

    def cargar_ventas(self):
        """Cargar todas las ventas"""
        try:
            # Limpiar árbol
            for item in self.tree_ventas.get_children():
                self.tree_ventas.delete(item)
            
            # Obtener ventas
            ventas = self.db.obtener_ventas()
            
            for venta in ventas:
                # Formatear el total con símbolo de moneda
                venta_list = list(venta)
                venta_list[2] = f"${venta[2]:,.2f}"
                self.tree_ventas.insert('', 'end', values=tuple(venta_list))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando ventas: {str(e)}")

    def seleccionar_venta(self, event):
        """Cuando se selecciona una venta, mostrar sus detalles"""
        selected = self.tree_ventas.selection()
        if not selected:
            return
            
        try:
            item = self.tree_ventas.item(selected[0])
            values = item['values']
            
            if values:
                venta_id = values[0]
                self.venta_seleccionada = venta_id
                self.cargar_detalles(venta_id)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error seleccionando venta: {str(e)}")

    def cargar_detalles(self, venta_id):
        """Cargar los detalles de una venta específica"""
        try:
            # Limpiar árbol de detalles
            for item in self.tree_detalles.get_children():
                self.tree_detalles.delete(item)
            
            # Obtener detalles de la venta
            detalles = self.db.obtener_detalles_venta(venta_id)
            
            total = 0
            for detalle in detalles:
                # detalle = (articulo_nombre, cantidad, precio_unitario, subtotal)
                detalle_formateado = (
                    detalle[0],  # Artículo
                    detalle[1],  # Cantidad
                    f"${detalle[2]:,.2f}",  # Precio unitario
                    f"${detalle[3]:,.2f}"   # Subtotal
                )
                self.tree_detalles.insert('', 'end', values=detalle_formateado)
                total += detalle[3]
            
            # Actualizar label de total
            self.lbl_total.configure(
                text=f"💰 Total de la venta: ${total:,.2f}"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando detalles: {str(e)}")

    def eliminar_venta_seleccionada(self):
        """Eliminar la venta seleccionada"""
        if not self.venta_seleccionada:
            messagebox.showwarning("Advertencia", "Seleccione una venta para eliminar")
            return
        
        respuesta = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro de eliminar la venta #{self.venta_seleccionada}?\n\n"
            "Esta acción:\n"
            "• Eliminará todos los detalles de la venta\n"
            "• Restaurará el stock de los artículos\n"
            "• No se puede deshacer"
        )
        
        if respuesta:
            try:
                ok, msg = self.db.eliminar_venta(self.venta_seleccionada)
                if ok:
                    messagebox.showinfo("Éxito", msg)
                    self.venta_seleccionada = None
                    self.cargar_ventas()
                    
                    # Limpiar detalles
                    for item in self.tree_detalles.get_children():
                        self.tree_detalles.delete(item)
                    self.lbl_total.configure(text="Seleccione una venta para ver detalles")
                else:
                    messagebox.showerror("Error", msg)
            except Exception as e:
                messagebox.showerror("Error", f"Error eliminando venta: {str(e)}")
