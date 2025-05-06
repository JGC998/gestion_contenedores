# almacen/gestion_almacen.py
# ACTUALIZADO: Eliminadas importaciones de clases específicas de contenedor/nacional
# para romper ciclo de importación.
# registrar_entrada_almacen ahora usa cursor y pedido_id.

import sqlite3
import datetime
import traceback
from typing import Union, Optional, List, Dict, Any

# --- Imports Necesarios ---
try:
    # Funciones de DB
    from .database import conectar_db, insertar_item_stock, actualizar_status_item, select_item_por_id
except ImportError:
    print("ERROR FATAL [gestion_almacen]: No se pudieron importar funciones de database.py")
    # Definir Dummies si falla
    def conectar_db(): return None
    def insertar_item_stock(cursor, datos): return False
    def actualizar_status_item(conn, id_stock, tabla, status): return False
    def select_item_por_id(cursor, tabla, id): return None

try:
    # --- SOLO IMPORTAR CLASES BASE ---
    from contenedor.contenedor import Contenedor
    from nacional.mercanciaNacional import MercanciaNacional
except ImportError as e:
    print(f"ADVERTENCIA [gestion_almacen]: Error importando clases Contenedor/MercanciaNacional BASE: {e}")
    Contenedor = MercanciaNacional = object # Dummies para las clases base

try:
    # Modelos necesarios para los items DENTRO del contenido
    from modelos import Goma, GomaNacional, PVC, PVCNacional, Fieltro, FieltroNacional #, Componente
except ImportError:
    print("Error crítico [gestion_almacen]: importando clases desde modelos.py")
    # Definir Dummies si faltan los modelos
    Goma = GomaNacional = PVC = PVCNacional = Fieltro = FieltroNacional = object
    # Componente = object

# === INICIO: registrar_entrada_almacen MODIFICADA para usar cursor ===
def registrar_entrada_almacen(cursor: sqlite3.Cursor, source_object, pedido_db_id: Optional[int]):
    """
    Registra items en StockMateriasPrimas o StockComponentes usando el CURSOR proporcionado.
    Asocia los items al pedido_db_id.
    NO abre ni cierra conexión, NO hace commit/rollback.
    """
    factura_debug = getattr(source_object, 'numero_factura', 'N/A')
    print(f"--- Iniciando registro en almacén para Factura: {factura_debug} (Pedido DB ID: {pedido_db_id}) ---")

    # Validar cursor
    if not isinstance(cursor, sqlite3.Cursor):
        print("Error: Se requiere un objeto cursor de base de datos válido.")
        raise TypeError("Cursor de base de datos inválido proporcionado a registrar_entrada_almacen.")

    # Validar pedido_db_id
    if pedido_db_id is not None and (not isinstance(pedido_db_id, int) or pedido_db_id <= 0):
        print(f"Error: ID de pedido de base de datos inválido ({pedido_db_id}).")
        raise ValueError(f"ID de pedido inválido: {pedido_db_id}")

    # Validar objeto fuente (usando clases base)
    if not isinstance(source_object, (Contenedor, MercanciaNacional)):
        print(f"Error: Objeto fuente no reconocido ({type(source_object)}). Debe ser Contenedor o MercanciaNacional.")
        raise TypeError(f"Tipo de objeto fuente no válido: {type(source_object)}")

    origen_factura = getattr(source_object, 'numero_factura', None)
    if not origen_factura:
        print("Error: No se puede registrar stock sin número de factura en el objeto fuente.")
        raise ValueError("Falta número de factura en el objeto fuente.")

    if not hasattr(source_object, 'contenido') or not source_object.contenido:
         print(f"Advertencia: {factura_debug} no tiene contenido para registrar.")
         return

    fecha_entrada = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    items_registrados_con_exito = 0
    items_intentados = 0

    print(f"  [Registro Stock] Procesando {len(source_object.contenido)} item(s) del contenido...")
    for i, item_contenido in enumerate(source_object.contenido): # Renombrado 'item' a 'item_contenido'
        items_intentados += 1
        print(f"\n  [Registro Stock] Procesando item_contenido #{i+1}, Tipo Objeto: {type(item_contenido)}")

        datos_item_stock = { # Renombrado para claridad
            'pedido_id': pedido_db_id,
            'origen_factura': origen_factura,
            'fecha_entrada_almacen': fecha_entrada,
            'status': 'DISPONIBLE',
            'ubicacion': None,
            'notas': None,
            'referencia_stock': f"STK-{origen_factura}-{type(item_contenido).__name__.replace('Nacional','').upper()[:3]}-{i+1}"
        }
        item_identificado = False
        tabla_destino = 'StockMateriasPrimas'

        # --- Identificar tipo y extraer datos del ITEM DEL CONTENIDO ---
        if isinstance(item_contenido, (Goma, GomaNacional)):
            item_identificado = True
            datos_item_stock.update({
                'material_tipo': 'GOMA',
                'subtipo_material': getattr(item_contenido, 'subtipo', 'NORMAL'),
                'espesor': getattr(item_contenido, 'espesor', None),
                'ancho': getattr(item_contenido, 'ancho', None),
                'largo_inicial': getattr(item_contenido, 'largo', None),
                'largo_actual': getattr(item_contenido, 'largo', None),
                'unidad_medida': 'm',
                'coste_unitario_final': getattr(item_contenido, 'metro_lineal_euro_mas_gastos', 0.0) or 0.0,
                'color': None
            })
        elif isinstance(item_contenido, (PVC, PVCNacional)):
            item_identificado = True
            datos_item_stock.update({
                'material_tipo': 'PVC',
                'subtipo_material': None,
                'espesor': getattr(item_contenido, 'espesor', None),
                'ancho': getattr(item_contenido, 'ancho', None),
                'largo_inicial': getattr(item_contenido, 'largo', None),
                'largo_actual': getattr(item_contenido, 'largo', None),
                'unidad_medida': 'm',
                'coste_unitario_final': getattr(item_contenido, 'metro_lineal_euro_mas_gastos', 0.0) or 0.0,
                'color': getattr(item_contenido, 'color', None)
            })
        elif isinstance(item_contenido, (Fieltro, FieltroNacional)):
            item_identificado = True
            datos_item_stock.update({
                'material_tipo': 'FIELTRO',
                'subtipo_material': None,
                'espesor': getattr(item_contenido, 'espesor', None),
                'ancho': getattr(item_contenido, 'ancho', None),
                'largo_inicial': getattr(item_contenido, 'largo', None),
                'largo_actual': getattr(item_contenido, 'largo', None),
                'unidad_medida': 'm',
                'coste_unitario_final': getattr(item_contenido, 'metro_lineal_euro_mas_gastos', 0.0) or 0.0,
                'color': None
            })
        # --- Añadir bloque para Componentes si se implementa ---
        # elif isinstance(item_contenido, Componente):
        #     # ... (lógica para componentes) ...
        else:
            print(f"Advertencia: Tipo item_contenido desconocido ({type(item_contenido)}) en {factura_debug}. Omitiendo.")
            continue

        if item_identificado:
             coste_final_item = datos_item_stock.get('coste_unitario_final')
             if coste_final_item is None or not isinstance(coste_final_item, (int, float)):
                   print(f"  ERROR CRÍTICO: Coste unitario final inválido ({coste_final_item}) para item_contenido {i+1}. NO SE INSERTA.")
                   continue

             print(f"  [Registro Stock] Intentando insertar en tabla '{tabla_destino}'...")
             insert_id = insertar_item_stock(cursor, datos_item_stock)
             if insert_id:
                 items_registrados_con_exito += 1
             else:
                 print(f"  Fallo al registrar item_contenido #{i+1} en DB.")
                 # Considerar si fallar aquí debe detener toda la transacción
                 # raise sqlite3.Error(f"Fallo al insertar item de stock para factura {factura_debug}")

    print(f"--- Registro en almacén (DB) finalizado para {factura_debug}. Items intentados: {items_intentados}. Registrados con éxito: {items_registrados_con_exito}. ---")
    # NO hacer commit ni cerrar conexión aquí

# === FIN: registrar_entrada_almacen MODIFICADA ===

# ... (Resto de funciones como get_stock_item_details, obtener_datos_para_tarifa, consultar_stock, marcar_item_agotado, marcar_item_empezado) ...
# Asegúrate de que las funciones get_stock_item_details, obtener_datos_para_tarifa, etc.,
# estén definidas en este archivo si no lo estaban antes.

def get_stock_item_details(item_id: int, tabla_stock: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene los detalles completos de un item de stock por su ID y tabla.
    Devuelve un diccionario o None si no se encuentra o hay error.
    """
    print(f"\n--- Buscando detalles para ID: {item_id} en Tabla: {tabla_stock} ---")
    if not isinstance(item_id, int) or item_id <= 0:
        print("  Error: ID inválido.")
        return None
    if tabla_stock not in ['StockMateriasPrimas', 'StockComponentes']:
        print(f"  Error: Tabla '{tabla_stock}' inválida.")
        return None

    conn = None
    item_details = None
    try:
        conn = conectar_db()
        if conn is None: print("  Error: No se pudo conectar a DB."); return None

        conn.row_factory = sqlite3.Row # Para obtener resultados como diccionarios
        cursor = conn.cursor()

        # Importar la función de database aquí para asegurar que está disponible
        # No es necesario si select_item_por_id está en este mismo módulo o importado
        # from .database import select_item_por_id
        fila = select_item_por_id(cursor, tabla_stock, item_id) # Asume que select_item_por_id está disponible

        if fila:
            item_details = dict(fila) # Convertir el objeto Row a diccionario
            print(f"  -> Detalles encontrados para ID {item_id}.")
        else:
            print(f"  -> No se encontró ningún item con ID {item_id} en {tabla_stock}.")

    except ImportError: # Si select_item_por_id se importa y falla
        print("Error: No se pudo importar 'select_item_por_id' desde database.py")
    except sqlite3.Error as e:
        print(f"Error de SQLite obteniendo detalles del item {item_id}: {e}")
        traceback.print_exc()
    except Exception as e_gen:
        print(f"Error inesperado obteniendo detalles del item {item_id}: {e_gen}")
        traceback.print_exc()
    finally:
        if conn: conn.close()
    return item_details

def obtener_datos_para_tarifa() -> List[Dict[str, Any]]:
    """
    Obtiene los datos necesarios de los items de stock disponibles
    (principalmente materias primas) para generar la tarifa de precios.
    """
    print("\n--- Obteniendo datos de stock para la tarifa ---")
    stock_disponible = []
    # Primero intentar con filtros específicos por tipo de material
    for mat_tipo in ['GOMA', 'PVC', 'FIELTRO']:
         filtros = {'status': 'DISPONIBLE', 'material_tipo': mat_tipo}
         # Asegurarse de que consultar_stock está definida o importada
         if callable(consultar_stock):
             stock_disponible.extend(consultar_stock(filtros=filtros))
         else:
             print(f"Advertencia: La función 'consultar_stock' no está disponible. No se pueden obtener datos para {mat_tipo}.")

    if not stock_disponible:
        print("  -> No se encontraron items disponibles para la tarifa.")
        return []

    print(f"  -> Se encontraron {len(stock_disponible)} items relevantes para la tarifa.")
    return stock_disponible

def consultar_stock(filtros=None) -> List[Dict[str, Any]]:
    """
    Consulta el stock de Materias Primas y Componentes aplicando filtros.
    Devuelve una lista de diccionarios.
    """
    print("\n--- Consultando Stock del Almacén (Materias Primas y Componentes) ---")
    if filtros and any(filtros.values()): print(f"  Aplicando Filtros: {filtros}")
    else: print("  (Sin filtros)")

    conn = None
    resultados_combinados_dict = []
    try:
        conn = conectar_db()
        if conn is None:
            print("Error: No se pudo conectar a la base de datos para consultar stock.")
            return []
        conn.row_factory = sqlite3.Row # Para obtener resultados como diccionarios
        cursor = conn.cursor()

        # Importar funciones de database.py si no están ya en este módulo
        # from .database import select_stock_con_filtros, select_todo_stock

        resultados_materias_primas_db = []
        resultados_componentes_db = []

        # Usar las funciones de database.py para las consultas
        if filtros and any(filtros.values()):
            print("  -> Aplicando filtros a ambas tablas...");
            # Suponiendo que select_stock_con_filtros está en database.py
            from almacen.database import select_stock_con_filtros as db_select_filtros
            resultados_materias_primas_db = db_select_filtros(cursor, 'StockMateriasPrimas', filtros)
            resultados_componentes_db = db_select_filtros(cursor, 'StockComponentes', filtros)
        else:
            print("  -> Obteniendo todo el stock de ambas tablas...");
            # Suponiendo que select_todo_stock está en database.py
            from almacen.database import select_todo_stock as db_select_todo
            resultados_materias_primas_db = db_select_todo(cursor, 'StockMateriasPrimas')
            resultados_componentes_db = db_select_todo(cursor, 'StockComponentes')

        # Convertir resultados a diccionarios
        lista_materias_primas_dict = [dict(fila) for fila in resultados_materias_primas_db]
        lista_componentes_dict = [dict(fila) for fila in resultados_componentes_db]
        resultados_combinados_dict = lista_materias_primas_dict + lista_componentes_dict

        print(f"  -> Consulta completada. Se encontraron {len(resultados_combinados_dict)} item(s) en total.")

    except sqlite3.Error as e:
        print(f"Error de SQLite durante la consulta de stock combinada: {e}")
    except AttributeError as ae:
        print(f"Error: ¿Faltan funciones actualizadas en database.py o hay un problema de importación? ({ae})")
        traceback.print_exc()
    except Exception as e_gen:
        print(f"Error inesperado consultando stock combinado: {e_gen}")
        traceback.print_exc()
    finally:
        if conn:
            conn.close()

    try: # Ordenar por fecha descendente
        resultados_combinados_dict.sort(key=lambda x: x.get('fecha_entrada_almacen', '0000-00-00'), reverse=True)
    except Exception as e_sort:
        print(f"Advertencia: No se pudo ordenar la lista combinada de stock: {e_sort}")

    return resultados_combinados_dict


def marcar_item_agotado(id_stock: int, tabla_stock: str = 'StockMateriasPrimas') -> bool:
    """Marca un item de stock como 'AGOTADO' en la base de datos."""
    conn = None
    exito = False
    try:
        id_a_marcar = int(id_stock)
        if id_a_marcar <= 0: raise ValueError("El ID de stock debe ser un entero positivo.")
        if tabla_stock not in ['StockMateriasPrimas', 'StockComponentes']:
            raise ValueError(f"Nombre de tabla de stock inválido ('{tabla_stock}').")

        print(f"\n--- Intentando marcar como AGOTADO id_stock: {id_a_marcar} en tabla {tabla_stock} ---")
        conn = conectar_db()
        if conn is None:
            print("Error: No se pudo conectar a la base de datos."); return False
        # La función actualizar_status_item de database.py se encarga del cursor y commit/rollback
        exito = actualizar_status_item(conn, id_a_marcar, tabla_stock, 'AGOTADO')
    except (ValueError, TypeError) as ve:
        print(f"Error de validación en marcar_item_agotado: {ve}")
        exito = False
    except ImportError:
        print("Error Crítico: No se pudo importar 'actualizar_status_item' desde database.py.")
        exito = False
    except Exception as e:
        print(f"Error inesperado en marcar_item_agotado para ID {id_stock}: {e}")
        traceback.print_exc(); exito = False
    finally:
        if conn: conn.close(); print(f"  -> Conexión a DB cerrada para marcar_item_agotado (ID: {id_stock}).")
    return exito

def marcar_item_empezado(id_stock: int, tabla_stock: str = 'StockMateriasPrimas') -> bool:
    """Marca un item de stock como 'EMPEZADA' en la base de datos."""
    conn = None
    exito = False
    try:
        id_a_marcar = int(id_stock)
        if id_a_marcar <= 0: raise ValueError("El ID de stock debe ser un entero positivo.")
        if tabla_stock not in ['StockMateriasPrimas', 'StockComponentes']:
            raise ValueError(f"Nombre de tabla de stock inválido ('{tabla_stock}').")

        print(f"\n--- Intentando marcar como EMPEZADA id_stock: {id_a_marcar} en tabla {tabla_stock} ---")
        conn = conectar_db()
        if conn is None:
            print("Error: No se pudo conectar a la base de datos."); return False
        exito = actualizar_status_item(conn, id_a_marcar, tabla_stock, 'EMPEZADA')
    except (ValueError, TypeError) as ve:
        print(f"Error de validación en marcar_item_empezado: {ve}")
        exito = False
    except ImportError:
        print("Error Crítico: No se pudo importar 'actualizar_status_item' desde database.py.")
        exito = False
    except Exception as e:
        print(f"Error inesperado en marcar_item_empezado para ID {id_stock}: {e}")
        traceback.print_exc(); exito = False
    finally:
        if conn: conn.close(); print(f"  -> Conexión a DB cerrada para marcar_item_empezado (ID: {id_stock}).")
    return exito
