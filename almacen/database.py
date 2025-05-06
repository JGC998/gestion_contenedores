# almacen/database.py
# ACTUALIZADO: Eliminadas tablas de Presupuestos/Productos Terminados.
#              Mantiene tablas de Pedidos, Gastos, Stock y Configuración.

import sqlite3
import os
import datetime
import traceback # Para imprimir errores detallados si es necesario

# --- Configuración ---
DB_FILENAME = 'almacen.db'
# Asegura que la ruta se construye correctamente relativa a este archivo
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), DB_FILENAME)

# --- Funciones Básicas ---

def conectar_db():
    """Establece conexión con la base de datos SQLite."""
    try:
        conn = sqlite3.connect(DB_PATH)
        # conn.execute("PRAGMA foreign_keys = ON;") # Descomentar si usas FOREIGN KEYs
        print(f"Conexión a DB establecida: {DB_PATH}")
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos SQLite en {DB_PATH}: {e}")
        return None

def inicializar_database():
    """
    Crea las tablas esenciales (Pedidos, Gastos, Stock, Config) si no existen.
    Las tablas de Presupuestos/Productos han sido eliminadas.
    """
    conn = None
    try:
        conn = conectar_db()
        if conn is None:
            print("Error: No se pudo conectar a la DB para inicializar.")
            return

        cursor = conn.cursor()
        print("Inicializando/Verificando tablas de la base de datos (Esquema Simplificado)...")

        # --- Tabla: PedidosProveedores --- (Se mantiene para trazabilidad)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS PedidosProveedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_factura TEXT NOT NULL UNIQUE,
            proveedor TEXT,
            fecha_pedido TEXT,
            fecha_llegada TEXT,
            origen_tipo TEXT NOT NULL CHECK(origen_tipo IN ('CONTENEDOR', 'NACIONAL')),
            observaciones TEXT,
            valor_conversion REAL -- NULL para pedidos nacionales
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pp_numero_factura ON PedidosProveedores (numero_factura);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pp_proveedor ON PedidosProveedores (proveedor);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pp_fecha_llegada ON PedidosProveedores (fecha_llegada);")
        print("  - Tabla PedidosProveedores verificada/creada.")

        # --- Tabla: LineasPedido --- (Se mantiene por ahora, utilidad a evaluar)
        # Podría eliminarse si no se guarda detalle original de factura
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS LineasPedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            descripcion_original TEXT,
            cantidad_original REAL NOT NULL,
            unidad_original TEXT NOT NULL,
            precio_unitario_original REAL NOT NULL,
            moneda_original TEXT CHECK(moneda_original IN ('USD', 'EUR'))
            -- FOREIGN KEY(pedido_id) REFERENCES PedidosProveedores(id) ON DELETE CASCADE
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_lp_pedido_id ON LineasPedido (pedido_id);")
        print("  - Tabla LineasPedido verificada/creada.")

        # --- Tabla: GastosPedido --- (Se mantiene para asociar gastos)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS GastosPedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            tipo_gasto TEXT CHECK(tipo_gasto IN ('SUPLIDOS', 'EXENTO', 'SUJETO', 'NACIONAL', 'OTRO')),
            descripcion TEXT NOT NULL,
            coste_eur REAL NOT NULL
            -- FOREIGN KEY(pedido_id) REFERENCES PedidosProveedores(id) ON DELETE CASCADE
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_gp_pedido_id ON GastosPedido (pedido_id);")
        print("  - Tabla GastosPedido verificada/creada.")

        # --- Tabla: StockMateriasPrimas --- (Esencial)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS StockMateriasPrimas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER, -- Enlace al pedido/contenedor de origen
            material_tipo TEXT NOT NULL CHECK(material_tipo IN ('GOMA', 'PVC', 'FIELTRO')),
            subtipo_material TEXT,
            referencia_stock TEXT UNIQUE,
            fecha_entrada_almacen TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'DISPONIBLE' CHECK(status IN ('DISPONIBLE', 'AGOTADO', 'EMPEZADA', 'DESCATALOGADO')),
            espesor TEXT,
            ancho REAL,
            largo_inicial REAL,
            largo_actual REAL,
            unidad_medida TEXT NOT NULL DEFAULT 'm',
            coste_unitario_final REAL NOT NULL, -- Coste por unidad_medida (ej: €/m)
            color TEXT,
            ubicacion TEXT,
            notas TEXT,
            origen_factura TEXT -- Redundante si pedido_id está, pero útil
            -- FOREIGN KEY(pedido_id) REFERENCES PedidosProveedores(id) ON DELETE SET NULL
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_smp_referencia_stock ON StockMateriasPrimas (referencia_stock);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_smp_material_tipo ON StockMateriasPrimas (material_tipo, subtipo_material);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_smp_status ON StockMateriasPrimas (status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_smp_pedido_id ON StockMateriasPrimas (pedido_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_smp_origen_factura ON StockMateriasPrimas (origen_factura);")
        print("  - Tabla StockMateriasPrimas verificada/creada.")

        # --- Tabla: StockComponentes --- (Esencial si se usan componentes)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS StockComponentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            componente_ref TEXT NOT NULL UNIQUE,
            descripcion TEXT,
            pedido_id INTEGER, -- Enlace al pedido/contenedor de origen (si aplica)
            cantidad_inicial REAL NOT NULL,
            cantidad_actual REAL NOT NULL,
            unidad_medida TEXT NOT NULL DEFAULT 'ud',
            coste_unitario_final REAL NOT NULL,
            fecha_entrada_almacen TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'DISPONIBLE' CHECK(status IN ('DISPONIBLE', 'AGOTADO', 'RESERVADO', 'DESCATALOGADO')),
            ubicacion TEXT,
            notas TEXT,
            origen_factura TEXT -- Si viene de una factura específica
            -- FOREIGN KEY(pedido_id) REFERENCES PedidosProveedores(id) ON DELETE SET NULL
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sc_componente_ref ON StockComponentes (componente_ref);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sc_status ON StockComponentes (status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sc_origen_factura ON StockComponentes (origen_factura);")
        print("  - Tabla StockComponentes verificada/creada.")

        # --- Tabla Configuracion --- (Esencial para márgenes, etc.)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Configuracion (
            clave TEXT PRIMARY KEY,  -- Clave única (ej: 'margen_Cliente Final')
            valor TEXT               -- Valor del ajuste
        );
        """)
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_conf_clave ON Configuracion (clave);")
        print("  - Tabla Configuracion verificada/creada.")

        # --- Tablas ELIMINADAS (Presupuestos/Productos) ---
        # cursor.execute("DROP TABLE IF EXISTS ProductosTerminados;") # Opcional: Borrar si existen
        # cursor.execute("DROP TABLE IF EXISTS RecetasProducto;")
        # cursor.execute("DROP TABLE IF EXISTS Presupuestos;")
        # cursor.execute("DROP TABLE IF EXISTS LineasPresupuesto;")
        print("  - Tablas de Presupuestos/Productos Terminados OMITIDAS.")

        conn.commit()
        print("Base de datos (esquema simplificado) inicializada/actualizada con éxito.")

    except sqlite3.Error as e:
        print(f"Error de SQLite durante la inicialización de la base de datos: {e}")
        if conn: conn.rollback()
    except Exception as e_gen:
         print(f"Error inesperado inicializando la base de datos: {e_gen}")
         traceback.print_exc()
         if conn: conn.rollback()
    finally:
        if conn:
            conn.close()
            print("Conexión a DB cerrada después de inicializar.")

# --- Funciones de Manipulación de Datos ---
# (Mantener las funciones relevantes: insertar_item_stock, actualizar_status_item,
#  select_*, obtener_margenes_configuracion)

def insertar_item_stock(cursor, datos_item):
    """
    Inserta un nuevo item en la tabla de stock apropiada (Materias Primas o Componentes).
    Requiere que 'datos_item' sea un diccionario con las claves correspondientes a las columnas.
    Devuelve el ID del nuevo registro insertado o None si falla.
    """
    columnas = []
    tabla = None

    # Determinar la tabla y las columnas basadas en los datos proporcionados
    if datos_item.get('material_tipo') in ['GOMA', 'PVC', 'FIELTRO']:
        tabla = 'StockMateriasPrimas'
        columnas = [
            'pedido_id', 'material_tipo', 'subtipo_material', 'referencia_stock',
            'fecha_entrada_almacen', 'status', 'espesor', 'ancho', 'largo_inicial',
            'largo_actual', 'unidad_medida', 'coste_unitario_final', 'color',
            'ubicacion', 'notas', 'origen_factura'
        ]
    elif 'componente_ref' in datos_item:
        tabla = 'StockComponentes'
        columnas = [
            'componente_ref', 'descripcion', 'pedido_id', 'cantidad_inicial',
            'cantidad_actual', 'unidad_medida', 'coste_unitario_final',
            'fecha_entrada_almacen', 'status', 'ubicacion', 'notas', 'origen_factura'
        ]
    else:
        print(f"Error: Tipo de item desconocido o datos insuficientes para determinar tabla de stock. Datos: {datos_item}")
        return None

    # Verificar que pedido_id esté presente (es crucial para la trazabilidad)
    if 'pedido_id' not in datos_item or datos_item.get('pedido_id') is None:
        ref_o_comp = datos_item.get('referencia_stock') or datos_item.get('componente_ref', 'N/A')
        print(f"Advertencia: Insertando item en {tabla} sin 'pedido_id' asociado. Ref/Comp: {ref_o_comp}")

    placeholders = ', '.join('?' * len(columnas))
    sql = f"INSERT INTO {tabla} ({', '.join(columnas)}) VALUES ({placeholders})"
    valores = tuple(datos_item.get(col) for col in columnas)

    try:
        cursor.execute(sql, valores)
        print(f"  [DB Insert OK] Item insertado en {tabla} (ID: {cursor.lastrowid}) Ref/Comp: {datos_item.get('referencia_stock') or datos_item.get('componente_ref')}")
        return cursor.lastrowid
    except sqlite3.IntegrityError as e:
        ref_o_comp = datos_item.get('referencia_stock') or datos_item.get('componente_ref', 'N/A')
        print(f"Error de Integridad al insertar en {tabla} (Ref/Comp: {ref_o_comp}): {e}")
        print(f"  Puede que la referencia '{ref_o_comp}' ya exista (UNIQUE constraint).")
        return None
    except sqlite3.Error as e:
        print(f"Error SQLite al insertar item en {tabla}: {e}")
        return None
    except Exception as e_gen:
         print(f"Error inesperado al insertar item en {tabla}: {e_gen}")
         traceback.print_exc()
         return None

def actualizar_status_item(conn, id_stock: int, tabla_stock: str, nuevo_status: str):
    """Actualiza el estado (status) de un item específico en la tabla de stock dada."""
    estados_validos = ['DISPONIBLE', 'AGOTADO', 'EMPEZADA', 'DESCATALOGADO', 'RESERVADO']
    if nuevo_status.upper() not in estados_validos:
        print(f"Error: Estado '{nuevo_status}' no válido para actualizar.")
        return False
    if not isinstance(id_stock, int) or id_stock <= 0:
        print(f"Error: ID de stock inválido ({id_stock}) para actualizar.")
        return False
    if tabla_stock not in ['StockMateriasPrimas', 'StockComponentes']:
        print(f"Error: Tabla de stock inválida ({tabla_stock}) para actualizar.")
        return False

    sql = f"UPDATE {tabla_stock} SET status = ? WHERE id = ?"
    cursor = None
    exito = False
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (nuevo_status.upper(), id_stock))
        if cursor.rowcount > 0:
            conn.commit()
            exito = True
            print(f"  [DB Update OK] Status actualizado a '{nuevo_status.upper()}' para ID {id_stock} en {tabla_stock}.")
        else:
            print(f"Advertencia: No se encontró item con ID {id_stock} en {tabla_stock} para actualizar status.")
            exito = False
    except sqlite3.Error as e:
        print(f"Error SQLite actualizando status en {tabla_stock} (ID:{id_stock}): {e}")
        if conn: conn.rollback()
        exito = False
    except Exception as e_gen:
        print(f"Error inesperado actualizando status: {e_gen}")
        traceback.print_exc()
        if conn: conn.rollback()
        exito = False
    return exito

def select_todo_stock(cursor, tabla_stock):
    """Selecciona todos los registros de una tabla de stock, ordenados por fecha descendente."""
    if tabla_stock not in ['StockMateriasPrimas', 'StockComponentes']:
        print(f"Error: Tabla de stock inválida '{tabla_stock}' en select_todo_stock.")
        return []
    try:
        cursor.execute(f"SELECT * FROM {tabla_stock} ORDER BY fecha_entrada_almacen DESC")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error SQLite seleccionando todo de {tabla_stock}: {e}")
        return []
    except Exception as e_gen:
        print(f"Error inesperado seleccionando todo de {tabla_stock}: {e_gen}")
        traceback.print_exc()
        return []

def select_stock_con_filtros(cursor, tabla_stock, filtros):
    """
    Selecciona registros de una tabla de stock aplicando filtros opcionales.
    'filtros' es un diccionario como {'status': 'DISPONIBLE', 'buscar': 'texto'}.
    """
    if tabla_stock not in ['StockMateriasPrimas', 'StockComponentes']:
        print(f"Error: Tabla de stock inválida '{tabla_stock}' en select_stock_con_filtros.")
        return []
    if not isinstance(filtros, dict):
        print("Advertencia: Filtros no proporcionados o no es un diccionario. Se devolverá todo.")
        filtros = {}

    base_sql = f"SELECT * FROM {tabla_stock}"
    where_clauses = []
    params = []

    filtro_columnas_directas = {
        'status': 'status', 'material_tipo': 'material_tipo',
        'subtipo_material': 'subtipo_material', 'referencia_stock': 'referencia_stock',
        'componente_ref': 'componente_ref', 'origen_factura': 'origen_factura'
    }

    for filtro_key, columna_db in filtro_columnas_directas.items():
        valor_filtro = filtros.get(filtro_key)
        if valor_filtro:
            # Validar columna existe en tabla (simplificado)
            if (tabla_stock == 'StockMateriasPrimas' and columna_db not in ['componente_ref']) or \
               (tabla_stock == 'StockComponentes' and columna_db not in ['material_tipo', 'subtipo_material', 'referencia_stock']):
                if filtro_key in ['status', 'material_tipo']: # Coincidencia exacta para estos
                    where_clauses.append(f"UPPER({columna_db}) = ?")
                    params.append(str(valor_filtro).upper())
                else: # Búsqueda parcial para otros
                    where_clauses.append(f"UPPER({columna_db}) LIKE ?")
                    params.append(f"%{str(valor_filtro).upper()}%")

    termino_busqueda = filtros.get('buscar')
    if termino_busqueda:
        termino_like = f"%{str(termino_busqueda).upper()}%"
        if tabla_stock == 'StockMateriasPrimas':
            columnas_busqueda = ["referencia_stock", "origen_factura", "subtipo_material", "espesor", "color", "ubicacion", "notas"]
        elif tabla_stock == 'StockComponentes':
            columnas_busqueda = ["componente_ref", "descripcion", "origen_factura", "ubicacion", "notas"]
        else: columnas_busqueda = []

        if columnas_busqueda:
            like_clauses = [f"UPPER({col}) LIKE ?" for col in columnas_busqueda]
            where_clauses.append(f"({' OR '.join(like_clauses)})")
            params.extend([termino_like] * len(columnas_busqueda))

    sql = base_sql
    if where_clauses: sql += " WHERE " + " AND ".join(where_clauses)
    sql += " ORDER BY fecha_entrada_almacen DESC;"

    try:
        cursor.execute(sql, tuple(params))
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error SQLite aplicando filtros en {tabla_stock}: {e}")
        return []
    except Exception as e_gen:
         print(f"Error inesperado aplicando filtros en {tabla_stock}: {e_gen}")
         traceback.print_exc()
         return []

def select_item_por_id(cursor, tabla_stock: str, item_id: int):
    """Selecciona un único item de stock por su ID numérico."""
    if tabla_stock not in ['StockMateriasPrimas', 'StockComponentes']:
        print(f"Error: Tabla de stock inválida ('{tabla_stock}') en select_item_por_id")
        return None
    if not isinstance(item_id, int) or item_id <= 0:
        print(f"Error: ID de item inválido ({item_id}). Debe ser un entero positivo.")
        return None

    sql = f"SELECT * FROM {tabla_stock} WHERE id = ?"
    try:
        cursor.execute(sql, (item_id,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Error SQLite seleccionando item por ID en {tabla_stock} (ID: {item_id}): {e}")
        return None
    except Exception as e_gen:
        print(f"Error inesperado seleccionando item por ID en {tabla_stock} (ID: {item_id}): {e_gen}")
        traceback.print_exc()
        return None

def obtener_margenes_configuracion():
    """
    Consulta la tabla Configuracion y devuelve un diccionario con los márgenes de venta.
    Busca claves que empiecen con 'margen_', extrae el nombre y convierte el valor a float.
    """
    margenes = {}
    conn = None
    print("Intentando obtener márgenes de configuración desde DB...")
    try:
        conn = conectar_db()
        if conn is None:
            print("Error: No se pudo conectar a la DB para obtener márgenes.")
            return {}

        cursor = conn.cursor()
        sql = "SELECT clave, valor FROM Configuracion WHERE LOWER(clave) LIKE 'margen_%'"
        cursor.execute(sql)
        rows = cursor.fetchall()
        print(f"  [DB Config] Filas encontradas para márgenes: {len(rows)}")

        prefijo_lower = 'margen_'
        for clave, valor_str in rows:
            if clave.lower().startswith(prefijo_lower):
                nombre_margen = clave[len(prefijo_lower):].strip()
                if nombre_margen:
                    try:
                        valor_float = float(valor_str.replace(',', '.'))
                        margenes[nombre_margen] = valor_float
                        print(f"  [DB Config] Margen cargado: '{nombre_margen}' = {valor_float}%")
                    except (ValueError, TypeError):
                        print(f"Advertencia: Valor no numérico encontrado para la clave '{clave}' en Configuracion: '{valor_str}'. Se omite.")
                    except Exception as e_conv:
                        print(f"Advertencia: Error convirtiendo valor para clave '{clave}': {e_conv}. Se omite.")
                else:
                     print(f"Advertencia: Clave de margen inválida encontrada (sin nombre después del prefijo): '{clave}'")

    except sqlite3.Error as e:
        print(f"Error de SQLite al obtener márgenes de configuración: {e}")
        margenes = {}
    except Exception as e_gen:
         print(f"Error inesperado al obtener márgenes de configuración: {e_gen}")
         traceback.print_exc()
         margenes = {}
    finally:
        if conn:
            conn.close()
            print("Conexión a DB cerrada después de obtener márgenes.")

    if not margenes:
        print("Advertencia: No se cargaron márgenes válidos desde la base de datos. Verifica la tabla 'Configuracion'.")
    return margenes

# --- Ejecución para inicializar/verificar la DB ---
if __name__ == "__main__":
    print("-" * 50)
    print(f"Ejecutando inicialización de base de datos en: {DB_PATH}")
    print("(Esquema Simplificado: Sin tablas de Presupuestos/Productos)")
    print("-" * 50)
    inicializar_database()
    print("-" * 50)
    print("Proceso de inicialización de base de datos completado.")
    print("Puedes verificar el archivo 'almacen.db'.")
    print("-" * 50)
