import customtkinter as ctk
from tkinter import ttk, messagebox
from dbVentas import DBVentas
from dbArticulos import DBArticulos
from dbClientes import DBClientes
from conexion import ConexionDB

class VentasUI:
    def __init__(self, parent, usuario_actual=None):
        self.parent = parent
        self.usuario_actual = usuario_actual
        self.con = ConexionDB()
        self.db_ventas = DBVentas(self.con)
        self.db_articulos = DBArticulos(self.con)
        self.db_clientes = DBClientes(self.con)
        
        main_container = ctk.CTkFrame(parent)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.frame = ctk.CTkFrame(main_container)
        self.frame.pack(fill='both', expand=True)

        if not usuario_actual:
            ctk.CTkLabel(self.frame, text="Acceso denegado",
                font=("Sans", 14), text_color='red').pack(expand=True)
            return

        self.var_cliente_id = ctk.StringVar()
        self.var_cliente_nombre = ctk.StringVar()
        self.var_cliente_puntos = ctk.IntVar(value=0)
        self.var_articulo_id = ctk.StringVar()
        self.var_articulo_nombre = ctk.StringVar()
        self.var_cantidad = ctk.StringVar(value="1")
        self.var_precio = ctk.StringVar(value="0.0")
        self.var_total_venta = ctk.DoubleVar(value=0.0)

        self.carrito = []
        self.promo_window = None  # Referencia a la ventana de promoción
        self.configurar_estilo_treeview()
        self.build_ui()
        self.cargar_ventas()
        self.cargar_clientes()
        self.cargar_articulos()

    def configurar_estilo_treeview(self):
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

        # Sección de nueva venta
        venta_frame = ctk.CTkFrame(main_frame)
        venta_frame.pack(fill='x', padx=10, pady=10)

        ctk.CTkLabel(venta_frame, text="💰 Nueva Venta", font=("Sans", 18, "bold")).pack(pady=10)

        # Formulario de venta
        form_frame = ctk.CTkFrame(venta_frame)
        form_frame.pack(fill='x', padx=20, pady=10)

        # Cliente con búsqueda por ID
        cliente_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        cliente_frame.pack(fill='x', pady=5)
        
        ctk.CTkLabel(cliente_frame, text="👤 Cliente:", width=100, font=("Sans", 12, "bold")).pack(side='left', padx=5)
        
        # Entry para ID del cliente
        ctk.CTkLabel(cliente_frame, text="ID:", font=("Sans", 11)).pack(side='left', padx=(10, 2))
        self.entry_cliente_id = ctk.CTkEntry(cliente_frame, textvariable=self.var_cliente_id, width=60, height=35)
        self.entry_cliente_id.pack(side='left', padx=2)
        self.entry_cliente_id.bind('<Return>', lambda e: self.buscar_cliente_por_id())
        
        ctk.CTkButton(
            cliente_frame,
            text="🔍",
            command=self.buscar_cliente_por_id,
            width=40,
            height=35
        ).pack(side='left', padx=2)
        
        # ComboBox para nombre
        self.combo_clientes = ctk.CTkComboBox(
            cliente_frame, 
            variable=self.var_cliente_nombre, 
            width=300,
            height=35,
            command=self.seleccionar_cliente
        )
        self.combo_clientes.pack(side='left', padx=5)
        
        # Mostrar puntos del cliente
        self.lbl_puntos_cliente = ctk.CTkLabel(
            cliente_frame,
            text="⭐ Puntos: 0",
            font=("Sans", 12, "bold"),
            text_color="#ffa500"
        )
        self.lbl_puntos_cliente.pack(side='left', padx=10)
        
        # Botón canjear puntos
        self.btn_canjear = ctk.CTkButton(
            cliente_frame,
            text="🎁 Canjear 50 Puntos",
            command=self.mostrar_promociones,
            width=150,
            height=35,
            fg_color="#ff9800",
            hover_color="#f57c00"
        )
        self.btn_canjear.pack(side='left', padx=5)

        # Artículo
        articulo_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        articulo_frame.pack(fill='x', pady=5)
        
        ctk.CTkLabel(articulo_frame, text="💊 Artículo:", width=100, font=("Sans", 12, "bold")).pack(side='left', padx=5)
        self.combo_articulos = ctk.CTkComboBox(
            articulo_frame, 
            variable=self.var_articulo_nombre, 
            width=500,
            height=35,
            command=self.seleccionar_articulo
        )
        self.combo_articulos.pack(side='left', padx=5, fill='x', expand=True)

        # Cantidad y Precio
        datos_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        datos_frame.pack(fill='x', pady=5)

        ctk.CTkLabel(datos_frame, text="Cantidad:", width=100, font=("Sans", 12, "bold")).pack(side='left', padx=5)
        self.entry_cantidad = ctk.CTkEntry(datos_frame, textvariable=self.var_cantidad, width=100, height=35)
        self.entry_cantidad.pack(side='left', padx=5)

        ctk.CTkLabel(datos_frame, text="Precio:", width=100, font=("Sans", 12, "bold")).pack(side='left', padx=(20,5))
        self.entry_precio = ctk.CTkEntry(datos_frame, textvariable=self.var_precio, width=100, height=35, state='readonly')
        self.entry_precio.pack(side='left', padx=5)

        # Botones de venta
        botones_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        botones_frame.pack(fill='x', pady=15)

        ctk.CTkButton(
            botones_frame, 
            text="➕ Agregar al Carrito", 
            command=self.agregar_al_carrito, 
            width=160,
            height=40,
            font=("Sans", 13, "bold")
        ).pack(side='left', padx=5)
        
        ctk.CTkButton(
            botones_frame, 
            text="💳 Procesar Venta", 
            command=self.procesar_venta, 
            width=160,
            height=40,
            font=("Sans", 13, "bold"),
            fg_color="#107c10", 
            hover_color="#0e6a0e"
        ).pack(side='left', padx=5)
        
        ctk.CTkButton(
            botones_frame, 
            text="🗑️ Limpiar Carrito", 
            command=self.limpiar_carrito, 
            width=160,
            height=40,
            font=("Sans", 13, "bold"),
            fg_color="#d13438", 
            hover_color="#a42c2f"
        ).pack(side='left', padx=5)

        # Carrito de compras
        carrito_frame = ctk.CTkFrame(main_frame)
        carrito_frame.pack(fill='x', padx=10, pady=5)

        ctk.CTkLabel(carrito_frame, text="🛒 Carrito de Compras", font=("Sans", 14, "bold")).pack(pady=5)

        # Treeview del carrito - AGREGADO CÓDIGO
        columns_carrito = ('Código', 'Artículo', 'Cantidad', 'Precio Unit.', 'Subtotal')
        self.tree_carrito = ttk.Treeview(carrito_frame, columns=columns_carrito, show='headings', height=6)
        
        self.tree_carrito.heading('Código', text='Código')
        self.tree_carrito.column('Código', width=100, anchor='center')
        
        self.tree_carrito.heading('Artículo', text='Artículo')
        self.tree_carrito.column('Artículo', width=250)
        
        self.tree_carrito.heading('Cantidad', text='Cantidad')
        self.tree_carrito.column('Cantidad', width=100, anchor='center')
        
        self.tree_carrito.heading('Precio Unit.', text='Precio Unitario')
        self.tree_carrito.column('Precio Unit.', width=120, anchor='e')
        
        self.tree_carrito.heading('Subtotal', text='Subtotal')
        self.tree_carrito.column('Subtotal', width=120, anchor='e')

        self.tree_carrito.pack(fill='x', padx=10, pady=5)
        self.tree_carrito.bind('<Double-1>', self.eliminar_del_carrito)

        # Total y puntos a ganar
        total_frame = ctk.CTkFrame(carrito_frame, fg_color="#2b2b2b", corner_radius=10)
        total_frame.pack(fill='x', padx=10, pady=5)

        ctk.CTkLabel(total_frame, text="💰 Total Venta:", font=("Sans", 14, "bold")).pack(side='left', padx=15, pady=10)
        self.lbl_total = ctk.CTkLabel(total_frame, text="$0.00", font=("Sans", 16, "bold"), text_color="#4caf50")
        self.lbl_total.pack(side='left', padx=5, pady=10)
        
        self.lbl_puntos_ganar = ctk.CTkLabel(
            total_frame,
            text="⭐ Puntos a ganar: 0",
            font=("Sans", 13, "bold"),
            text_color="#ffa500"
        )
        self.lbl_puntos_ganar.pack(side='right', padx=15, pady=10)

        # Historial de ventas
        historial_frame = ctk.CTkFrame(main_frame)
        historial_frame.pack(fill='both', expand=True, padx=10, pady=10)

        header_frame = ctk.CTkFrame(historial_frame, fg_color="transparent")
        header_frame.pack(fill='x', padx=10, pady=(10, 5))
        
        ctk.CTkLabel(header_frame, text="📋 Historial de Ventas", font=("Sans", 14, "bold")).pack(side='left')
        
        ctk.CTkButton(
            header_frame, 
            text="🔄 Actualizar", 
            command=self.cargar_ventas, 
            width=120,
            height=35
        ).pack(side='right', padx=5)

        # Treeview de ventas
        columns_ventas = ('ID', 'Cliente', 'Total', 'Puntos', 'Fecha', 'Estado')
        self.tree_ventas = ttk.Treeview(historial_frame, columns=columns_ventas, show='headings', height=12)
        
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

        scrollbar = ttk.Scrollbar(historial_frame, orient='vertical', command=self.tree_ventas.yview)
        self.tree_ventas.configure(yscrollcommand=scrollbar.set)

        self.tree_ventas.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=(0, 10))
        scrollbar.pack(side='right', fill='y', pady=(0, 10))

    def buscar_cliente_por_id(self):
        """Buscar cliente por ID"""
        try:
            cliente_id = self.var_cliente_id.get().strip()
            if not cliente_id:
                return
            
            cliente = self.db_clientes.obtener_cliente(cliente_id)
            if cliente:
                self.var_cliente_nombre.set(f"{cliente[2]} {cliente[3]}")  # nombre apellido
                self.var_cliente_puntos.set(cliente[7])  # puntos
                self.lbl_puntos_cliente.configure(text=f"⭐ Puntos: {cliente[7]}")
                
                # Verificar si el cliente alcanzó los 50 puntos y mostrar promoción automáticamente
                if cliente[7] >= 50:
                    self.mostrar_promociones_automatico()
            else:
                messagebox.showwarning("No encontrado", f"No existe cliente con ID: {cliente_id}")
                self.var_cliente_id.set("")
        except Exception as e:
            messagebox.showerror("Error", f"Error buscando cliente: {str(e)}")

    def cargar_clientes(self):
        try:
            clientes = self.db_clientes.obtener_clientes()
            nombres_clientes = [f"ID:{cliente[0]} - {cliente[2]} {cliente[3]} (⭐{cliente[7]})" for cliente in clientes]
            self.combo_clientes.configure(values=nombres_clientes)
        except Exception as e:
            print(f"Error cargando clientes: {e}")

    def cargar_articulos(self):
        try:
            articulos = self.db_articulos.obtener_articulos()
            nombres_articulos = [
                f"[{articulo[1]}] {articulo[2]} - ${articulo[4]} (Stock: {articulo[5]})" 
                for articulo in articulos
            ]
            self.combo_articulos.configure(values=nombres_articulos)
        except Exception as e:
            print(f"Error cargando artículos: {e}")

    def seleccionar_cliente(self, choice):
        try:
            # Extraer ID del formato "ID:X - Nombre..."
            if choice and "ID:" in choice:
                cliente_id = choice.split("ID:")[1].split(" -")[0]
                self.var_cliente_id.set(cliente_id)
                
                cliente = self.db_clientes.obtener_cliente(cliente_id)
                if cliente:
                    self.var_cliente_puntos.set(cliente[7])
                    self.lbl_puntos_cliente.configure(text=f"⭐ Puntos: {cliente[7]}")
                    
                    # Verificar si el cliente alcanzó los 50 puntos y mostrar promoción automáticamente
                    if cliente[7] >= 50:
                        self.mostrar_promociones_automatico()
        except Exception as e:
            print(f"Error seleccionando cliente: {e}")

    def seleccionar_articulo(self, choice):
        try:
            if choice:
                # Extraer código del formato "[CODIGO] Nombre..."
                codigo = choice.split("[")[1].split("]")[0]
                articulos = self.db_articulos.obtener_articulos()
                for articulo in articulos:
                    if articulo[1] == codigo:
                        self.var_articulo_id.set(str(articulo[0]))
                        self.var_precio.set(str(float(articulo[4])))
                        print(f"Artículo seleccionado: {articulo[2]} (Código: {codigo})")
                        break
        except Exception as e:
            print(f"Error seleccionando artículo: {e}")

    def mostrar_promociones_automatico(self):
        """Mostrar promociones automáticamente cuando el cliente alcanza 50 puntos"""
        if not self.var_cliente_id.get():
            return
        
        puntos_actuales = self.var_cliente_puntos.get()
        if puntos_actuales >= 50:
            # Pequeña pausa para que no sea intrusivo
            self.parent.after(1000, self.mostrar_promociones)

    def mostrar_promociones(self):
        """Mostrar ventana para canjear puntos por promociones"""
        if not self.var_cliente_id.get():
            messagebox.showwarning("Advertencia", "Seleccione un cliente primero")
            return
        
        # Cerrar ventana anterior si existe
        if self.promo_window and self.promo_window.winfo_exists():
            self.promo_window.destroy()
        
        puntos_actuales = self.var_cliente_puntos.get()
        if puntos_actuales < 50:
            messagebox.showinfo(
                "Puntos insuficientes",
                f"El cliente tiene {puntos_actuales} puntos.\nNecesita 50 puntos para canjear una promoción."
            )
            return
        
        # Ventana de promociones
        self.promo_window = ctk.CTkToplevel(self.parent)
        self.promo_window.title("🎁 Artículos en Promoción")
        self.promo_window.geometry("600x500")
        self.promo_window.resizable(False, False)
        
        # Centrar ventana
        self.promo_window.update_idletasks()
        x = (self.promo_window.winfo_screenwidth() - 600) // 2
        y = (self.promo_window.winfo_screenheight() - 500) // 2
        self.promo_window.geometry(f"600x500+{x}+{y}")
        
        # Hacer la ventana modal
        self.promo_window.transient(self.parent)
        self.promo_window.grab_set()
        
        # Título
        title_frame = ctk.CTkFrame(self.promo_window, fg_color="#1f6aa5", corner_radius=10)
        title_frame.pack(fill='x', padx=20, pady=20)
        
        ctk.CTkLabel(
            title_frame,
            text="🎁 ¡Felicidades! Puedes canjear tus puntos",
            font=("Sans", 16, "bold"),
            text_color="white"
        ).pack(pady=10)
        
        ctk.CTkLabel(
            title_frame,
            text=f"Puntos disponibles: {puntos_actuales}",
            font=("Sans", 14),
            text_color="white"
        ).pack(pady=(0, 10))
        
        # Lista de promociones
        promos_frame = ctk.CTkFrame(self.promo_window)
        promos_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(
            promos_frame,
            text="Selecciona un artículo para canjear 50 puntos:",
            font=("Sans", 12, "bold")
        ).pack(pady=10)
        
        # Lista de promociones
        promos = self.db_articulos.obtener_articulos_promocion()
        
        if not promos:
            ctk.CTkLabel(
                promos_frame,
                text="No hay artículos en promoción disponibles",
                font=("Sans", 14)
            ).pack(pady=20)
        else:
            # Frame scrollable para promociones
            scroll_frame = ctk.CTkScrollableFrame(promos_frame, height=250)
            scroll_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            for promo in promos:
                promo_frame = ctk.CTkFrame(scroll_frame, corner_radius=8)
                promo_frame.pack(fill='x', padx=5, pady=5)
                
                # Información del artículo
                info_frame = ctk.CTkFrame(promo_frame, fg_color="transparent")
                info_frame.pack(fill='x', padx=10, pady=8)
                
                ctk.CTkLabel(
                    info_frame,
                    text=f"📦 {promo[2]}",
                    font=("Sans", 12, "bold"),
                    anchor='w'
                ).pack(fill='x')
                
                ctk.CTkLabel(
                    info_frame,
                    text=f"🔢 Código: {promo[1]} | 💰 Precio regular: ${promo[4]}",
                    font=("Sans", 10),
                    anchor='w',
                    text_color="gray"
                ).pack(fill='x')
                
                ctk.CTkLabel(
                    info_frame,
                    text=f"📝 {promo[3] if promo[3] else 'Sin descripción'}",
                    font=("Sans", 10),
                    anchor='w',
                    text_color="lightgray"
                ).pack(fill='x')
                
                # Botón canjear
                ctk.CTkButton(
                    promo_frame,
                    text="🎁 Canjear por 50 puntos",
                    command=lambda p=promo: self.canjear_promocion(p),
                    width=200,
                    height=35,
                    fg_color="#ff9800",
                    hover_color="#f57c00"
                ).pack(pady=5)
        
        # Botón de rechazar canjeo
        button_frame = ctk.CTkFrame(self.promo_window, fg_color="transparent")
        button_frame.pack(fill='x', padx=20, pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="❌ Rechazar Canjeo",
            command=self.rechazar_canjeo,
            width=200,
            height=40,
            fg_color="#757575",
            hover_color="#616161",
            font=("Sans", 12, "bold")
        ).pack(pady=5)
        
        ctk.CTkLabel(
            button_frame,
            text="Los puntos se restablecerán a 0 sin importar tu elección",
            font=("Sans", 10),
            text_color="gray"
        ).pack()

    def rechazar_canjeo(self):
        """Rechazar el canjeo y restablecer puntos a 0"""
        try:
            # Restablecer puntos a 0 en la interfaz
            self.var_cliente_puntos.set(0)
            self.lbl_puntos_cliente.configure(text="⭐ Puntos: 0")
            
            # Cerrar ventana de promoción
            if self.promo_window and self.promo_window.winfo_exists():
                self.promo_window.destroy()
            
            messagebox.showinfo("Canjeo Rechazado", "Has rechazado el canjeo. Los puntos se han restablecido a 0.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error rechazando canjeo: {str(e)}")

    def canjear_promocion(self, articulo):
        """Agregar artículo de promoción al carrito"""
        try:
            # Agregar al carrito con precio 0 y cantidad 1
            item_carrito = {
                'articulo_id': articulo[0],
                'articulo_codigo': articulo[1],
                'articulo_nombre': articulo[2],
                'cantidad': 1,
                'precio': 0.0,
                'subtotal': 0.0,
                'es_promocion': True
            }
            self.carrito.append(item_carrito)
            self.actualizar_carrito_ui()
            
            # Restablecer puntos a 0 en la interfaz
            self.var_cliente_puntos.set(0)
            self.lbl_puntos_cliente.configure(text="⭐ Puntos: 0")
            
            # Cerrar ventana de promoción
            if self.promo_window and self.promo_window.winfo_exists():
                self.promo_window.destroy()
            
            messagebox.showinfo("✅ Éxito", f"Promoción agregada: {articulo[2]}\nPuntos restablecidos a 0")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error canjeando promoción: {str(e)}")

    def agregar_al_carrito(self):
        if not self.validar_item_venta():
            return

        try:
            articulo_id = self.var_articulo_id.get()
            # Extraer código y nombre
            articulo_info = self.var_articulo_nombre.get()
            articulo_codigo = articulo_info.split("[")[1].split("]")[0]
            articulo_nombre = articulo_info.split("] ")[1].split(" - $")[0]
            
            cantidad = int(self.var_cantidad.get())
            precio = float(self.var_precio.get())
            subtotal = cantidad * precio

            # Verificar stock
            articulo = self.db_articulos.obtener_articulo(articulo_id)
            if not articulo:
                messagebox.showerror("Error", "Artículo no encontrado")
                return

            stock_actual = articulo[5]
            if cantidad > stock_actual:
                messagebox.showerror("Error", f"Stock insuficiente. Stock actual: {stock_actual}")
                return

            # Verificar si el artículo ya está en el carrito
            articulo_en_carrito = None
            for item in self.carrito:
                if item['articulo_id'] == articulo_id and not item.get('es_promocion', False):
                    articulo_en_carrito = item
                    break

            if articulo_en_carrito:
                # Sumar cantidad al artículo existente
                articulo_en_carrito['cantidad'] += cantidad
                articulo_en_carrito['subtotal'] = articulo_en_carrito['cantidad'] * articulo_en_carrito['precio']
            else:
                # Agregar nuevo artículo al carrito
                item_carrito = {
                    'articulo_id': articulo_id,
                    'articulo_codigo': articulo_codigo,
                    'articulo_nombre': articulo_nombre,
                    'cantidad': cantidad,
                    'precio': precio,
                    'subtotal': subtotal,
                    'es_promocion': False
                }
                self.carrito.append(item_carrito)

            self.actualizar_carrito_ui()
            self.limpiar_item_formulario()
            
            messagebox.showinfo("✅ Éxito", "Artículo agregado al carrito")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error agregando al carrito: {str(e)}")

    def actualizar_carrito_ui(self):
        for item in self.tree_carrito.get_children():
            self.tree_carrito.delete(item)

        total = 0
        for item in self.carrito:
            self.tree_carrito.insert('', 'end', values=(
                item['articulo_codigo'],
                item['articulo_nombre'] + (" 🎁" if item.get('es_promocion') else ""),
                item['cantidad'],
                f"${item['precio']:.2f}",
                f"${item['subtotal']:.2f}"
            ))
            total += item['subtotal']

        # Calcular puntos a ganar (4 puntos por cada $100)
        puntos_a_ganar = int(total // 100 * 4)
        
        self.var_total_venta.set(total)
        self.lbl_total.configure(text=f"${total:.2f}")
        self.lbl_puntos_ganar.configure(text=f"⭐ Puntos a ganar: {puntos_a_ganar}")

    def eliminar_del_carrito(self, event):
        try:
            item_seleccionado = self.tree_carrito.selection()
            if item_seleccionado:
                if messagebox.askyesno("Confirmar", "¿Eliminar este artículo del carrito?"):
                    index = self.tree_carrito.index(item_seleccionado[0])
                    if 0 <= index < len(self.carrito):
                        # Si es promoción, ya no podemos devolver los puntos porque se restablecieron a 0
                        self.carrito.pop(index)
                        self.actualizar_carrito_ui()
        except Exception as e:
            print(f"Error eliminando del carrito: {e}")

    def limpiar_item_formulario(self):
        self.var_articulo_id.set("")
        self.var_articulo_nombre.set("")
        self.var_cantidad.set("1")
        self.var_precio.set("0.0")

    def limpiar_carrito(self):
        if self.carrito and not messagebox.askyesno("Confirmar", "¿Limpiar todo el carrito?"):
            return
            
        self.carrito = []
        self.actualizar_carrito_ui()
        self.var_cliente_id.set("")
        self.var_cliente_nombre.set("")
        self.var_cliente_puntos.set(0)
        self.lbl_puntos_cliente.configure(text="⭐ Puntos: 0")

    def procesar_venta(self):
        if not self.carrito:
            messagebox.showwarning("Advertencia", "El carrito está vacío")
            return

        if not self.var_cliente_id.get():
            messagebox.showwarning("Validación", "Seleccione un cliente")
            return

        try:
            cliente_id = self.var_cliente_id.get()
            total_venta = float(self.var_total_venta.get())
            puntos_a_ganar = int(total_venta // 100 * 4)
            usuario_id = self.usuario_actual.get('id')
            
            # Verificar si hay promociones en el carrito
            tiene_promocion = any(item.get('es_promocion') for item in self.carrito)

            # Crear venta
            venta_id = self.db_ventas.crear_venta({
                'cliente_id': cliente_id,
                'total': total_venta,
                'puntos_ganados': puntos_a_ganar,
                'usuario_id': usuario_id
            })

            if venta_id:
                # Crear detalles de venta y actualizar stock
                for item in self.carrito:
                    self.db_ventas.crear_detalle_venta({
                        'venta_id': venta_id,
                        'articulo_id': item['articulo_id'],
                        'articulo_codigo': item['articulo_codigo'],
                        'cantidad': item['cantidad'],
                        'precio_unitario': item['precio'],
                        'subtotal': item['subtotal'],
                        'es_promocion': item.get('es_promocion', False)
                    })

                    # Actualizar stock (solo para artículos no promocionales)
                    if not item.get('es_promocion'):
                        self.db_articulos.actualizar_stock(item['articulo_id'], -item['cantidad'])

                # Actualizar puntos del cliente
                self.db_clientes.actualizar_puntos(cliente_id, puntos_a_ganar)
                
                # Si canjeó promoción, descontar 50 puntos por cada promoción
                if tiene_promocion:
                    promociones_count = sum(1 for item in self.carrito if item.get('es_promocion'))
                    self.db_clientes.canjear_puntos(cliente_id, promociones_count * 50)

                mensaje = f"Venta procesada correctamente\n\nID Venta: {venta_id}\nTotal: ${total_venta:.2f}\n⭐ Puntos ganados: {puntos_a_ganar}"
                
                if tiene_promocion:
                    promociones_count = sum(1 for item in self.carrito if item.get('es_promocion'))
                    mensaje += f"\n🎁 Promociones canjeadas: {promociones_count}"

                messagebox.showinfo("✅ Éxito", mensaje)
                self.limpiar_carrito()
                self.cargar_ventas()
                self.cargar_articulos()
                self.cargar_clientes()
            else:
                messagebox.showerror("Error", "No se pudo procesar la venta")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error procesando venta: {str(e)}")

    def cargar_ventas(self):
        try:
            for item in self.tree_ventas.get_children():
                self.tree_ventas.delete(item)
            
            ventas = self.db_ventas.obtener_ventas()
            for venta in ventas:
                venta_list = list(venta)
                if len(venta_list) > 2:
                    venta_list[2] = f"${float(venta[2]):,.2f}"
                self.tree_ventas.insert('', 'end', values=tuple(venta_list))
        except Exception as e:
            print(f"Error cargando ventas: {e}")

    def validar_item_venta(self):
        if not self.var_articulo_id.get() or not self.var_articulo_nombre.get():
            messagebox.showwarning("Validación", "Debe seleccionar un artículo del menú desplegable")
            return False
        
        try:
            cantidad = int(self.var_cantidad.get())
            if cantidad <= 0:
                messagebox.showwarning("Validación", "La cantidad debe ser mayor a 0")
                return False
        except ValueError:
            messagebox.showwarning("Validación", "La cantidad debe ser un número válido")
            return False
        
        try:
            precio = float(self.var_precio.get())
            if precio <= 0:
                messagebox.showwarning("Validación", "El precio debe ser mayor a 0")
                return False
        except ValueError:
            messagebox.showwarning("Validación", "El precio debe ser un número válido")
            return False
        
        return True