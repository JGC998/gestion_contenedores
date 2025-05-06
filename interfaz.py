# interfaz.py Imports Corregidos

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
import traceback
# json ya no debería ser necesario para la configuración principal
# import json

# --- IMPORTS DE LÓGICA Y MODELOS (PRIMERO) ---
try:
    # Modelos (asumiendo que está en la raíz)
    from modelos import Goma, GomaNacional, PVC, PVCNacional, Fieltro, FieltroNacional
except ImportError as e:
    print(f"ERROR CRÍTICO: No se pudieron importar clases de 'modelos.py': {e}")
    # Definir Dummies para evitar fallos posteriores
    Goma = GomaNacional = PVC = PVCNacional = Fieltro = FieltroNacional = object
    # Considera salir de la aplicación si los modelos son esenciales
    # exit()

try:
    # Clases Base
    from contenedor.contenedor import Contenedor
    from nacional.mercanciaNacional import MercanciaNacional
except ImportError as e:
    print(f"ADVERTENCIA: Error importando clases base Contenedor/MercanciaNacional: {e}")
    Contenedor = MercanciaNacional = object # Dummies

try:
    # Clases Específicas y Funciones de Guardado/Carga CONTENEDOR
    from contenedor.contenedorGoma import ContenedorGoma, guardar_o_actualizar_contenedores_goma, cargar_contenedores_goma
    from contenedor.contenedorPVC import ContenedorPVC, guardar_o_actualizar_contenedores_pvc, cargar_contenedores_pvc
    from contenedor.contenedorFieltro import ContenedorFieltro, guardar_o_actualizar_contenedores_fieltro, cargar_contenedores_fieltro
except ImportError as e:
    print(f"ADVERTENCIA: Error importando módulos de Contenedor: {e}")
    # Definir Dummies si es necesario
    ContenedorGoma = ContenedorPVC = ContenedorFieltro = None
    guardar_o_actualizar_contenedores_goma = guardar_o_actualizar_contenedores_pvc = guardar_o_actualizar_contenedores_fieltro  = None
    cargar_contenedores_goma = cargar_contenedores_pvc = cargar_contenedores_fieltro = lambda: []

try:
    # Clases Específicas y Funciones de Guardado/Carga NACIONAL
    from nacional.mercanciaNacionalGoma import MercanciaNacionalGoma, guardar_o_actualizar_mercancias_goma, cargar_mercancias_goma
    from nacional.mercanciaNacionalPVC import MercanciaNacionalPVC, guardar_o_actualizar_mercancias_pvc, cargar_mercancias_pvc
    from nacional.mercanciaNacionalFieltro import MercanciaNacionalFieltro, guardar_o_actualizar_mercancias_fieltro, cargar_mercancias_fieltro
except ImportError as e:
    print(f"ADVERTENCIA: Error importando módulos Nacional: {e}")
    # Definir Dummies
    MercanciaNacionalGoma = MercanciaNacionalPVC = MercanciaNacionalFieltro = None
    guardar_o_actualizar_mercancias_goma = guardar_o_actualizar_mercancias_pvc = guardar_o_actualizar_mercancias_fieltro = None
    cargar_mercancias_goma = cargar_mercancias_pvc = cargar_mercancias_fieltro = lambda: []

# --- IMPORTS DE ALMACÉN Y BASE DE DATOS (DESPUÉS) ---
try:
    from almacen.database import DB_PATH, obtener_margenes_configuracion
except ImportError as e:
    messagebox.showerror("Error Crítico de Importación (DB)", f"No se pudieron cargar módulos/funciones de database: {e}")
    # Definir Dummies si falla
    DB_PATH = "error_db_path.db"
    def obtener_margenes_configuracion(): return {}
    # Considera salir si la DB es esencial
    # exit()

try:
    # Funciones esenciales de gestión de almacén
    from almacen.gestion_almacen import (
        registrar_entrada_almacen, consultar_stock, marcar_item_agotado,
        marcar_item_empezado, get_stock_item_details, obtener_datos_para_tarifa
    )
except ImportError as e:
     messagebox.showerror("Error Crítico de Importación (Almacén)", f"No se pudieron cargar módulos/funciones para Almacén: {e}")
     # Definir Dummies para funciones esenciales
     def registrar_entrada_almacen(obj, pid): pass
     def consultar_stock(filtros=None): return []
     def marcar_item_agotado(id, tabla): return False
     def marcar_item_empezado(id, tabla): return False
     def get_stock_item_details(id, tabla): return None
     def obtener_datos_para_tarifa(): return []
     # Considera salir si el almacén es esencial
     # exit()


# --- Constantes Globales ---
TIPOS_GASTO_VALIDOS = ["SUPLIDOS", "EXENTO", "SUJETO"] # Para contenedores

# --- Inicio Clase Interfaz ---
class Interfaz:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Almacén")

        # --- Ajustar geometría a pantalla completa ---
        try:
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            # Dejar un pequeño margen por si acaso
            geometry_str = f"{int(screen_width*0.98)}x{int(screen_height*0.9)}+0+0"
            # geometry_str = f"{screen_width}x{screen_height}+0+0" # Original
            print(f"Ajustando geometría principal a: {geometry_str}")
            self.root.geometry(geometry_str)
            # self.root.state('zoomed') # Alternativa para maximizar en Windows
        except Exception as e:
            print(f"Error al intentar ajustar la geometría principal: {e}")
            self.root.geometry("1200x750") # Tamaño por defecto más grande

        # --- Configurar Grid Principal ---
        self.root.grid_columnconfigure(1, weight=1) # Columna contenido principal se expande
        self.root.grid_rowconfigure(0, weight=1)    # Fila única se expande

        # --- Crear Frame para la Barra Lateral (Sidebar) ---
        self.sidebar_frame = ttk.Frame(self.root, width=210, style="Sidebar.TFrame") # Un poco más ancha
        self.sidebar_frame.grid(row=0, column=0, sticky="nsw", padx=(0, 5), pady=5)
        self.sidebar_frame.grid_propagate(False) # Evitar que se encoja

        # --- Crear Frame para el Contenido Principal ---
        self.main_content_frame = ttk.Frame(self.root, padding="10")
        self.main_content_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        # Asegurar que el contenido principal pueda expandirse
        self.main_content_frame.grid_rowconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(0, weight=1)


        # Diccionarios para guardar objetos cargados y mapeo de stock
        self.contenedores_mostrados = {}
        self.pedidos_nacionales_mostrados = {}
        self.stock_item_tablas = {} # Para mapear IID del treeview -> {tabla, db_id}

        # --- Añadir Botones a la Sidebar ---
        self._crear_botones_sidebar()

        # --- Estilo ---
        self._configurar_estilos()

        # --- Mostrar Vista Inicial ---
        # Es mejor cargar la vista de stock por defecto si la DB está lista
        # self._mostrar_vista_inicial()
        self._mostrar_vista_almacen() # Mostrar stock al inicio


    def _configurar_estilos(self):
        """Configura estilos personalizados para ttk widgets."""
        style = ttk.Style()
        # Usar un tema base que se vea bien en la mayoría de OS
        try:
            available_themes = style.theme_names()
            if 'vista' in available_themes: style.theme_use('vista')
            elif 'clam' in available_themes: style.theme_use('clam')
            # Añadir otros si conoces ('aqua' en Mac, etc.)
            else: style.theme_use(style.theme_use()) # Usar el default del sistema
        except tk.TclError: pass # Ignorar si hay problemas con temas

        style.configure("Sidebar.TFrame", background="#e1e1e1") # Gris más claro
        style.configure("Sidebar.TButton", font=('Segoe UI', 10), padding=8) # Padding interno
        style.map("Sidebar.TButton",
                  background=[('active', '#c0c0c0'), ('!active', '#f0f0f0')], # Gris al pasar/normal
                  foreground=[('active', 'black')])
        style.configure("Accent.TButton", font=('Segoe UI', 10, 'bold'), padding=8) # Botón destacado

    def _crear_botones_sidebar(self):
        """Crea los botones de navegación principales en la barra lateral."""
        # --- Sección Contenedores ---
        ttk.Label(self.sidebar_frame, text="IMPORTACIÓN", font=("Segoe UI", 11, "bold"), background="#e1e1e1").pack(pady=(10, 5), padx=10, anchor="w")
        ttk.Button(self.sidebar_frame, text="Añadir Goma", style="Sidebar.TButton", command=self._mostrar_form_add_goma).pack(fill="x", padx=10, pady=1)
        ttk.Button(self.sidebar_frame, text="Añadir PVC", style="Sidebar.TButton", command=self._mostrar_form_add_pvc).pack(fill="x", padx=10, pady=1)
        ttk.Button(self.sidebar_frame, text="Añadir Fieltro", style="Sidebar.TButton", command=self._mostrar_form_add_fieltro).pack(fill="x", padx=10, pady=1)
        ttk.Button(self.sidebar_frame, text="Ver Contenedores", style="Sidebar.TButton", command=self._mostrar_vista_ver_contenedores).pack(fill="x", padx=10, pady=(1, 15))

        # --- Sección Nacional ---
        ttk.Label(self.sidebar_frame, text="NACIONAL", font=("Segoe UI", 11, "bold"), background="#e1e1e1").pack(pady=(5, 5), padx=10, anchor="w")
        ttk.Button(self.sidebar_frame, text="Añadir Goma Nac.", style="Sidebar.TButton", command=self._mostrar_form_add_nacional_goma).pack(fill="x", padx=10, pady=1)
        ttk.Button(self.sidebar_frame, text="Añadir PVC Nac.", style="Sidebar.TButton", command=self._mostrar_form_add_nacional_pvc).pack(fill="x", padx=10, pady=1)
        ttk.Button(self.sidebar_frame, text="Añadir Fieltro Nac.", style="Sidebar.TButton", command=self._mostrar_form_add_nacional_fieltro).pack(fill="x", padx=10, pady=1)
        ttk.Button(self.sidebar_frame, text="Ver Pedidos Nac.", style="Sidebar.TButton", command=self._mostrar_vista_ver_nacional).pack(fill="x", padx=10, pady=(1, 15))

        # --- Sección Almacén ---
        ttk.Label(self.sidebar_frame, text="ALMACÉN", font=("Segoe UI", 11, "bold"), background="#e1e1e1").pack(pady=(5, 5), padx=10, anchor="w")
        ttk.Button(self.sidebar_frame, text="Ver Stock", style="Sidebar.TButton", command=self._mostrar_vista_almacen).pack(fill="x", padx=10, pady=1)
        ttk.Button(self.sidebar_frame, text="Ver Tarifa Venta", style="Sidebar.TButton", command=self._mostrar_vista_tarifa).pack(fill="x", padx=10, pady=1)
        # -------------------------
        # ttk.Button(self.sidebar_frame, text="Imprimir Stock", ...).pack(...)

    def _limpiar_main_content(self):
        """Elimina todos los widgets hijos del frame de contenido principal."""
        for widget in self.main_content_frame.winfo_children():
            widget.destroy()

    # --- Métodos para MOSTRAR cada VISTA/FORMULARIO ---
    #     Estos son llamados por los botones. Limpian el área principal
    #     y DEBERÍAN llamar a otra función que construya los widgets específicos.

    # En interfaz.py (reemplaza el bloque de funciones _mostrar_* que me pasaste)

    # --- Métodos para MOSTRAR cada VISTA/FORMULARIO ---

    def _mostrar_vista_inicial(self):
        """Muestra la pantalla de bienvenida."""
        self._limpiar_main_content()
        ttk.Label(self.main_content_frame, text="Bienvenido - Selecciona una opción", font=("Arial", 16)).pack(pady=50, padx=20)

    # --- Formularios Contenedor ---
    def _mostrar_form_add_goma(self):
        """Limpia y construye el formulario para añadir Contenedor Goma."""
        self._limpiar_main_content()
        # Inicializar listas temporales específicas para este formulario
        self.gastos_temp_goma = []
        self.bobinas_temp_goma = []
        self._crear_widgets_formulario_goma(self.main_content_frame)
        print("Mostrando formulario para añadir Contenedor Goma.")

    def _mostrar_form_add_pvc(self):
        """Limpia y construye el formulario para añadir Contenedor PVC."""
        self._limpiar_main_content()
        self.gastos_temp_pvc = []
        self.bobinas_temp_pvc = []
        self._crear_widgets_formulario_pvc(self.main_content_frame)
        print("Mostrando formulario para añadir Contenedor PVC.")

    def _mostrar_form_add_fieltro(self):
        """Limpia y construye el formulario para añadir Contenedor Fieltro."""
        self._limpiar_main_content()
        self.gastos_temp_fieltro = []
        self.bobinas_temp_fieltro = [] # Usamos 'bobinas' por consistencia interna
        self._crear_widgets_formulario_fieltro(self.main_content_frame)
        print("Mostrando formulario para añadir Contenedor Fieltro.")

    # --- Vistas Contenedor ---
    def _mostrar_vista_ver_contenedores(self):
        """Limpia y construye la vista para Ver/Gestionar Contenedores."""
        self._limpiar_main_content()
        self.contenedores_mostrados = {} # Reiniciar dict de objetos mostrados
        print("Mostrando vista para Ver/Gestionar Contenedores.")
        self._crear_widgets_vista_ver_contenedores(self.main_content_frame)
        self._cargar_y_mostrar_contenedores() # Cargar datos al mostrar

    # --- Formularios Nacional ---
    def _mostrar_form_add_nacional_goma(self):
        """Limpia y construye el formulario para añadir Goma Nacional."""
        self._limpiar_main_content()
        self.gastos_temp_nac_goma = []
        self.items_temp_nac_goma = []
        self._crear_widgets_formulario_nacional_goma(self.main_content_frame)
        print("Mostrando formulario para añadir Pedido Goma Nacional.")

    def _mostrar_form_add_nacional_pvc(self):
        """Limpia y construye el formulario para añadir PVC Nacional."""
        self._limpiar_main_content()
        self.gastos_temp_nac_pvc = []
        self.items_temp_nac_pvc = []
        self._crear_widgets_formulario_nacional_pvc(self.main_content_frame)
        print("Mostrando formulario para añadir Pedido PVC Nacional.")

    def _mostrar_form_add_nacional_fieltro(self):
        """Limpia y construye el formulario para añadir Fieltro Nacional."""
        self._limpiar_main_content()
        self.gastos_temp_nac_fieltro = []
        self.items_temp_nac_fieltro = []
        self._crear_widgets_formulario_nacional_fieltro(self.main_content_frame)
        print("Mostrando formulario para añadir Pedido Fieltro Nacional.")

    # --- Vistas Nacional ---
    def _mostrar_vista_ver_nacional(self):
        """Limpia y construye la vista para Ver/Gestionar Pedidos Nacionales."""
        self._limpiar_main_content()
        self.pedidos_nacionales_mostrados = {} # Reiniciar dict de objetos mostrados
        print("Mostrando vista para Ver/Gestionar Pedidos Nacionales.")
        self._crear_widgets_vista_ver_nacional(self.main_content_frame)
        self._cargar_y_mostrar_pedidos_nacionales() # Cargar datos al mostrar

    # --- Vista Almacén ---
    def _mostrar_vista_almacen(self):
        """Limpia el frame principal y crea la vista para ver el Stock."""
        self._limpiar_main_content()
        print("Mostrando vista de Stock del Almacén.")
        self._crear_widgets_vista_almacen(self.main_content_frame)
        # Cargar con filtro predeterminado 'DISPONIBLE'
        self._cargar_y_mostrar_stock()

    # --- Vista Tarifa (Ya implementada en paso anterior) ---
    def _mostrar_vista_tarifa(self):
        """Limpia el frame principal y crea la vista para la tarifa de venta."""
        self._limpiar_main_content()
        print("Mostrando vista para Tarifa de Venta.")
        self._crear_widgets_vista_tarifa(self.main_content_frame)
        self._cargar_y_mostrar_tarifa()

    # --- (Aquí irían las funciones _crear_widgets_* y _cargar_y_mostrar_* que ya tenemos) ---
    # ... _crear_widgets_formulario_goma ...
    # ... _guardar_contenedor_goma ...
    # ... _crear_widgets_vista_almacen ...
    # ... _cargar_y_mostrar_stock ...
    # ... etc ...
   

    # ===================================================================
    # ===================================================================
    # ### INICIO FUNCIONALIDAD AÑADIR CONTENEDOR GOMA ###
    # ===================================================================
    # ===================================================================

    def _mostrar_form_add_goma(self):
        """Limpia el área principal y construye el formulario de Goma."""
        self._limpiar_main_content()
        # Inicializar listas temporales para este nuevo contenedor
        self.gastos_temp_goma = []
        self.bobinas_temp_goma = []
        # Llamar a la función que construye los widgets visuales
        self._crear_widgets_formulario_goma(self.main_content_frame)
        print("Mostrando formulario para añadir Contenedor Goma.")

    # Dentro de la clase Interfaz en interfaz.py

    def _crear_widgets_formulario_goma(self, parent_frame):
        """Crea y posiciona los widgets para el formulario de Añadir Contenedor Goma."""
        form_frame = ttk.Frame(parent_frame, padding="10")
        form_frame.pack(expand=True, fill="both")
        form_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(form_frame, text="Añadir Nuevo Contenedor de Goma", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=4, pady=(0, 15), sticky="w")

        # Datos Generales (Sin cambios funcionales aquí)
        frame_datos_gen = ttk.LabelFrame(form_frame, text="Datos Generales", padding="10")
        frame_datos_gen.grid(row=1, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        frame_datos_gen.grid_columnconfigure(1, weight=1); frame_datos_gen.grid_columnconfigure(3, weight=1)
        labels_contenedor = ["Fecha Pedido (DD-MM-YYYY):", "Fecha Llegada (DD-MM-YYYY):", "Proveedor:",
                            "Número Factura:", "Observaciones:", "Valor Conversión (USD-EUR):"]
        self.entries_cont_goma = {}
        key_map = ["fecha_pedido", "fecha_llegada", "proveedor", "numero_factura", "observaciones", "valor_conversion"]
        for i, text in enumerate(labels_contenedor):
            row, col = divmod(i, 2)
            lbl = ttk.Label(frame_datos_gen, text=text); lbl.grid(row=row, column=col*2, sticky="w", padx=5, pady=3)
            entry_widget = None; current_key = key_map[i]
            if current_key in ["fecha_pedido", "fecha_llegada"]:
                entry_widget = DateEntry(frame_datos_gen, width=18, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd-mm-yyyy', locale='es_ES')
            else:
                entry_widget = ttk.Entry(frame_datos_gen, width=30)
            entry_widget.grid(row=row, column=col*2 + 1, sticky="ew", padx=5, pady=3)
            self.entries_cont_goma[current_key] = entry_widget

        # Gastos (Sin cambios funcionales aquí)
        frame_gastos = ttk.LabelFrame(form_frame, text="Gastos Asociados", padding="10")
        frame_gastos.grid(row=2, column=0, columnspan=4, sticky="ew", padx=5, pady=10)
        frame_gastos.grid_columnconfigure(1, weight=1)
        ttk.Label(frame_gastos, text="Tipo:").grid(row=0, column=0, padx=(0, 5), pady=3, sticky="nw")
        self.combo_gasto_tipo_goma = ttk.Combobox(frame_gastos, values=TIPOS_GASTO_VALIDOS, state="readonly", width=10)
        self.combo_gasto_tipo_goma.grid(row=1, column=0, padx=(0, 5), pady=3, sticky="w")
        ttk.Label(frame_gastos, text="Descripción:").grid(row=0, column=1, padx=5, pady=3, sticky="w")
        self.entry_gasto_desc_goma = ttk.Entry(frame_gastos)
        self.entry_gasto_desc_goma.grid(row=1, column=1, padx=5, pady=3, sticky="ew")
        ttk.Label(frame_gastos, text="Coste (€):").grid(row=0, column=2, padx=5, pady=3, sticky="w")
        self.entry_gasto_coste_goma = ttk.Entry(frame_gastos, width=10)
        self.entry_gasto_coste_goma.grid(row=1, column=2, padx=5, pady=3, sticky="w")
        ttk.Button(frame_gastos, text="Añadir Gasto", command=self._add_gasto_goma_temp).grid(row=1, column=3, padx=5, pady=5, sticky="w")
        cols_gastos = ("Tipo", "Descripción", "Coste")
        self.tree_gastos_goma = ttk.Treeview(frame_gastos, columns=cols_gastos, show="headings", height=3, selectmode="browse")
        self.tree_gastos_goma.heading("Tipo", text="Tipo"); self.tree_gastos_goma.column("Tipo", width=80, anchor=tk.W)
        self.tree_gastos_goma.heading("Descripción", text="Descripción"); self.tree_gastos_goma.column("Descripción", width=250, anchor=tk.W)
        self.tree_gastos_goma.heading("Coste", text="Coste (€)"); self.tree_gastos_goma.column("Coste", width=80, anchor=tk.E)
        self.tree_gastos_goma.grid(row=2, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        # TODO: Scrollbar Gastos Goma
        ttk.Button(frame_gastos, text="Eliminar Gasto Sel.", command=self._del_gasto_goma_temp).grid(row=3, column=0, columnspan=4, pady=(0, 5))

        # --- Sub-Frame: Bobinas (MODIFICADO) ---
        frame_bobinas = ttk.LabelFrame(form_frame, text="Bobinas de Goma", padding="10")
        frame_bobinas.grid(row=3, column=0, columnspan=4, sticky="ew", padx=5, pady=10)
        # frame_bobinas.grid_columnconfigure(1, weight=1) # Ajustar si es necesario

        ## CAMBIO ## Añadir 'Subtipo:' a las etiquetas y clave 'subtipo' al map
        labels_bobinas = ["Espesor:", "Ancho(mm):", "Largo(m):",
                        "Nº Bobinas:", "Precio/m(USD):", "Subtipo:"]
        self.entries_bobina_goma = {}
        key_map_bobinas = ["espesor", "ancho", "largo", "n_bobinas", "metro_lineal_usd", "subtipo"]

        b_row = 0
        for i, text in enumerate(labels_bobinas):
            lbl = ttk.Label(frame_bobinas, text=text)
            col_lbl = (i % 3) * 2 # 0, 2, 4
            col_entry = col_lbl + 1 # 1, 3, 5
            row_entry = b_row + (i // 3) * 2 # Filas 0, 2
            lbl.grid(row=row_entry, column=col_lbl, padx=5, pady=3, sticky="w")

            ## CAMBIO ## Crear un Entry para subtipo (podría ser Combobox)
            entry = ttk.Entry(frame_bobinas, width=15) # Ancho ajustado para subtipo
            entry.grid(row=row_entry, column=col_entry, padx=5, pady=3, sticky="ew")
            self.entries_bobina_goma[key_map_bobinas[i]] = entry

        # Botón añadir bobina (ajustar grid si layout cambió)
        ttk.Button(frame_bobinas, text="Añadir Bobina", command=self._add_bobina_goma_temp).grid(
            row=row_entry + 1, column=4, columnspan=2, padx=5, pady=5, sticky="e"
        ) # Ajustar fila/columna según sea necesario

        ## CAMBIO ## Añadir 'Subtipo' a las columnas del Treeview
        cols_bobinas = ("Espesor", "Ancho", "Largo", "Nº", "USD/m", "Subtipo")
        self.tree_bobinas_goma = ttk.Treeview(frame_bobinas, columns=cols_bobinas, show="headings", height=4, selectmode="browse")

        ## CAMBIO ## Configurar las columnas incluyendo 'Subtipo'
        for col in cols_bobinas:
            self.tree_bobinas_goma.heading(col, text=col)
            width = 70 # Ancho por defecto
            anchor = tk.CENTER # Anclaje por defecto
            if col == "Subtipo":
                width = 90
                anchor = tk.W
            elif col == "USD/m":
                anchor = tk.E
            elif col == "Nº":
                width = 40
            elif col == "Ancho" or col == "Largo":
                anchor = tk.E
                width = 60
            elif col == "Espesor":
                width = 110 # Más ancho para string
                anchor = tk.W
            self.tree_bobinas_goma.column(col, width=width, anchor=anchor, stretch=(col=="Subtipo")) # Permitir que subtipo se estire un poco

        # Ajustar grid del Treeview
        self.tree_bobinas_goma.grid(row=b_row + (len(labels_bobinas)//3)*2 + 1, column=0, columnspan=6, sticky="nsew", padx=5, pady=5)
        # TODO: Scrollbar Tree Bobinas Goma
        ttk.Button(frame_bobinas, text="Eliminar Bobina Sel.", command=self._del_bobina_goma_temp).grid(
            row=b_row + (len(labels_bobinas)//3)*2 + 2, column=0, columnspan=6, pady=(0, 5)
        )

        # --- Botón Guardar Final y Status Label (Sin cambios) ---
        ttk.Button(form_frame, text="GUARDAR CONTENEDOR GOMA", command=self._guardar_contenedor_goma, style="Accent.TButton").grid(row=4, column=0, columnspan=4, pady=20, ipady=5)
        self.status_label_form_goma = ttk.Label(form_frame, text="Formulario listo para añadir datos.", foreground="blue")
        self.status_label_form_goma.grid(row=5, column=0, columnspan=4, pady=5)



    def _add_gasto_goma_temp(self):
        """Lee datos de gasto, valida, y añade a lista temporal y TreeView."""
        tipo = self.combo_gasto_tipo_goma.get()
        descripcion = self.entry_gasto_desc_goma.get().strip()
        coste_str = self.entry_gasto_coste_goma.get().strip()

        # Validar
        if not tipo:
            messagebox.showerror("Error Gasto", "Debe seleccionar un tipo de gasto.")
            return
        if not descripcion:
            messagebox.showerror("Error Gasto", "La descripción no puede estar vacía.")
            return
        try:
            coste = float(coste_str)
            if coste < 0: raise ValueError("El coste no puede ser negativo.")
        except ValueError as e:
            messagebox.showerror("Error Gasto", f"Coste inválido: {e}")
            return

        # Añadir a lista temporal
        gasto_data = {"tipo": tipo, "descripcion": descripcion, "coste": coste}
        self.gastos_temp_goma.append(gasto_data)
        # Añadir a Treeview
        self.tree_gastos_goma.insert("", tk.END, values=(tipo, descripcion, f"{coste:.2f}"))

        # Limpiar campos de entrada
        self.combo_gasto_tipo_goma.set('')
        self.entry_gasto_desc_goma.delete(0, tk.END)
        self.entry_gasto_coste_goma.delete(0, tk.END)
        self.status_label_form_goma.config(text=f"Gasto '{descripcion}' añadido temporalmente.")

    def _del_gasto_goma_temp(self):
        """Elimina el gasto seleccionado de la lista temporal y TreeView."""
        selected_iid = self.tree_gastos_goma.selection() # Obtiene el ID interno del item seleccionado
        if not selected_iid:
            messagebox.showwarning("Eliminar Gasto", "Seleccione un gasto de la lista para eliminar.")
            return

        item_index = self.tree_gastos_goma.index(selected_iid[0]) # Obtiene el índice (0, 1, 2...)
        item_values = self.tree_gastos_goma.item(selected_iid[0], 'values') # Obtiene los valores mostrados

        try:
            # Eliminar de la lista temporal usando el índice
            del self.gastos_temp_goma[item_index]
            # Eliminar del TreeView usando su ID interno
            self.tree_gastos_goma.delete(selected_iid[0])
            self.status_label_form_goma.config(text=f"Gasto '{item_values[1]}' eliminado de la lista temporal.")
        except IndexError:
             # Este error podría ocurrir si el índice no coincide con la lista (raro pero posible)
             messagebox.showerror("Error", "No se pudo encontrar el gasto para eliminar (Error de índice).")
    def _add_bobina_goma_temp(self):
        """Lee datos de bobina (incluyendo subtipo), valida, y añade a lista temporal y TreeView."""
        bobina_params = {} # Para guardar los parámetros validados
        try:
            # Leer de todos los entries definidos para la bobina
            for key, widget in self.entries_bobina_goma.items():
                value_str = widget.get().strip()
                if not value_str and key != "subtipo": # Subtipo puede estar vacío, usamos default 'NORMAL'
                    raise ValueError(f"El campo '{key}' no puede estar vacío.")

                # Conversiones y validaciones específicas
                if key in ["ancho", "largo", "metro_lineal_usd"]:
                    value = float(value_str.replace(',', '.'))
                    if value < 0 or (key != "metro_lineal_usd" and value == 0): # Ancho/Largo > 0, Precio >= 0
                        raise ValueError(f"Valor inválido para '{key}'.")
                elif key == "n_bobinas":
                    value = int(value_str)
                    if value <= 0: raise ValueError("Nº Bobinas debe ser > 0.")
                ## CAMBIO ## Leer subtipo como string, usar default si está vacío
                elif key == "subtipo":
                    value = value_str.upper() if value_str else "NORMAL"
                else: # Espesor (se guarda como string)
                    value = value_str

                bobina_params[key] = value # Guardar valor procesado

        except KeyError as e:
            messagebox.showerror("Error Bobina", f"Error interno del programador: Clave no encontrada {e}")
            return
        except ValueError as e:
            messagebox.showerror("Error Bobina", f"Datos de bobina inválidos: {e}")
            return
        except Exception as e:
            messagebox.showerror("Error Bobina", f"Error inesperado al leer datos de bobina: {e}")
            return

        # Añadir a lista temporal
        if not hasattr(self, 'bobinas_temp_goma'): self.bobinas_temp_goma = []
        self.bobinas_temp_goma.append(bobina_params)

        # Añadir a Treeview (asegurar que el orden de valores coincide con cols_bobinas)
        ## CAMBIO ## Incluir el subtipo en los valores para el TreeView
        valores_tree = (
            bobina_params["espesor"],
            f"{bobina_params['ancho']:.1f}", # Formatear números para display
            f"{bobina_params['largo']:.1f}",
            bobina_params["n_bobinas"],
            f"{bobina_params['metro_lineal_usd']:.2f}",
            bobina_params["subtipo"] # <-- Añadido subtipo
        )
        self.tree_bobinas_goma.insert("", tk.END, values=valores_tree)

        # Limpiar campos de entrada de bobina
        for entry_widget in self.entries_bobina_goma.values():
            entry_widget.delete(0, tk.END)

        # Mensaje de estado
        status_label = getattr(self, 'status_label_form_goma', None)
        if status_label and status_label.winfo_exists():
            status_label.config(text=f"Bobina {bobina_params['subtipo']} ({bobina_params['espesor']}mm) añadida temporalmente.")


    def _del_bobina_goma_temp(self):
        """Elimina la bobina seleccionada de la lista temporal y TreeView."""
        selected_iid = self.tree_bobinas_goma.selection()
        if not selected_iid:
            messagebox.showwarning("Eliminar Bobina", "Seleccione una bobina de la lista para eliminar.")
            return

        item_index = self.tree_bobinas_goma.index(selected_iid[0])
        item_values = self.tree_bobinas_goma.item(selected_iid[0], 'values') # values=(espesor,...)

        try:
            del self.bobinas_temp_goma[item_index]
            self.tree_bobinas_goma.delete(selected_iid[0])
            self.status_label_form_goma.config(text=f"Bobina {item_values[0]}mm eliminada de la lista temporal.")
        except IndexError:
             messagebox.showerror("Error", "No se pudo encontrar la bobina para eliminar (Error de índice).")

    # Dentro de la clase Interfaz en interfaz.py

    def _guardar_contenedor_goma(self):
        """Recoge datos Goma, crea obj, calcula, guarda JSON y registra en DB."""
        status_label = getattr(self, 'status_label_form_goma', None)
        if status_label and status_label.winfo_exists():
            status_label.config(text="Procesando...", foreground="blue")

        datos_a_guardar = {}
        valor_conv_final = 0.0

        try: # Validar datos generales (sin cambios aquí)
            from datetime import datetime
            datos_generales_widgets = self.entries_cont_goma
            for key, widget in datos_generales_widgets.items():
                if key in ["fecha_pedido", "fecha_llegada"]:
                    fecha_dt = widget.get_date(); datos_a_guardar[key] = fecha_dt.strftime('%Y-%m-%d')
                elif key == "valor_conversion":
                    valor_str = widget.get().strip().replace(',', '.'); valor_conversion = float(valor_str)
                    if valor_conversion <= 0: raise ValueError("Valor conversión > 0.")
                    datos_a_guardar[key] = valor_conversion
                else: datos_a_guardar[key] = widget.get().strip()
            if not datos_a_guardar.get("proveedor") or not datos_a_guardar.get("numero_factura"):
                raise ValueError("Proveedor y Número Factura obligatorios.")
            valor_conv_final = datos_a_guardar.pop('valor_conversion')
        except ValueError as e:
            messagebox.showerror("Error Datos Generales", f"Datos inválidos: {e}")
            if status_label and status_label.winfo_exists(): status_label.config(text="Error datos generales.", foreground="red")
            return
        except Exception as e:
            messagebox.showerror("Error Datos Generales", f"Error inesperado: {e}")
            if status_label and status_label.winfo_exists(): status_label.config(text="Error interno formulario.", foreground="red")
            return

        if not hasattr(self, 'bobinas_temp_goma') or not self.bobinas_temp_goma:
            messagebox.showerror("Error Contenido", "Debe añadir al menos una bobina.")
            if status_label and status_label.winfo_exists(): status_label.config(text="Error: Faltan bobinas.", foreground="red")
            return

        contenedor = None
        try: # Crear objeto ContenedorGoma (sin cambios aquí)
            from contenedor.contenedorGoma import ContenedorGoma
            contenedor = ContenedorGoma(
                gastos={}, contenido_goma=[],
                valor_conversion=valor_conv_final,
                **datos_a_guardar
            )
        except Exception as e:
            messagebox.showerror("Error Creación", f"No se pudo crear el objeto ContenedorGoma: {e}")
            if status_label and status_label.winfo_exists(): status_label.config(text="Error interno.", foreground="red")
            return

        # --- Lógica Backend ---
        json_guardado = False
        try:
            # Añadir gastos (sin cambios aquí)
            if hasattr(self, 'gastos_temp_goma'):
                for gasto_data in self.gastos_temp_goma:
                    contenedor.agregar_gasto(gasto_data["tipo"], gasto_data["descripcion"], gasto_data["coste"])

            # Añadir bobinas
            ## CAMBIO ## Asegurarse que el método backend 'agregar_bobina' acepta 'subtipo'
            ##          (ya lo hicimos en el paso anterior)
            add_bobina_method = getattr(contenedor, 'agregar_bobina', None) # El nombre correcto es agregar_bobina
            if not add_bobina_method:
                raise AttributeError("Método 'agregar_bobina' no encontrado en ContenedorGoma.")

            if hasattr(self, 'bobinas_temp_goma'):
                for bobina_data in self.bobinas_temp_goma:
                    # bobina_data ya contiene 'subtipo' desde _add_bobina_goma_temp
                    # El método agregar_bobina actualizado en backend acepta subtipo
                    add_bobina_method(**bobina_data, valor_conversion=contenedor.valor_conversion)

            # Calcular precios finales (sin cambios aquí)
            contenedor.calcular_precios_finales()

            # Guardar en JSON (sin cambios aquí, ya que guarda __dict__ que incluye subtipo)
            guardar_o_actualizar_contenedores_goma([contenedor])
            json_guardado = True
            print(f"Contenedor Goma {contenedor.numero_factura} guardado/actualizado en JSON (incluyendo subtipos).")

        except Exception as e:
            messagebox.showerror("Error Procesamiento", f"Error procesando datos del contenedor Goma: {e}")
            if status_label and status_label.winfo_exists():
                status_label.config(text="Error procesando datos.", foreground="red")
            return

        # Registrar en Almacén DB
        db_registrado = False
        if json_guardado:
            try:
                # registrar_entrada_almacen necesita ser adaptado para leer 'subtipo' del item
                # y guardarlo en la columna 'subtipo_material' de la DB.
                # Asumimos que se adaptará en el siguiente paso.
                registrar_entrada_almacen(contenedor)
                db_registrado = True
                print(f"Contenedor Goma {contenedor.numero_factura} registrado en almacén DB.")
            except Exception as e:
                messagebox.showwarning("Error Registro Almacén", f"JSON guardado, pero falló el registro en Almacén DB: {e}\n(La función necesita adaptación para subtipos)")

        # Feedback final y limpiar (sin cambios aquí)
        if status_label and status_label.winfo_exists():
            if json_guardado and db_registrado:
                messagebox.showinfo("Éxito", f"Contenedor Goma '{contenedor.numero_factura}' guardado y registrado en almacén.")
                self._limpiar_form_goma()
                status_label.config(text=f"Contenedor '{contenedor.numero_factura}' procesado con éxito.", foreground="green")
            elif json_guardado and not db_registrado:
                status_label.config(text=f"Cont. '{contenedor.numero_factura}' guardado en JSON, pero falló registro DB.", foreground="orange")
            else:
                status_label.config(text="Error al guardar el contenedor en JSON.", foreground="red")


    def _limpiar_form_goma(self):
        """Limpia todos los campos de entrada y listas del formulario Goma."""
        # Limpiar entries generales
        for entry_widget in self.entries_cont_goma.values():
            entry_widget.delete(0, tk.END)
        # Limpiar entries de añadir gasto/bobina
        self.combo_gasto_tipo_goma.set('')
        self.entry_gasto_desc_goma.delete(0, tk.END)
        self.entry_gasto_coste_goma.delete(0, tk.END)
        for entry_widget in self.entries_bobina_goma.values():
            entry_widget.delete(0, tk.END)
        # Limpiar Treeviews
        # Usar get_children() para obtener los iids y luego borrarlos
        for iid in self.tree_gastos_goma.get_children():
            self.tree_gastos_goma.delete(iid)
        for iid in self.tree_bobinas_goma.get_children():
            self.tree_bobinas_goma.delete(iid)
        # Limpiar listas temporales (ya deberían estar en self)
        if hasattr(self, 'gastos_temp_goma'): self.gastos_temp_goma.clear()
        if hasattr(self, 'bobinas_temp_goma'): self.bobinas_temp_goma.clear()
        # Resetear label de estado
        if hasattr(self, 'status_label_form_goma'): # Comprobar si existe
            self.status_label_form_goma.config(text="Formulario limpio.", foreground="black")
        print("Formulario Goma limpiado.")

    # ###############################################################
    # ### FIN FUNCIONALIDAD AÑADIR CONTENEDOR GOMA ###
    # ###############################################################

    # ===================================================================
    # ### INICIO FUNCIONALIDAD AÑADIR CONTENEDOR PVC ###
    # ===================================================================
    # ===================================================================

    def _mostrar_form_add_pvc(self):
        """Limpia el área principal y construye el formulario de PVC."""
        self._limpiar_main_content()
        # Inicializar listas temporales para este formulario específico
        self.gastos_temp_pvc = []
        self.bobinas_temp_pvc = []
        # Llamar a la función que construye los widgets visuales
        self._crear_widgets_formulario_pvc(self.main_content_frame)
        print("Mostrando formulario para añadir Contenedor PVC.")

    # Dentro de la clase Interfaz en interfaz.py

    def _crear_widgets_formulario_pvc(self, parent_frame):
        """Crea y posiciona los widgets para el formulario de Añadir Contenedor PVC."""
        # --- Frame principal ---
        form_frame = ttk.Frame(parent_frame, padding="10")
        form_frame.pack(expand=True, fill="both")
        form_frame.grid_columnconfigure(1, weight=1)

        # --- Título ---
        ttk.Label(form_frame, text="Añadir Nuevo Contenedor de PVC", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=4, pady=(0, 15), sticky="w")

        # --- Sub-Frame: Datos Generales ---
        frame_datos_gen = ttk.LabelFrame(form_frame, text="Datos Generales", padding="10")
        frame_datos_gen.grid(row=1, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        frame_datos_gen.grid_columnconfigure(1, weight=1); frame_datos_gen.grid_columnconfigure(3, weight=1)

        # --- CAMBIO AQUÍ: Texto de etiquetas de fecha ---
        labels_contenedor = ["Fecha Pedido (DD-MM-YYYY):", "Fecha Llegada (DD-MM-YYYY):", "Proveedor:",
                             "Número Factura:", "Observaciones:", "Valor Conversión (USD-EUR):"]
        self.entries_cont_pvc = {} # Diccionario específico para PVC
        key_map = ["fecha_pedido", "fecha_llegada", "proveedor", "numero_factura", "observaciones", "valor_conversion"]

        for i, text in enumerate(labels_contenedor):
            row, col = divmod(i, 2)
            lbl = ttk.Label(frame_datos_gen, text=text); lbl.grid(row=row, column=col*2, sticky="w", padx=5, pady=3)

            entry_widget = None
            current_key = key_map[i]

            # --- CAMBIO AQUÍ: Crear DateEntry o Entry ---
            if current_key in ["fecha_pedido", "fecha_llegada"]:
                 # ¡Asegúrate de tener 'from tkcalendar import DateEntry' al principio del archivo!
                entry_widget = DateEntry(frame_datos_gen, width=18, background='darkblue',
                                     foreground='white', borderwidth=2,
                                     date_pattern='dd-mm-yyyy', locale='es_ES')
            else:
                entry_widget = ttk.Entry(frame_datos_gen, width=30)
            # ---------------------------------------------

            entry_widget.grid(row=row, column=col*2 + 1, sticky="ew", padx=5, pady=3)
            self.entries_cont_pvc[current_key] = entry_widget

        # --- Sub-Frame: Gastos (Sin cambios, usa widgets _pvc) ---
        frame_gastos = ttk.LabelFrame(form_frame, text="Gastos Asociados", padding="10")
        frame_gastos.grid(row=2, column=0, columnspan=4, sticky="ew", padx=5, pady=10)
        frame_gastos.grid_columnconfigure(1, weight=1)
        # ... (widgets de gastos _pvc: combo_gasto_tipo_pvc, etc.) ...
        ttk.Label(frame_gastos, text="Tipo:").grid(row=0, column=0, padx=(0, 5), pady=3, sticky="nw")
        self.combo_gasto_tipo_pvc = ttk.Combobox(frame_gastos, values=TIPOS_GASTO_VALIDOS, state="readonly", width=10)
        self.combo_gasto_tipo_pvc.grid(row=1, column=0, padx=(0, 5), pady=3, sticky="w")
        ttk.Label(frame_gastos, text="Descripción:").grid(row=0, column=1, padx=5, pady=3, sticky="w")
        self.entry_gasto_desc_pvc = ttk.Entry(frame_gastos)
        self.entry_gasto_desc_pvc.grid(row=1, column=1, padx=5, pady=3, sticky="ew")
        ttk.Label(frame_gastos, text="Coste (€):").grid(row=0, column=2, padx=5, pady=3, sticky="w")
        self.entry_gasto_coste_pvc = ttk.Entry(frame_gastos, width=10)
        self.entry_gasto_coste_pvc.grid(row=1, column=2, padx=5, pady=3, sticky="w")
        ttk.Button(frame_gastos, text="Añadir Gasto", command=self._add_gasto_pvc_temp).grid(row=1, column=3, padx=5, pady=5, sticky="w")
        cols_gastos = ("Tipo", "Descripción", "Coste")
        self.tree_gastos_pvc = ttk.Treeview(frame_gastos, columns=cols_gastos, show="headings", height=3, selectmode="browse")
        self.tree_gastos_pvc.heading("Tipo", text="Tipo"); self.tree_gastos_pvc.column("Tipo", width=80, anchor=tk.W)
        self.tree_gastos_pvc.heading("Descripción", text="Descripción"); self.tree_gastos_pvc.column("Descripción", width=250, anchor=tk.W)
        self.tree_gastos_pvc.heading("Coste", text="Coste (€)"); self.tree_gastos_pvc.column("Coste", width=80, anchor=tk.E)
        self.tree_gastos_pvc.grid(row=2, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        ttk.Button(frame_gastos, text="Eliminar Gasto Sel.", command=self._del_gasto_pvc_temp).grid(row=3, column=0, columnspan=4, pady=(0, 5))

        # --- Sub-Frame: Bobinas PVC (Sin cambios aquí) ---
        frame_bobinas = ttk.LabelFrame(form_frame, text="Bobinas de PVC", padding="10")
        frame_bobinas.grid(row=3, column=0, columnspan=4, sticky="ew", padx=5, pady=10)
        # ... (widgets de bobinas _pvc: incluye Color) ...
        labels_bobinas = ["Espesor:", "Ancho(mm):", "Largo(m):", "Nº Bobinas:", "Precio/m(USD):", "Color:"] # Quitado (mm) de Espesor
        self.entries_bobina_pvc = {}
        key_map_bobinas = ["espesor", "ancho", "largo", "n_bobinas", "metro_lineal_usd", "color"]
        b_row = 0
        for i, text in enumerate(labels_bobinas):
            lbl = ttk.Label(frame_bobinas, text=text)
            col_lbl = (i % 3) * 2
            col_entry = col_lbl + 1
            row_entry = b_row + (i // 3) * 2
            lbl.grid(row=row_entry, column=col_lbl, padx=5, pady=3, sticky="w")
            entry = ttk.Entry(frame_bobinas, width=12) # Espesor es Entry normal
            entry.grid(row=row_entry, column=col_entry, padx=5, pady=3, sticky="ew")
            self.entries_bobina_pvc[key_map_bobinas[i]] = entry
        ttk.Button(frame_bobinas, text="Añadir Bobina", command=self._add_bobina_pvc_temp).grid(row=b_row + (len(labels_bobinas)//3)*2 + 1, column=4, padx=5, pady=5, sticky="se", rowspan=2)
        cols_bobinas = ("Espesor", "Ancho", "Largo", "Nº", "USD/m", "Color")
        self.tree_bobinas_pvc = ttk.Treeview(frame_bobinas, columns=cols_bobinas, show="headings", height=4, selectmode="browse")
        for col in cols_bobinas: self.tree_bobinas_pvc.heading(col, text=col)
        for col in cols_bobinas: self.tree_bobinas_pvc.column(col, width=70, anchor=tk.CENTER)
        self.tree_bobinas_pvc.column("Color", width=90)
        self.tree_bobinas_pvc.grid(row=b_row + 4, column=0, columnspan=5, sticky="nsew", padx=5, pady=5)
        ttk.Button(frame_bobinas, text="Eliminar Bobina Sel.", command=self._del_bobina_pvc_temp).grid(row=b_row + 5, column=0, columnspan=5, pady=(0, 5))

        # --- Botón Guardar Final y Status Label (Sin cambios) ---
        ttk.Button(form_frame, text="GUARDAR CONTENEDOR PVC", command=self._guardar_contenedor_pvc, style="Accent.TButton").grid(row=4, column=0, columnspan=4, pady=20, ipady=5)
        self.status_label_form_pvc = ttk.Label(form_frame, text="Formulario listo.")
        self.status_label_form_pvc.grid(row=5, column=0, columnspan=4, pady=5)


    def _add_gasto_pvc_temp(self):
        """Lee datos de gasto, valida, y añade a lista temporal y TreeView PVC."""
        tipo = self.combo_gasto_tipo_pvc.get()
        descripcion = self.entry_gasto_desc_pvc.get().strip()
        coste_str = self.entry_gasto_coste_pvc.get().strip()
        try:
            coste = float(coste_str)
            if not tipo or not descripcion or coste < 0: raise ValueError("Tipo, descripción (no vacía) y coste (>=0) requeridos.")
        except ValueError as e: messagebox.showerror("Error Gasto", f"Datos de gasto inválidos: {e}"); return

        gasto_data = {"tipo": tipo, "descripcion": descripcion, "coste": coste}
        self.gastos_temp_pvc.append(gasto_data)
        self.tree_gastos_pvc.insert("", tk.END, values=(tipo, descripcion, f"{coste:.2f}"))
        self.combo_gasto_tipo_pvc.set(''); self.entry_gasto_desc_pvc.delete(0, tk.END); self.entry_gasto_coste_pvc.delete(0, tk.END)
        self.status_label_form_pvc.config(text=f"Gasto '{descripcion}' añadido temporalmente.")

    def _del_gasto_pvc_temp(self):
        """Elimina el gasto seleccionado de la lista temporal y TreeView PVC."""
        selected_iid = self.tree_gastos_pvc.selection()
        if not selected_iid: messagebox.showwarning("Eliminar Gasto", "Seleccione un gasto."); return
        item_index = self.tree_gastos_pvc.index(selected_iid[0])
        item_values = self.tree_gastos_pvc.item(selected_iid[0], 'values')
        try:
            del self.gastos_temp_pvc[item_index]; self.tree_gastos_pvc.delete(selected_iid[0])
            self.status_label_form_pvc.config(text=f"Gasto '{item_values[1]}' eliminado.")
        except IndexError: messagebox.showerror("Error", "Índice de gasto no válido.")

    def _add_bobina_pvc_temp(self):
        """Lee datos de bobina PVC (incluye color), valida, y añade a lista y TreeView."""
        try:
            espesor = self.entries_bobina_pvc["espesor"].get().strip() # Leer como string
            ancho = float(self.entries_bobina_pvc["ancho"].get().strip().replace(',', '.'))
            largo = float(self.entries_bobina_pvc["largo"].get().strip().replace(',', '.'))
            n_bobinas = int(self.entries_bobina_pvc["n_bobinas"].get().strip())
            metro_lineal_usd_str = self.entries_bobina_pvc["metro_lineal_usd"].get().strip().replace(',', '.')
            if not metro_lineal_usd_str: raise ValueError("Precio/m(USD) no puede estar vacío.")
            metro_lineal_usd = float(metro_lineal_usd_str)
            color = self.entries_bobina_pvc["color"].get().strip()
            if not color: raise ValueError("Color no puede estar vacío.")

            if not all(v > 0 for v in [ancho, largo, n_bobinas]) or metro_lineal_usd < 0:
                raise ValueError("Valores numéricos > 0 (precio >= 0).")
        except KeyError as e: messagebox.showerror("Error Bobina", f"Error interno: Clave no encontrada {e}"); return
        except ValueError as e: messagebox.showerror("Error Bobina", f"Datos de bobina inválidos: {e}"); return

        bobina_params = {
            "espesor": espesor, "ancho": ancho, "largo": largo, "n_bobinas": n_bobinas,
            "metro_lineal_usd": metro_lineal_usd, "color": color # <-- Añadido color
        }
        self.bobinas_temp_pvc.append(bobina_params)
        self.tree_bobinas_pvc.insert("", tk.END, values=(espesor, ancho, largo, n_bobinas, f"{metro_lineal_usd:.2f}", color))

        for entry_widget in self.entries_bobina_pvc.values(): entry_widget.delete(0, tk.END)
        self.status_label_form_pvc.config(text=f"Bobina {espesor}mm {color} añadida.")

    def _del_bobina_pvc_temp(self):
        """Elimina la bobina PVC seleccionada de la lista temporal y TreeView."""
        selected_iid = self.tree_bobinas_pvc.selection()
        if not selected_iid: messagebox.showwarning("Eliminar Bobina", "Seleccione una bobina."); return
        item_index = self.tree_bobinas_pvc.index(selected_iid[0])
        item_values = self.tree_bobinas_pvc.item(selected_iid[0], 'values')
        try:
            del self.bobinas_temp_pvc[item_index]; self.tree_bobinas_pvc.delete(selected_iid[0])
            self.status_label_form_pvc.config(text=f"Bobina {item_values[0]}mm {item_values[5]} eliminada.")
        except IndexError: messagebox.showerror("Error", "Índice de bobina no válido.")

    # Dentro de la clase Interfaz en interfaz.py

    def _guardar_contenedor_pvc(self):
        """Recoge datos del form PVC, crea obj ContenedorPVC, calcula, guarda JSON y registra en DB."""
        # Asegurarse de que el label de estado existe
        if not hasattr(self, 'status_label_form_pvc') or self.status_label_form_pvc is None:
             print("Advertencia: status_label_form_pvc no inicializado.")
        else:
             self.status_label_form_pvc.config(text="Procesando...", foreground="blue")

        datos_a_guardar = {}
        valor_conv_final = 0.0

        try: # Validar y procesar datos generales
            from datetime import datetime # Importar si es necesario

            datos_generales_widgets = self.entries_cont_pvc
            for key, widget in datos_generales_widgets.items():
                if key in ["fecha_pedido", "fecha_llegada"]:
                    try:
                        fecha_dt = widget.get_date()
                        datos_a_guardar[key] = fecha_dt.strftime('%Y-%m-%d')
                    except Exception as e_date:
                        raise ValueError(f"Error al obtener la fecha del campo '{key}': {e_date}")
                elif key == "valor_conversion":
                     valor_str = widget.get().strip().replace(',', '.')
                     if not valor_str: raise ValueError("Valor Conversión obligatorio.")
                     valor_conversion = float(valor_str)
                     if valor_conversion <=0: raise ValueError("Valor conversión debe ser > 0.")
                     datos_a_guardar[key] = valor_conversion
                else:
                    datos_a_guardar[key] = widget.get().strip()

            if not datos_a_guardar.get("proveedor") or not datos_a_guardar.get("numero_factura"):
                 raise ValueError("Proveedor y Número Factura son obligatorios.")

            valor_conv_final = datos_a_guardar.pop('valor_conversion')

        except ValueError as e:
            messagebox.showerror("Error Datos Generales", f"Datos inválidos: {e}")
            if hasattr(self, 'status_label_form_pvc') and self.status_label_form_pvc:
                 self.status_label_form_pvc.config(text="Error en datos generales.", foreground="red")
            return
        except Exception as e:
             messagebox.showerror("Error Datos Generales", f"Error inesperado recogiendo datos: {e}")
             if hasattr(self, 'status_label_form_pvc') and self.status_label_form_pvc:
                 self.status_label_form_pvc.config(text="Error interno formulario.", foreground="red")
             return

        # Validar que haya bobinas
        if not self.bobinas_temp_pvc:
            messagebox.showerror("Error Contenido", "Debe añadir al menos una bobina.")
            if hasattr(self, 'status_label_form_pvc') and self.status_label_form_pvc:
                 self.status_label_form_pvc.config(text="Error: Faltan bobinas.", foreground="red")
            return

        # Crear objeto, calcular, guardar, registrar
        contenedor = None
        try:
            # Importar aquí o globalmente
            # from contenedor.contenedorPVC import ContenedorPVC
            contenedor = ContenedorPVC(
                gastos={},
                contenido_pvc=[],
                valor_conversion=valor_conv_final,
                **datos_a_guardar
            )

            for gasto_data in self.gastos_temp_pvc:
                contenedor.agregar_gasto(gasto_data["tipo"], gasto_data["descripcion"], gasto_data["coste"])

            add_bobina_pvc_method = getattr(contenedor, 'agregar_bobina_pvc', None)
            if not add_bobina_pvc_method: raise AttributeError("Método 'agregar_bobina_pvc' no encontrado.")
            for bobina_data in self.bobinas_temp_pvc:
                add_bobina_pvc_method(**bobina_data, valor_conversion=contenedor.valor_conversion)

            contenedor.calcular_precios_finales()
            guardar_o_actualizar_contenedores_pvc([contenedor]) # Función específica PVC
            json_guardado = True
            print(f"Contenedor PVC {contenedor.numero_factura} guardado/actualizado en JSON.")
        except Exception as e:
            messagebox.showerror("Error Procesamiento", f"Error procesando datos Cont. PVC: {e}")
            if hasattr(self, 'status_label_form_pvc') and self.status_label_form_pvc:
                 self.status_label_form_pvc.config(text="Error procesando datos.", foreground="red")
            return

        # Registrar en Almacén
        db_registrado = False
        if json_guardado:
            try:
                registrar_entrada_almacen(contenedor)
                db_registrado = True
                print(f"Contenedor PVC {contenedor.numero_factura} registrado en almacén DB.")
            except Exception as e: messagebox.showwarning("Error Registro Almacén", f"JSON guardado, pero falló registro Almacén DB: {e}")

        # Feedback final
        if hasattr(self, 'status_label_form_pvc') and self.status_label_form_pvc:
            if json_guardado and db_registrado:
                messagebox.showinfo("Éxito", f"Contenedor PVC '{contenedor.numero_factura}' guardado y registrado.")
                self._limpiar_form_pvc()
                self.status_label_form_pvc.config(text=f"Contenedor '{contenedor.numero_factura}' procesado.", foreground="green")
            elif json_guardado:
                self.status_label_form_pvc.config(text=f"Cont. '{contenedor.numero_factura}' guardado JSON, falló registro DB.", foreground="orange")
            else:
                self.status_label_form_pvc.config(text="Error al guardar Cont. PVC en JSON.", foreground="red")




    def _limpiar_form_pvc(self):
        """Limpia todos los campos de entrada y listas del formulario PVC."""
        for entry in self.entries_cont_pvc.values(): entry.delete(0, tk.END)
        self.combo_gasto_tipo_pvc.set(''); self.entry_gasto_desc_pvc.delete(0, tk.END); self.entry_gasto_coste_pvc.delete(0, tk.END)
        for entry in self.entries_bobina_pvc.values(): entry.delete(0, tk.END)
        for iid in self.tree_gastos_pvc.get_children(): self.tree_gastos_pvc.delete(iid)
        for iid in self.tree_bobinas_pvc.get_children(): self.tree_bobinas_pvc.delete(iid)
        if hasattr(self, 'gastos_temp_pvc'): self.gastos_temp_pvc.clear()
        if hasattr(self, 'bobinas_temp_pvc'): self.bobinas_temp_pvc.clear()
        if hasattr(self, 'status_label_form_pvc'): self.status_label_form_pvc.config(text="Formulario limpio.", foreground="black")
        print("Formulario PVC limpiado.")

    # ===================================================================
    # ### FIN FUNCIONALIDAD AÑADIR CONTENEDOR PVC ###
    # ===================================================================

    # ===================================================================
    # ===================================================================
    # ### INICIO FUNCIONALIDAD AÑADIR CONTENEDOR FIELTRO ###
    # ===================================================================
    # ===================================================================

    def _mostrar_form_add_fieltro(self):
        """Limpia el área principal y construye el formulario de Fieltro."""
        self._limpiar_main_content()
        # Inicializar listas temporales específicas para Fieltro
        self.gastos_temp_fieltro = []
        self.bobinas_temp_fieltro = [] # Usamos 'bobinas' internamente por consistencia, aunque sean rollos
        # Llamar a la función que construye los widgets visuales
        self._crear_widgets_formulario_fieltro(self.main_content_frame)
        print("Mostrando formulario para añadir Contenedor Fieltro.")

    # Dentro de la clase Interfaz en interfaz.py

    def _crear_widgets_formulario_fieltro(self, parent_frame):
        """Crea y posiciona los widgets para el formulario de Añadir Contenedor Fieltro."""
        # --- Frame principal ---
        form_frame = ttk.Frame(parent_frame, padding="10")
        form_frame.pack(expand=True, fill="both")
        form_frame.grid_columnconfigure(1, weight=1)

        # --- Título ---
        ttk.Label(form_frame, text="Añadir Nuevo Contenedor de Fieltro", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=4, pady=(0, 15), sticky="w")

        # --- Sub-Frame: Datos Generales ---
        frame_datos_gen = ttk.LabelFrame(form_frame, text="Datos Generales", padding="10")
        frame_datos_gen.grid(row=1, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        frame_datos_gen.grid_columnconfigure(1, weight=1); frame_datos_gen.grid_columnconfigure(3, weight=1)

        # --- CAMBIO AQUÍ: Texto de etiquetas de fecha ---
        labels_contenedor = ["Fecha Pedido (DD-MM-YYYY):", "Fecha Llegada (DD-MM-YYYY):", "Proveedor:",
                             "Número Factura:", "Observaciones:", "Valor Conversión (USD-EUR):"]
        self.entries_cont_fieltro = {} # Diccionario específico
        key_map = ["fecha_pedido", "fecha_llegada", "proveedor", "numero_factura", "observaciones", "valor_conversion"]

        for i, text in enumerate(labels_contenedor):
            row, col = divmod(i, 2)
            lbl = ttk.Label(frame_datos_gen, text=text); lbl.grid(row=row, column=col*2, sticky="w", padx=5, pady=3)

            entry_widget = None
            current_key = key_map[i]

            # --- CAMBIO AQUÍ: Crear DateEntry o Entry ---
            if current_key in ["fecha_pedido", "fecha_llegada"]:
                 # ¡Asegúrate de tener 'from tkcalendar import DateEntry' al principio del archivo!
                entry_widget = DateEntry(frame_datos_gen, width=18, background='darkblue',
                                     foreground='white', borderwidth=2,
                                     date_pattern='dd-mm-yyyy', locale='es_ES')
            else:
                entry_widget = ttk.Entry(frame_datos_gen, width=30)
            # ---------------------------------------------

            entry_widget.grid(row=row, column=col*2 + 1, sticky="ew", padx=5, pady=3)
            self.entries_cont_fieltro[current_key] = entry_widget

        # --- Sub-Frame: Gastos (Sin cambios, usa widgets _fieltro) ---
        frame_gastos = ttk.LabelFrame(form_frame, text="Gastos Asociados", padding="10")
        frame_gastos.grid(row=2, column=0, columnspan=4, sticky="ew", padx=5, pady=10)
        frame_gastos.grid_columnconfigure(1, weight=1)
        # ... (widgets de gastos _fieltro: combo_gasto_tipo_fieltro, etc.) ...
        ttk.Label(frame_gastos, text="Tipo:").grid(row=0, column=0, padx=(0, 5), pady=3, sticky="nw")
        self.combo_gasto_tipo_fieltro = ttk.Combobox(frame_gastos, values=TIPOS_GASTO_VALIDOS, state="readonly", width=10)
        self.combo_gasto_tipo_fieltro.grid(row=1, column=0, padx=(0, 5), pady=3, sticky="w")
        ttk.Label(frame_gastos, text="Descripción:").grid(row=0, column=1, padx=5, pady=3, sticky="w")
        self.entry_gasto_desc_fieltro = ttk.Entry(frame_gastos)
        self.entry_gasto_desc_fieltro.grid(row=1, column=1, padx=5, pady=3, sticky="ew")
        ttk.Label(frame_gastos, text="Coste (€):").grid(row=0, column=2, padx=5, pady=3, sticky="w")
        self.entry_gasto_coste_fieltro = ttk.Entry(frame_gastos, width=10)
        self.entry_gasto_coste_fieltro.grid(row=1, column=2, padx=5, pady=3, sticky="w")
        ttk.Button(frame_gastos, text="Añadir Gasto", command=self._add_gasto_fieltro_temp).grid(row=1, column=3, padx=5, pady=5, sticky="w")
        cols_gastos = ("Tipo", "Descripción", "Coste")
        self.tree_gastos_fieltro = ttk.Treeview(frame_gastos, columns=cols_gastos, show="headings", height=3, selectmode="browse")
        self.tree_gastos_fieltro.heading("Tipo", text="Tipo"); self.tree_gastos_fieltro.column("Tipo", width=80, anchor=tk.W)
        self.tree_gastos_fieltro.heading("Descripción", text="Descripción"); self.tree_gastos_fieltro.column("Descripción", width=250, anchor=tk.W)
        self.tree_gastos_fieltro.heading("Coste", text="Coste (€)"); self.tree_gastos_fieltro.column("Coste", width=80, anchor=tk.E)
        self.tree_gastos_fieltro.grid(row=2, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        ttk.Button(frame_gastos, text="Eliminar Gasto Sel.", command=self._del_gasto_fieltro_temp).grid(row=3, column=0, columnspan=4, pady=(0, 5))


        # --- Sub-Frame: Rollos Fieltro (Sin cambios aquí) ---
        frame_bobinas = ttk.LabelFrame(form_frame, text="Rollos de Fieltro", padding="10")
        frame_bobinas.grid(row=3, column=0, columnspan=4, sticky="ew", padx=5, pady=10)
        # ... (widgets de rollos _fieltro: sin Color) ...
        labels_bobinas = ["Espesor:", "Ancho(mm):", "Largo(m):", "Nº Rollos:", "Precio/m(USD):"] # Quitado (mm) de Espesor
        self.entries_bobina_fieltro = {} # Diccionario específico
        key_map_bobinas = ["espesor", "ancho", "largo", "n_bobinas", "metro_lineal_usd"]
        b_row = 0
        for i, text in enumerate(labels_bobinas):
            lbl = ttk.Label(frame_bobinas, text=text)
            col_lbl = (i % 3) * 2
            col_entry = col_lbl + 1
            row_entry = b_row + (i // 3) * 2
            lbl.grid(row=row_entry, column=col_lbl, padx=5, pady=3, sticky="w")
            entry = ttk.Entry(frame_bobinas, width=12) # Espesor es Entry normal
            entry.grid(row=row_entry, column=col_entry, padx=5, pady=3, sticky="ew")
            self.entries_bobina_fieltro[key_map_bobinas[i]] = entry
        ttk.Button(frame_bobinas, text="Añadir Rollo", command=self._add_bobina_fieltro_temp).grid(row=b_row + 2 , column=4, padx=5, pady=5, sticky="se", rowspan=2)
        cols_bobinas = ("Espesor", "Ancho", "Largo", "Nº", "USD/m")
        self.tree_bobinas_fieltro = ttk.Treeview(frame_bobinas, columns=cols_bobinas, show="headings", height=4, selectmode="browse")
        for col in cols_bobinas: self.tree_bobinas_fieltro.heading(col, text=col); self.tree_bobinas_fieltro.column(col, width=80, anchor=tk.CENTER)
        self.tree_bobinas_fieltro.grid(row=b_row + 4, column=0, columnspan=5, sticky="nsew", padx=5, pady=5)
        ttk.Button(frame_bobinas, text="Eliminar Rollo Sel.", command=self._del_bobina_fieltro_temp).grid(row=b_row + 5, column=0, columnspan=5, pady=(0, 5))

        # --- Botón Guardar Final y Status Label (Sin cambios) ---
        ttk.Button(form_frame, text="GUARDAR CONTENEDOR FIELTRO", command=self._guardar_contenedor_fieltro, style="Accent.TButton").grid(row=4, column=0, columnspan=4, pady=20, ipady=5)
        self.status_label_form_fieltro = ttk.Label(form_frame, text="Formulario listo.")
        self.status_label_form_fieltro.grid(row=5, column=0, columnspan=4, pady=5)


    # --- Métodos de lógica interna del formulario Fieltro ---

    def _add_gasto_fieltro_temp(self):
        """Lee datos de gasto, valida, y añade a lista temporal y TreeView Fieltro."""
        # Lógica idéntica a _add_gasto_goma_temp, usando widgets _fieltro
        tipo = self.combo_gasto_tipo_fieltro.get()
        descripcion = self.entry_gasto_desc_fieltro.get().strip()
        coste_str = self.entry_gasto_coste_fieltro.get().strip()
        try:
            coste = float(coste_str)
            if not tipo or not descripcion or coste < 0: raise ValueError("Tipo, descripción (no vacía) y coste (>=0) requeridos.")
        except ValueError as e: messagebox.showerror("Error Gasto", f"Datos de gasto inválidos: {e}"); return

        gasto_data = {"tipo": tipo, "descripcion": descripcion, "coste": coste}
        self.gastos_temp_fieltro.append(gasto_data)
        self.tree_gastos_fieltro.insert("", tk.END, values=(tipo, descripcion, f"{coste:.2f}"))
        self.combo_gasto_tipo_fieltro.set(''); self.entry_gasto_desc_fieltro.delete(0, tk.END); self.entry_gasto_coste_fieltro.delete(0, tk.END)
        self.status_label_form_fieltro.config(text=f"Gasto '{descripcion}' añadido.")

    def _del_gasto_fieltro_temp(self):
        """Elimina el gasto seleccionado de la lista temporal y TreeView Fieltro."""
        # Lógica idéntica a _del_gasto_goma_temp, usando widgets _fieltro
        selected_iid = self.tree_gastos_fieltro.selection()
        if not selected_iid: messagebox.showwarning("Eliminar Gasto", "Seleccione un gasto."); return
        item_index = self.tree_gastos_fieltro.index(selected_iid[0])
        item_values = self.tree_gastos_fieltro.item(selected_iid[0], 'values')
        try:
            del self.gastos_temp_fieltro[item_index]; self.tree_gastos_fieltro.delete(selected_iid[0])
            self.status_label_form_fieltro.config(text=f"Gasto '{item_values[1]}' eliminado.")
        except IndexError: messagebox.showerror("Error", "Índice de gasto no válido.")

    def _add_bobina_fieltro_temp(self):
        """Lee datos de rollo Fieltro, valida, y añade a lista y TreeView."""
        # Lógica idéntica a _add_bobina_goma_temp (sin color)
        try:
            espesor = self.entries_bobina_fieltro["espesor"].get().strip()            
            ancho = float(self.entries_bobina_fieltro["ancho"].get().strip().replace(',', '.'))
            largo = float(self.entries_bobina_fieltro["largo"].get().strip().replace(',', '.'))
            n_bobinas = int(self.entries_bobina_fieltro["n_bobinas"].get().strip())
            metro_lineal_usd_str = self.entries_bobina_fieltro["metro_lineal_usd"].get().strip().replace(',', '.')
            if not metro_lineal_usd_str: raise ValueError("Precio/m(USD) no puede estar vacío.")
            metro_lineal_usd = float(metro_lineal_usd_str)

            if not all(v > 0 for v in [ancho, largo, n_bobinas]) or metro_lineal_usd < 0:
                raise ValueError("Valores numéricos > 0 (precio >= 0).")
        except KeyError as e: messagebox.showerror("Error Rollo", f"Error interno: Clave no encontrada {e}"); return
        except ValueError as e: messagebox.showerror("Error Rollo", f"Datos de rollo inválidos: {e}"); return

        bobina_params = { # Usamos 'bobina' como nombre interno consistente
            "espesor": espesor, "ancho": ancho, "largo": largo,
            "n_bobinas": n_bobinas, "metro_lineal_usd": metro_lineal_usd
            # Sin color para fieltro
        }
        self.bobinas_temp_fieltro.append(bobina_params)
        self.tree_bobinas_fieltro.insert("", tk.END, values=(espesor, ancho, largo, n_bobinas, f"{metro_lineal_usd:.2f}"))

        for entry_widget in self.entries_bobina_fieltro.values(): entry_widget.delete(0, tk.END)
        self.status_label_form_fieltro.config(text=f"Rollo {espesor}mm añadido.")

    def _del_bobina_fieltro_temp(self):
        """Elimina el rollo Fieltro seleccionado de la lista temporal y TreeView."""
        # Lógica idéntica a _del_bobina_goma_temp, usando widgets _fieltro
        selected_iid = self.tree_bobinas_fieltro.selection()
        if not selected_iid: messagebox.showwarning("Eliminar Rollo", "Seleccione un rollo."); return
        item_index = self.tree_bobinas_fieltro.index(selected_iid[0])
        item_values = self.tree_bobinas_fieltro.item(selected_iid[0], 'values')
        try:
            del self.bobinas_temp_fieltro[item_index]; self.tree_bobinas_fieltro.delete(selected_iid[0])
            self.status_label_form_fieltro.config(text=f"Rollo {item_values[0]}mm eliminado.")
        except IndexError: messagebox.showerror("Error", "Índice de rollo no válido.")

    # Dentro de la clase Interfaz en interfaz.py

    def _guardar_contenedor_fieltro(self):
        """Recoge datos del form Fieltro, crea obj ContenedorFieltro, calcula, guarda JSON y registra en DB."""
        # Asegurarse de que el label de estado existe
        if not hasattr(self, 'status_label_form_fieltro') or self.status_label_form_fieltro is None:
             print("Advertencia: status_label_form_fieltro no inicializado.")
        else:
            self.status_label_form_fieltro.config(text="Procesando...", foreground="blue")

        datos_a_guardar = {}
        valor_conv_final = 0.0

        try: # Validar y procesar datos generales
            # Importar datetime si no está ya importado globalmente
            from datetime import datetime

            datos_generales_widgets = self.entries_cont_fieltro # Diccionario con los widgets {key: widget}

            # --- Recoger y procesar datos generales ---
            for key, widget in datos_generales_widgets.items():
                if key in ["fecha_pedido", "fecha_llegada"]:
                    try:
                        fecha_dt = widget.get_date() # Obtiene objeto datetime.date
                        # Formatear a yyyy-mm-dd para consistencia interna y guardado
                        datos_a_guardar[key] = fecha_dt.strftime('%Y-%m-%d')
                    except Exception as e_date:
                        raise ValueError(f"Error al obtener la fecha del campo '{key}': {e_date}")
                elif key == "valor_conversion":
                     valor_str = widget.get().strip().replace(',', '.')
                     if not valor_str: raise ValueError("Valor Conversión obligatorio.")
                     valor_conversion = float(valor_str) # Convertir y validar
                     if valor_conversion <=0: raise ValueError("Valor conversión debe ser > 0.")
                     datos_a_guardar[key] = valor_conversion # Guardar como float
                else:
                    # Para otros campos como proveedor, factura, observaciones
                    datos_a_guardar[key] = widget.get().strip()

            # --- Validaciones básicas usando el diccionario procesado ---
            if not datos_a_guardar.get("proveedor") or not datos_a_guardar.get("numero_factura"):
                 raise ValueError("Proveedor y Número Factura son obligatorios.")
            # Añadir otras validaciones necesarias sobre datos_a_guardar aquí...

            # --- PREPARACIÓN FINAL ---
            # Sacar valor_conversion de datos_a_guardar si se pasa aparte al constructor
            valor_conv_final = datos_a_guardar.pop('valor_conversion')
            # datos_a_guardar ahora contiene el resto de datos generales listos

        except ValueError as e:
            messagebox.showerror("Error Datos Generales", f"Datos inválidos: {e}")
            if hasattr(self, 'status_label_form_fieltro') and self.status_label_form_fieltro:
                 self.status_label_form_fieltro.config(text="Error en datos generales.", foreground="red")
            return
        except Exception as e: # Captura otros errores inesperados
             messagebox.showerror("Error Datos Generales", f"Error inesperado recogiendo datos: {e}")
             if hasattr(self, 'status_label_form_fieltro') and self.status_label_form_fieltro:
                  self.status_label_form_fieltro.config(text="Error interno formulario.", foreground="red")
             return

        # Validar que haya rollos añadidos
        if not hasattr(self, 'bobinas_temp_fieltro') or not self.bobinas_temp_fieltro: # Comprobar si el atributo existe
            messagebox.showerror("Error Contenido", "Debe añadir al menos un rollo.")
            if hasattr(self, 'status_label_form_fieltro') and self.status_label_form_fieltro:
                self.status_label_form_fieltro.config(text="Error: Faltan rollos.", foreground="red")
            return

        # Crear instancia ContenedorFieltro
        contenedor = None # Inicializar
        try:
            # Importar aquí o globalmente
            # from contenedor.contenedorFieltro import ContenedorFieltro
            contenedor = ContenedorFieltro(
                gastos={}, # Se añadirán después
                contenido_fieltro=[], # Usar la clave correcta
                valor_conversion=valor_conv_final, # Pasar el float
                **datos_a_guardar # Pasar el diccionario con el resto
            )
        except Exception as e:
            messagebox.showerror("Error Creación", f"No se pudo crear el objeto ContenedorFieltro: {e}")
            if hasattr(self, 'status_label_form_fieltro') and self.status_label_form_fieltro:
                 self.status_label_form_fieltro.config(text="Error interno.", foreground="red")
            return

        # --- Lógica Backend ---
        json_guardado = False
        try:
            # Añadir gastos
            if hasattr(self, 'gastos_temp_fieltro'): # Comprobar si existe la lista
                for gasto_data in self.gastos_temp_fieltro:
                    contenedor.agregar_gasto(gasto_data["tipo"], gasto_data["descripcion"], gasto_data["coste"])

            # Añadir rollos (asegurarse del nombre del método)
            add_rollo_method = getattr(contenedor, 'agregar_rollo_fieltro', None)
            if not add_rollo_method: raise AttributeError("Método 'agregar_rollo_fieltro' no encontrado.")
            if hasattr(self, 'bobinas_temp_fieltro'): # Usamos bobinas_temp_fieltro internamente
                for rollo_data in self.bobinas_temp_fieltro:
                    add_rollo_method(**rollo_data, valor_conversion=contenedor.valor_conversion)

            # Calcular precios finales
            contenedor.calcular_precios_finales()

            # Guardar en JSON
            guardar_o_actualizar_contenedores_fieltro([contenedor]) # Función específica de fieltro
            json_guardado = True
            print(f"Contenedor Fieltro {contenedor.numero_factura} guardado/actualizado en JSON.")

        except Exception as e: # Capturar cualquier error durante el procesamiento backend
            messagebox.showerror("Error Procesamiento", f"Error procesando datos del contenedor Fieltro: {e}")
            if hasattr(self, 'status_label_form_fieltro') and self.status_label_form_fieltro:
                 self.status_label_form_fieltro.config(text="Error procesando datos.", foreground="red")
            return # No continuar si falla

        # Registrar en Almacén DB
        db_registrado = False
        if json_guardado: # Solo intentar registrar si se guardó el JSON
             try:
                 registrar_entrada_almacen(contenedor)
                 db_registrado = True
                 print(f"Contenedor Fieltro {contenedor.numero_factura} registrado en almacén DB.")
             except Exception as e:
                 messagebox.showwarning("Error Registro Almacén", f"JSON guardado, pero falló el registro en Almacén DB: {e}\nRevise la base de datos manualmente si es necesario.")

        # Feedback final y limpiar
        if hasattr(self, 'status_label_form_fieltro') and self.status_label_form_fieltro:
            if json_guardado and db_registrado:
                messagebox.showinfo("Éxito", f"Contenedor Fieltro '{contenedor.numero_factura}' guardado y registrado en almacén.")
                self._limpiar_form_fieltro() # Limpiar solo si todo fue bien
                self.status_label_form_fieltro.config(text=f"Contenedor '{contenedor.numero_factura}' procesado con éxito.", foreground="green")
            elif json_guardado and not db_registrado:
                self.status_label_form_fieltro.config(text=f"Cont. '{contenedor.numero_factura}' guardado en JSON, pero falló registro DB.", foreground="orange")
            else: # Falló el guardado JSON
                 self.status_label_form_fieltro.config(text="Error al guardar el contenedor en JSON.", foreground="red")

    def _limpiar_form_fieltro(self):
        """Limpia todos los campos de entrada y listas del formulario Fieltro."""
        # Lógica idéntica a _limpiar_form_goma, usando widgets _fieltro
        for entry in self.entries_cont_fieltro.values(): entry.delete(0, tk.END)
        self.combo_gasto_tipo_fieltro.set(''); self.entry_gasto_desc_fieltro.delete(0, tk.END); self.entry_gasto_coste_fieltro.delete(0, tk.END)
        for entry in self.entries_bobina_fieltro.values(): entry.delete(0, tk.END)
        for iid in self.tree_gastos_fieltro.get_children(): self.tree_gastos_fieltro.delete(iid)
        for iid in self.tree_bobinas_fieltro.get_children(): self.tree_bobinas_fieltro.delete(iid)
        if hasattr(self, 'gastos_temp_fieltro'): self.gastos_temp_fieltro.clear()
        if hasattr(self, 'bobinas_temp_fieltro'): self.bobinas_temp_fieltro.clear()
        if hasattr(self, 'status_label_form_fieltro'): self.status_label_form_fieltro.config(text="Formulario limpio.", foreground="black")
        print("Formulario Fieltro limpiado.")


    # ===================================================================
    # ### FIN FUNCIONALIDAD AÑADIR CONTENEDOR FIELTRO ###
    # ===================================================================


    # ===================================================================
    # ===================================================================
    # ### INICIO FUNCIONALIDAD VER/GESTIONAR CONTENEDORES ###
    # ===================================================================
    # ===================================================================

    def _mostrar_vista_ver_contenedores(self):
        """Limpia el frame principal y crea la vista para ver contenedores."""
        self._limpiar_main_content()
        print("Mostrando vista para Ver/Gestionar Contenedores.")
        # Llamar a la función que construye los widgets de esta vista
        self._crear_widgets_vista_ver_contenedores(self.main_content_frame)
        # Cargar los datos iniciales en la tabla
        self._cargar_y_mostrar_contenedores()

    # DENTRO de la clase Interfaz en interfaz.py

    def _crear_widgets_vista_ver_contenedores(self, parent_frame):
        """Crea los widgets para la vista de listado de contenedores, incluyendo scrollbars."""
        view_frame = ttk.Frame(parent_frame, padding="5")
        view_frame.pack(expand=True, fill="both")
        # Configurar grid dentro de view_frame para que la tabla/scrollbars se expandan
        view_frame.grid_rowconfigure(1, weight=1)    # Fila 1 (con tabla) se expande
        view_frame.grid_columnconfigure(0, weight=1) # Columna 0 (con tabla) se expande

        # Título
        ttk.Label(view_frame, text="Listado de Contenedores Importados", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky='w')

        # --- Frame para filtros (dejamos el espacio por si lo añadimos después) ---
        filter_frame = ttk.Frame(view_frame)
        filter_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=5)
        # Aquí irían los filtros... por ahora vacío o con un label
        ttk.Label(filter_frame, text="Filtros (Pendiente):").pack(side=tk.LEFT, padx=5)

        # --- Frame para contener el Treeview y las Scrollbars ---
        tree_frame = ttk.Frame(view_frame)
        tree_frame.grid(row=2, column=0, columnspan=2, sticky='nsew', pady=5)
        # Configurar grid dentro de tree_frame
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # --- Treeview para mostrar los contenedores ---
        cols = ("Factura", "Proveedor", "Tipo", "F. Llegada", "Observaciones")
        self.tree_ver_contenedores = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")

        # Configurar cabeceras y columnas (igual que antes)
        self.tree_ver_contenedores.heading("Factura", text="Nº Factura"); self.tree_ver_contenedores.column("Factura", width=120, anchor=tk.W)
        self.tree_ver_contenedores.heading("Proveedor", text="Proveedor"); self.tree_ver_contenedores.column("Proveedor", width=180, anchor=tk.W)
        self.tree_ver_contenedores.heading("Tipo", text="Material"); self.tree_ver_contenedores.column("Tipo", width=80, anchor=tk.CENTER)
        self.tree_ver_contenedores.heading("F. Llegada", text="F. Llegada"); self.tree_ver_contenedores.column("F. Llegada", width=100, anchor=tk.CENTER)
        self.tree_ver_contenedores.heading("Observaciones", text="Observaciones"); self.tree_ver_contenedores.column("Observaciones", width=300)

        # --- Crear y Configurar Scrollbars ---
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_ver_contenedores.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree_ver_contenedores.xview)
        self.tree_ver_contenedores.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # --- Posicionar Treeview y Scrollbars usando grid DENTRO de tree_frame ---
        self.tree_ver_contenedores.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        # --- Frame para botones de acción ---
        action_frame = ttk.Frame(view_frame)
        action_frame.grid(row=3, column=0, columnspan=2, sticky='ew', pady=5) # Ajustado a grid

        ttk.Button(action_frame, text="Ver Detalles", command=self._ver_detalles_contenedor).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Editar", command=self._editar_contenedor).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Eliminar", command=self._eliminar_contenedor).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Refrescar Lista", command=self._cargar_y_mostrar_contenedores).pack(side=tk.RIGHT, padx=5)

        # --- Label de estado ---
        self.status_label_ver_contenedores = ttk.Label(view_frame, text="")
        self.status_label_ver_contenedores.grid(row=4, column=0, columnspan=2, sticky='ew') # Ajustado a grid

    def _cargar_y_mostrar_contenedores(self):
        """Carga datos de todos los JSON de contenedor, los guarda internamente
        y los muestra en el Treeview, mostrando subtipo para Goma si aplica."""

        # Verificar que los widgets necesarios existen
        status_label = getattr(self, 'status_label_ver_contenedores', None)
        tree_widget = getattr(self, 'tree_ver_contenedores', None)
        cont_dict = getattr(self, 'contenedores_mostrados', None)

        if not tree_widget or not tree_widget.winfo_exists():
            print("Error: Treeview para contenedores no existe.")
            return
        if cont_dict is None:
            print("Error: Diccionario 'contenedores_mostrados' no inicializado.")
            self.contenedores_mostrados = {} # Inicializar por si acaso
            cont_dict = self.contenedores_mostrados

        if status_label and status_label.winfo_exists():
            status_label.config(text="Cargando datos...", foreground="blue")

        # Limpiar tabla y diccionario interno
        for i in tree_widget.get_children():
            tree_widget.delete(i)
        cont_dict.clear()

        todos_los_contenedores = []
        # Diccionario de carga (como estaba antes)
        tipos_carga = {
            'GOMA': cargar_contenedores_goma,
            'PVC': cargar_contenedores_pvc,
            'FIELTRO': cargar_contenedores_fieltro,
        }

        # Cargar datos de cada tipo (como estaba antes)
        for tipo, func_carga in tipos_carga.items():
            if func_carga:
                try:
                    contenedores_tipo = func_carga()
                    if contenedores_tipo:
                        for cont in contenedores_tipo:
                            cont.tipo_material_display = tipo # Guardamos el tipo principal
                            todos_los_contenedores.append(cont)
                            factura_id = getattr(cont, 'numero_factura', None)
                            if factura_id:
                                cont_dict[factura_id] = cont # Guardar objeto completo
                except Exception as e:
                    print(f"Error al cargar contenedores de tipo {tipo}: {e}")
            else:
                print(f"Función de carga para {tipo} no disponible.")

        # Ordenar (como estaba antes)
        try: todos_los_contenedores.sort(key=lambda x: getattr(x, 'fecha_llegada', ''), reverse=True)
        except Exception: print("Advertencia: No se pudo ordenar por fecha.")

        # Poblar Treeview
        items_insertados = 0
        if todos_los_contenedores:
            for cont in todos_los_contenedores:
                factura = getattr(cont, 'numero_factura', 'N/A')
                proveedor = getattr(cont, 'proveedor', 'N/A')
                f_llegada = getattr(cont, 'fecha_llegada', 'N/A')
                obs = getattr(cont, 'observaciones', '')

                ## CAMBIO ## Determinar qué mostrar en la columna de material
                tipo_mat_display = getattr(cont, 'tipo_material_display', 'N/A') # Default: GOMA, PVC, etc.

                # Si es un contenedor de Goma y tiene contenido...
                if isinstance(cont, ContenedorGoma) and hasattr(cont, 'contenido') and cont.contenido:
                    # ...intenta obtener el subtipo de la *primera* bobina
                    primer_item_subtipo = getattr(cont.contenido[0], 'subtipo', 'NORMAL')
                    # Si el subtipo no es el normal, úsalo para mostrar
                    if primer_item_subtipo and primer_item_subtipo != 'NORMAL':
                        tipo_mat_display = primer_item_subtipo # Mostrar "CARAMELO", "VERDE", etc.
                ## FIN CAMBIO ##

                # Formatear fecha para mostrar (opcional, como estaba antes)
                try:
                    f_llegada_dt = datetime.strptime(f_llegada, '%Y-%m-%d')
                    f_llegada_display = f_llegada_dt.strftime('%d-%m-%Y')
                except (ValueError, TypeError):
                    f_llegada_display = f_llegada # Mostrar como está si no se puede formatear

                # Ensamblar valores para la fila
                valores = (factura, proveedor, tipo_mat_display, f_llegada_display, obs)

                # Insertar en Treeview (lógica de manejo de duplicados como estaba antes)
                try:
                    tree_widget.insert('', tk.END, iid=factura, values=valores)
                    items_insertados += 1
                except tk.TclError:
                    try:
                        alt_iid = f"{factura}_{items_insertados}"
                        tree_widget.insert('', tk.END, iid=alt_iid, values=valores)
                        items_insertados += 1
                        # Actualizar clave en diccionario si se usó ID alternativo
                        if factura in cont_dict:
                            cont_dict[alt_iid] = cont_dict.pop(factura)
                    except Exception as e_ins: print(f"Error insertando fila contenedor alternativa para {factura}: {e_ins}")
                except Exception as e_gral: print(f"Error general insertando fila contenedor para {factura}: {e_gral}")

        # Actualizar label de estado (como estaba antes)
        if status_label and status_label.winfo_exists():
            if items_insertados > 0:
                status_label.config(text=f"{items_insertados} contenedor(es) cargado(s).", foreground="black")
            else:
                status_label.config(text="No se encontraron contenedores.", foreground="orange")

    def _ver_detalles_contenedor(self):
        """Muestra los detalles completos del contenedor seleccionado en una nueva ventana."""
        selected_iids = self.tree_ver_contenedores.selection()
        if not selected_iids:
            messagebox.showinfo("Ver Detalles", "Por favor, seleccione un contenedor de la lista.")
            return

        selected_iid = selected_iids[0] # El iid es el numero_factura

        # Recuperar el objeto completo del diccionario
        contenedor_obj = self.contenedores_mostrados.get(selected_iid)

        if not contenedor_obj:
            messagebox.showerror("Error", f"No se encontraron los datos completos para la factura '{selected_iid}'. Intente refrescar la lista.")
            return

        # --- Crear la nueva ventana Toplevel ---
        details_window = tk.Toplevel(self.root)
        # Usar el nombre de la clase para el tipo (Goma, PVC, etc.)
        tipo_display = getattr(contenedor_obj, 'tipo_material_display', type(contenedor_obj).__name__)
        details_window.title(f"Detalles {tipo_display} - Factura: {contenedor_obj.numero_factura}")
        details_window.minsize(600, 400) # Tamaño mínimo
        details_window.transient(self.root)
        details_window.grab_set() # Hacerla modal

        
        try:
                screen_width = details_window.winfo_screenwidth() # O self.root.winfo_screenwidth()
                screen_height = details_window.winfo_screenheight() # O self.root.winfo_screenheight()
                geometry_str = f"{screen_width}x{screen_height}+0+0"
                print(f"Ajustando geometría detalles a: {geometry_str}")
                details_window.geometry(geometry_str)
        except Exception as e:
                print(f"Error al intentar ajustar la geometría de detalles: {e}")
                # Usar un tamaño por defecto si falla
                # details_window.geometry("850x650")

        # Configurar grid principal de la ventana de detalles
        details_window.rowconfigure(2, weight=1) # Frame contenido se expande más
        details_window.rowconfigure(1, weight=1) # Frame gastos se expande
        details_window.columnconfigure(0, weight=1)

        # --- Frame para Datos Generales ---
        frame_general = ttk.LabelFrame(details_window, text="Datos Generales", padding="10")
        frame_general.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        frame_general.grid_columnconfigure(1, weight=1)
        frame_general.grid_columnconfigure(3, weight=1)

        # Poblar Datos Generales (usando grid)
        gen_labels = {
            "Factura:": getattr(contenedor_obj, 'numero_factura', 'N/A'),
            "Proveedor:": getattr(contenedor_obj, 'proveedor', 'N/A'),
            "Fecha Pedido:": getattr(contenedor_obj, 'fecha_pedido', 'N/A'),
            "Fecha Llegada:": getattr(contenedor_obj, 'fecha_llegada', 'N/A'),
            "Valor Conversión:": getattr(contenedor_obj, 'valor_conversion', 'N/A'),
            "Observaciones:": getattr(contenedor_obj, 'observaciones', '')
        }
        row_num = 0
        for label_text, value_text in gen_labels.items():
            lbl = ttk.Label(frame_general, text=label_text, anchor="w")
            lbl.grid(row=row_num, column=0, sticky="w", padx=5, pady=2)
            # Usar Label para mostrar el valor, ajustando columnspan para observaciones
            cols = 3 if label_text != "Observaciones:" else 1
            val = ttk.Label(frame_general, text=value_text, anchor="w", wraplength=600) # Wraplength para observaciones
            val.grid(row=row_num, column=1, columnspan=cols, sticky="ew", padx=5, pady=2)
            row_num += 1

        # --- Frame para Gastos (con Treeview y Scrollbar) ---
        frame_gastos = ttk.LabelFrame(details_window, text="Gastos Asociados", padding="10")
        frame_gastos.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        frame_gastos.grid_rowconfigure(0, weight=1)
        frame_gastos.grid_columnconfigure(0, weight=1)

        cols_gastos = ("Tipo", "Descripción", "Coste")
        tree_gastos = ttk.Treeview(frame_gastos, columns=cols_gastos, show="headings", height=4, selectmode="none")
        tree_gastos.heading("Tipo", text="Tipo"); tree_gastos.column("Tipo", width=80, anchor="w")
        tree_gastos.heading("Descripción", text="Descripción"); tree_gastos.column("Descripción", width=400, anchor="w") # Más ancho
        tree_gastos.heading("Coste", text="Coste (€)"); tree_gastos.column("Coste", width=100, anchor="e")

        scrollbar_gastos = ttk.Scrollbar(frame_gastos, orient="vertical", command=tree_gastos.yview)
        tree_gastos.configure(yscrollcommand=scrollbar_gastos.set)

        tree_gastos.grid(row=0, column=0, sticky="nsew")
        scrollbar_gastos.grid(row=0, column=1, sticky="ns")

        # Poblar Treeview de gastos
        if hasattr(contenedor_obj, 'gastos') and isinstance(contenedor_obj.gastos, dict):
            for tipo, lista_gastos in sorted(contenedor_obj.gastos.items()): # Ordenar por tipo
                 if lista_gastos:
                      # Insertar una fila separadora/título para el tipo (opcional)
                      # tree_gastos.insert('', 'end', values=(f"--- {tipo} ---", "", ""))
                      for gasto in lista_gastos:
                           desc = gasto.get('descripcion', '?')
                           cost = gasto.get('coste', 0)
                           # Formatear coste como número flotante con 2 decimales
                           cost_str = f"{float(cost):.2f}" if isinstance(cost, (int, float, str)) and str(cost).replace('.','',1).isdigit() else "Inválido"
                           tree_gastos.insert('', 'end', values=(tipo, desc, cost_str))
        else:
             tree_gastos.insert('', 'end', values=("", "(Sin datos de gastos)", ""))


        # --- Frame para Contenido (con Treeview y Scrollbars V/H) ---
        frame_contenido = ttk.LabelFrame(details_window, text="Contenido del Contenedor", padding="10")
        frame_contenido.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        frame_contenido.grid_rowconfigure(0, weight=1)
        frame_contenido.grid_columnconfigure(0, weight=1)

        # Definir todas las columnas posibles, se mostrará '-' si no aplica
        cols_contenido = ("Item", "Tipo", "Espesor", "Ancho", "Largo", "Nº", "Color", "Código", "Modelo", "Coste/m (€)", "Coste Total (€)")
        tree_contenido = ttk.Treeview(frame_contenido, columns=cols_contenido, show="headings", height=8, selectmode="none")

        # Configurar cabeceras y anchos (ajusta según necesidad)
        tree_contenido.heading("Item", text="#"); tree_contenido.column("Item", width=30, anchor="center")
        tree_contenido.heading("Tipo", text="Tipo"); tree_contenido.column("Tipo", width=80)
        tree_contenido.heading("Espesor", text="Espesor"); tree_contenido.column("Espesor", width=120) # Más ancho para string
        tree_contenido.heading("Ancho", text="Ancho"); tree_contenido.column("Ancho", width=70, anchor="e")
        tree_contenido.heading("Largo", text="Largo"); tree_contenido.column("Largo", width=70, anchor="e")
        tree_contenido.heading("Nº", text="Nº"); tree_contenido.column("Nº", width=40, anchor="center")
        tree_contenido.heading("Color", text="Color"); tree_contenido.column("Color", width=90)
        
        tree_contenido.heading("Coste/m (€)", text="Coste/m (€)"); tree_contenido.column("Coste/m (€)", width=100, anchor="e")
        tree_contenido.heading("Coste Total (€)", text="Coste Total (€)"); tree_contenido.column("Coste Total (€)", width=120, anchor="e")

        # Scrollbars (Vertical y Horizontal)
        v_scroll_cont = ttk.Scrollbar(frame_contenido, orient="vertical", command=tree_contenido.yview)
        h_scroll_cont = ttk.Scrollbar(frame_contenido, orient="horizontal", command=tree_contenido.xview)
        tree_contenido.configure(yscrollcommand=v_scroll_cont.set, xscrollcommand=h_scroll_cont.set)

        tree_contenido.grid(row=0, column=0, sticky="nsew")
        v_scroll_cont.grid(row=0, column=1, sticky="ns")
        h_scroll_cont.grid(row=1, column=0, columnspan=2, sticky="ew")

        # Poblar Treeview de contenido
        if hasattr(contenedor_obj, 'contenido') and contenedor_obj.contenido:
            for i, item in enumerate(contenedor_obj.contenido):
                # Extraer datos de forma segura con getattr
                tipo_item = type(item).__name__
                espesor = getattr(item, 'espesor', '-')
                ancho = getattr(item, 'ancho', '-')
                largo = getattr(item, 'largo', '-')
                n_bobinas = getattr(item, 'n_bobinas', '-')
                color = getattr(item, 'color', '-')
                codigo = getattr(item, 'codigo', '-')
                modelo = getattr(item, 'modelo', '-')
                coste_m = getattr(item, 'metro_lineal_euro_mas_gastos', None)
                coste_t = getattr(item, 'precio_total_euro_gastos', None)

                # Formatear para display
                coste_m_str = f"{coste_m:.4f}" if isinstance(coste_m, (int, float)) else "-"
                coste_t_str = f"{coste_t:.2f}" if isinstance(coste_t, (int, float)) else "-"
                # Formatear números si son válidos
                ancho_str = f"{float(ancho):.1f}" if isinstance(ancho, (int, float)) else str(ancho)
                largo_str = f"{float(largo):.1f}" if isinstance(largo, (int, float)) else str(largo)

                # Insertar valores en el orden de cols_contenido
                tree_contenido.insert('', 'end', values=(
                    i+1, tipo_item, espesor, ancho_str, largo_str, n_bobinas,
                    color, codigo, modelo, coste_m_str, coste_t_str
                ))
        else:
            tree_contenido.insert('', 'end', values=("", "", "", "(Sin contenido)", "", "", "", "", "", "", ""))


        # --- Botón Cerrar ---
        close_button = ttk.Button(details_window, text="Cerrar", command=details_window.destroy)
        close_button.grid(row=3, column=0, pady=(10, 10))

        # Enfocar la nueva ventana
        details_window.focus_set()

    # --- FIN de la función _ver_detalles_contenedor ---
    def _editar_contenedor(self):
        selected_iid = self.tree_ver_contenedores.selection()
        if not selected_iid:
            messagebox.showinfo("Editar Contenedor", "Seleccione un contenedor de la lista para editar.")
            return
        numero_factura_sel = selected_iid[0]
        print(f"TODO: Implementar Editar para factura: {numero_factura_sel}")
        messagebox.showinfo("Editar Contenedor", f"Aquí se abriría el formulario de edición para:\nFactura: {numero_factura_sel}\n(Funcionalidad pendiente)")

    def _eliminar_contenedor(self):
        selected_iid = self.tree_ver_contenedores.selection()
        if not selected_iid:
            messagebox.showinfo("Eliminar Contenedor", "Seleccione un contenedor de la lista para eliminar.")
            return
        numero_factura_sel = selected_iid[0]
        print(f"TODO: Implementar Eliminar para factura: {numero_factura_sel}")
        if messagebox.askyesno("Confirmar Eliminación", f"¿Seguro que quieres eliminar el contenedor con factura '{numero_factura_sel}'?\nEsta acción NO se puede deshacer y eliminará el registro del JSON."):
            print(f"TODO: LLAMAR A FUNCIÓN BACKEND PARA BORRAR FACTURA {numero_factura_sel} del JSON correspondiente")
            # Después de borrar en backend: self._cargar_y_mostrar_contenedores() # Refrescar lista
            messagebox.showinfo("Eliminar Contenedor", f"Contenedor '{numero_factura_sel}' supuestamente eliminado.\n(Funcionalidad real pendiente)")
        else:
            print("Eliminación cancelada.")


    # ===================================================================
    # ### FIN FUNCIONALIDAD VER/GESTIONAR CONTENEDORES ###
    # ===================================================================

# ===================================================================
    # ===================================================================
    # ### INICIO FUNCIONALIDAD AÑADIR GOMA NACIONAL ###
    # ===================================================================
    # ===================================================================

    def _mostrar_form_add_nacional_goma(self):
        """Limpia el área principal y construye el formulario de Goma Nacional."""
        self._limpiar_main_content()
        # Inicializar listas temporales específicas para este formulario
        self.gastos_temp_nac_goma = []
        self.items_temp_nac_goma = [] # Usaremos 'items' como nombre genérico
        # Llamar a la función que construye los widgets visuales
        self._crear_widgets_formulario_nacional_goma(self.main_content_frame)
        print("Mostrando formulario para añadir Pedido Goma Nacional.")

    def _crear_widgets_formulario_nacional_goma(self, parent_frame):
        """Crea y posiciona los widgets para el formulario de Añadir Goma Nacional."""
        form_frame = ttk.Frame(parent_frame, padding="10")
        form_frame.pack(expand=True, fill="both")
        form_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(form_frame, text="Añadir Nuevo Pedido Nacional de Goma", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=4, pady=(0, 15), sticky="w")

        # --- Sub-Frame: Datos Generales (Sin cambios funcionales aquí) ---
        frame_datos_gen = ttk.LabelFrame(form_frame, text="Datos Generales", padding="10")
        frame_datos_gen.grid(row=1, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        frame_datos_gen.grid_columnconfigure(1, weight=1); frame_datos_gen.grid_columnconfigure(3, weight=1)
        labels_contenedor = ["Fecha Pedido (DD-MM-YYYY):", "Fecha Llegada (DD-MM-YYYY):", "Proveedor:",
                            "Número Factura:", "Observaciones:"]
        self.entries_nac_goma = {}
        key_map = ["fecha_pedido", "fecha_llegada", "proveedor", "numero_factura", "observaciones"]
        for i, text in enumerate(labels_contenedor):
            is_last = (i == len(labels_contenedor) - 1); row, col = divmod(i, 2)
            lbl = ttk.Label(frame_datos_gen, text=text); lbl.grid(row=row, column=col*2, sticky="w", padx=5, pady=3)
            entry_widget = None; current_key = key_map[i]
            if current_key in ["fecha_pedido", "fecha_llegada"]:
                entry_widget = DateEntry(frame_datos_gen, width=18, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd-mm-yyyy', locale='es_ES')
            else:
                entry_widget = ttk.Entry(frame_datos_gen, width=30)
            colspan_entry = 3 if (col == 0 and is_last) else 1
            entry_widget.grid(row=row, column=col*2 + 1, columnspan=colspan_entry, sticky="ew", padx=5, pady=3)
            self.entries_nac_goma[current_key] = entry_widget

        # --- Sub-Frame: Gastos (Sin cambios funcionales aquí) ---
        frame_gastos = ttk.LabelFrame(form_frame, text="Gastos Asociados (Transporte, etc.)", padding="10")
        frame_gastos.grid(row=2, column=0, columnspan=4, sticky="ew", padx=5, pady=10)
        frame_gastos.grid_columnconfigure(0, weight=1)
        ttk.Label(frame_gastos, text="Descripción:").grid(row=0, column=0, padx=5, pady=3, sticky="w")
        self.entry_gasto_desc_nac_goma = ttk.Entry(frame_gastos)
        self.entry_gasto_desc_nac_goma.grid(row=1, column=0, padx=5, pady=3, sticky="ew")
        ttk.Label(frame_gastos, text="Coste (€):").grid(row=0, column=1, padx=5, pady=3, sticky="w")
        self.entry_gasto_coste_nac_goma = ttk.Entry(frame_gastos, width=10)
        self.entry_gasto_coste_nac_goma.grid(row=1, column=1, padx=5, pady=3, sticky="w")
        ttk.Button(frame_gastos, text="Añadir Gasto", command=self._add_gasto_nac_goma_temp).grid(row=1, column=2, padx=5, pady=5, sticky="w")
        cols_gastos = ("Descripción", "Coste")
        self.tree_gastos_nac_goma = ttk.Treeview(frame_gastos, columns=cols_gastos, show="headings", height=3, selectmode="browse")
        self.tree_gastos_nac_goma.heading("Descripción", text="Descripción"); self.tree_gastos_nac_goma.column("Descripción", width=350, anchor=tk.W)
        self.tree_gastos_nac_goma.heading("Coste", text="Coste (€)"); self.tree_gastos_nac_goma.column("Coste", width=100, anchor=tk.E)
        self.tree_gastos_nac_goma.grid(row=2, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        ttk.Button(frame_gastos, text="Eliminar Gasto Sel.", command=self._del_gasto_nac_goma_temp).grid(row=3, column=0, columnspan=3, pady=(0, 5))

        # --- Sub-Frame: Bobinas Goma Nacional (MODIFICADO AQUI) ---
        frame_items = ttk.LabelFrame(form_frame, text="Bobinas de Goma (Pedido Nacional)", padding="10")
        frame_items.grid(row=3, column=0, columnspan=4, sticky="ew", padx=5, pady=10)

        ## CAMBIO ## Añadir 'Subtipo:' a etiquetas y 'subtipo' a claves
        labels_items = ["Espesor:", "Ancho(mm):", "Largo(m):",
                        "Nº Bobinas:", "Precio/m (€):", "Subtipo:"] # <-- Añadido
        self.entries_item_nac_goma = {}
        key_map_items = ["espesor", "ancho", "largo", "n_bobinas", "metro_lineal_eur", "subtipo"] # <-- Añadido

        i_row = 0
        for i, text in enumerate(labels_items):
            lbl = ttk.Label(frame_items, text=text)
            col_lbl = (i % 3) * 2
            col_entry = col_lbl + 1
            row_entry = i_row + (i // 3) * 2
            lbl.grid(row=row_entry, column=col_lbl, padx=5, pady=3, sticky="w")
            ## CAMBIO ## Crear Entry para subtipo
            entry = ttk.Entry(frame_items, width=15) # Ancho ajustado
            entry.grid(row=row_entry, column=col_entry, padx=5, pady=3, sticky="ew")
            self.entries_item_nac_goma[key_map_items[i]] = entry

        # Botón añadir
        ttk.Button(frame_items, text="Añadir Bobina", command=self._add_bobina_nac_goma_temp).grid(
            row=row_entry + 1, column=4, columnspan=2, padx=5, pady=5, sticky="e" # Ajustar grid si es necesario
        )

        ## CAMBIO ## Añadir 'Subtipo' a columnas Treeview
        cols_items = ("Espesor", "Ancho", "Largo", "Nº", "EUR/m", "Subtipo") # <-- Añadido
        self.tree_items_nac_goma = ttk.Treeview(frame_items, columns=cols_items, show="headings", height=4, selectmode="browse")

        ## CAMBIO ## Configurar columnas incluyendo 'Subtipo'
        for col in cols_items:
            self.tree_items_nac_goma.heading(col, text=col)
            width = 70; anchor = tk.CENTER
            if col == "Subtipo": width = 90; anchor = tk.W
            elif col == "EUR/m": anchor = tk.E
            elif col == "Nº": width = 40
            elif col == "Ancho" or col == "Largo": anchor = tk.E; width = 60
            elif col == "Espesor": width = 110; anchor = tk.W
            self.tree_items_nac_goma.column(col, width=width, anchor=anchor, stretch=(col=="Subtipo"))

        # Posicionar Treeview
        tree_row_nac = i_row + (len(labels_items)//3)*2 + 1
        self.tree_items_nac_goma.grid(row=tree_row_nac, column=0, columnspan=6, sticky="nsew", padx=5, pady=5)
        # TODO: Scrollbar para Treeview items nac goma

        # Botón eliminar bobina
        ttk.Button(frame_items, text="Eliminar Bobina Sel.", command=self._del_bobina_nac_goma_temp).grid(
            row=tree_row_nac + 1, column=0, columnspan=6, pady=(0, 5)
        )

        # --- Botón Guardar Final y Status Label ---
        ttk.Button(form_frame, text="GUARDAR PEDIDO GOMA NACIONAL", command=self._guardar_pedido_nacional_goma, style="Accent.TButton").grid(row=4, column=0, columnspan=4, pady=20, ipady=5)
        self.status_label_form_nac_goma = ttk.Label(form_frame, text="Formulario listo.", foreground="blue")
        self.status_label_form_nac_goma.grid(row=5, column=0, columnspan=4, pady=5)

    # --- Funciones auxiliares para Goma Nacional ---

    def _add_gasto_nac_goma_temp(self):
        """Añade gasto a lista temporal y TreeView Goma Nacional (sin tipo)."""
        descripcion = self.entry_gasto_desc_nac_goma.get().strip()
        coste_str = self.entry_gasto_coste_nac_goma.get().strip().replace(',', '.')
        try:
            coste = float(coste_str)
            if not descripcion or coste < 0: raise ValueError("Descripción (no vacía) y coste (>=0) requeridos.")
        except ValueError as e: messagebox.showerror("Error Gasto", f"Datos inválidos: {e}"); return

        # El backend nacional podría esperar un dict con 'descripcion' y 'coste'
        gasto_data = {"descripcion": descripcion, "coste": coste}
        if not hasattr(self, 'gastos_temp_nac_goma'): self.gastos_temp_nac_goma = []
        self.gastos_temp_nac_goma.append(gasto_data)
        self.tree_gastos_nac_goma.insert("", tk.END, values=(descripcion, f"{coste:.2f}")) # Solo 2 valores
        self.entry_gasto_desc_nac_goma.delete(0, tk.END); self.entry_gasto_coste_nac_goma.delete(0, tk.END)
        if hasattr(self, 'status_label_form_nac_goma'): self.status_label_form_nac_goma.config(text=f"Gasto '{descripcion}' añadido.")

    def _del_gasto_nac_goma_temp(self):
        """Elimina gasto de lista temporal y TreeView Goma Nacional."""
        selected_iid = self.tree_gastos_nac_goma.selection()
        if not selected_iid: messagebox.showwarning("Eliminar Gasto", "Seleccione un gasto."); return
        item_index = self.tree_gastos_nac_goma.index(selected_iid[0])
        item_values = self.tree_gastos_nac_goma.item(selected_iid[0], 'values')
        try:
            if not hasattr(self, 'gastos_temp_nac_goma'): raise AttributeError("Lista gastos temp no existe")
            del self.gastos_temp_nac_goma[item_index]; self.tree_gastos_nac_goma.delete(selected_iid[0])
            if hasattr(self, 'status_label_form_nac_goma'): self.status_label_form_nac_goma.config(text=f"Gasto '{item_values[0]}' eliminado.") # Índice 0 ahora es descripción
        except (IndexError, AttributeError) as e: messagebox.showerror("Error", f"No se pudo eliminar el gasto: {e}")

    def _add_bobina_nac_goma_temp(self):
        """Añade bobina a lista temporal y TreeView Goma Nacional (precio EUR, con subtipo)."""
        item_params = {}
        try:
            for key, widget in self.entries_item_nac_goma.items():
                value_str = widget.get().strip()
                if not value_str and key not in ["subtipo"]:
                    raise ValueError(f"El campo '{key}' no puede estar vacío.")

                if key in ["ancho", "largo", "metro_lineal_eur"]:
                    value = float(value_str.replace(',', '.'))
                    if value < 0 or (key != "metro_lineal_eur" and value == 0):
                        raise ValueError(f"Valor inválido para '{key}'.")
                elif key == "n_bobinas":
                    value = int(value_str)
                    if value <= 0: raise ValueError("Nº Bobinas debe ser > 0.")
                ## CAMBIO ## Leer subtipo, default 'NORMAL'
                elif key == "subtipo":
                    value = value_str.upper() if value_str else "NORMAL"
                else: # Espesor
                    value = value_str
                item_params[key] = value

        except KeyError as e: messagebox.showerror("Error Bobina Nac.", f"Error interno: Clave no encontrada {e}"); return
        except ValueError as e: messagebox.showerror("Error Bobina Nac.", f"Datos de bobina inválidos: {e}"); return
        except Exception as e: messagebox.showerror("Error Bobina Nac.", f"Error inesperado: {e}"); return

        if not hasattr(self, 'items_temp_nac_goma'): self.items_temp_nac_goma = []
        self.items_temp_nac_goma.append(item_params)

        ## CAMBIO ## Incluir subtipo en valores Treeview
        valores_tree = (
            item_params["espesor"],
            f"{item_params['ancho']:.1f}",
            f"{item_params['largo']:.1f}",
            item_params["n_bobinas"],
            f"{item_params['metro_lineal_eur']:.2f}", # EUR
            item_params["subtipo"] # <-- Subtipo
        )
        self.tree_items_nac_goma.insert("", tk.END, values=valores_tree)

        for key, entry_widget in self.entries_item_nac_goma.items():
            entry_widget.delete(0, tk.END) # Limpiar todos, incluido subtipo

        status_label = getattr(self, 'status_label_form_nac_goma', None)
        if status_label and status_label.winfo_exists():
            status_label.config(text=f"Bobina Goma Nac. {item_params['subtipo']} ({item_params['espesor']}) añadida.")


    def _del_bobina_nac_goma_temp(self):
        """Elimina la bobina seleccionada de la lista temporal y TreeView de Goma Nacional."""
        # Asegurarse que los widgets existen
        if not hasattr(self, 'tree_items_nac_goma') or not self.tree_items_nac_goma.winfo_exists():
            messagebox.showerror("Error", "El TreeView de bobinas nacionales de goma no está disponible.")
            return
        if not hasattr(self, 'items_temp_nac_goma'):
            # Si la lista no existe, no hay nada que borrar
            messagebox.showwarning("Eliminar Bobina", "No hay bobinas en la lista temporal para eliminar.")
            return

        selected_iid = self.tree_items_nac_goma.selection()
        if not selected_iid:
            messagebox.showwarning("Eliminar Bobina", "Seleccione una bobina de la lista para eliminar.")
            return

        # Obtener el índice real en el TreeView (para sincronizar con la lista)
        item_index = self.tree_items_nac_goma.index(selected_iid[0])
        item_values = self.tree_items_nac_goma.item(selected_iid[0], 'values') # Para el mensaje

        try:
            # Eliminar de la lista temporal usando el índice
            del self.items_temp_nac_goma[item_index]
            # Eliminar del TreeView usando su ID interno
            self.tree_items_nac_goma.delete(selected_iid[0])

            # Actualizar mensaje de estado
            status_label = getattr(self, 'status_label_form_nac_goma', None)
            if status_label and status_label.winfo_exists():
                # Usar el espesor (índice 0) y subtipo (índice 5) si están disponibles en item_values
                desc_item = item_values[0] if len(item_values) > 0 else 'seleccionada'
                subtipo_item = item_values[5] if len(item_values) > 5 else ''
                status_label.config(text=f"Bobina Goma Nac. {subtipo_item} ({desc_item}) eliminada.")

        except IndexError:
            # Este error podría ocurrir si el índice no coincide con la lista (raro)
            messagebox.showerror("Error", "No se pudo encontrar la bobina para eliminar (Error de índice).")
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado al eliminar la bobina: {e}")


    def _guardar_pedido_nacional_goma(self):
        """Recoge datos Goma Nac, crea obj, calcula, guarda JSON y registra en DB."""
        status_label = getattr(self, 'status_label_form_nac_goma', None)
        if status_label and status_label.winfo_exists(): status_label.config(text="Procesando...", foreground="blue")

        datos_a_guardar = {}
        try: # Validar datos generales
            # ... (Código de validación general igual que antes) ...
            from datetime import datetime
            datos_generales_widgets = self.entries_nac_goma
            for key, widget in datos_generales_widgets.items():
                if key in ["fecha_pedido", "fecha_llegada"]:
                    fecha_dt = widget.get_date(); datos_a_guardar[key] = fecha_dt.strftime('%Y-%m-%d')
                else: datos_a_guardar[key] = widget.get().strip()
            if not datos_a_guardar.get("proveedor") or not datos_a_guardar.get("numero_factura"):
                raise ValueError("Proveedor y Número Factura son obligatorios.")
        except ValueError as e:
            messagebox.showerror("Error Datos Generales", f"Datos inválidos: {e}")
            if status_label and status_label.winfo_exists(): status_label.config(text="Error en datos generales.", foreground="red")
            return
        except Exception as e:
            messagebox.showerror("Error Datos Generales", f"Error inesperado: {e}")
            if status_label and status_label.winfo_exists(): status_label.config(text="Error interno.", foreground="red")
            return

        if not hasattr(self, 'items_temp_nac_goma') or not self.items_temp_nac_goma:
            messagebox.showerror("Error Contenido", "Debe añadir al menos una bobina.")
            if status_label and status_label.winfo_exists(): status_label.config(text="Error: Faltan bobinas.", foreground="red")
            return

        pedido = None
        try: # Crear objeto MercanciaNacionalGoma
            from nacional.mercanciaNacionalGoma import MercanciaNacionalGoma
            pedido = MercanciaNacionalGoma(**datos_a_guardar)
        except ImportError:
            messagebox.showerror("Error Importación", "No se encontró la clase 'MercanciaNacionalGoma'.")
            if status_label and status_label.winfo_exists(): status_label.config(text="Error interno (backend).", foreground="red")
            return
        except Exception as e:
            messagebox.showerror("Error Creación", f"No se pudo crear el objeto MercanciaNacionalGoma: {e}")
            if status_label and status_label.winfo_exists(): status_label.config(text="Error interno (creación).", foreground="red")
            return

        # --- Lógica Backend ---
        json_guardado = False
        try:
            # Añadir gastos (sin cambios)
            if hasattr(self, 'gastos_temp_nac_goma'):
                for gasto_data in self.gastos_temp_nac_goma:
                    if hasattr(pedido, 'agregar_gasto'):
                        pedido.agregar_gasto(gasto_data["descripcion"], gasto_data["coste"])

            # Añadir bobinas
            if hasattr(self, 'items_temp_nac_goma'):
                add_item_method = getattr(pedido, 'agregar_bobina', None)
                if not add_item_method: raise AttributeError("Método 'agregar_bobina' no encontrado.")
                for item_data in self.items_temp_nac_goma:
                    ## CAMBIO ## Al usar **item_data, el subtipo se pasa si existe
                    ## El método backend agregar_bobina ya fue modificado
                    add_item_method(**item_data)

            # Calcular precios finales (sin cambios)
            if hasattr(pedido, 'calcular_precios_finales'): pedido.calcular_precios_finales()

            # Guardar en JSON (sin cambios, __dict__ incluye subtipo)
            try:
                guardar_o_actualizar_mercancias_goma([pedido])
                json_guardado = True
                print(f"Pedido Goma Nacional {pedido.numero_factura} guardado/actualizado en JSON.")
            except ImportError: messagebox.showerror("Error Guardado", "Función 'guardar_o_actualizar_mercancias_goma' no encontrada."); raise

        except Exception as e:
            messagebox.showerror("Error Procesamiento", f"Error procesando Pedido Goma Nac: {e}")
            if status_label and status_label.winfo_exists(): status_label.config(text="Error procesando datos.", foreground="red")
            return

        # Registrar en Almacén DB
        db_registrado = False
        if json_guardado:
            try:
                # Asumimos que registrar_entrada_almacen está adaptado para subtipo
                registrar_entrada_almacen(pedido)
                db_registrado = True
                print(f"Pedido Goma Nacional {pedido.numero_factura} registrado en almacén DB.")
            except Exception as e:
                messagebox.showwarning("Error Registro Almacén", f"JSON guardado, pero falló registro DB: {e}")

        # Feedback final y limpiar (sin cambios)
        if status_label and status_label.winfo_exists():
            if json_guardado and db_registrado:
                messagebox.showinfo("Éxito", f"Pedido Goma Nacional '{pedido.numero_factura}' guardado y registrado.")
                self._limpiar_form_nac_goma()
                status_label.config(text=f"Pedido '{pedido.numero_factura}' procesado.", foreground="green")
            elif json_guardado:
                status_label.config(text=f"Pedido '{pedido.numero_factura}' guardado JSON, falló registro DB.", foreground="orange")
            else:
                status_label.config(text="Error al guardar Pedido Goma Nac. en JSON.", foreground="red")

    # ===================================================================
    # ### FIN FUNCIONALIDAD AÑADIR GOMA NACIONAL ###
    # ===================================================================

    # ===================================================================
    # ===================================================================
    # ### INICIO FUNCIONALIDAD AÑADIR PVC NACIONAL ###
    # ===================================================================
    # ===================================================================

    def _mostrar_form_add_nacional_pvc(self):
        """Limpia el área principal y construye el formulario de PVC Nacional."""
        self._limpiar_main_content()
        # Inicializar listas temporales específicas
        self.gastos_temp_nac_pvc = []
        self.items_temp_nac_pvc = []
        # Llamar a la función que construye los widgets
        self._crear_widgets_formulario_nacional_pvc(self.main_content_frame)
        print("Mostrando formulario para añadir Pedido PVC Nacional.")

    def _crear_widgets_formulario_nacional_pvc(self, parent_frame):
        """Crea y posiciona los widgets para el formulario de Añadir PVC Nacional."""
        # --- Frame principal ---
        form_frame = ttk.Frame(parent_frame, padding="10")
        form_frame.pack(expand=True, fill="both")
        form_frame.grid_columnconfigure(1, weight=1)

        # --- Título ---
        ttk.Label(form_frame, text="Añadir Nuevo Pedido Nacional de PVC", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=4, pady=(0, 15), sticky="w")

        # --- Sub-Frame: Datos Generales (Igual que Goma Nac) ---
        frame_datos_gen = ttk.LabelFrame(form_frame, text="Datos Generales", padding="10")
        frame_datos_gen.grid(row=1, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        frame_datos_gen.grid_columnconfigure(1, weight=1); frame_datos_gen.grid_columnconfigure(3, weight=1)

        labels_contenedor = ["Fecha Pedido (DD-MM-YYYY):", "Fecha Llegada (DD-MM-YYYY):", "Proveedor:",
                             "Número Factura:", "Observaciones:"]
        self.entries_nac_pvc = {} # Diccionario específico
        key_map = ["fecha_pedido", "fecha_llegada", "proveedor", "numero_factura", "observaciones"]

        for i, text in enumerate(labels_contenedor):
            is_last = (i == len(labels_contenedor) - 1)
            row, col = divmod(i, 2)
            lbl = ttk.Label(frame_datos_gen, text=text); lbl.grid(row=row, column=col*2, sticky="w", padx=5, pady=3)
            entry_widget = None
            current_key = key_map[i]
            if current_key in ["fecha_pedido", "fecha_llegada"]:
                entry_widget = DateEntry(frame_datos_gen, width=18, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd-mm-yyyy', locale='es_ES')
            else:
                entry_widget = ttk.Entry(frame_datos_gen, width=30)
            colspan_entry = 3 if (col == 0 and is_last) else 1
            entry_widget.grid(row=row, column=col*2 + 1, columnspan=colspan_entry, sticky="ew", padx=5, pady=3)
            self.entries_nac_pvc[current_key] = entry_widget

        # --- Sub-Frame: Gastos (Igual que Goma Nac, usa widgets _nac_pvc) ---
        frame_gastos = ttk.LabelFrame(form_frame, text="Gastos Asociados (Transporte, etc.)", padding="10")
        frame_gastos.grid(row=2, column=0, columnspan=4, sticky="ew", padx=5, pady=10)
        frame_gastos.grid_columnconfigure(0, weight=1)

        ttk.Label(frame_gastos, text="Descripción:").grid(row=0, column=0, padx=5, pady=3, sticky="w")
        self.entry_gasto_desc_nac_pvc = ttk.Entry(frame_gastos)
        self.entry_gasto_desc_nac_pvc.grid(row=1, column=0, padx=5, pady=3, sticky="ew")
        ttk.Label(frame_gastos, text="Coste (€):").grid(row=0, column=1, padx=5, pady=3, sticky="w")
        self.entry_gasto_coste_nac_pvc = ttk.Entry(frame_gastos, width=10)
        self.entry_gasto_coste_nac_pvc.grid(row=1, column=1, padx=5, pady=3, sticky="w")
        ttk.Button(frame_gastos, text="Añadir Gasto", command=self._add_gasto_nac_pvc_temp).grid(row=1, column=2, padx=5, pady=5, sticky="w")

        cols_gastos = ("Descripción", "Coste")
        self.tree_gastos_nac_pvc = ttk.Treeview(frame_gastos, columns=cols_gastos, show="headings", height=3, selectmode="browse")
        self.tree_gastos_nac_pvc.heading("Descripción", text="Descripción"); self.tree_gastos_nac_pvc.column("Descripción", width=350, anchor=tk.W)
        self.tree_gastos_nac_pvc.heading("Coste", text="Coste (€)"); self.tree_gastos_nac_pvc.column("Coste", width=100, anchor=tk.E)
        self.tree_gastos_nac_pvc.grid(row=2, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        # TODO: Scrollbar Tree Gasto Nac PVC
        ttk.Button(frame_gastos, text="Eliminar Gasto Sel.", command=self._del_gasto_nac_pvc_temp).grid(row=3, column=0, columnspan=3, pady=(0, 5))

        # --- Sub-Frame: Bobinas PVC Nacional (Añadir Color) ---
        frame_items = ttk.LabelFrame(form_frame, text="Bobinas de PVC (Pedido Nacional)", padding="10")
        frame_items.grid(row=3, column=0, columnspan=4, sticky="ew", padx=5, pady=10)

        labels_items = ["Espesor:", "Ancho(mm):", "Largo(m):", "Nº Bobinas:", "Precio/m (€):", "Color:"] # <-- Añadido Color
        self.entries_item_nac_pvc = {} # Diccionario específico
        key_map_items = ["espesor", "ancho", "largo", "n_bobinas", "metro_lineal_eur", "color"] # <-- Añadido Color

        i_row = 0
        for i, text in enumerate(labels_items):
            lbl = ttk.Label(frame_items, text=text)
            # Ajustar layout para 3 columnas de Label+Entry
            col_lbl = (i % 3) * 2
            col_entry = col_lbl + 1
            row_entry = i_row + (i // 3) * 2
            lbl.grid(row=row_entry, column=col_lbl, padx=5, pady=3, sticky="w")
            entry = ttk.Entry(frame_items, width=12)
            entry.grid(row=row_entry, column=col_entry, padx=5, pady=3, sticky="ew")
            self.entries_item_nac_pvc[key_map_items[i]] = entry

        ttk.Button(frame_items, text="Añadir Bobina", command=self._add_bobina_nac_pvc_temp).grid(row=i_row + 2, column=4, padx=5, pady=5, sticky="se", rowspan=2) # Ajustar columna botón

        cols_items = ("Espesor", "Ancho", "Largo", "Nº", "EUR/m", "Color") # <-- Añadido Color
        self.tree_items_nac_pvc = ttk.Treeview(frame_items, columns=cols_items, show="headings", height=4, selectmode="browse")
        for col in cols_items: self.tree_items_nac_pvc.heading(col, text=col)
        self.tree_items_nac_pvc.column("Espesor", width=70, anchor=tk.W); self.tree_items_nac_pvc.column("Ancho", width=70, anchor=tk.E)
        self.tree_items_nac_pvc.column("Largo", width=70, anchor=tk.E); self.tree_items_nac_pvc.column("Nº", width=40, anchor=tk.CENTER)
        self.tree_items_nac_pvc.column("EUR/m", width=80, anchor=tk.E); self.tree_items_nac_pvc.column("Color", width=100, anchor=tk.W)
        self.tree_items_nac_pvc.grid(row=i_row + 4, column=0, columnspan=5, sticky="nsew", padx=5, pady=5)
        # TODO: Scrollbar Tree Items Nac PVC

        ttk.Button(frame_items, text="Eliminar Bobina Sel.", command=self._del_bobina_nac_pvc_temp).grid(row=i_row + 5, column=0, columnspan=5, pady=(0, 5))

        # --- Botón Guardar Final ---
        ttk.Button(form_frame, text="GUARDAR PEDIDO PVC NACIONAL", command=self._guardar_pedido_nacional_pvc, style="Accent.TButton").grid(row=4, column=0, columnspan=4, pady=20, ipady=5)

        # --- Label de Estado/Mensajes ---
        self.status_label_form_nac_pvc = ttk.Label(form_frame, text="Formulario listo.", foreground="blue")
        self.status_label_form_nac_pvc.grid(row=5, column=0, columnspan=4, pady=5)

    # --- Funciones auxiliares para PVC Nacional ---

    def _add_gasto_nac_pvc_temp(self):
        """Añade gasto a lista temporal y TreeView PVC Nacional."""
        # Idéntica a Goma Nacional, usando widgets _nac_pvc
        descripcion = self.entry_gasto_desc_nac_pvc.get().strip()
        coste_str = self.entry_gasto_coste_nac_pvc.get().strip().replace(',', '.')
        try:
            coste = float(coste_str)
            if not descripcion or coste < 0: raise ValueError("Descripción y coste (>=0) requeridos.")
        except ValueError as e: messagebox.showerror("Error Gasto", f"Datos inválidos: {e}"); return
        gasto_data = {"descripcion": descripcion, "coste": coste}
        if not hasattr(self, 'gastos_temp_nac_pvc'): self.gastos_temp_nac_pvc = []
        self.gastos_temp_nac_pvc.append(gasto_data)
        self.tree_gastos_nac_pvc.insert("", tk.END, values=(descripcion, f"{coste:.2f}"))
        self.entry_gasto_desc_nac_pvc.delete(0, tk.END); self.entry_gasto_coste_nac_pvc.delete(0, tk.END)
        if hasattr(self, 'status_label_form_nac_pvc'): self.status_label_form_nac_pvc.config(text=f"Gasto '{descripcion}' añadido.")

    def _del_gasto_nac_pvc_temp(self):
        """Elimina gasto de lista temporal y TreeView PVC Nacional."""
        # Idéntica a Goma Nacional, usando widgets _nac_pvc
        selected_iid = self.tree_gastos_nac_pvc.selection()
        if not selected_iid: messagebox.showwarning("Eliminar Gasto", "Seleccione un gasto."); return
        item_index = self.tree_gastos_nac_pvc.index(selected_iid[0])
        item_values = self.tree_gastos_nac_pvc.item(selected_iid[0], 'values')
        try:
            if not hasattr(self, 'gastos_temp_nac_pvc'): raise AttributeError("Lista gastos temp no existe")
            del self.gastos_temp_nac_pvc[item_index]; self.tree_gastos_nac_pvc.delete(selected_iid[0])
            if hasattr(self, 'status_label_form_nac_pvc'): self.status_label_form_nac_pvc.config(text=f"Gasto '{item_values[0]}' eliminado.")
        except (IndexError, AttributeError) as e: messagebox.showerror("Error", f"No se pudo eliminar el gasto: {e}")

    def _add_bobina_nac_pvc_temp(self):
        """Añade bobina a lista temporal y TreeView PVC Nacional (con color)."""
        try:
            espesor = self.entries_item_nac_pvc["espesor"].get().strip() # String
            ancho_str = self.entries_item_nac_pvc["ancho"].get().strip().replace(',', '.')
            largo_str = self.entries_item_nac_pvc["largo"].get().strip().replace(',', '.')
            n_bobinas_str = self.entries_item_nac_pvc["n_bobinas"].get().strip()
            metro_lineal_eur_str = self.entries_item_nac_pvc["metro_lineal_eur"].get().strip().replace(',', '.')
            color = self.entries_item_nac_pvc["color"].get().strip() # Leer Color

            if not espesor: raise ValueError("Espesor no puede estar vacío.")
            if not color: raise ValueError("Color no puede estar vacío.") # Validar Color
            if not ancho_str or not largo_str or not n_bobinas_str or not metro_lineal_eur_str:
                raise ValueError("Ancho, Largo, Nº Bobinas y Precio/m EUR no pueden estar vacíos.")

            ancho = float(ancho_str)
            largo = float(largo_str)
            n_bobinas = int(n_bobinas_str)
            metro_lineal_eur = float(metro_lineal_eur_str)

            if not all(v > 0 for v in [ancho, largo, n_bobinas]) or metro_lineal_eur < 0:
                 raise ValueError("Valores Ancho, Largo, Nº Bobinas deben ser > 0 (precio >= 0).")

        except KeyError as e: messagebox.showerror("Error Bobina", f"Error interno: Clave no encontrada {e}"); return
        except ValueError as e: messagebox.showerror("Error Bobina", f"Datos de bobina inválidos: {e}"); return
        except Exception as e: messagebox.showerror("Error Bobina", f"Error inesperado: {e}"); return

        item_params = {
            "espesor": espesor, "ancho": ancho, "largo": largo,
            "n_bobinas": n_bobinas, "metro_lineal_eur": metro_lineal_eur,
            "color": color # Añadir color al diccionario
        }
        if not hasattr(self, 'items_temp_nac_pvc'): self.items_temp_nac_pvc = []
        self.items_temp_nac_pvc.append(item_params)
        self.tree_items_nac_pvc.insert("", tk.END, values=(espesor, ancho, largo, n_bobinas, f"{metro_lineal_eur:.2f}", color)) # Añadir color al treeview

        for entry_widget in self.entries_item_nac_pvc.values(): entry_widget.delete(0, tk.END)
        if hasattr(self, 'status_label_form_nac_pvc'): self.status_label_form_nac_pvc.config(text=f"Bobina '{espesor}' {color} añadida.")

    def _del_bobina_nac_pvc_temp(self):
        """Elimina bobina de lista temporal y TreeView PVC Nacional."""
        selected_iid = self.tree_items_nac_pvc.selection()
        if not selected_iid: messagebox.showwarning("Eliminar Bobina", "Seleccione una bobina."); return
        item_index = self.tree_items_nac_pvc.index(selected_iid[0])
        item_values = self.tree_items_nac_pvc.item(selected_iid[0], 'values')
        try:
            if not hasattr(self, 'items_temp_nac_pvc'): raise AttributeError("Lista items temp no existe")
            del self.items_temp_nac_pvc[item_index]; self.tree_items_nac_pvc.delete(selected_iid[0])
            if hasattr(self, 'status_label_form_nac_pvc'): self.status_label_form_nac_pvc.config(text=f"Bobina '{item_values[0]}' {item_values[5]} eliminada.") # Usa índice 5 para color
        except (IndexError, AttributeError) as e: messagebox.showerror("Error", f"No se pudo eliminar la bobina: {e}")

    # --- Función Principal de Guardado para PVC Nacional ---

    # Dentro de la clase Interfaz en interfaz.py
    # (Asegúrate de tener imports: tk, ttk, messagebox, datetime,
    # MercanciaNacionalPVC, guardar_o_actualizar_mercancias_pvc, registrar_entrada_almacen)

    def _guardar_pedido_nacional_pvc(self):
        """Recoge datos PVC Nac, crea obj, calcula, guarda JSON y registra en DB."""
        # Verificar y configurar label de estado
        status_label = getattr(self, 'status_label_form_nac_pvc', None)
        if status_label and status_label.winfo_exists():
            status_label.config(text="Procesando...", foreground="blue")
        else:
            print("Advertencia: status_label_form_nac_pvc no encontrado.")

        datos_a_guardar = {}
        # No hay valor_conversion para Nacional

        try: # Validar y procesar datos generales
            # Importar datetime si no está ya importado globalmente
            from datetime import datetime

            datos_generales_widgets = self.entries_nac_pvc # Usar el diccionario correcto
            for key, widget in datos_generales_widgets.items():
                if key in ["fecha_pedido", "fecha_llegada"]:
                    try:
                        fecha_dt = widget.get_date() # Leer de DateEntry
                        datos_a_guardar[key] = fecha_dt.strftime('%Y-%m-%d') # Guardar como YYYY-MM-DD
                    except Exception as e_date:
                        raise ValueError(f"Error al obtener la fecha del campo '{key}': {e_date}")
                # No hay valor_conversion
                else:
                    # Leer otros campos como string
                    datos_a_guardar[key] = widget.get().strip()

            # Validaciones básicas
            if not datos_a_guardar.get("proveedor") or not datos_a_guardar.get("numero_factura"):
                 raise ValueError("Proveedor y Número Factura son obligatorios.")
            if not datos_a_guardar["numero_factura"]:
                 raise ValueError("Número Factura no puede estar vacío.")

        except ValueError as e:
            messagebox.showerror("Error Datos Generales", f"Datos inválidos: {e}")
            if status_label and status_label.winfo_exists(): status_label.config(text="Error en datos generales.", foreground="red")
            return
        except Exception as e:
             messagebox.showerror("Error Datos Generales", f"Error inesperado recogiendo datos: {e}")
             if status_label and status_label.winfo_exists(): status_label.config(text="Error interno formulario.", foreground="red")
             return

        # Validar que haya bobinas añadidas
        if not hasattr(self, 'items_temp_nac_pvc') or not self.items_temp_nac_pvc:
            messagebox.showerror("Error Contenido", "Debe añadir al menos una bobina.")
            if status_label and status_label.winfo_exists(): status_label.config(text="Error: Faltan bobinas.", foreground="red")
            return

        # Crear instancia MercanciaNacionalPVC
        pedido = None
        try:
            # Importar clase backend PVC Nacional
            from nacional.mercanciaNacionalPVC import MercanciaNacionalPVC
            # Pasar solo los datos generales al constructor
            pedido = MercanciaNacionalPVC(**datos_a_guardar)
        except ImportError:
             messagebox.showerror("Error Importación", "No se encontró la clase 'MercanciaNacionalPVC'.")
             if status_label and status_label.winfo_exists(): status_label.config(text="Error interno (backend).", foreground="red")
             return
        except Exception as e:
            messagebox.showerror("Error Creación", f"No se pudo crear el objeto MercanciaNacionalPVC: {e}")
            if status_label and status_label.winfo_exists(): status_label.config(text="Error interno (creación).", foreground="red")
            return

        # --- Lógica Backend: Añadir gastos/items, calcular, guardar, registrar ---
        json_guardado = False
        try:
            # 1. Añadir gastos
            if hasattr(self, 'gastos_temp_nac_pvc'):
                for gasto_data in self.gastos_temp_nac_pvc:
                    pedido.agregar_gasto(gasto_data["descripcion"], gasto_data["coste"])

            # 2. Añadir bobinas (items)
            if hasattr(self, 'items_temp_nac_pvc'):
                 # Usar el método específico de la subclase MercanciaNacionalPVC
                 add_item_method = getattr(pedido, 'agregar_bobina_pvc', None) # Usa el nombre correcto
                 if not add_item_method: raise AttributeError("Método 'agregar_bobina_pvc' no encontrado.")
                 for item_data in self.items_temp_nac_pvc:
                     add_item_method(**item_data) # Pasa el dict (incluye color y metro_lineal_eur)

            # 3. Calcular precios finales
            pedido.calcular_precios_finales()

            # 4. Guardar en JSON Nacional
            # --- LLAMADA CORRECTA Y ÚNICA AL GUARDADO JSON ---
            try:
                 # Importar función de guardado NACIONAL PVC
                 from nacional.mercanciaNacionalPVC import guardar_o_actualizar_mercancias_pvc # Func específica Nac PVC
                 guardar_o_actualizar_mercancias_pvc([pedido]) # Solo esta llamada
                 json_guardado = True
                 print(f"Pedido PVC Nacional {pedido.numero_factura} guardado/actualizado en JSON.")
            except ImportError:
                 messagebox.showerror("Error Guardado", "Función 'guardar_o_actualizar_mercancias_pvc' no encontrada.")
                 raise
            # --- FIN LLAMADA CORRECTA ---

        except Exception as e:
            messagebox.showerror("Error Procesamiento", f"Error procesando datos Pedido PVC Nac: {e}")
            if status_label and status_label.winfo_exists(): status_label.config(text="Error procesando datos.", foreground="red")
            return

        # 5. Registrar en Almacén DB
        db_registrado = False
        if json_guardado: # Solo registrar si el JSON se guardó bien
            try:
                registrar_entrada_almacen(pedido)
                db_registrado = True
                # El mensaje ya se imprime en registrar_entrada_almacen
            except Exception as e:
                messagebox.showwarning("Error Registro Almacén", f"JSON guardado, pero falló el registro en Almacén DB: {e}")

        # 6. Feedback final y limpiar
        if status_label and status_label.winfo_exists():
            if json_guardado and db_registrado:
                messagebox.showinfo("Éxito", f"Pedido PVC Nacional '{pedido.numero_factura}' guardado y registrado.")
                self._limpiar_form_nac_pvc() # Llamar a la función de limpieza específica
                status_label.config(text=f"Pedido '{pedido.numero_factura}' procesado.", foreground="green")
            elif json_guardado:
                status_label.config(text=f"Pedido '{pedido.numero_factura}' guardado JSON, falló registro DB.", foreground="orange")
            # Si json_guardado es False, el error ya se mostró antes

    def _limpiar_form_nac_pvc(self):
        """Limpia todos los campos de entrada y listas del formulario PVC Nacional."""
        try:
            if hasattr(self, 'entries_nac_pvc'):
                 for key, widget in self.entries_nac_pvc.items():
                     if isinstance(widget, ttk.Entry): widget.delete(0, tk.END)
            if hasattr(self, 'entry_gasto_desc_nac_pvc'): self.entry_gasto_desc_nac_pvc.delete(0, tk.END)
            if hasattr(self, 'entry_gasto_coste_nac_pvc'): self.entry_gasto_coste_nac_pvc.delete(0, tk.END)
            if hasattr(self, 'entries_item_nac_pvc'):
                 for entry_widget in self.entries_item_nac_pvc.values(): entry_widget.delete(0, tk.END)
            if hasattr(self, 'tree_gastos_nac_pvc'):
                 for iid in self.tree_gastos_nac_pvc.get_children(): self.tree_gastos_nac_pvc.delete(iid)
            if hasattr(self, 'tree_items_nac_pvc'):
                 for iid in self.tree_items_nac_pvc.get_children(): self.tree_items_nac_pvc.delete(iid)
            if hasattr(self, 'gastos_temp_nac_pvc'): self.gastos_temp_nac_pvc.clear()
            if hasattr(self, 'items_temp_nac_pvc'): self.items_temp_nac_pvc.clear()
            if hasattr(self, 'status_label_form_nac_pvc') and self.status_label_form_nac_pvc:
                self.status_label_form_nac_pvc.config(text="Formulario limpio.", foreground="black")
            print("Formulario PVC Nacional limpiado.")
        except Exception as e: print(f"Error limpiando formulario PVC Nacional: {e}")


    # ===================================================================
    # ### FIN FUNCIONALIDAD AÑADIR PVC NACIONAL ###
    # ===================================================================


    # ===================================================================
    # ===================================================================
    # ### INICIO FUNCIONALIDAD AÑADIR FIELTRO NACIONAL ###
    # ===================================================================
    # ===================================================================

    def _mostrar_form_add_nacional_fieltro(self):
        """Limpia el área principal y construye el formulario de Fieltro Nacional."""
        self._limpiar_main_content()
        # Inicializar listas temporales específicas
        self.gastos_temp_nac_fieltro = []
        self.items_temp_nac_fieltro = [] # Rollos/Items
        # Llamar a la función que construye los widgets
        self._crear_widgets_formulario_nacional_fieltro(self.main_content_frame)
        print("Mostrando formulario para añadir Pedido Fieltro Nacional.")

    def _crear_widgets_formulario_nacional_fieltro(self, parent_frame):
        """Crea y posiciona los widgets para el formulario de Añadir Fieltro Nacional."""
        # --- Frame principal ---
        form_frame = ttk.Frame(parent_frame, padding="10")
        form_frame.pack(expand=True, fill="both")
        form_frame.grid_columnconfigure(1, weight=1)

        # --- Título ---
        ttk.Label(form_frame, text="Añadir Nuevo Pedido Nacional de Fieltro", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=4, pady=(0, 15), sticky="w")

        # --- Sub-Frame: Datos Generales (Igual que Goma/PVC Nac) ---
        frame_datos_gen = ttk.LabelFrame(form_frame, text="Datos Generales", padding="10")
        frame_datos_gen.grid(row=1, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        frame_datos_gen.grid_columnconfigure(1, weight=1); frame_datos_gen.grid_columnconfigure(3, weight=1)

        labels_contenedor = ["Fecha Pedido (DD-MM-YYYY):", "Fecha Llegada (DD-MM-YYYY):", "Proveedor:",
                             "Número Factura:", "Observaciones:"]
        self.entries_nac_fieltro = {} # Diccionario específico
        key_map = ["fecha_pedido", "fecha_llegada", "proveedor", "numero_factura", "observaciones"]

        for i, text in enumerate(labels_contenedor):
            is_last = (i == len(labels_contenedor) - 1)
            row, col = divmod(i, 2)
            lbl = ttk.Label(frame_datos_gen, text=text); lbl.grid(row=row, column=col*2, sticky="w", padx=5, pady=3)
            entry_widget = None
            current_key = key_map[i]
            if current_key in ["fecha_pedido", "fecha_llegada"]:
                entry_widget = DateEntry(frame_datos_gen, width=18, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd-mm-yyyy', locale='es_ES')
            else:
                entry_widget = ttk.Entry(frame_datos_gen, width=30)
            colspan_entry = 3 if (col == 0 and is_last) else 1
            entry_widget.grid(row=row, column=col*2 + 1, columnspan=colspan_entry, sticky="ew", padx=5, pady=3)
            self.entries_nac_fieltro[current_key] = entry_widget

        # --- Sub-Frame: Gastos (Igual que Goma Nac, usa widgets _nac_fieltro) ---
        frame_gastos = ttk.LabelFrame(form_frame, text="Gastos Asociados (Transporte, etc.)", padding="10")
        frame_gastos.grid(row=2, column=0, columnspan=4, sticky="ew", padx=5, pady=10)
        frame_gastos.grid_columnconfigure(0, weight=1)

        ttk.Label(frame_gastos, text="Descripción:").grid(row=0, column=0, padx=5, pady=3, sticky="w")
        self.entry_gasto_desc_nac_fieltro = ttk.Entry(frame_gastos)
        self.entry_gasto_desc_nac_fieltro.grid(row=1, column=0, padx=5, pady=3, sticky="ew")
        ttk.Label(frame_gastos, text="Coste (€):").grid(row=0, column=1, padx=5, pady=3, sticky="w")
        self.entry_gasto_coste_nac_fieltro = ttk.Entry(frame_gastos, width=10)
        self.entry_gasto_coste_nac_fieltro.grid(row=1, column=1, padx=5, pady=3, sticky="w")
        ttk.Button(frame_gastos, text="Añadir Gasto", command=self._add_gasto_nac_fieltro_temp).grid(row=1, column=2, padx=5, pady=5, sticky="w")

        cols_gastos = ("Descripción", "Coste")
        self.tree_gastos_nac_fieltro = ttk.Treeview(frame_gastos, columns=cols_gastos, show="headings", height=3, selectmode="browse")
        self.tree_gastos_nac_fieltro.heading("Descripción", text="Descripción"); self.tree_gastos_nac_fieltro.column("Descripción", width=350, anchor=tk.W)
        self.tree_gastos_nac_fieltro.heading("Coste", text="Coste (€)"); self.tree_gastos_nac_fieltro.column("Coste", width=100, anchor=tk.E)
        self.tree_gastos_nac_fieltro.grid(row=2, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        # TODO: Scrollbar Tree Gasto Nac Fieltro
        ttk.Button(frame_gastos, text="Eliminar Gasto Sel.", command=self._del_gasto_nac_fieltro_temp).grid(row=3, column=0, columnspan=3, pady=(0, 5))

        # --- Sub-Frame: Rollos Fieltro Nacional (Precio en EUR, sin Color) ---
        frame_items = ttk.LabelFrame(form_frame, text="Rollos de Fieltro (Pedido Nacional)", padding="10")
        frame_items.grid(row=3, column=0, columnspan=4, sticky="ew", padx=5, pady=10)

        labels_items = ["Espesor:", "Ancho(mm):", "Largo(m):", "Nº Rollos:", "Precio/m (€):"] # Sin Color
        self.entries_item_nac_fieltro = {} # Diccionario específico
        key_map_items = ["espesor", "ancho", "largo", "n_bobinas", "metro_lineal_eur"] # Sin Color

        i_row = 0
        for i, text in enumerate(labels_items):
            lbl = ttk.Label(frame_items, text=text)
            col_lbl = (i % 3) * 2
            col_entry = col_lbl + 1
            row_entry = i_row + (i // 3) * 2
            lbl.grid(row=row_entry, column=col_lbl, padx=5, pady=3, sticky="w")
            entry = ttk.Entry(frame_items, width=12)
            entry.grid(row=row_entry, column=col_entry, padx=5, pady=3, sticky="ew")
            self.entries_item_nac_fieltro[key_map_items[i]] = entry

        ttk.Button(frame_items, text="Añadir Rollo", command=self._add_item_nac_fieltro_temp).grid(row=i_row + 2, column=4, padx=5, pady=5, sticky="se", rowspan=2) # Ajustar columna

        cols_items = ("Espesor", "Ancho", "Largo", "Nº", "EUR/m") # Sin Color
        self.tree_items_nac_fieltro = ttk.Treeview(frame_items, columns=cols_items, show="headings", height=4, selectmode="browse")
        for col in cols_items: self.tree_items_nac_fieltro.heading(col, text=col); self.tree_items_nac_fieltro.column(col, width=85, anchor=tk.CENTER) # Ajustar anchos
        self.tree_items_nac_fieltro.column("EUR/m", anchor=tk.E)
        self.tree_items_nac_fieltro.grid(row=i_row + 4, column=0, columnspan=5, sticky="nsew", padx=5, pady=5)
        # TODO: Scrollbar Tree Items Nac Fieltro

        ttk.Button(frame_items, text="Eliminar Rollo Sel.", command=self._del_item_nac_fieltro_temp).grid(row=i_row + 5, column=0, columnspan=5, pady=(0, 5))

        # --- Botón Guardar Final ---
        ttk.Button(form_frame, text="GUARDAR PEDIDO FIELTRO NACIONAL", command=self._guardar_pedido_nacional_fieltro, style="Accent.TButton").grid(row=4, column=0, columnspan=4, pady=20, ipady=5)

        # --- Label de Estado/Mensajes ---
        self.status_label_form_nac_fieltro = ttk.Label(form_frame, text="Formulario listo.", foreground="blue")
        self.status_label_form_nac_fieltro.grid(row=5, column=0, columnspan=4, pady=5)

    # --- Funciones auxiliares para Fieltro Nacional ---

    def _add_gasto_nac_fieltro_temp(self):
        """Añade gasto a lista temporal y TreeView Fieltro Nacional."""
        # Idéntica a Goma/PVC Nac, usando widgets _nac_fieltro
        descripcion = self.entry_gasto_desc_nac_fieltro.get().strip()
        coste_str = self.entry_gasto_coste_nac_fieltro.get().strip().replace(',', '.')
        try:
            coste = float(coste_str)
            if not descripcion or coste < 0: raise ValueError("Descripción y coste (>=0) requeridos.")
        except ValueError as e: messagebox.showerror("Error Gasto", f"Datos inválidos: {e}"); return
        gasto_data = {"descripcion": descripcion, "coste": coste}
        if not hasattr(self, 'gastos_temp_nac_fieltro'): self.gastos_temp_nac_fieltro = []
        self.gastos_temp_nac_fieltro.append(gasto_data)
        self.tree_gastos_nac_fieltro.insert("", tk.END, values=(descripcion, f"{coste:.2f}"))
        self.entry_gasto_desc_nac_fieltro.delete(0, tk.END); self.entry_gasto_coste_nac_fieltro.delete(0, tk.END)
        if hasattr(self, 'status_label_form_nac_fieltro'): self.status_label_form_nac_fieltro.config(text=f"Gasto '{descripcion}' añadido.")

    def _del_gasto_nac_fieltro_temp(self):
        """Elimina gasto de lista temporal y TreeView Fieltro Nacional."""
        # Idéntica a Goma/PVC Nac, usando widgets _nac_fieltro
        selected_iid = self.tree_gastos_nac_fieltro.selection()
        if not selected_iid: messagebox.showwarning("Eliminar Gasto", "Seleccione un gasto."); return
        item_index = self.tree_gastos_nac_fieltro.index(selected_iid[0])
        item_values = self.tree_gastos_nac_fieltro.item(selected_iid[0], 'values')
        try:
            if not hasattr(self, 'gastos_temp_nac_fieltro'): raise AttributeError("Lista gastos temp no existe")
            del self.gastos_temp_nac_fieltro[item_index]; self.tree_gastos_nac_fieltro.delete(selected_iid[0])
            if hasattr(self, 'status_label_form_nac_fieltro'): self.status_label_form_nac_fieltro.config(text=f"Gasto '{item_values[0]}' eliminado.")
        except (IndexError, AttributeError) as e: messagebox.showerror("Error", f"No se pudo eliminar el gasto: {e}")

    def _add_item_nac_fieltro_temp(self): # Renombrado a _add_item...
        """Añade rollo a lista temporal y TreeView Fieltro Nacional."""
        # Idéntica a Goma Nac, usando widgets _nac_fieltro
        try:
            espesor = self.entries_item_nac_fieltro["espesor"].get().strip() # String
            ancho_str = self.entries_item_nac_fieltro["ancho"].get().strip().replace(',', '.')
            largo_str = self.entries_item_nac_fieltro["largo"].get().strip().replace(',', '.')
            n_bobinas_str = self.entries_item_nac_fieltro["n_bobinas"].get().strip() # n_bobinas se usa internamente aunque sean rollos
            metro_lineal_eur_str = self.entries_item_nac_fieltro["metro_lineal_eur"].get().strip().replace(',', '.')

            if not espesor: raise ValueError("Espesor no puede estar vacío.")
            if not ancho_str or not largo_str or not n_bobinas_str or not metro_lineal_eur_str:
                raise ValueError("Ancho, Largo, Nº Rollos y Precio/m EUR no pueden estar vacíos.")

            ancho = float(ancho_str)
            largo = float(largo_str)
            n_bobinas = int(n_bobinas_str)
            metro_lineal_eur = float(metro_lineal_eur_str)

            if not all(v > 0 for v in [ancho, largo, n_bobinas]) or metro_lineal_eur < 0:
                 raise ValueError("Valores Ancho, Largo, Nº Rollos deben ser > 0 (precio >= 0).")

        except KeyError as e: messagebox.showerror("Error Rollo", f"Error interno: Clave no encontrada {e}"); return
        except ValueError as e: messagebox.showerror("Error Rollo", f"Datos de rollo inválidos: {e}"); return
        except Exception as e: messagebox.showerror("Error Rollo", f"Error inesperado: {e}"); return

        item_params = {
            "espesor": espesor, "ancho": ancho, "largo": largo,
            "n_bobinas": n_bobinas, "metro_lineal_eur": metro_lineal_eur
        }
        if not hasattr(self, 'items_temp_nac_fieltro'): self.items_temp_nac_fieltro = []
        self.items_temp_nac_fieltro.append(item_params)
        self.tree_items_nac_fieltro.insert("", tk.END, values=(espesor, ancho, largo, n_bobinas, f"{metro_lineal_eur:.2f}"))

        for entry_widget in self.entries_item_nac_fieltro.values(): entry_widget.delete(0, tk.END)
        if hasattr(self, 'status_label_form_nac_fieltro'): self.status_label_form_nac_fieltro.config(text=f"Rollo '{espesor}' añadido.")

    def _del_item_nac_fieltro_temp(self): # Renombrado a _del_item...
        """Elimina rollo de lista temporal y TreeView Fieltro Nacional."""
         # Idéntica a Goma Nac, usando widgets _nac_fieltro
        selected_iid = self.tree_items_nac_fieltro.selection()
        if not selected_iid: messagebox.showwarning("Eliminar Rollo", "Seleccione un rollo."); return
        item_index = self.tree_items_nac_fieltro.index(selected_iid[0])
        item_values = self.tree_items_nac_fieltro.item(selected_iid[0], 'values')
        try:
            if not hasattr(self, 'items_temp_nac_fieltro'): raise AttributeError("Lista items temp no existe")
            del self.items_temp_nac_fieltro[item_index]; self.tree_items_nac_fieltro.delete(selected_iid[0])
            if hasattr(self, 'status_label_form_nac_fieltro'): self.status_label_form_nac_fieltro.config(text=f"Rollo '{item_values[0]}' eliminado.")
        except (IndexError, AttributeError) as e: messagebox.showerror("Error", f"No se pudo eliminar el rollo: {e}")

    # --- Función Principal de Guardado para Fieltro Nacional ---

    # Dentro de la clase Interfaz en interfaz.py
    # (Asegúrate de tener imports: tk, ttk, messagebox, datetime,
    # MercanciaNacionalFieltro, guardar_o_actualizar_mercancias_fieltro, registrar_entrada_almacen)

    def _guardar_pedido_nacional_fieltro(self):
        """Recoge datos Fieltro Nac, crea obj, calcula, guarda JSON y registra en DB."""
        # Verificar y configurar label de estado
        status_label = getattr(self, 'status_label_form_nac_fieltro', None)
        if status_label and status_label.winfo_exists():
            status_label.config(text="Procesando...", foreground="blue")
        else:
            print("Advertencia: status_label_form_nac_fieltro no encontrado.")

        datos_a_guardar = {}
        # No hay valor_conversion para Nacional

        try: # Validar y procesar datos generales
            # Importar datetime si no está ya importado globalmente
            from datetime import datetime

            datos_generales_widgets = self.entries_nac_fieltro # Usar el diccionario correcto
            for key, widget in datos_generales_widgets.items():
                if key in ["fecha_pedido", "fecha_llegada"]:
                    try:
                        fecha_dt = widget.get_date() # Leer de DateEntry
                        datos_a_guardar[key] = fecha_dt.strftime('%Y-%m-%d') # Guardar como YYYY-MM-DD
                    except Exception as e_date:
                        raise ValueError(f"Error al obtener la fecha del campo '{key}': {e_date}")
                # No hay valor_conversion
                else:
                    # Leer otros campos como string
                    datos_a_guardar[key] = widget.get().strip()

            # Validaciones básicas
            if not datos_a_guardar.get("proveedor") or not datos_a_guardar.get("numero_factura"):
                 raise ValueError("Proveedor y Número Factura son obligatorios.")
            if not datos_a_guardar["numero_factura"]: # Comprobación extra por si acaso
                 raise ValueError("Número Factura no puede estar vacío.")

            # Sacar valor_conversion si existiera por error (no debería en nacional)
            # valor_conv_final = datos_a_guardar.pop('valor_conversion', None) # No aplica

        except ValueError as e:
            messagebox.showerror("Error Datos Generales", f"Datos inválidos: {e}")
            if status_label and status_label.winfo_exists(): status_label.config(text="Error en datos generales.", foreground="red")
            return
        except Exception as e:
             messagebox.showerror("Error Datos Generales", f"Error inesperado recogiendo datos: {e}")
             if status_label and status_label.winfo_exists(): status_label.config(text="Error interno formulario.", foreground="red")
             return

        # Validar que haya rollos (items) añadidos
        if not hasattr(self, 'items_temp_nac_fieltro') or not self.items_temp_nac_fieltro:
            messagebox.showerror("Error Contenido", "Debe añadir al menos un rollo.")
            if status_label and status_label.winfo_exists(): status_label.config(text="Error: Faltan rollos.", foreground="red")
            return

        # Crear instancia MercanciaNacionalFieltro
        pedido = None
        try:
            # Importar clase backend Fieltro Nacional
            from nacional.mercanciaNacionalFieltro import MercanciaNacionalFieltro
            # Pasar solo los datos generales al constructor
            pedido = MercanciaNacionalFieltro(**datos_a_guardar)
        except ImportError:
             messagebox.showerror("Error Importación", "No se encontró la clase 'MercanciaNacionalFieltro'.")
             if status_label and status_label.winfo_exists(): status_label.config(text="Error interno (backend).", foreground="red")
             return
        except Exception as e:
            messagebox.showerror("Error Creación", f"No se pudo crear el objeto MercanciaNacionalFieltro: {e}")
            if status_label and status_label.winfo_exists(): status_label.config(text="Error interno (creación).", foreground="red")
            return

        # --- Lógica Backend: Añadir gastos/items, calcular, guardar, registrar ---
        json_guardado = False
        try:
            # 1. Añadir gastos
            if hasattr(self, 'gastos_temp_nac_fieltro'):
                for gasto_data in self.gastos_temp_nac_fieltro:
                    pedido.agregar_gasto(gasto_data["descripcion"], gasto_data["coste"])

            # 2. Añadir rollos (items)
            if hasattr(self, 'items_temp_nac_fieltro'):
                 add_item_method = getattr(pedido, 'agregar_rollo_fieltro', None) # Usa el nombre correcto
                 if not add_item_method: raise AttributeError("Método 'agregar_rollo_fieltro' no encontrado.")
                 for item_data in self.items_temp_nac_fieltro:
                     add_item_method(**item_data) # Pasa el dict (ya tiene metro_lineal_eur)

            # 3. Calcular precios finales
            pedido.calcular_precios_finales()

            # 4. Guardar en JSON Nacional
            # --- LLAMADA CORRECTA Y ÚNICA AL GUARDADO JSON ---
            try:
                 from nacional.mercanciaNacionalFieltro import guardar_o_actualizar_mercancias_fieltro # Func específica Nac
                 guardar_o_actualizar_mercancias_fieltro([pedido]) # Solo esta llamada
                 json_guardado = True
                 print(f"Pedido Fieltro Nacional {pedido.numero_factura} guardado/actualizado en JSON.")
            except ImportError:
                 messagebox.showerror("Error Guardado", "Función 'guardar_o_actualizar_mercancias_fieltro' no encontrada.")
                 raise
            # --- FIN LLAMADA CORRECTA ---

        except Exception as e:
            messagebox.showerror("Error Procesamiento", f"Error procesando datos Pedido Fieltro Nac: {e}")
            if status_label and status_label.winfo_exists(): status_label.config(text="Error procesando datos.", foreground="red")
            return

        # 5. Registrar en Almacén DB
        db_registrado = False
        if json_guardado: # Solo registrar si el JSON se guardó bien
            try:
                registrar_entrada_almacen(pedido)
                db_registrado = True
                # El mensaje de éxito ya se imprime dentro de registrar_entrada_almacen
            except Exception as e:
                messagebox.showwarning("Error Registro Almacén", f"JSON guardado, pero falló el registro en Almacén DB: {e}")

        # 6. Feedback final y limpiar
        if status_label and status_label.winfo_exists():
            if json_guardado and db_registrado:
                messagebox.showinfo("Éxito", f"Pedido Fieltro Nacional '{pedido.numero_factura}' guardado y registrado.")
                self._limpiar_form_nac_fieltro() # Llamar a la función de limpieza específica
                status_label.config(text=f"Pedido '{pedido.numero_factura}' procesado.", foreground="green")
            elif json_guardado:
                status_label.config(text=f"Pedido '{pedido.numero_factura}' guardado JSON, falló registro DB.", foreground="orange")
            # Si json_guardado es False, el error ya se mostró antes

    def _limpiar_form_nac_fieltro(self):
        """Limpia todos los campos de entrada y listas del formulario Fieltro Nacional."""
        try:
            if hasattr(self, 'entries_nac_fieltro'):
                 for key, widget in self.entries_nac_fieltro.items():
                     if isinstance(widget, ttk.Entry): widget.delete(0, tk.END)
            if hasattr(self, 'entry_gasto_desc_nac_fieltro'): self.entry_gasto_desc_nac_fieltro.delete(0, tk.END)
            if hasattr(self, 'entry_gasto_coste_nac_fieltro'): self.entry_gasto_coste_nac_fieltro.delete(0, tk.END)
            if hasattr(self, 'entries_item_nac_fieltro'):
                 for entry_widget in self.entries_item_nac_fieltro.values(): entry_widget.delete(0, tk.END)
            if hasattr(self, 'tree_gastos_nac_fieltro'):
                 for iid in self.tree_gastos_nac_fieltro.get_children(): self.tree_gastos_nac_fieltro.delete(iid)
            if hasattr(self, 'tree_items_nac_fieltro'):
                 for iid in self.tree_items_nac_fieltro.get_children(): self.tree_items_nac_fieltro.delete(iid)
            if hasattr(self, 'gastos_temp_nac_fieltro'): self.gastos_temp_nac_fieltro.clear()
            if hasattr(self, 'items_temp_nac_fieltro'): self.items_temp_nac_fieltro.clear()
            if hasattr(self, 'status_label_form_nac_fieltro') and self.status_label_form_nac_fieltro:
                self.status_label_form_nac_fieltro.config(text="Formulario limpio.", foreground="black")
            print("Formulario Fieltro Nacional limpiado.")
        except Exception as e: print(f"Error limpiando formulario Fieltro Nacional: {e}")

    # ===================================================================
    # ### FIN FUNCIONALIDAD AÑADIR FIELTRO NACIONAL ###
    # ===================================================================



# ===================================================================
    # ===================================================================
    # ### INICIO FUNCIONALIDAD VER/GESTIONAR PEDIDOS NACIONALES ###
    # ===================================================================
    # ===================================================================

    def _mostrar_vista_ver_nacional(self):
        """Limpia el frame principal y crea la vista para ver pedidos nacionales."""
        self._limpiar_main_content()
        # Inicializar diccionario para guardar objetos nacionales cargados
        self.pedidos_nacionales_mostrados = {}
        print("Mostrando vista para Ver/Gestionar Pedidos Nacionales.")
        # Llamar a las funciones que construyen y pueblan la vista
        self._crear_widgets_vista_ver_nacional(self.main_content_frame)
        self._cargar_y_mostrar_pedidos_nacionales() # Cargar datos al mostrar

    def _crear_widgets_vista_ver_nacional(self, parent_frame):
        """Crea los widgets para la vista de listado de pedidos nacionales."""
        view_frame = ttk.Frame(parent_frame, padding="5")
        view_frame.pack(expand=True, fill="both")
        view_frame.grid_rowconfigure(1, weight=1)    # Fila con tabla se expande
        view_frame.grid_columnconfigure(0, weight=1) # Columna con tabla se expande

        # Título
        ttk.Label(view_frame, text="Listado de Pedidos Nacionales", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky='w')

        # --- Frame para contener el Treeview y las Scrollbars ---
        tree_frame = ttk.Frame(view_frame)
        tree_frame.grid(row=1, column=0, columnspan=2, sticky='nsew', pady=5) # Ajustar row a 1
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # --- Treeview para mostrar los pedidos nacionales ---
        # Columnas similares a la vista de contenedores
        cols = ("Factura", "Proveedor", "Tipo", "F. Llegada", "Observaciones")
        self.tree_ver_nacional = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")

        # Configurar cabeceras y columnas
        self.tree_ver_nacional.heading("Factura", text="Nº Factura"); self.tree_ver_nacional.column("Factura", width=120, anchor=tk.W)
        self.tree_ver_nacional.heading("Proveedor", text="Proveedor"); self.tree_ver_nacional.column("Proveedor", width=180, anchor=tk.W)
        self.tree_ver_nacional.heading("Tipo", text="Material"); self.tree_ver_nacional.column("Tipo", width=80, anchor=tk.CENTER)
        self.tree_ver_nacional.heading("F. Llegada", text="F. Llegada"); self.tree_ver_nacional.column("F. Llegada", width=100, anchor=tk.CENTER)
        self.tree_ver_nacional.heading("Observaciones", text="Observaciones"); self.tree_ver_nacional.column("Observaciones", width=300) # Esta columna se estirará

        # --- Crear y Configurar Scrollbars ---
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_ver_nacional.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree_ver_nacional.xview)
        self.tree_ver_nacional.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Posicionar Treeview y Scrollbars
        self.tree_ver_nacional.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        # --- Frame para botones de acción ---
        action_frame = ttk.Frame(view_frame)
        action_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=5) # Ajustar row a 2

        ttk.Button(action_frame, text="Ver Detalles", command=self._ver_detalles_pedido_nacional).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Editar", command=self._editar_pedido_nacional).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Eliminar", command=self._eliminar_pedido_nacional).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Refrescar Lista", command=self._cargar_y_mostrar_pedidos_nacionales).pack(side=tk.RIGHT, padx=5)

        # --- Label de estado ---
        self.status_label_ver_nacional = ttk.Label(view_frame, text="Cargando...")
        self.status_label_ver_nacional.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(5,0)) # Ajustar row a 3

    # En interfaz.py, dentro de la clase Interfaz


    def _cargar_y_mostrar_pedidos_nacionales(self):
        """Carga datos de todos los JSON de pedidos nacionales, los guarda
        internamente y los muestra en el Treeview, mostrando subtipo para Goma."""

        # Verificar que los widgets necesarios existen
        status_label = getattr(self, 'status_label_ver_nacional', None)
        tree_widget = getattr(self, 'tree_ver_nacional', None)
        pedidos_dict = getattr(self, 'pedidos_nacionales_mostrados', None)

        if not tree_widget or not tree_widget.winfo_exists():
            print("Error: Treeview para pedidos nacionales no existe.")
            return
        if pedidos_dict is None:
            print("Error: Diccionario 'pedidos_nacionales_mostrados' no inicializado.")
            self.pedidos_nacionales_mostrados = {} # Inicializar
            pedidos_dict = self.pedidos_nacionales_mostrados

        if status_label and status_label.winfo_exists():
            status_label.config(text="Cargando datos...", foreground="blue")

        # Limpiar tabla y diccionario interno
        for i in tree_widget.get_children():
            tree_widget.delete(i)
        pedidos_dict.clear()

        todos_los_pedidos = []
        # Diccionario de carga (como estaba antes)
        funciones_carga_nacional = {
            'GOMA': cargar_mercancias_goma,
            'PVC': cargar_mercancias_pvc,
            'FIELTRO': cargar_mercancias_fieltro,
           
        }

        # Cargar datos de cada tipo (como estaba antes)
        for tipo, func_carga in funciones_carga_nacional.items():
            if func_carga:
                try:
                    pedidos_tipo = func_carga()
                    if pedidos_tipo:
                        for pedido in pedidos_tipo:
                            pedido.tipo_material_display = tipo # Guardamos tipo principal
                            todos_los_pedidos.append(pedido)
                            factura_id = getattr(pedido, 'numero_factura', None)
                            if factura_id:
                                pedidos_dict[factura_id] = pedido # Guardar objeto
                except Exception as e:
                    print(f"Error al cargar pedidos nacionales de tipo {tipo}: {e}")
            else:
                print(f"Función de carga para {tipo} Nacional no disponible.")

        # Ordenar (como estaba antes)
        try: todos_los_pedidos.sort(key=lambda x: getattr(x, 'fecha_llegada', ''), reverse=True)
        except Exception as e_sort: print(f"Advertencia: No se pudo ordenar pedidos nacionales: {e_sort}")

        # Poblar Treeview
        items_insertados = 0
        if todos_los_pedidos:
            for pedido in todos_los_pedidos:
                factura = getattr(pedido, 'numero_factura', 'N/A')
                proveedor = getattr(pedido, 'proveedor', 'N/A')
                f_llegada_str = getattr(pedido, 'fecha_llegada', 'N/A')
                obs = getattr(pedido, 'observaciones', '')

                ## CAMBIO ## Determinar qué mostrar en la columna de material
                tipo_mat_display = getattr(pedido, 'tipo_material_display', 'N/A') # Default: GOMA, PVC, etc.

                # Si es un pedido de Goma Nacional y tiene contenido...
                if isinstance(pedido, MercanciaNacionalGoma) and hasattr(pedido, 'contenido') and pedido.contenido:
                    # ...intenta obtener el subtipo de la *primera* bobina
                    primer_item_subtipo = getattr(pedido.contenido[0], 'subtipo', 'NORMAL')
                    # Si el subtipo no es el normal, úsalo para mostrar
                    if primer_item_subtipo and primer_item_subtipo != 'NORMAL':
                        tipo_mat_display = primer_item_subtipo # Mostrar "CARAMELO", "VERDE", etc.
                ## FIN CAMBIO ##

                # Formatear fecha para mostrar (como estaba antes)
                try:
                    f_llegada_dt = datetime.strptime(f_llegada_str, '%Y-%m-%d')
                    f_llegada_display = f_llegada_dt.strftime('%d-%m-%Y')
                except (ValueError, TypeError):
                    f_llegada_display = f_llegada_str

                # Ensamblar valores para la fila
                valores = (factura, proveedor, tipo_mat_display, f_llegada_display, obs)

                # Insertar en Treeview (lógica de manejo de duplicados como estaba antes)
                try:
                    tree_widget.insert('', tk.END, iid=factura, values=valores)
                    items_insertados += 1
                except tk.TclError:
                    try:
                        alt_iid = f"{factura}_{items_insertados}"
                        tree_widget.insert('', tk.END, iid=alt_iid, values=valores)
                        items_insertados += 1
                        if factura in pedidos_dict:
                            pedidos_dict[alt_iid] = pedidos_dict.pop(factura)
                    except Exception as e_ins: print(f"Error insertando fila nacional alternativa para {factura}: {e_ins}")
                except Exception as e_gral: print(f"Error general insertando fila nacional para {factura}: {e_gral}")

        # Actualizar label de estado (como estaba antes)
        if status_label and status_label.winfo_exists():
            if items_insertados > 0:
                status_label.config(text=f"{items_insertados} pedido(s) nacional(es) cargado(s).", foreground="black")
            else:
                status_label.config(text="No se encontraron pedidos nacionales.", foreground="orange")

    # Dentro de la clase Interfaz en interfaz.py
        # Asegúrate de tener los imports necesarios: tk, ttk, messagebox, datetime
        # Y potencialmente los modelos Nacionales si usas isinstance en el futuro:
        # from modelos import GomaNacional, PVCNacional, FieltroNacional # etc.

    # ===================================================================
    # ### INICIO ACCIONES VISTA PEDIDOS NACIONALES ###
    # ===================================================================

    def _ver_detalles_pedido_nacional(self):
        """Muestra los detalles completos del pedido nacional seleccionado en una nueva ventana."""
        if not hasattr(self, 'tree_ver_nacional') or not self.tree_ver_nacional.winfo_exists():
            messagebox.showerror("Error", "La tabla de pedidos nacionales no está disponible.")
            return
        selected_iids = self.tree_ver_nacional.selection()
        if not selected_iids:
            messagebox.showinfo("Ver Detalles", "Seleccione un pedido nacional de la lista.")
            return

        selected_iid = selected_iids[0] # El iid es la factura

        # Recuperar el objeto completo del diccionario
        pedido_obj = self.pedidos_nacionales_mostrados.get(selected_iid)

        # Intento extra por si se usó ID alternativo en la inserción del Treeview
        if not pedido_obj and "_" in selected_iid:
            original_factura = selected_iid.split("_")[0]
            pedido_obj = self.pedidos_nacionales_mostrados.get(original_factura)

        if not pedido_obj:
            messagebox.showerror("Error", f"No se encontraron los datos completos para la factura '{selected_iid}'. Intente refrescar.")
            return

        # --- Crear la nueva ventana Toplevel ---
        details_window = tk.Toplevel(self.root)
        tipo_display = getattr(pedido_obj, 'tipo_material_display', type(pedido_obj).__name__.replace('MercanciaNacional',''))
        details_window.title(f"Detalles Pedido Nac. {tipo_display} - Factura: {pedido_obj.numero_factura}")
        details_window.geometry("850x650")
        details_window.minsize(600, 400)
        details_window.transient(self.root)
        details_window.grab_set()

        # Configurar grid principal de la ventana de detalles
        details_window.rowconfigure(2, weight=1) # Frame contenido
        details_window.rowconfigure(1, weight=1) # Frame gastos
        details_window.columnconfigure(0, weight=1)

        # --- Frame para Datos Generales ---
        frame_general = ttk.LabelFrame(details_window, text="Datos Generales", padding="10")
        frame_general.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        frame_general.grid_columnconfigure(1, weight=1)

        # Poblar Datos Generales
        gen_labels = {
            "Factura:": getattr(pedido_obj, 'numero_factura', 'N/A'),
            "Proveedor:": getattr(pedido_obj, 'proveedor', 'N/A'),
            "Fecha Pedido:": getattr(pedido_obj, 'fecha_pedido', 'N/A'),
            "Fecha Llegada:": getattr(pedido_obj, 'fecha_llegada', 'N/A'),
            "Observaciones:": getattr(pedido_obj, 'observaciones', '')
            # No hay valor conversión en nacional
        }
        row_num = 0
        for label_text, value_text in gen_labels.items():
            lbl = ttk.Label(frame_general, text=label_text, anchor="w")
            lbl.grid(row=row_num, column=0, sticky="w", padx=5, pady=2)
            # Formatear fechas para mostrar en DD-MM-YYYY
            display_value = value_text
            if "Fecha" in label_text and isinstance(value_text, str) and len(value_text) == 10:
                 try:
                      dt_obj = datetime.strptime(value_text, '%Y-%m-%d')
                      display_value = dt_obj.strftime('%d-%m-%Y')
                 except ValueError: pass # Dejar como está si el formato no es YYYY-MM-DD

            val = ttk.Label(frame_general, text=display_value, anchor="w", wraplength=details_window.winfo_width() - 50)
            val.grid(row=row_num, column=1, sticky="ew", padx=5, pady=2)
            row_num += 1

        # --- Frame para Gastos (Lista simple) ---
        frame_gastos = ttk.LabelFrame(details_window, text="Gastos Asociados", padding="10")
        frame_gastos.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        frame_gastos.grid_rowconfigure(0, weight=1)
        frame_gastos.grid_columnconfigure(0, weight=1)

        cols_gastos = ("Descripción", "Coste") # Sin columna "Tipo"
        tree_gastos = ttk.Treeview(frame_gastos, columns=cols_gastos, show="headings", height=4, selectmode="none")
        tree_gastos.heading("Descripción", text="Descripción"); tree_gastos.column("Descripción", width=400, anchor="w")
        tree_gastos.heading("Coste", text="Coste (€)"); tree_gastos.column("Coste", width=100, anchor="e")

        scrollbar_gastos = ttk.Scrollbar(frame_gastos, orient="vertical", command=tree_gastos.yview)
        tree_gastos.configure(yscrollcommand=scrollbar_gastos.set)
        tree_gastos.grid(row=0, column=0, sticky="nsew")
        scrollbar_gastos.grid(row=0, column=1, sticky="ns")

        # Poblar Treeview de gastos (lista simple)
        if hasattr(pedido_obj, 'gastos') and isinstance(pedido_obj.gastos, list):
            if not pedido_obj.gastos:
                 tree_gastos.insert('', 'end', values=("(Sin gastos registrados)", ""))
            else:
                 for gasto in pedido_obj.gastos:
                      if isinstance(gasto, dict):
                           desc = gasto.get('descripcion', '?')
                           cost = gasto.get('coste', 0)
                           try: cost_str = f"{float(cost):.2f}"
                           except: cost_str = "Inválido"
                           tree_gastos.insert('', 'end', values=(desc, cost_str)) # Solo desc y coste
        else:
             tree_gastos.insert('', 'end', values=("(Formato de gastos no reconocido)", ""))

        # --- Frame para Contenido ---
        frame_contenido = ttk.LabelFrame(details_window, text="Contenido del Pedido", padding="10")
        frame_contenido.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        frame_contenido.grid_rowconfigure(0, weight=1)
        frame_contenido.grid_columnconfigure(0, weight=1)

        # Columnas: Ajustar según los modelos Nacionales (GomaNacional, PVCNacional, etc.)
      
        cols_contenido = ("Item", "Tipo", "Espesor", "Ancho", "Largo", "Nº", "Color", "Coste/m (€)", "Coste Total (€)")
        tree_contenido = ttk.Treeview(frame_contenido, columns=cols_contenido, show="headings", height=8, selectmode="none")

        # Configurar cabeceras y anchos/minwidth/stretch
        tree_contenido.heading("Item", text="#"); tree_contenido.column("Item", width=35, minwidth=35, stretch=tk.NO, anchor="center")
        tree_contenido.heading("Tipo", text="Tipo"); tree_contenido.column("Tipo", width=100, minwidth=80, stretch=tk.NO) # Un poco más ancho
        tree_contenido.heading("Espesor", text="Espesor"); tree_contenido.column("Espesor", width=130, minwidth=100)
        tree_contenido.heading("Ancho", text="Ancho"); tree_contenido.column("Ancho", width=70, minwidth=60, stretch=tk.NO, anchor="e")
        tree_contenido.heading("Largo", text="Largo"); tree_contenido.column("Largo", width=70, minwidth=60, stretch=tk.NO, anchor="e")
        tree_contenido.heading("Nº", text="Nº"); tree_contenido.column("Nº", width=40, minwidth=40, stretch=tk.NO, anchor="center")
        tree_contenido.heading("Color", text="Color"); tree_contenido.column("Color", width=100, minwidth=80)
        tree_contenido.heading("Coste/m (€)", text="Coste/m (€)"); tree_contenido.column("Coste/m (€)", width=100, minwidth=90, anchor="e")
        tree_contenido.heading("Coste Total (€)", text="Coste Total (€)"); tree_contenido.column("Coste Total (€)", width=120, minwidth=100, anchor="e")

        # Ocultar columnas no aplicables inicialmente
        tree_contenido.column("Color", width=0, minwidth=0, stretch=tk.NO)
        # Mostrar Coste/m por defecto para Goma/PVC/Fieltro Nacional
        tree_contenido.column("Coste/m (€)", width=100, minwidth=90, anchor="e")

        # Configurar columnas específicas (ej: mostrar Color para PVC)
        if "PVCNacional" in tipo_display: # Comprobar por el nombre del tipo
            tree_contenido.column("Color", width=100, minwidth=80)
       
        # Scrollbars
        v_scroll_cont = ttk.Scrollbar(frame_contenido, orient="vertical", command=tree_contenido.yview)
        h_scroll_cont = ttk.Scrollbar(frame_contenido, orient="horizontal", command=tree_contenido.xview)
        tree_contenido.configure(yscrollcommand=v_scroll_cont.set, xscrollcommand=h_scroll_cont.set)
        tree_contenido.grid(row=0, column=0, sticky="nsew")
        v_scroll_cont.grid(row=0, column=1, sticky="ns")
        h_scroll_cont.grid(row=1, column=0, columnspan=2, sticky="ew")

        # Poblar Treeview de contenido
        if hasattr(pedido_obj, 'contenido') and pedido_obj.contenido:
            for i, item in enumerate(pedido_obj.contenido):
                # Extraer datos de forma segura
                # Asume que los modelos Nacionales (GomaNacional, PVCNacional, FieltroNacional)
                # tienen los atributos necesarios.
                tipo_item = type(item).__name__ # GomaNacional, PVCNacional...
                espesor = getattr(item, 'espesor', '-')
                ancho = getattr(item, 'ancho', '-')
                largo = getattr(item, 'largo', '-')
                n_bobinas = getattr(item, 'n_bobinas', '-')
                color = getattr(item, 'color', '-') # Relevante para PVCNacional
                coste_m = getattr(item, 'metro_lineal_euro_mas_gastos', None)
                coste_t = getattr(item, 'precio_total_euro_gastos', None)

                # Formatear para display
                coste_m_str = f"{coste_m:.4f}" if isinstance(coste_m, (int, float)) else "-"
                coste_t_str = f"{coste_t:.2f}" if isinstance(coste_t, (int, float)) else "-"
                try: ancho_str = f"{float(ancho):.1f}" if isinstance(ancho, (int, float, str)) and str(ancho).replace('.','',1).isdigit() else str(ancho)
                except: ancho_str = str(ancho)
                try: largo_str = f"{float(largo):.1f}" if isinstance(largo, (int, float, str)) and str(largo).replace('.','',1).isdigit() else str(largo)
                except: largo_str = str(largo)


               
                tree_contenido.insert('', 'end', values=(
                    i+1, tipo_item, espesor, ancho_str, largo_str, n_bobinas,
                    color, # Columna color
                    coste_m_str, coste_t_str
                ))
        else:
            tree_contenido.insert('', 'end', values=("", "", "", "(Sin contenido)", "", "", "", "", ""))


        # --- Botón Cerrar ---
        close_button = ttk.Button(details_window, text="Cerrar", command=details_window.destroy)
        close_button.grid(row=3, column=0, pady=(10, 10))

        # Enfocar la nueva ventana
        details_window.focus_set()

    def _editar_pedido_nacional(self):
        """Placeholder para la funcionalidad de editar un pedido nacional."""
        selected_iids = self.tree_ver_nacional.selection()
        if not selected_iids: messagebox.showinfo("Editar Pedido", "Seleccione un pedido."); return
        # Obtener factura de los valores mostrados en la columna 0
        numero_factura_sel = self.tree_ver_nacional.item(selected_iids[0], 'values')[0]
        print(f"Acción pendiente: Editar Pedido Nacional con Factura: {numero_factura_sel}")
        messagebox.showinfo("Funcionalidad Pendiente", f"La edición del pedido nacional '{numero_factura_sel}' aún no está implementada.\nSe necesitaría abrir el formulario correspondiente con estos datos cargados.")

    def _eliminar_pedido_nacional(self):
        """Placeholder para la funcionalidad de eliminar un pedido nacional."""
        selected_iids = self.tree_ver_nacional.selection()
        if not selected_iids: messagebox.showinfo("Eliminar Pedido", "Seleccione un pedido."); return
        numero_factura_sel = self.tree_ver_nacional.item(selected_iids[0], 'values')[0]

        # Recuperar el objeto para saber el tipo (necesario para llamar a la función backend correcta)
        pedido_obj = self.pedidos_nacionales_mostrados.get(selected_iids[0])
        # Intento extra por ID alternativo
        if not pedido_obj and "_" in selected_iids[0]:
             original_factura = selected_iids[0].split("_")[0]
             pedido_obj = self.pedidos_nacionales_mostrados.get(original_factura)

        if not pedido_obj:
             messagebox.showerror("Error", f"No se pudo determinar el tipo del pedido {numero_factura_sel} para eliminar.")
             return

        tipo_material = getattr(pedido_obj, 'tipo_material_display', 'Desconocido')

        print(f"Acción pendiente: Eliminar Pedido Nacional ({tipo_material}) con Factura: {numero_factura_sel}")
        if messagebox.askyesno("Confirmar Eliminación", f"¿Seguro que quieres eliminar el pedido nacional '{numero_factura_sel}' ({tipo_material})?\n\nEsta acción eliminará permanentemente el registro del archivo JSON.\n\n(NOTA: La funcionalidad de borrado real aún no está implementada en el backend)."):
            print(f"SIMULACIÓN: Llamando a función backend para borrar {numero_factura_sel} del JSON de {tipo_material} Nacional.")
            # --- Aquí iría la llamada a la función backend ---
            # ej: exito_borrado = backend_nacional_XX.eliminar_pedido(numero_factura_sel)
            # if exito_borrado:
            #     messagebox.showinfo("Eliminado", f"Pedido '{numero_factura_sel}' eliminado.")
            #     self._cargar_y_mostrar_pedidos_nacionales() # Refrescar
            # else:
            #     messagebox.showerror("Error", f"No se pudo eliminar el pedido '{numero_factura_sel}'.")
            # -------------------------------------------------
            messagebox.showinfo("Eliminar Pedido", f"Pedido '{numero_factura_sel}' supuestamente eliminado.\n(Funcionalidad real pendiente)") # Mensaje temporal
        else:
            print("Eliminación cancelada.")

    # ===================================================================
    # ### FIN ACCIONES VISTA PEDIDOS NACIONALES ###
    # ===================================================================
    # ===================================================================
    # ### FIN FUNCIONALIDAD VER/GESTIONAR PEDIDOS NACIONALES ###
    # ===================================================================


    # ===================================================================
    # ===================================================================
    # ### INICIO FUNCIONALIDAD VISTA ALMACÉN (STOCK) ###
    # ===================================================================
    # ===================================================================
  
   

    # En interfaz.py, dentro de la clase Interfaz

    def _crear_widgets_vista_almacen(self, parent_frame):
        """Crea los widgets para la vista de listado de stock (CORREGIDO LAYOUT)."""

        # --- Configurar grid del CONTENEDOR PADRE (main_content_frame) ---
        # Esto asegura que view_frame pueda expandirse dentro de él.
        # Hacemos esto aquí para asegurarnos de que se aplica a esta vista.
        parent_frame.grid_rowconfigure(0, weight=1)
        parent_frame.grid_columnconfigure(0, weight=1)

        # --- Frame principal de la vista (usando grid) ---
        view_frame = ttk.Frame(parent_frame, padding="5")
        # !!! CAMBIO CLAVE: Usar grid en lugar de pack !!!
        view_frame.grid(row=0, column=0, sticky="nsew")

        # --- Configurar grid INTERNO de view_frame ---
        # La fila que contiene la tabla (fila 2) debe poder expandirse verticalmente.
        # La primera columna (columna 0) debe poder expandirse horizontalmente.
        view_frame.grid_rowconfigure(2, weight=1)
        view_frame.grid_columnconfigure(0, weight=1) # Permitir expansión horizontal

        # --- Título ---
        # Ajustar columnspan si solo hay una columna principal expandiéndose
        ttk.Label(view_frame, text="Listado de Stock Almacén", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=1, pady=(0, 10), sticky='w')

        # --- Frame para filtros ---
        filter_frame = ttk.LabelFrame(view_frame, text="Filtros", padding="10")
        # Ajustar columnspan si solo hay una columna principal expandiéndose
        filter_frame.grid(row=1, column=0, columnspan=1, sticky='ew', padx=5, pady=5)
        # Configurar columnas internas del frame de filtros si es necesario (ej: para el botón)
        filter_frame.grid_columnconfigure(4, weight=1) # Dar peso a la columna del botón para que se alinee a la derecha

        # (Widgets de filtro - sin cambios en su lógica interna, solo el grid del contenedor)
        ttk.Label(filter_frame, text="Material:").grid(row=0, column=0, padx=(0,5), pady=2, sticky='w')
        tipos_material_stock = ["", "GOMA", "PVC", "FIELTRO", "COMPONENTE"] # Añadido COMPONENTE
        self.combo_stock_material = ttk.Combobox(filter_frame, values=tipos_material_stock, state="readonly", width=15)
        self.combo_stock_material.grid(row=0, column=1, padx=5, pady=2, sticky='w')

        ttk.Label(filter_frame, text="Estado:").grid(row=0, column=2, padx=(10,5), pady=2, sticky='w')
        estados_stock = ["", "DISPONIBLE", "EMPEZADA", "AGOTADO", "DESCATALOGADO"]
        self.combo_stock_status = ttk.Combobox(filter_frame, values=estados_stock, state="readonly", width=15)
        self.combo_stock_status.grid(row=0, column=3, padx=5, pady=2, sticky='w')

        ttk.Label(filter_frame, text="Buscar Ref./Factura:").grid(row=1, column=0, padx=(0,5), pady=2, sticky='w')
        self.entry_stock_buscar = ttk.Entry(filter_frame, width=30)
        self.entry_stock_buscar.grid(row=1, column=1, columnspan=3, padx=5, pady=2, sticky='ew')

        btn_frame = ttk.Frame(filter_frame)
        # Colocar btn_frame en la columna 4 que tiene peso
        btn_frame.grid(row=0, column=4, rowspan=2, padx=(10,0), sticky='e')
        ttk.Button(btn_frame, text="Aplicar Filtros", command=self._filtrar_y_mostrar_stock).pack(pady=2, anchor='e')
        ttk.Button(btn_frame, text="Limpiar Filtros", command=self._limpiar_filtros_y_recargar_stock).pack(pady=2, anchor='e')


        # --- Frame para Treeview y Scrollbars ---
        tree_frame = ttk.Frame(view_frame)
        # Ajustar columnspan si solo hay una columna principal expandiéndose
        tree_frame.grid(row=2, column=0, columnspan=1, sticky='nsew', pady=5)
        # Configurar grid INTERNO de tree_frame (para que Treeview y Scrollbar se ajusten)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # --- Treeview (Definición sin cambios) ---
        cols = ("ID", "Ref.", "Material", "Origen Fact.", "Fecha Entr.", "Estado", "Espesor", "Ancho", "Largo/Cant", "Coste U.", "Ubicación")
        self.tree_stock = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")

        # Configurar cabeceras y columnas (Importante ajustar anchos si es necesario)
        self.tree_stock.heading("ID", text="ID"); self.tree_stock.column("ID", width=40, stretch=False, anchor="center")
        self.tree_stock.heading("Ref.", text="Ref."); self.tree_stock.column("Ref.", width=150, anchor="w")
        self.tree_stock.heading("Material", text="Material"); self.tree_stock.column("Material", width=120, anchor="w")
        self.tree_stock.heading("Origen Fact.", text="Fact. Origen"); self.tree_stock.column("Origen Fact.", width=100, anchor="w")
        self.tree_stock.heading("Fecha Entr.", text="Entrada"); self.tree_stock.column("Fecha Entr.", width=85, anchor="center")
        self.tree_stock.heading("Estado", text="Estado"); self.tree_stock.column("Estado", width=85, anchor="center")
        self.tree_stock.heading("Espesor", text="Espesor"); self.tree_stock.column("Espesor", width=80, anchor="w")
        self.tree_stock.heading("Ancho", text="Ancho"); self.tree_stock.column("Ancho", width=60, anchor="e")
        self.tree_stock.heading("Largo/Cant", text="Largo/Cant"); self.tree_stock.column("Largo/Cant", width=80, anchor="e") # Largo o Cantidad Actual
        self.tree_stock.heading("Coste U.", text="Coste Unit."); self.tree_stock.column("Coste U.", width=90, anchor="e")
        self.tree_stock.heading("Ubicación", text="Ubicación"); self.tree_stock.column("Ubicación", width=100, anchor="w")

        self.tree_stock.bind("<Double-1>", self._abrir_ventana_detalles_stock) # Doble clic

        # --- Scrollbars ---
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_stock.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree_stock.xview)
        self.tree_stock.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # --- Posicionar Treeview y Scrollbars DENTRO de tree_frame ---
        self.tree_stock.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew') # Scrollbar horizontal debajo

        # --- Frame para botones de acción ---
        action_frame = ttk.Frame(view_frame)
        # Ajustar columnspan si solo hay una columna principal expandiéndose
        action_frame.grid(row=3, column=0, columnspan=1, sticky='ew', pady=5)
        # (Botones sin cambios en su lógica interna)
        ttk.Button(action_frame, text="Marcar Empezada", command=self._marcar_item_empezado).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Dar de Baja (Agotado)", command=self._dar_baja_stock_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Imprimir Stock", command=self._imprimir_listado_stock).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Refrescar Lista", command=lambda: self._cargar_y_mostrar_stock(filtros={'status': 'DISPONIBLE'})).pack(side=tk.RIGHT, padx=5)


        # --- Label de estado ---
        self.status_label_stock = ttk.Label(view_frame, text="") # Inicializar vacío
        # Ajustar columnspan si solo hay una columna principal expandiéndose
        self.status_label_stock.grid(row=4, column=0, columnspan=1, sticky='ew', pady=(5,0))

    
    def _get_current_stock_filters(self) -> dict:
         """Devuelve un diccionario con los filtros actualmente aplicados en la vista de stock."""
         filtros = {}
         try:
             if hasattr(self, 'combo_stock_material'):
                  mat_tipo = self.combo_stock_material.get()
                  if mat_tipo: filtros['material_tipo'] = mat_tipo
             if hasattr(self, 'combo_stock_status'):
                  status = self.combo_stock_status.get()
                  if status: filtros['status'] = status
             if hasattr(self, 'entry_stock_buscar'):
                  buscar_texto = self.entry_stock_buscar.get().strip()
                  if buscar_texto: filtros['buscar'] = buscar_texto
         except Exception as e:
             print(f"Error obteniendo filtros actuales: {e}")
         return filtros

    
    
       
    try:
        from almacen.gestion_almacen import consultar_stock
    except ImportError:
        # Define una función dummy si la importación falla para evitar errores posteriores
        def consultar_stock(filtros=None):
            print("ERROR: La función consultar_stock no está disponible.")
            messagebox.showerror("Error Backend", "Función consultar_stock no disponible.")
            return []

    def _cargar_y_mostrar_stock(self, filtros=None):
        """
        Carga datos de stock, los muestra en el Treeview usando un IID único
        (prefijo_tabla + id_db) y guarda la info original en stock_item_tablas.
        Ordena por fecha de entrada descendente por defecto (desde la consulta SQL).
        """
        print("\n--- INICIO _cargar_y_mostrar_stock (con IID único) ---")
        status_label = getattr(self, 'status_label_stock', None)
        tree_widget = getattr(self, 'tree_stock', None)
        # Cambiamos stock_item_tablas para guardar dict: {unique_iid: {'tabla': tabla, 'db_id': id}}
        stock_item_info = getattr(self, 'stock_item_tablas', None)

        # --- Verificaciones iniciales ---
        if not tree_widget or not tree_widget.winfo_exists():
            print("Error: Treeview para stock no existe.")
            return
        if not callable(consultar_stock):
            # El error ya se maneja en el import, pero verificamos de nuevo
            return
        if stock_item_info is None:
            print("Error: Diccionario 'stock_item_tablas' no inicializado. Creando uno nuevo.")
            self.stock_item_tablas = {}
            stock_item_info = self.stock_item_tablas
        else:
            stock_item_info.clear() # Limpiar diccionario para mapeo

        # --- Limpieza y Estado Inicial ---
        if status_label and status_label.winfo_exists():
            status_label.config(text="Consultando base de datos...", foreground="blue")
            self.root.update_idletasks()

        print("Limpiando Treeview de stock...")
        try:
            for i in tree_widget.get_children():
                tree_widget.delete(i)
            print("Treeview limpiado.")
        except Exception as e_clear:
            print(f"Error limpiando treeview: {e_clear}")

        # --- Carga de Datos ---
        stock_data = []
        items_insertados = 0
        try:
            print(f"Llamando consultar_stock con filtros: {filtros}")
            stock_data = consultar_stock(filtros=filtros)
            print(f"consultar_stock devolvió {len(stock_data)} items.")

            if not stock_data:
                msg = "No hay items en stock" + (" con los filtros aplicados." if filtros else ".")
                if status_label and status_label.winfo_exists():
                    status_label.config(text=msg, foreground="orange")
                return

            # --- Bucle para Poblar el Treeview con IID ÚNICO ---
            print("Poblando Treeview...")
            for item in stock_data:
                db_id = item.get('id')
                if db_id is None:
                    print(f"Advertencia: Item sin 'id' encontrado: {item}. Saltando.")
                    continue

                tabla_origen = None
                prefijo_iid = None
                if 'material_tipo' in item:
                    tabla_origen = 'StockMateriasPrimas'
                    prefijo_iid = "MP_"
                elif 'componente_ref' in item:
                    tabla_origen = 'StockComponentes'
                    prefijo_iid = "CP_"
                else:
                    print(f"Advertencia: No se pudo determinar la tabla para item ID {db_id}. Saltando.")
                    continue

                # Crear el IID único para el Treeview
                unique_treeview_iid = f"{prefijo_iid}{db_id}"

                # Guardar mapeo: unique_iid -> {tabla, id_original}
                stock_item_info[unique_treeview_iid] = {'tabla': tabla_origen, 'db_id': db_id}

                # --- Extraer y formatear datos ---
                # Columnas: ("ID", "Ref.", "Material", "Origen Fact.", "Fecha Entr.", "Estado",
                #            "Espesor", "Ancho", "Largo/Cant", "Coste U.", "Ubicación")
                ref = item.get('referencia_stock') or item.get('componente_ref', 'N/A')
                mat_tipo = item.get('material_tipo', 'COMPONENTE')
                subtipo = item.get('subtipo_material', '')
                material_display = mat_tipo
                if mat_tipo == 'GOMA' and subtipo and subtipo != 'NORMAL': material_display = f"GOMA ({subtipo})"
                elif mat_tipo != 'GOMA' and subtipo: material_display = f"{mat_tipo} ({subtipo})"
                fecha_str = item.get('fecha_entrada_almacen', 'N/A')
                fecha_display = fecha_str
                try: fecha_dt = datetime.strptime(fecha_str.split()[0], '%Y-%m-%d'); fecha_display = fecha_dt.strftime('%d-%m-%Y')
                except: pass
                largo_o_cant = item.get('largo_actual') if tabla_origen == 'StockMateriasPrimas' else item.get('cantidad_actual')
                largo_cant_str = f"{largo_o_cant:.2f}" if isinstance(largo_o_cant, (int, float)) else str(largo_o_cant or '-')
                coste_u = item.get('coste_unitario_final')
                coste_u_str = f"{coste_u:.4f}" if isinstance(coste_u, (int, float)) else str(coste_u or '-')
                ancho_str = str(item.get('ancho', '-'))
                if isinstance(item.get('ancho'), (int, float)): ancho_str = f"{item.get('ancho'):.0f}" # Ancho sin decimales si es número
                # --- Fin extracción/formateo ---

                valores_fila = (
                    db_id, # Mostrar ID original
                    ref,
                    material_display,
                    item.get('origen_factura', '-'),
                    fecha_display,
                    item.get('status', '-'),
                    item.get('espesor', '-'),
                    ancho_str, # Ancho formateado
                    largo_cant_str,
                    coste_u_str,
                    item.get('ubicacion', '-')
                )

                # Insertar en el Treeview USANDO EL IID ÚNICO
                try:
                    tree_widget.insert('', tk.END, iid=unique_treeview_iid, values=valores_fila)
                    items_insertados += 1
                except tk.TclError as e_tcl:
                    print(f"ERROR TclError INESPERADO insertando con IID '{unique_treeview_iid}': {e_tcl}")
                except Exception as e_ins:
                    print(f"Error general insertando fila stock con IID '{unique_treeview_iid}': {e_ins}")
                    traceback.print_exc(limit=1)

            print(f"Treeview poblado con {items_insertados} items.")

            # --- Actualizar Label de Estado Final ---
            if status_label and status_label.winfo_exists():
                if items_insertados > 0:
                    msg = f"{items_insertados} item(s) en stock cargado(s)."
                    if filtros: msg += " (Filtros aplicados)"
                    status_label.config(text=msg, foreground="black")
                else:
                    msg = "No hay items en stock" + (" con los filtros aplicados." if filtros else ".")
                    status_label.config(text=msg, foreground="orange")

        except Exception as e:
            print(f"ERROR FATAL en _cargar_y_mostrar_stock: {e}")
            traceback.print_exc()
            messagebox.showerror("Error de Carga Stock", f"No se pudo cargar/mostrar el stock.\n{e}")
            if status_label and status_label.winfo_exists():
                status_label.config(text="Error al cargar stock.", foreground="red")

        print("--- FIN _cargar_y_mostrar_stock (con IID único) ---")

    def _filtrar_y_mostrar_stock(self):
        """Recoge los filtros y llama a _cargar_y_mostrar_stock con ellos."""
        filtros = {}
        try:
            mat_tipo = self.combo_stock_material.get()
            status = self.combo_stock_status.get()
            buscar_texto = self.entry_stock_buscar.get().strip()

            if mat_tipo: filtros['material_tipo'] = mat_tipo
            if status: filtros['status'] = status
            if buscar_texto: filtros['buscar'] = buscar_texto # El backend decidirá en qué columnas buscar

            print(f"Aplicando filtros: {filtros}") # Debug
            self._cargar_y_mostrar_stock(filtros=filtros)

        except AttributeError:
             messagebox.showerror("Error", "Los widgets de filtro no están correctamente inicializados.")
        except Exception as e:
            messagebox.showerror("Error Filtro", f"Error al aplicar filtros: {e}")

    def _limpiar_filtros_y_recargar_stock(self):
        """Limpia los widgets de filtro y recarga la lista completa."""
        try:
            self.combo_stock_material.set('')
            self.combo_stock_status.set('')
            self.entry_stock_buscar.delete(0, tk.END)
            print("Filtros limpiados.")
            self._cargar_y_mostrar_stock(filtros=None) # Cargar sin filtros
        except AttributeError:
             messagebox.showerror("Error", "Los widgets de filtro no están correctamente inicializados.")
        except Exception as e:
            messagebox.showerror("Error Limpiando Filtros", f"Error inesperado: {e}")


        # En interfaz.py, dentro de la clase Interfaz

    # (Asegúrate de tener imports: tk, ttk, messagebox, traceback)
    # (Y los imports de las funciones backend: get_stock_item_details,
    #  marcar_item_empezado, marcar_item_agotado de almacen.gestion_almacen)
   
    try:
        from almacen.gestion_almacen import get_stock_item_details, marcar_item_empezado, marcar_item_agotado
    except ImportError:
        # Definir dummies si fallan los imports para evitar errores al definir las funciones
        def get_stock_item_details(item_id, tabla_stock): return None
        def marcar_item_empezado(id_stock, tabla_stock): return False
        def marcar_item_agotado(id_stock, tabla_stock): return False
        print("ADVERTENCIA: No se pudieron importar funciones de gestion_almacen.")


    def _abrir_ventana_detalles_stock(self, event=None):
        """
        Abre una nueva ventana mostrando los detalles del item de stock seleccionado.
        CORREGIDO para manejar el iid único ("MP_X", "CP_Y").
        """
        if not hasattr(self, 'tree_stock') or not self.tree_stock.winfo_exists(): return
        selected_iids = self.tree_stock.selection()
        if not selected_iids:
            # No mostrar mensaje si se activa por error sin selección
            return

        selected_unique_iid = selected_iids[0] # Este es ahora "MP_X" o "CP_Y"

        # --- Buscar la información original usando el iid único ---
        if not hasattr(self, 'stock_item_tablas'):
            messagebox.showerror("Error Interno", "Diccionario 'stock_item_tablas' no encontrado.")
            return
        item_info = self.stock_item_tablas.get(selected_unique_iid)

        if not item_info or 'tabla' not in item_info or 'db_id' not in item_info:
            messagebox.showerror("Error", f"No se pudo encontrar la información original para el item seleccionado ({selected_unique_iid}). Intente refrescar la lista.")
            return

        tabla_item = item_info['tabla']
        db_item_id = item_info['db_id']
        print(f"DEBUG: Ver detalles para iid={selected_unique_iid} -> tabla={tabla_item}, db_id={db_item_id}") # Debug

        # --- Obtener detalles del backend usando el ID numérico y la tabla ---
        try:
            if not callable(get_stock_item_details):
                messagebox.showerror("Error Backend", "Función get_stock_item_details no disponible.")
                return
            item_details = get_stock_item_details(db_item_id, tabla_item) # Usar db_item_id y tabla_item
        except Exception as e:
            messagebox.showerror("Error Backend", f"Error al obtener detalles del item ID {db_item_id}:\n{e}")
            traceback.print_exc()
            return

        if not item_details:
            messagebox.showwarning("No Encontrado", f"No se encontraron detalles para el item ID {db_item_id} en la tabla {tabla_item}.")
            return

        # --- Cargar márgenes y Calcular precios (igual que antes) ---
        margenes = self._cargar_margenes()
        if not margenes: return # El error ya se mostró

        precios_venta = {}
        coste_final = item_details.get('coste_unitario_final')
        if isinstance(coste_final, (int, float)) and coste_final >= 0:
            for nombre_margen, porcentaje in margenes.items():
                try:
                    precio = coste_final * (1 + (float(porcentaje) / 100.0))
                    precios_venta[nombre_margen] = f"{precio:.4f} €"
                except (ValueError, TypeError): precios_venta[nombre_margen] = "Error Cálculo"
        else:
            for nombre_margen in margenes.keys(): precios_venta[nombre_margen] = "N/A (sin coste)"

        # --- Crear y poblar ventana de detalles (igual que antes) ---
        details_win = tk.Toplevel(self.root)
        ref_display = item_details.get('referencia_stock', item_details.get('componente_ref', 'N/A'))
        details_win.title(f"Detalles Stock ID: {db_item_id} (Ref: {ref_display})")
        details_win.geometry("650x550")
        details_win.transient(self.root); details_win.grab_set()
        details_frame = ttk.Frame(details_win, padding="15")
        details_frame.pack(expand=True, fill="both")
        details_frame.columnconfigure(1, weight=1)

        row_idx = 0
        ttk.Label(details_frame, text="--- Detalles del Item ---", font=("Arial", 12, "bold")).grid(row=row_idx, column=0, columnspan=2, pady=(0,10)); row_idx += 1
        campos_a_mostrar = [
            ("ID DB:", lambda d: db_item_id), # Mostrar ID de la DB
            ('Tabla Origen:', lambda d: tabla_item),
            ('Referencia:', 'referencia_stock' if tabla_item == 'StockMateriasPrimas' else 'componente_ref'),
            ('Descripción:', 'descripcion' if tabla_item == 'StockComponentes' else None),
            ('Material:', 'material_tipo'), ('Subtipo:', 'subtipo_material'),
            ('Origen Factura:', 'origen_factura'), ('Fecha Entrada:', 'fecha_entrada_almacen'),
            ('Estado:', 'status'), ('Espesor:', 'espesor'),
            ('Ancho (mm):', 'ancho'),
            ('Largo/Cant. Inicial:', 'largo_inicial' if tabla_item == 'StockMateriasPrimas' else 'cantidad_inicial'),
            ('Largo/Cant. Actual:', 'largo_actual' if tabla_item == 'StockMateriasPrimas' else 'cantidad_actual'),
            ('Unidad:', 'unidad_medida'), ('Color:', 'color'),
            ('Ubicación:', 'ubicacion'), ('Notas:', 'notas'),
        ]
        for label_text, key_or_func in campos_a_mostrar:
            value = None; key = None
            if callable(key_or_func): value = key_or_func(item_details)
            elif isinstance(key_or_func, str): key = key_or_func; value = item_details.get(key)
            if key and (value is not None and value != '') or key in ['descripcion', 'notas'] or callable(key_or_func):
                display_value = value
                if key == 'fecha_entrada_almacen' and isinstance(value, str):
                    try: display_value = datetime.strptime(value.split()[0], '%Y-%m-%d').strftime('%d-%m-%Y')
                    except: pass
                elif key in ['ancho', 'largo_inicial', 'largo_actual', 'cantidad_inicial', 'cantidad_actual']:
                    try: display_value = f"{float(value):.2f}" if value is not None else "-"
                    except: pass
                ttk.Label(details_frame, text=label_text, anchor="e").grid(row=row_idx, column=0, sticky="ew", padx=(0,5), pady=1)
                value_label = ttk.Label(details_frame, text=str(display_value if display_value is not None else "-"), anchor="w", wraplength=450)
                value_label.grid(row=row_idx, column=1, sticky="ew", pady=1)
                row_idx += 1

        ttk.Separator(details_frame, orient='horizontal').grid(row=row_idx, column=0, columnspan=2, sticky='ew', pady=10); row_idx += 1
        ttk.Label(details_frame, text="--- Coste y Precios Venta ---", font=("Arial", 12, "bold")).grid(row=row_idx, column=0, columnspan=2, pady=(0,5)); row_idx += 1
        coste_final_str = f"{coste_final:.4f} € / {item_details.get('unidad_medida', 'ud')}" if isinstance(coste_final, (int, float)) else "N/A"
        ttk.Label(details_frame, text="Coste Unitario Final:", anchor="e").grid(row=row_idx, column=0, sticky="ew", padx=(0,5), pady=1)
        ttk.Label(details_frame, text=coste_final_str, anchor="w", font=("Arial", 10, "bold")).grid(row=row_idx, column=1, sticky="ew", pady=1); row_idx += 1
        for nombre_precio, precio_str in precios_venta.items():
            ttk.Label(details_frame, text=f"Precio Venta ({nombre_precio}):", anchor="e").grid(row=row_idx, column=0, sticky="ew", padx=(0,5), pady=1)
            ttk.Label(details_frame, text=f"{precio_str} / {item_details.get('unidad_medida', 'ud')}", anchor="w", foreground="blue", font=("Arial", 10)).grid(row=row_idx, column=1, sticky="ew", pady=1)
            row_idx += 1

        ttk.Separator(details_frame, orient='horizontal').grid(row=row_idx, column=0, columnspan=2, sticky='ew', pady=10); row_idx += 1
        ttk.Button(details_frame, text="Cerrar", command=details_win.destroy).grid(row=row_idx, column=0, columnspan=2, pady=5)
        details_win.focus_set()


    def _marcar_item_empezado(self):
        """
        Marca como EMPEZADA el item de stock seleccionado.
        CORREGIDO para manejar el iid único ("MP_X", "CP_Y").
        """
        if not hasattr(self, 'tree_stock') or not self.tree_stock.winfo_exists(): return
        if not callable(marcar_item_empezado):
            messagebox.showerror("Error Backend", "Función marcar_item_empezado no disponible.")
            return

        selected_iids = self.tree_stock.selection()
        if not selected_iids:
            messagebox.showinfo("Marcar Empezada", "Seleccione un item para marcar como 'Empezada'.")
            return

        selected_unique_iid = selected_iids[0]

        # --- Buscar la información original ---
        if not hasattr(self, 'stock_item_tablas'):
            messagebox.showerror("Error Interno", "'stock_item_tablas' no existe.")
            return
        item_info = self.stock_item_tablas.get(selected_unique_iid)
        if not item_info or 'tabla' not in item_info or 'db_id' not in item_info:
            messagebox.showerror("Error", f"No se encontró info para item {selected_unique_iid}. Refresque.")
            return
        tabla_item = item_info['tabla']
        db_item_id = item_info['db_id']
        print(f"DEBUG: Marcar Empezada para iid={selected_unique_iid} -> tabla={tabla_item}, db_id={db_item_id}")

        # Obtener referencia para mensaje
        try: ref_stock = self.tree_stock.item(selected_unique_iid, 'values')[1]
        except: ref_stock = db_item_id

        if messagebox.askyesno("Confirmar Estado", f"¿Seguro que quieres marcar como 'EMPEZADA' el item ID {db_item_id} (Ref: {ref_stock})?"):
            try:
                # Llamar al backend con el ID numérico y la tabla correcta
                exito = marcar_item_empezado(db_item_id, tabla_item)
                if exito:
                    messagebox.showinfo("Éxito", f"Item {db_item_id} marcado como EMPEZADA.")
                    current_filters = self._get_current_stock_filters()
                    self._cargar_y_mostrar_stock(filtros=current_filters or {'status': 'DISPONIBLE'}) # Recargar
                else:
                    messagebox.showerror("Error", f"No se pudo marcar como 'Empezada' el item {db_item_id}.")
            except Exception as e:
                messagebox.showerror("Error Backend", f"Error al intentar marcar como 'Empezada': {e}")
                print(f"Error llamando a marcar_item_empezado para ID {db_item_id}: {e}")
                traceback.print_exc()


    def _dar_baja_stock_item(self):
        """
        Marca como AGOTADO el item de stock seleccionado.
        CORREGIDO para manejar el iid único ("MP_X", "CP_Y").
        """
        if not hasattr(self, 'tree_stock') or not self.tree_stock.winfo_exists(): return
        if not callable(marcar_item_agotado):
            messagebox.showerror("Error Backend", "Función marcar_item_agotado no disponible.")
            return

        selected_iids = self.tree_stock.selection()
        if not selected_iids:
            messagebox.showinfo("Dar de Baja", "Seleccione un item del stock para dar de baja.")
            return

        selected_unique_iid = selected_iids[0]

        # --- Buscar la información original ---
        if not hasattr(self, 'stock_item_tablas'):
            messagebox.showerror("Error Interno", "'stock_item_tablas' no existe.")
            return
        item_info = self.stock_item_tablas.get(selected_unique_iid)
        if not item_info or 'tabla' not in item_info or 'db_id' not in item_info:
            messagebox.showerror("Error", f"No se encontró info para item {selected_unique_iid}. Refresque.")
            return
        tabla_item = item_info['tabla']
        db_item_id = item_info['db_id']
        print(f"DEBUG: Dar Baja para iid={selected_unique_iid} -> tabla={tabla_item}, db_id={db_item_id}")

        # Obtener referencia para mensaje
        try: ref_stock = self.tree_stock.item(selected_unique_iid, 'values')[1]
        except: ref_stock = db_item_id

        if messagebox.askyesno("Confirmar Baja", f"¿Seguro que quieres marcar como 'AGOTADO' el item ID {db_item_id} (Ref: {ref_stock})?"):
            try:
                # Llamar al backend con el ID numérico y la tabla correcta
                # !!! CORRECCIÓN IMPORTANTE: La función backend se llama marcar_item_agotado, no el mismo nombre que esta función !!!
                exito = marcar_item_agotado(db_item_id, tabla_item)
                if exito:
                    messagebox.showinfo("Éxito", f"Item {db_item_id} marcado como AGOTADO.")
                    current_filters = self._get_current_stock_filters()
                    # Recargar mostrando también los agotados o solo disponibles? Decidimos recargar con filtro default.
                    self._cargar_y_mostrar_stock(filtros=current_filters or {'status': 'DISPONIBLE'})
                else:
                    messagebox.showerror("Error", f"No se pudo dar de baja el item {db_item_id}.")
            except Exception as e:
                messagebox.showerror("Error Backend", f"Error al intentar dar de baja el item: {e}")
                print(f"Error llamando a marcar_item_agotado para ID {db_item_id}: {e}")
                traceback.print_exc()

    def _imprimir_listado_stock(self):
        """
        Obtiene los datos actualmente mostrados en la tabla de stock
        y los imprime en la consola con formato.
        """
        if not hasattr(self, 'tree_stock') or not self.tree_stock.winfo_exists():
            messagebox.showerror("Error", "La tabla de stock no está disponible para imprimir.")
            return

        items_en_tabla = self.tree_stock.get_children()

        if not items_en_tabla:
            messagebox.showinfo("Imprimir Stock", "La tabla de stock está vacía. No hay nada que imprimir.")
            return

        print("\n" + "="*80)
        print("=== LISTADO DE STOCK ACTUAL ===")
        print("="*80)

        # Obtener cabeceras (columnas visibles)
        column_ids = self.tree_stock['columns']
        headers = [self.tree_stock.heading(col_id)['text'] for col_id in column_ids]

        # Definir anchos aproximados para formato (ajustar según necesidad)
        # El orden debe coincidir con 'cols' en _crear_widgets_vista_almacen
        widths = {
            "ID": 5, "Ref.": 25, "Material": 15, "Origen Fact.": 15, "Fecha Entr.": 12,
            "Estado": 12, "Espesor": 15, "Ancho": 8, "Largo": 12, "Coste U.": 12, "Ubicación": 20
        }
        # Crear línea de formato y cabecera formateada
        format_string = " | ".join([f"{{:<{widths.get(h, 15)}}}" for h in headers]) # Default 15
        header_line = format_string.format(*headers)
        separator_line = "-+-".join(["-" * widths.get(h, 15) for h in headers])

        print(header_line)
        print(separator_line)

        # Imprimir cada fila
        for item_iid in items_en_tabla:
            valores = self.tree_stock.item(item_iid, 'values')
            try:
                # Asegurarse que hay suficientes valores para las cabeceras
                valores_formato = list(valores)
                while len(valores_formato) < len(headers):
                    valores_formato.append('') # Añadir strings vacíos si faltan datos

                # Truncar valores largos si exceden el ancho definido (opcional)
                valores_truncados = []
                for i, val in enumerate(valores_formato):
                    header_name = headers[i]
                    max_width = widths.get(header_name, 15)
                    str_val = str(val)
                    if len(str_val) > max_width:
                        valores_truncados.append(str_val[:max_width-1] + "…")
                    else:
                        valores_truncados.append(str_val)

                print(format_string.format(*valores_truncados))
            except Exception as e:
                print(f"Error formateando fila {valores}: {e}") # Imprimir error si falla el formato

        print("="*80)
        print(f"=== Fin del Listado ({len(items_en_tabla)} items) ===")
        print("="*80 + "\n")
        messagebox.showinfo("Imprimir Stock", f"Listado de stock ({len(items_en_tabla)} items) impreso en la consola.")
    # Dentro de la clase Interfaz en interfaz.py

    def _cargar_margenes(self):
        """Carga los márgenes de venta desde la base de datos."""
        print("Cargando márgenes desde la base de datos...") # Mensaje de log
        try:
            # Llama a la nueva función que consulta la base de datos
            # (Asegúrate de que la importación al principio del archivo está hecha)
            margenes = obtener_margenes_configuracion()

            if not margenes:
                # La función obtener_margenes_configuracion ya imprime advertencias
                messagebox.showwarning("Advertencia Márgenes", "No se encontraron márgenes de venta en la configuración de la base de datos.\n\nPor favor, asegúrate de haberlos añadido a la tabla 'Configuracion' en 'almacen.db' con claves como 'margen_Cliente Final'.\n\nLos precios de venta no se calcularán.")
                return {} # Devuelve diccionario vacío

            print(f"Márgenes cargados desde DB: {margenes}") # Log
            return margenes # Devuelve el diccionario de márgenes

        except NameError:
            # Este error ocurriría si la importación falló y la función dummy no se definió bien
            messagebox.showerror("Error Crítico", "La función 'obtener_margenes_configuracion' no está definida. Revisa las importaciones.")
            return {}
        except Exception as e:
            messagebox.showerror("Error Configuración", f"Error inesperado al cargar márgenes desde la base de datos: {e}")
            traceback.print_exc() # Imprime el traceback detallado en la consola
            return {} # Devuelve diccionario vacío en caso de error inesperado

    # ... (resto de tus métodos en la clase Interfaz) ...
    
    def _mostrar_vista_tarifa(self):
        """Limpia el frame principal y crea la vista para la tarifa de venta."""
        self._limpiar_main_content()
        print("Mostrando vista para Tarifa de Venta.")
        # Crear la estructura visual de la vista
        self._crear_widgets_vista_tarifa(self.main_content_frame)
        # Llamar a la función para cargar y mostrar los datos (la implementaremos después)
        self._cargar_y_mostrar_tarifa()

        # Añadir ESTA FUNCIÓN a la clase Interfaz en interfaz.py

    def _crear_widgets_vista_tarifa(self, parent_frame):
        """Crea los widgets para la vista de la tarifa de venta."""
        view_frame = ttk.Frame(parent_frame, padding="10")
        view_frame.pack(expand=True, fill="both")
        # Configurar grid para que la tabla se expanda
        view_frame.grid_rowconfigure(1, weight=1)
        view_frame.grid_columnconfigure(0, weight=1)

        # --- Título ---
        ttk.Label(view_frame, text="Tarifa de Venta (Basada en Stock Disponible)", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky='w')

        # --- Frame para Treeview y Scrollbars ---
        tree_frame = ttk.Frame(view_frame)
        tree_frame.grid(row=1, column=0, columnspan=2, sticky='nsew', pady=5)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # --- Treeview para mostrar la tarifa ---
        # Definimos las columnas que mostraremos
        cols = ("Material", "Espesor", "Coste Base", "Precio CF", "Precio Fab", "Precio Metr")
        self.tree_tarifa = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse") # selectmode='none' para que no se puedan seleccionar filas

        # Configurar cabeceras y columnas (ajusta anchos/anclajes)
        # Nota: La unidad (€/m, €/ud) se añadirá al valor al poblar
        self.tree_tarifa.heading("Material", text="Material/Subtipo"); self.tree_tarifa.column("Material", width=150, anchor=tk.W)
        self.tree_tarifa.heading("Espesor", text="Espesor"); self.tree_tarifa.column("Espesor", width=120, anchor=tk.W)
        self.tree_tarifa.heading("Coste Base", text="Coste Base"); self.tree_tarifa.column("Coste Base", width=110, anchor=tk.E)
        self.tree_tarifa.heading("Precio CF", text="P. Cliente Final"); self.tree_tarifa.column("Precio CF", width=120, anchor=tk.E)
        self.tree_tarifa.heading("Precio Fab", text="P. Fabricante"); self.tree_tarifa.column("Precio Fab", width=120, anchor=tk.E)
        self.tree_tarifa.heading("Precio Metr", text="P. Metrajes"); self.tree_tarifa.column("Precio Metr", width=110, anchor=tk.E)

        # --- Scrollbars ---
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_tarifa.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree_tarifa.xview)
        self.tree_tarifa.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # --- Vincular Doble Clic ---
        self.tree_tarifa.bind("<Double-1>", self._mostrar_detalles_stock_tarifa)

        # --- Posicionar Treeview y Scrollbars ---
        self.tree_tarifa.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        # --- Frame para botones ---
        action_frame = ttk.Frame(view_frame)
        action_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=(10, 0))
        action_frame.columnconfigure(0, weight=1) # Para centrar el botón de refrescar

        # --- Botón Refrescar ---
        # Llama a la función que cargará/recargará los datos (la crearemos después)
        ttk.Button(action_frame, text="Refrescar Tarifa", command=self._cargar_y_mostrar_tarifa).pack(pady=5)

        # --- Label de estado ---
        self.status_label_tarifa = ttk.Label(view_frame, text="Generando tarifa...")
        self.status_label_tarifa.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(5,0))

                # Añadir ESTA FUNCIÓN a la clase Interfaz en interfaz.py
    # (Asegúrate de tener imports: json, traceback, tk, ttk, messagebox, datetime
    #  y desde gestion_almacen: obtener_datos_para_tarifa)
  

   


    def _cargar_y_mostrar_tarifa(self):
        """
        Obtiene datos de stock, agrupa por material/subtipo/espesor, encuentra
        el COSTE MÁXIMO, calcula precios de venta, muestra la tarifa agregada
        y guarda los detalles de los items individuales para el doble clic.
        """
        tree_widget = getattr(self, 'tree_tarifa', None)
        status_label = getattr(self, 'status_label_tarifa', None)
        # Diccionario para mapear IID de tarifa a lista de items detallados
        self.tarifa_details_map = {} # Inicializar/limpiar mapa de detalles

        if not tree_widget or not tree_widget.winfo_exists(): return
        if not callable(obtener_datos_para_tarifa): return

        if status_label and status_label.winfo_exists():
            status_label.config(text="Obteniendo datos y calculando tarifa...", foreground="blue")
            self.root.update_idletasks()

        for i in tree_widget.get_children(): tree_widget.delete(i)

        try:
            stock_data = obtener_datos_para_tarifa()
            margenes = self._cargar_margenes()
            if not stock_data or not margenes:
                msg = "No hay stock disponible" if not stock_data else "Error cargando márgenes"
                if status_label and status_label.winfo_exists(): status_label.config(text=msg, foreground="orange")
                return

            items_agrupados = {} # Clave: (mat, sub, esp), Valor: {'max_cost': X, 'unit': Y, 'esp_disp': Z, 'items': []}
            print("Agrupando stock, buscando coste máximo y guardando detalles...")

            for item in stock_data:
                coste_base = item.get('coste_unitario_final')
                mat_tipo = item.get('material_tipo')
                subtipo = item.get('subtipo_material', '') or ''
                espesor = item.get('espesor', '') or ''
                unidad = item.get('unidad_medida', 'ud')
                db_id = item.get('id')
                ref = item.get('referencia_stock') or item.get('componente_ref', 'N/A')
                status_item = item.get('status', 'N/A')
                largo_o_cant = item.get('largo_actual') if 'largo_actual' in item else item.get('cantidad_actual')

                if not isinstance(coste_base, (int, float)) or coste_base < 0 or not mat_tipo or db_id is None:
                    continue # Saltar items inválidos

                # Determinar tabla (necesario si obtenemos detalles después, aunque aquí guardamos directo)
                tabla_origen = 'StockMateriasPrimas' if 'material_tipo' in item else 'StockComponentes'

                group_key = (mat_tipo.upper(), subtipo.upper(), str(espesor))

                # Preparar detalles del item individual
                item_detail_data = {
                    'db_id': db_id,
                    'tabla': tabla_origen,
                    'ref': ref,
                    'largo_actual': largo_o_cant,
                    'coste_unitario_final': coste_base,
                    'status': status_item,
                    'unidad': unidad
                    # Añadir más campos si se necesitan en el popup
                }

                if group_key not in items_agrupados:
                    items_agrupados[group_key] = {
                        'max_cost': coste_base,
                        'unit': unidad,
                        'espesor_display': str(espesor),
                        'items': [item_detail_data] # Iniciar lista de items
                    }
                else:
                    if coste_base > items_agrupados[group_key]['max_cost']:
                        items_agrupados[group_key]['max_cost'] = coste_base
                    items_agrupados[group_key]['items'].append(item_detail_data) # Añadir detalles

            print(f"Se encontraron {len(items_agrupados)} combinaciones únicas.")

            # --- Calcular Precios de Venta y Poblar Treeview ---
            items_mostrados = 0
            if not items_agrupados:
                if status_label and status_label.winfo_exists(): status_label.config(text="No se encontraron items válidos.", foreground="orange")
                return

            # Ordenar (opcional)
            try:
                def sort_key_func(item_tuple):
                    key, data = item_tuple; mat, sub, esp_str = key
                    try: import re; num_match = re.match(r"([\d\.]+)", esp_str); esp_num = float(num_match.group(1)) if num_match else float('inf')
                    except: esp_num = float('inf')
                    return (mat, sub, esp_num)
                sorted_items = sorted(items_agrupados.items(), key=sort_key_func)
            except Exception as e_sort: sorted_items = items_agrupados.items(); print(f"Warn sort: {e_sort}")

            for group_key, data in sorted_items:
                mat_tipo_key, subtipo_key, _ = group_key
                max_cost = data['max_cost']
                unidad = data['unit']
                espesor_display = data['espesor_display']
                items_del_grupo = data['items'] # Lista de detalles

                precios_calc = {}
                for nombre_margen, porcentaje in margenes.items():
                    try: precios_calc[nombre_margen] = max_cost * (1 + (float(porcentaje) / 100.0))
                    except: precios_calc[nombre_margen] = None

                material_display = mat_tipo_key
                if mat_tipo_key == 'GOMA' and subtipo_key and subtipo_key != 'NORMAL': material_display = f"GOMA ({subtipo_key})"
                elif mat_tipo_key != 'GOMA' and subtipo_key: material_display = f"{mat_tipo_key} ({subtipo_key})"

                coste_base_str = f"{max_cost:.4f} €/{unidad}"
                precio_cf_str = f"{precios_calc.get('Cliente Final', 0):.4f} €/{unidad}" if precios_calc.get('Cliente Final') is not None else "Error"
                precio_fab_str = f"{precios_calc.get('Fabricante', 0):.4f} €/{unidad}" if precios_calc.get('Fabricante') is not None else "Error"
                precio_metr_str = f"{precios_calc.get('Metrajes', 0):.4f} €/{unidad}" if precios_calc.get('Metrajes') is not None else "Error"

                valores_fila = (material_display, espesor_display, coste_base_str, precio_cf_str, precio_fab_str, precio_metr_str)

                # Crear IID único para la fila de tarifa
                iid_tarifa = f"TAR_{'_'.join(map(str, group_key)).replace(' ', '_')}" # Reemplazar espacios por si acaso

                # Guardar la lista de items detallados en el mapa usando el iid_tarifa
                self.tarifa_details_map[iid_tarifa] = items_del_grupo

                # Insertar en el treeview
                tree_widget.insert('', tk.END, iid=iid_tarifa, values=valores_fila)
                items_mostrados += 1

            # --- Actualizar Estado Final ---
            if status_label and status_label.winfo_exists():
                if items_mostrados > 0: status_label.config(text=f"Tarifa generada con {items_mostrados} líneas (coste más alto).", foreground="black")
                else: status_label.config(text="No se generaron líneas para la tarifa.", foreground="orange")

        except Exception as e:
            print(f"Error al cargar o mostrar la tarifa: {e}")
            traceback.print_exc()
            messagebox.showerror("Error Tarifa", f"No se pudo generar la tarifa.\n{e}")
            if status_label and status_label.winfo_exists(): status_label.config(text="Error al generar tarifa.", foreground="red")

            # En interfaz.py, dentro de la clase Interfaz

    def _mostrar_detalles_stock_tarifa(self, event=None):
        """
        Manejador doble clic en Tarifa. Muestra ventana emergente con los
        items de stock individuales correspondientes a la línea seleccionada.
        """
        tree_widget = getattr(self, 'tree_tarifa', None)
        details_map = getattr(self, 'tarifa_details_map', None)

        if not tree_widget or not tree_widget.winfo_exists(): return # No hacer nada si la tabla no existe
        if details_map is None: # El mapa debería existir si la tarifa se cargó
            messagebox.showerror("Error Interno", "Mapa de detalles de tarifa no encontrado.")
            return

        selected_iids = tree_widget.selection()
        if not selected_iids: return # No hacer nada si no hay selección

        selected_iid = selected_iids[0] # Este es el IID tipo "TAR_MAT_SUB_ESP"

        # Obtener la lista de items detallados del mapa
        items_del_grupo = details_map.get(selected_iid)

        if not items_del_grupo:
            messagebox.showwarning("Sin Detalles", f"No se encontraron detalles para la línea seleccionada ({selected_iid}).")
            return

        # Cargar márgenes para calcular precios individuales
        margenes = self._cargar_margenes()
        if not margenes: return # Error ya mostrado

        # --- Crear ventana emergente ---
        popup_win = tk.Toplevel(self.root)
        # Obtener descripción de la fila para el título
        try:
            desc_fila = tree_widget.item(selected_iid, 'values')[0] # Material/Subtipo
            esp_fila = tree_widget.item(selected_iid, 'values')[1] # Espesor
            popup_win.title(f"Detalle Stock para: {desc_fila} - {esp_fila}")
        except:
            popup_win.title("Detalle Stock Tarifa") # Título genérico si falla

        popup_win.geometry("800x400") # Tamaño inicial
        popup_win.minsize(600, 300)
        popup_win.transient(self.root); popup_win.grab_set()

        popup_frame = ttk.Frame(popup_win, padding="10")
        popup_frame.pack(expand=True, fill="both")
        popup_frame.rowconfigure(0, weight=1); popup_frame.columnconfigure(0, weight=1)

        # --- Treeview para detalles ---
        cols_detalles = ("ID", "Ref.", "Estado", "Largo/Cant", "Coste Unit.", "P. CF", "P. Fab", "P. Metr")
        tree_detalles = ttk.Treeview(popup_frame, columns=cols_detalles, show="headings", selectmode="none")

        # Configurar columnas
        tree_detalles.heading("ID", text="ID"); tree_detalles.column("ID", width=40, anchor="c")
        tree_detalles.heading("Ref.", text="Referencia"); tree_detalles.column("Ref.", width=150)
        tree_detalles.heading("Estado", text="Estado"); tree_detalles.column("Estado", width=80, anchor="c")
        tree_detalles.heading("Largo/Cant", text="Largo/Cant"); tree_detalles.column("Largo/Cant", width=80, anchor="e")
        tree_detalles.heading("Coste Unit.", text="Coste"); tree_detalles.column("Coste Unit.", width=90, anchor="e")
        tree_detalles.heading("P. CF", text="P. Cliente F."); tree_detalles.column("P. CF", width=100, anchor="e")
        tree_detalles.heading("P. Fab", text="P. Fabricante"); tree_detalles.column("P. Fab", width=100, anchor="e")
        tree_detalles.heading("P. Metr", text="P. Metrajes"); tree_detalles.column("P. Metr", width=100, anchor="e")

        # Scrollbar
        v_scroll = ttk.Scrollbar(popup_frame, orient="vertical", command=tree_detalles.yview)
        tree_detalles.configure(yscrollcommand=v_scroll.set)
        tree_detalles.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")

        # --- Poblar tabla de detalles ---
        for item_data in items_del_grupo:
            db_id = item_data.get('db_id', 'N/A')
            ref = item_data.get('ref', 'N/A')
            status = item_data.get('status', 'N/A')
            largo_cant = item_data.get('largo_actual', '-')
            coste_unit = item_data.get('coste_unitario_final')
            unidad = item_data.get('unidad', 'ud')

            largo_cant_str = f"{largo_cant:.2f}" if isinstance(largo_cant, (int, float)) else str(largo_cant)
            coste_unit_str = f"{coste_unit:.4f} €/{unidad}" if isinstance(coste_unit, (int, float)) else "N/A"

            # Calcular precios de venta para ESTE item
            precio_cf_str, precio_fab_str, precio_metr_str = "N/A", "N/A", "N/A"
            if isinstance(coste_unit, (int, float)) and coste_unit >= 0:
                try:
                    cf = coste_unit * (1 + (margenes.get('Cliente Final', 0) / 100.0))
                    fab = coste_unit * (1 + (margenes.get('Fabricante', 0) / 100.0))
                    metr = coste_unit * (1 + (margenes.get('Metrajes', 0) / 100.0))
                    precio_cf_str = f"{cf:.4f} €"
                    precio_fab_str = f"{fab:.4f} €"
                    precio_metr_str = f"{metr:.4f} €"
                except Exception as e_calc:
                    print(f"Error calculando precio para ID {db_id}: {e_calc}")
                    precio_cf_str, precio_fab_str, precio_metr_str = "Error", "Error", "Error"

            valores_detalle = (
                db_id, ref, status, largo_cant_str, coste_unit_str,
                precio_cf_str, precio_fab_str, precio_metr_str
            )
            tree_detalles.insert('', tk.END, values=valores_detalle)

        # --- Botón Cerrar ---
        ttk.Button(popup_frame, text="Cerrar", command=popup_win.destroy).grid(row=1, column=0, columnspan=2, pady=10)

        popup_win.focus_set()
    
    # ===================================================================
    # ### FIN FUNCIONALIDAD VISTA ALMACÉN (STOCK) ###
    # ===================================================================