import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime, date
from DB.dbCompras import DBCompras
from DB.dbArticulos import DBArticulos
from conexion import ConexionDB

class ComprasUI:
    def __init__(self, parent, usuario_actual=None):
        self.parent = parent
        self.usuario_actual = usuario_actual
        self.con = ConexionDB()
        self.db_compras = DBCompras(self.con)
        self.db_articulos = DBArticulos(self.con)
        
        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(fill='both', expand=True, padx=10, pady=10)

        if not usuario_actual:
            ctk.CTkLabel(self.frame, text="Acceso denegado",
                font=("Sans", 14), text_color='red').pack(expand=True)
            return

        self.var_folio = ctk.StringVar()
        self.var_fecha = ctk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        self.var_articulo_id = ctk.StringVar()
        self.var_articulo_nombre = ctk.StringVar()
        self.var_cantidad = ctk.StringVar(value="1")
        self.var_precio = ctk.StringVar(value="0.0")
        self.var_total_compra = ctk.DoubleVar(value=0.0)

        self.carrito = []
        self.articulos_data = {}  # Diccionario para mapear nombres a datos completos
        self.configurar_estilo_treeview()
        self.build_ui()
        self.cargar_compras()
        self.cargar_articulos()
        self.actualizar_estado_botones()

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

        # Sección de nueva compra
        compra_frame = ctk.CTkFrame(main_frame)
        compra_frame.pack(fill='x', padx=10, pady=10)

        ctk.CTkLabel(compra_frame, text="📦 Nueva Compra", font=("Sans", 18, "bold")).pack(pady=10)

        # Formulario de compra
        form_frame = ctk.CTkFrame(compra_frame)
        form_frame.pack(fill='x', padx=20, pady=10)

        # Folio
        datos_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        datos_frame.pack(fill='x', pady=5)

        ctk.CTkLabel(datos_frame, text="📋 Folio:", width=100, font=("Sans", 12, "bold")).pack(side='left', padx=5)
        self.entry_folio = ctk.CTkEntry(datos_frame, textvariable=self.var_folio, width=200, height=35)
        self.entry_folio.pack(side='left', padx=5)
        self.entry_folio.bind('<KeyRelease>', lambda e: self.actualizar_estado_botones())

        # Fecha
        fecha_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        fecha_frame.pack(fill='x', pady=5)

        ctk.CTkLabel(fecha_frame, text="📅 Fecha:", width=100, font=("Sans", 12, "bold")).pack(side='left', padx=5)
        self.entry_fecha = ctk.CTkEntry(fecha_frame, textvariable=self.var_fecha, width=150, height=35)
        self.entry_fecha.pack(side='left', padx=5)
        self.entry_fecha.bind('<KeyRelease>', lambda e: self.actualizar_estado_botones())

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
        self.combo_articulos.bind('<KeyRelease>', lambda e: self.actualizar_estado_botones())

        # Cantidad y Precio
        datos_art_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        datos_art_frame.pack(fill='x', pady=5)

        ctk.CTkLabel(datos_art_frame, text="Cantidad:", width=100, font=("Sans", 12, "bold")).pack(side='left', padx=5)
        self.entry_cantidad = ctk.CTkEntry(datos_art_frame, textvariable=self.var_cantidad, width=100, height=35)
        self.entry_cantidad.pack(side='left', padx=5)
        self.entry_cantidad.bind('<KeyRelease>', lambda e: self.actualizar_estado_botones())

        ctk.CTkLabel(datos_art_frame, text="Precio Compra:", width=120, font=("Sans", 12, "bold")).pack(side='left', padx=(20,5))
        self.entry_precio = ctk.CTkEntry(datos_art_frame, textvariable=self.var_precio, width=100, height=35)
        self.entry_precio.pack(side='left', padx=5)
        self.entry_precio.bind('<KeyRelease>', lambda e: self.actualizar_estado_botones())

        # Botones de compra
        botones_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        botones_frame.pack(fill='x', pady=15)

        self.btn_agregar = ctk.CTkButton(
            botones_frame, 
            text="➕ Agregar al Carrito", 
            command=self.agregar_al_carrito, 
            width=160,
            height=40,
            font=("Sans", 13, "bold")
        )
        self.btn_agregar.pack(side='left', padx=5)
        
        self.btn_procesar = ctk.CTkButton(
            botones_frame, 
            text="💳 Procesar Compra", 
            command=self.procesar_compra, 
            width=160,
            height=40,
            font=("Sans", 13, "bold"),
            fg_color="#107c10", 
            hover_color="#0e6a0e"
        )
        self.btn_procesar.pack(side='left', padx=5)
        
        self.btn_limpiar = ctk.CTkButton(
            botones_frame, 
            text="🗑️ Limpiar Carrito", 
            command=self.limpiar_carrito, 
            width=160,
            height=40,
            font=("Sans", 13, "bold"),
            fg_color="#d13438", 
            hover_color="#a42c2f"
        )
        self.btn_limpiar.pack(side='left', padx=5)

        # Carrito de compras
        carrito_frame = ctk.CTkFrame(main_frame)
        carrito_frame.pack(fill='x', padx=10, pady=5)

        ctk.CTkLabel(carrito_frame, text="🛒 Carrito de Compras", font=("Sans", 14, "bold")).pack(pady=5)

        # Treeview del carrito
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

        # Total
        total_frame = ctk.CTkFrame(carrito_frame, fg_color="#2b2b2b", corner_radius=10)
        total_frame.pack(fill='x', padx=10, pady=5)

        ctk.CTkLabel(total_frame, text="💰 Total Compra:", font=("Sans", 14, "bold")).pack(side='left', padx=15, pady=10)
        self.lbl_total = ctk.CTkLabel(total_frame, text="$0.00", font=("Sans", 16, "bold"), text_color="#4caf50")
        self.lbl_total.pack(side='left', padx=5, pady=10)

        # Historial de compras
        historial_frame = ctk.CTkFrame(main_frame)
        historial_frame.pack(fill='both', expand=True, padx=10, pady=10)

        header_frame = ctk.CTkFrame(historial_frame, fg_color="transparent")
        header_frame.pack(fill='x', padx=10, pady=(10, 5))
        
        ctk.CTkLabel(header_frame, text="📋 Historial de Compras", font=("Sans", 14, "bold")).pack(side='left')
        
        ctk.CTkButton(
            header_frame, 
            text="🔄 Actualizar", 
            command=self.cargar_compras, 
            width=120,
            height=35
        ).pack(side='right', padx=5)

        # Treeview de compras
        columns_compras = ('ID', 'Folio', 'Total', 'Fecha', 'Estado')
        self.tree_compras = ttk.Treeview(historial_frame, columns=columns_compras, show='headings', height=12)
        
        self.tree_compras.heading('ID', text='ID')
        self.tree_compras.column('ID', width=60, anchor='center')
        
        self.tree_compras.heading('Folio', text='Folio')
        self.tree_compras.column('Folio', width=120, anchor='center')
        
        self.tree_compras.heading('Total', text='Total')
        self.tree_compras.column('Total', width=120, anchor='e')
        
        self.tree_compras.heading('Fecha', text='Fecha')
        self.tree_compras.column('Fecha', width=120, anchor='center')
        
        self.tree_compras.heading('Estado', text='Estado')
        self.tree_compras.column('Estado', width=120, anchor='center')

        scrollbar = ttk.Scrollbar(historial_frame, orient='vertical', command=self.tree_compras.yview)
        self.tree_compras.configure(yscrollcommand=scrollbar.set)

        self.tree_compras.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=(0, 10))
        scrollbar.pack(side='right', fill='y', pady=(0, 10))

    def cargar_articulos(self):
        try:
            articulos = self.db_articulos.obtener_articulos()
            nombres_articulos = []
            self.articulos_data = {}
            
            for articulo in articulos:
                # Manejar dinámicamente las columnas retornadas
                articulo_id = articulo[0]  # ID siempre en posición 0
                codigo = articulo[1]       # Código siempre en posición 1
                nombre = articulo[2]       # Nombre siempre en posición 2
                
                # Buscar stock - puede estar en diferentes posiciones
                stock = 0
                for i, valor in enumerate(articulo):
                    if isinstance(valor, (int, float)) and i > 2:  # Buscar números después de nombre
                        stock = valor
                        break
                
                display_text = f"[{codigo}] {nombre} - Stock: {stock}"
                nombres_articulos.append(display_text)
                self.articulos_data[display_text] = {
                    'id': articulo_id,
                    'codigo': codigo,
                    'nombre': nombre,
                    'stock': stock
                }
            
            self.combo_articulos.configure(values=nombres_articulos)
            print(f"✅ Cargados {len(nombres_articulos)} artículos correctamente")
            
        except Exception as e:
            print(f"❌ Error cargando artículos: {e}")
            # Debug: mostrar qué está retornando exactamente
            try:
                articulos = self.db_articulos.obtener_articulos()
                if articulos:
                    print(f"🔍 Estructura del primer artículo: {articulos[0]}")
                    print(f"🔍 Número de columnas: {len(articulos[0])}")
            except Exception as debug_e:
                print(f"🔍 Error en debug: {debug_e}")
            
            messagebox.showerror("Error", f"Error cargando artículos: {str(e)}")

    def seleccionar_articulo(self, choice):
        try:
            if choice and choice in self.articulos_data:
                articulo_data = self.articulos_data[choice]
                self.var_articulo_id.set(str(articulo_data['id']))
                # Establecer precio de compra sugerido
                precio_sugerido = "0.0"
                self.var_precio.set(precio_sugerido)
                print(f"✅ Artículo seleccionado: {articulo_data['nombre']} (ID: {articulo_data['id']})")
                self.actualizar_estado_botones()
        except Exception as e:
            print(f"❌ Error seleccionando artículo: {e}")

    def agregar_al_carrito(self):
        if not self.validar_item_compra():
            return

        try:
            articulo_id = self.var_articulo_id.get()
            articulo_nombre_completo = self.var_articulo_nombre.get()
            
            if articulo_nombre_completo not in self.articulos_data:
                messagebox.showerror("Error", "Artículo no encontrado en los datos")
                return
                
            articulo_data = self.articulos_data[articulo_nombre_completo]
            articulo_codigo = articulo_data['codigo']
            articulo_nombre = articulo_data['nombre']
            
            cantidad = int(self.var_cantidad.get())
            precio = float(self.var_precio.get())
            subtotal = cantidad * precio

            # Verificar stock disponible (solo para advertencia)
            stock_actual = articulo_data['stock']
            if cantidad > stock_actual + 100:  # Permitir sobrepasar stock pero con límite razonable
                if not messagebox.askyesno("Advertencia", 
                    f"La cantidad solicitada ({cantidad}) es significativamente mayor al stock actual ({stock_actual}). ¿Continuar?"):
                    return

            # Verificar si el artículo ya está en el carrito
            articulo_en_carrito = None
            for item in self.carrito:
                if item['articulo_id'] == articulo_id:
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
                    'subtotal': subtotal
                }
                self.carrito.append(item_carrito)

            self.actualizar_carrito_ui()
            self.limpiar_item_formulario()
            self.actualizar_estado_botones()
            
            messagebox.showinfo("✅ Éxito", "Artículo agregado al carrito")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error agregando al carrito: {str(e)}")

    def actualizar_carrito_ui(self):
        # Limpiar treeview
        for item in self.tree_carrito.get_children():
            self.tree_carrito.delete(item)

        total = 0
        for item in self.carrito:
            self.tree_carrito.insert('', 'end', values=(
                item['articulo_codigo'],
                item['articulo_nombre'],
                item['cantidad'],
                f"${item['precio']:.2f}",
                f"${item['subtotal']:.2f}"
            ))
            total += item['subtotal']

        self.var_total_compra.set(total)
        self.lbl_total.configure(text=f"${total:.2f}")

    def eliminar_del_carrito(self, event):
        try:
            item_seleccionado = self.tree_carrito.selection()
            if item_seleccionado:
                if messagebox.askyesno("Confirmar", "¿Eliminar este artículo del carrito?"):
                    index = self.tree_carrito.index(item_seleccionado[0])
                    if 0 <= index < len(self.carrito):
                        articulo_eliminado = self.carrito.pop(index)
                        self.actualizar_carrito_ui()
                        self.actualizar_estado_botones()
                        print(f"🗑️ Artículo eliminado: {articulo_eliminado['articulo_nombre']}")
        except Exception as e:
            print(f"❌ Error eliminando del carrito: {e}")
            messagebox.showerror("Error", f"Error eliminando del carrito: {str(e)}")

    def limpiar_item_formulario(self):
        self.var_articulo_id.set("")
        self.var_articulo_nombre.set("")
        self.var_cantidad.set("1")
        self.var_precio.set("0.0")
        self.actualizar_estado_botones()

    def limpiar_carrito(self):
        if not self.carrito:
            return
            
        if messagebox.askyesno("Confirmar", "¿Limpiar todo el carrito?"):
            self.carrito = []
            self.actualizar_carrito_ui()
            self.actualizar_estado_botones()
            messagebox.showinfo("Éxito", "Carrito limpiado correctamente")

    def procesar_compra(self):
        if not self.carrito:
            messagebox.showwarning("Advertencia", "El carrito está vacío")
            return

        if not self.validar_formulario_compra():
            return

        try:
            # Validar fecha - PERMITIR FECHA ACTUAL, solo rechazar anteriores
            fecha_compra = datetime.strptime(self.var_fecha.get(), '%Y-%m-%d').date()
            fecha_actual = date.today()
            
            if fecha_compra < fecha_actual:
                messagebox.showerror("Error", "No se puede registrar una compra con fecha anterior a la actual")
                return

            folio = self.var_folio.get().strip()
            total_compra = float(self.var_total_compra.get())
            usuario_id = self.usuario_actual.get('id')

            # Verificar si el folio ya existe
            compras_existentes = self.db_compras.obtener_compras()
            folios_existentes = [compra[1] for compra in compras_existentes if len(compra) > 1]  # compra[1] es el folio
            
            if folio in folios_existentes:
                messagebox.showerror("Error", "El folio ya existe. Use un folio único.")
                return

            # Crear compra
            compra_data = {
                'folio': folio,
                'fecha': self.var_fecha.get(),
                'total': total_compra,
                'usuario_id': usuario_id
            }
            
            compra_resultado = self.db_compras.crear_compra(compra_data)
            if compra_resultado:
                compra_id, folio_generado = compra_resultado  # desempaquetar tupla

                # Crear detalles de compra
                for item in self.carrito:
                    detalle_data = {
                        'compra_id': compra_id,
                        'articulo_id': item['articulo_id'],
                        'articulo_codigo': item['articulo_codigo'],
                        'cantidad': item['cantidad'],
                        'precio_unitario': item['precio'],
                        'subtotal': item['subtotal']
                    }
                    self.db_compras.crear_detalle_compra(detalle_data)

                    # Actualizar stock (INCREMENTAR stock en compras)
                    self.db_articulos.actualizar_stock(item['articulo_id'], item['cantidad'])

                messagebox.showinfo("✅ Éxito", 
                    f"Compra procesada correctamente\n\n"
                    f"ID Compra: {compra_id}\n"
                    f"Folio: {folio}\n"
                    f"Total: ${total_compra:.2f}")
                
                self.limpiar_carrito()
                self.var_folio.set("")
                self.var_fecha.set(date.today().strftime('%Y-%m-%d'))
                self.cargar_compras()
                self.cargar_articulos()
                self.actualizar_estado_botones()
            else:
                messagebox.showerror("Error", "No se pudo procesar la compra")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error procesando compra: {str(e)}")

    def cargar_compras(self):
        try:
            for item in self.tree_compras.get_children():
                self.tree_compras.delete(item)
            
            compras = self.db_compras.obtener_compras()
            for compra in compras:
                compra_list = list(compra)
                if len(compra_list) > 3 and compra_list[3]:  # Campo total
                    try:
                        compra_list[3] = f"${float(compra[3]):,.2f}"
                    except (ValueError, TypeError):
                        compra_list[3] = "$0.00"
                self.tree_compras.insert('', 'end', values=tuple(compra_list))
        except Exception as e:
            print(f"❌ Error cargando compras: {e}")
            messagebox.showerror("Error", f"Error cargando compras: {str(e)}")

    def validar_item_compra(self):
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

    def validar_formulario_compra(self):
        if not self.var_folio.get().strip():
            messagebox.showwarning("Validación", "El folio es obligatorio")
            return False
        
        try:
            datetime.strptime(self.var_fecha.get(), '%Y-%m-%d')
        except ValueError:
            messagebox.showwarning("Validación", "La fecha debe tener formato YYYY-MM-DD")
            return False
        
        return True

    def actualizar_estado_botones(self):
        """Actualizar estado de los botones según las condiciones"""
        tiene_carrito = len(self.carrito) > 0
        formulario_completo = all([
            self.var_folio.get().strip(),
            self.var_fecha.get().strip()
        ])
        
        item_valido = all([
            self.var_articulo_id.get(),
            self.var_cantidad.get().strip(),
            self.var_precio.get().strip()
        ]) and self.validar_cantidad_precio()
        
        # Botón procesar compra
        if tiene_carrito and formulario_completo:
            self.btn_procesar.configure(state="normal", fg_color="#107c10")
        else:
            self.btn_procesar.configure(state="disabled", fg_color="#666666")
        
        # Botón limpiar carrito
        if tiene_carrito:
            self.btn_limpiar.configure(state="normal", fg_color="#d13438")
        else:
            self.btn_limpiar.configure(state="disabled", fg_color="#666666")
        
        # Botón agregar al carrito
        if item_valido:
            self.btn_agregar.configure(state="normal")
        else:
            self.btn_agregar.configure(state="disabled")

    def validar_cantidad_precio(self):
        """Validar que cantidad y precio sean números válidos"""
        try:
            cantidad = int(self.var_cantidad.get())
            precio = float(self.var_precio.get())
            return cantidad > 0 and precio > 0
        except (ValueError, TypeError):
            return False
