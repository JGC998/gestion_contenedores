# contenedor/contenedorGoma.py
# ACTUALIZADO: guardar_o_actualizar usa DB. Carga desde JSON eliminada.

# --- Imports Necesarios ---
import sqlite3
import os
import traceback
from typing import List, Dict, Any # Para type hints
from abc import ABC

# Clases de Contenedor/Modelo
# Asegúrate que la ruta a contenedor.py es correcta (puede ser '.' o 'contenedor.')
try:
    # Asume que contenedor.py está en la misma carpeta
    from .contenedor import Contenedor
except ImportError:
    # Si ejecutas desde la carpeta raíz del proyecto
    from contenedor.contenedor import Contenedor

# Asume que modelos.py está en la carpeta raíz del proyecto
try:
    from modelos import Goma
except ImportError:
    # Si modelos.py está en la misma carpeta que este archivo (menos común)
    # from .modelos import Goma
    print("Error: No se pudo importar 'Goma' desde 'modelos'. Verifica la ubicación.")
    # Define una clase Dummy si la importación falla
    class Goma: pass


# Funciones de Base de Datos y Almacén
try:
    # Asume que 'almacen' es una carpeta al mismo nivel que 'contenedor'
    # y que ejecutas desde la raíz del proyecto.
    from almacen.database import conectar_db
    # Asegúrate que registrar_entrada_almacen ahora acepta pedido_id
    from almacen.gestion_almacen import registrar_entrada_almacen
except ImportError as e:
    print(f"ERROR CRÍTICO [contenedorGoma]: No se pueden importar funciones de almacen: {e}")
    # Definir Dummies para evitar errores si la importación falla
    def conectar_db(): return None
    # Dummy que acepta dos argumentos ahora
    def registrar_entrada_almacen(obj, pid): pass

# --- Clase ContenedorGoma (Sin cambios en la lógica interna) ---
class ContenedorGoma(Contenedor, ABC):
    def __init__(self, fecha_pedido, fecha_llegada, proveedor, numero_factura, observaciones, gastos, valor_conversion, contenido_goma=None):
        """Inicializa un contenedor de Goma."""
        super().__init__(fecha_pedido, fecha_llegada, proveedor, numero_factura, observaciones, gastos, valor_conversion)
        self.contenido = contenido_goma if contenido_goma is not None else []

    def agregar_bobina(self, espesor, ancho, largo, n_bobinas, metro_lineal_usd, valor_conversion, subtipo="NORMAL"):
        """Crea una bobina Goma (con subtipo), calcula sus precios base y la añade a la lista."""
        # Crear instancia de Goma pasando el subtipo
        goma = Goma(espesor=espesor, ancho=ancho, largo=largo,
                    n_bobinas=n_bobinas, metro_lineal_usd=metro_lineal_usd,
                    subtipo=subtipo) # <-- Pasar subtipo aquí

        # Calcula precios base en EUR (lógica sin cambios)
        try:
            if goma.metro_lineal_usd is not None and valor_conversion is not None:
                goma.metro_lineal_euro = float(goma.metro_lineal_usd) * float(valor_conversion)
            else:
                goma.metro_lineal_euro = None

            if goma.metro_lineal_euro is not None and goma.largo is not None and goma.n_bobinas is not None:
                goma.precio_total_euro = goma.metro_lineal_euro * float(goma.largo) * int(goma.n_bobinas)
            else:
                goma.precio_total_euro = None
        except (ValueError, TypeError) as e:
             print(f"Error calculando precios base para Goma {goma.subtipo}: {e}. Datos: {goma.__dict__}")
             goma.metro_lineal_euro = None
             goma.precio_total_euro = None

        self.contenido.append(goma)
        print(f"  + Bobina Goma {goma.subtipo} añadida: {espesor}mm (Factura: {self.numero_factura})")

    def calcular_precio_total_euro_gastos(self):
        """Calcula precio_total_euro_gastos para cada bobina."""
        bobinas = self.contenido
        # Asegurarse que calcular_total_gastos existe en la clase base Contenedor
        if not hasattr(self, 'calcular_total_gastos') or not callable(self.calcular_total_gastos):
             print("Error: Método 'calcular_total_gastos' no encontrado en Contenedor.")
             # Asignar None a los items si no se pueden calcular los gastos
             for bobina in bobinas:
                 bobina.precio_total_euro_gastos = None
             return

        gastos_repercutibles = self.calcular_total_gastos(tipos=["EXENTO", "SUJETO"])
        total_coste_bobinas_base = sum(getattr(b, 'precio_total_euro', 0) or 0 for b in bobinas)

        if total_coste_bobinas_base == 0:
            porcentaje_gastos = 0.0
        else:
            porcentaje_gastos = gastos_repercutibles / total_coste_bobinas_base

        for bobina in bobinas:
            precio_base = getattr(bobina, 'precio_total_euro', None)
            # Asegurar que el precio base es numérico antes de multiplicar
            if isinstance(precio_base, (int, float)):
                bobina.precio_total_euro_gastos = precio_base * (1 + porcentaje_gastos)
            else:
                bobina.precio_total_euro_gastos = None

    def calcular_precios_finales(self):
        """Calcula TODOS los precios finales."""
        self.calcular_precio_total_euro_gastos() # Llama al método anterior
        for bobina in self.contenido:
            coste_unitario_con_gastos = None
            precio_total_con_gastos = getattr(bobina, 'precio_total_euro_gastos', None)
            n_bobinas = getattr(bobina, 'n_bobinas', None)
            largo = getattr(bobina, 'largo', None)

            # Validar tipos antes de dividir
            if isinstance(precio_total_con_gastos, (int, float)) and \
               isinstance(n_bobinas, int) and n_bobinas > 0: # n_bobinas debe ser int
                coste_unitario_con_gastos = precio_total_con_gastos / n_bobinas

            if isinstance(coste_unitario_con_gastos, (int, float)) and \
               isinstance(largo, (int, float)) and largo != 0:
                bobina.metro_lineal_euro_mas_gastos = coste_unitario_con_gastos / largo
            else:
                bobina.metro_lineal_euro_mas_gastos = None

    # --- Métodos Abstractos Implementados (Sin cambios) ---
    def agregar_contenido(self, item_goma: Goma):
        """Añade un objeto Goma pre-creado al contenedor."""
        if isinstance(item_goma, Goma):
            self.contenido.append(item_goma)
        else:
            print(f"Error: Se intentó añadir un objeto que no es Goma: {type(item_goma)}")

    def eliminar_contenido(self, indice):
        """Elimina un item de Goma por su índice."""
        try:
            del self.contenido[indice]
        except IndexError:
            print(f"Error: Índice {indice} fuera de rango al intentar eliminar Goma.")

    def editar_contenido(self, indice, item_goma: Goma):
        """Reemplaza un item de Goma en el índice dado."""
        try:
            if not isinstance(item_goma, Goma):
                 raise TypeError("El item proporcionado no es de tipo Goma")
            self.contenido[indice] = item_goma
            # Opcional: Recalcular si se edita algo
            # self.calcular_precios_finales()
        except IndexError:
            print(f"Error: Índice {indice} fuera de rango al intentar editar.")
        except TypeError as e:
             print(f"Error al editar contenido Goma: {e}")

# ==============================================================================
# FUNCIÓN GUARDAR/ACTUALIZAR CONTENEDOR GOMA (Refactorizada para DB)
# ==============================================================================
def guardar_o_actualizar_contenedores_goma(lista_contenedores: List[ContenedorGoma]):
    """
    Guarda o actualiza una lista de objetos ContenedorGoma en la base de datos.
    Interactúa con las tablas PedidosProveedores, GastosPedido y llama a
    registrar_entrada_almacen para guardar los items de stock.
    """
    print(f"\n--- Iniciando guardado/actualización DB para {len(lista_contenedores)} Contenedor(es) Goma ---")
    contenedores_procesados = 0
    contenedores_fallidos = 0

    for contenedor_obj in lista_contenedores:
        # Validar objeto básico
        if not isinstance(contenedor_obj, ContenedorGoma):
             print(f"Error: Objeto no es de tipo ContenedorGoma. Tipo: {type(contenedor_obj)}. Saltando...")
             contenedores_fallidos += 1; continue
        if not hasattr(contenedor_obj, 'numero_factura') or not contenedor_obj.numero_factura:
            print("Error: Contenedor sin número de factura. Saltando...")
            contenedores_fallidos += 1; continue

        num_factura = contenedor_obj.numero_factura
        print(f"\nProcesando Contenedor Goma - Factura: {num_factura}")
        conn = None; pedido_id = None; commit_necesario = False

        try:
            conn = conectar_db()
            if conn is None: raise Exception("No se pudo conectar a la base de datos.")
            cursor = conn.cursor()

            # 1. Buscar/Insertar/Actualizar Cabecera en PedidosProveedores
            cursor.execute("SELECT id FROM PedidosProveedores WHERE numero_factura = ?", (num_factura,))
            resultado = cursor.fetchone()
            datos_pedido = {
                "numero_factura": num_factura,
                "proveedor": getattr(contenedor_obj, 'proveedor', None),
                "fecha_pedido": getattr(contenedor_obj, 'fecha_pedido', None),
                "fecha_llegada": getattr(contenedor_obj, 'fecha_llegada', None),
                "origen_tipo": 'CONTENEDOR',
                "observaciones": getattr(contenedor_obj, 'observaciones', None),
                "valor_conversion": getattr(contenedor_obj, 'valor_conversion', None)
            }
            try: # Validar valor_conversion
                if datos_pedido["valor_conversion"] is not None:
                    datos_pedido["valor_conversion"] = float(datos_pedido["valor_conversion"])
            except (ValueError, TypeError) as e_type:
                raise ValueError(f"Valor de conversión inválido: {e_type}")

            if resultado: # Ya existe, actualizar y obtener ID
                pedido_id = resultado[0]
                print(f"  - Factura '{num_factura}' encontrada (ID: {pedido_id}). Actualizando...")
                # Borrar gastos e items de stock antiguos asociados
                print(f"  - Borrando datos antiguos para pedido ID: {pedido_id}...")
                cursor.execute("DELETE FROM GastosPedido WHERE pedido_id = ?", (pedido_id,))
                cursor.execute("DELETE FROM StockMateriasPrimas WHERE pedido_id = ?", (pedido_id,))
                # cursor.execute("DELETE FROM StockComponentes WHERE pedido_id = ?", (pedido_id,)) # Si aplica

                # Actualizar la cabecera del pedido
                sql_update = """
                    UPDATE PedidosProveedores SET
                        proveedor = ?, fecha_pedido = ?, fecha_llegada = ?, origen_tipo = ?,
                        observaciones = ?, valor_conversion = ?
                    WHERE id = ?
                """
                cursor.execute(sql_update, (
                    datos_pedido['proveedor'], datos_pedido['fecha_pedido'], datos_pedido['fecha_llegada'],
                    datos_pedido['origen_tipo'], datos_pedido['observaciones'], datos_pedido['valor_conversion'],
                    pedido_id
                ))
            else: # No existe, insertar y obtener nuevo ID
                print(f"  - Factura '{num_factura}' no encontrada. Insertando nuevo pedido...")
                columnas_pedido = list(datos_pedido.keys())
                placeholders_pedido = ', '.join('?' * len(columnas_pedido))
                sql_insert = f"INSERT INTO PedidosProveedores ({', '.join(columnas_pedido)}) VALUES ({placeholders_pedido})"
                valores_pedido = tuple(datos_pedido.values())
                cursor.execute(sql_insert, valores_pedido)
                pedido_id = cursor.lastrowid # Obtener el ID recién insertado
                print(f"  - Nuevo pedido insertado con ID: {pedido_id}")
            commit_necesario = True # Marcar para commit

            if pedido_id is None:
                raise Exception(f"No se pudo obtener un ID de pedido para la factura {num_factura}")

            # 2. Insertar Gastos (SIEMPRE se insertan después de borrar los antiguos si existían)
            if hasattr(contenedor_obj, 'gastos') and isinstance(contenedor_obj.gastos, dict):
                print(f"  - Insertando gastos para pedido ID: {pedido_id}...")
                gastos_insertados = 0
                for tipo_gasto, lista_gastos_tipo in contenedor_obj.gastos.items():
                    if isinstance(lista_gastos_tipo, list):
                        for gasto_data in lista_gastos_tipo:
                            if isinstance(gasto_data, dict):
                                desc = gasto_data.get('descripcion')
                                coste = gasto_data.get('coste')
                                if desc and coste is not None:
                                    try:
                                        coste_float = float(coste)
                                        cursor.execute("""
                                            INSERT INTO GastosPedido (pedido_id, tipo_gasto, descripcion, coste_eur)
                                            VALUES (?, ?, ?, ?)
                                        """, (pedido_id, tipo_gasto, desc, coste_float))
                                        gastos_insertados += 1
                                    except (ValueError, TypeError):
                                        print(f"    * Advertencia: Coste inválido para gasto '{desc}'. Saltando.")
                                    except sqlite3.Error as e_gasto:
                                        print(f"    * Error insertando gasto '{desc}': {e_gasto}")
                print(f"  - {gastos_insertados} gastos insertados.")
            else:
                print("  - No se encontraron gastos válidos para insertar.")

            # 3. Registrar Items en Stock (Llamando a gestion_almacen)
            #    Se insertarán nuevos items porque los viejos asociados a pedido_id fueron borrados.
            print(f"  - Llamando a registrar_entrada_almacen para pedido ID: {pedido_id}...")
            try:
                # PASAMOS EL pedido_id OBTENIDO A LA FUNCIÓN DE REGISTRO
                # Asumimos que registrar_entrada_almacen está adaptada
                registrar_entrada_almacen(contenedor_obj, pedido_id)
                commit_necesario = True # Marcar commit necesario si el registro fue exitoso
            except TypeError as te:
                 # Comprobar si el error es por el argumento pedido_id
                 if 'pedido_id' in str(te) or ('positional argument' in str(te) and '2' in str(te)):
                      print("ERROR FATAL: La función 'registrar_entrada_almacen' no parece aceptar 'pedido_id'.")
                      print("           Necesitas modificar 'almacen/gestion_almacen.py' para que acepte este segundo argumento.")
                      raise # Re-lanzar el error para que falle la transacción
                 else:
                      print(f"Error de tipo inesperado llamando a registrar_entrada_almacen: {te}")
                      raise # Re-lanzar otros TypeError
            except Exception as e_stock:
                print(f"  - Error durante registrar_entrada_almacen: {e_stock}")
                raise # Re-lanzar para que falle la transacción

            # 4. Commit si todo fue bien y se hicieron cambios
            if commit_necesario:
                print(f"  - Realizando commit para Factura: {num_factura} (ID: {pedido_id})...")
                conn.commit()
                print(f"  - Commit exitoso.")
                contenedores_procesados += 1
            else:
                print(f"  - No se realizaron cambios que requieran commit para Factura: {num_factura}.")
                contenedores_procesados += 1 # Considerar éxito si no hubo errores

        except Exception as e:
            print(f"ERROR procesando contenedor Goma - Factura: {num_factura}. Error: {e}")
            traceback.print_exc()
            if conn:
                print(f"  - Realizando rollback para Factura: {num_factura}...")
                conn.rollback()
            contenedores_fallidos += 1
        finally:
            if conn:
                conn.close()
                print(f"  - Conexión DB cerrada para Factura: {num_factura}.")

    print(f"\n--- Finalizado guardado/actualización DB Contenedores Goma ---")
    print(f"    Procesados con éxito: {contenedores_procesados}")
    print(f"    Fallidos: {contenedores_fallidos}")
    print("-" * 60)

# --- Función de Carga (Placeholder - A implementar en Paso 4) ---
# contenedor/contenedorGoma.py
# ... (imports y clase ContenedorGoma como estaban antes) ...

# --- Imports ADICIONALES para Carga DB ---
import sqlite3
from typing import List, Dict, Any # Asegúrate que está
try:
    # Asume que database.py está en una carpeta 'almacen' al mismo nivel
    from almacen.database import conectar_db
except ImportError as e:
    print(f"ERROR CRÍTICO [cargar_contenedores_goma]: No se puede importar conectar_db: {e}")
    def conectar_db(): return None
try:
    # Modelo necesario para reconstruir contenido (simplificado)
    from modelos import Goma
except ImportError:
    print("Error: No se pudo importar 'Goma' desde 'modelos'.")
    class Goma: pass # Dummy

# ==============================================================================
# FUNCIÓN CARGAR CONTENEDORES GOMA (Refactorizada para DB)
# ==============================================================================
def cargar_contenedores_goma() -> List[ContenedorGoma]:
    """
    Carga TODOS los Contenedores de Goma desde la base de datos.
    Reconstruye los objetos ContenedorGoma, incluyendo gastos y una
    representación SIMPLIFICADA del contenido basada en StockMateriasPrimas.
    """
    print("\n--- Cargando Contenedores Goma desde la DB ---")
    contenedores_cargados = []
    conn = None
    try:
        conn = conectar_db()
        if conn is None:
            print("Error: No se pudo conectar a la DB para cargar Contenedores Goma.")
            return [] # Devuelve lista vacía si no hay conexión
        conn.row_factory = sqlite3.Row # Para obtener resultados como diccionarios
        cursor = conn.cursor()

        # 1. Obtener todos los pedidos de tipo CONTENEDOR
        cursor.execute("SELECT * FROM PedidosProveedores WHERE origen_tipo = 'CONTENEDOR'")
        pedidos_db = cursor.fetchall()
        print(f"  - Encontrados {len(pedidos_db)} pedidos de tipo CONTENEDOR.")

        for pedido_row in pedidos_db:
            pedido_dict = dict(pedido_row) # Convertir fila a diccionario
            pedido_id = pedido_dict['id']
            num_factura = pedido_dict['numero_factura']
            print(f"  - Procesando Pedido ID: {pedido_id}, Factura: {num_factura}")

            # 2. Obtener Gastos asociados
            cursor.execute("SELECT tipo_gasto, descripcion, coste_eur FROM GastosPedido WHERE pedido_id = ?", (pedido_id,))
            gastos_db = cursor.fetchall()
            gastos_dict_reconst = {} # Reconstruir el diccionario de gastos original
            for g_row in gastos_db:
                g_dict = dict(g_row)
                tipo = g_dict['tipo_gasto']
                if tipo not in gastos_dict_reconst: gastos_dict_reconst[tipo] = []
                gastos_dict_reconst[tipo].append({'descripcion': g_dict['descripcion'], 'coste': g_dict['coste_eur']})

            # 3. Obtener Items de Stock (Materias Primas GOMA) asociados
            cursor.execute("""
                SELECT id, referencia_stock, espesor, ancho, largo_actual, subtipo_material,
                       coste_unitario_final, unidad_medida, status
                FROM StockMateriasPrimas
                WHERE pedido_id = ? AND material_tipo = 'GOMA'
            """, (pedido_id,))
            items_stock_db = cursor.fetchall()
            contenido_reconst = [] # Lista para los objetos Goma (simplificados)
            print(f"    - Encontrados {len(items_stock_db)} items de Goma en stock para este pedido.")

            # Reconstruir objetos Goma simplificados desde el stock
            for item_stock_row in items_stock_db:
                item_stock_dict = dict(item_stock_row)
                try:
                    # Crear objeto Goma usando datos del stock.
                    # Faltan n_bobinas y metro_lineal_usd originales.
                    # Usamos coste_unitario_final como si fuera metro_lineal_eur base.
                    # ¡ESTO ES UNA APROXIMACIÓN!
                    goma_obj = Goma(
                        espesor=item_stock_dict.get('espesor', '?'),
                        ancho=item_stock_dict.get('ancho', 0.0),
                        largo=item_stock_dict.get('largo_actual', 0.0), # Usar largo actual
                        n_bobinas=1, # Asumir 1 bobina por entrada de stock
                        metro_lineal_usd=None, # No disponible en stock
                        subtipo=item_stock_dict.get('subtipo_material', 'NORMAL')
                    )
                    # Asignar costes calculados del stock directamente
                    goma_obj.metro_lineal_euro_mas_gastos = item_stock_dict.get('coste_unitario_final')
                    # Otros precios (base, con gastos) no se pueden reconstruir fácilmente desde aquí
                    goma_obj.precio_total_euro = None
                    goma_obj.precio_total_euro_gastos = None
                    goma_obj.metro_lineal_euro = None # Podría estimarse si se conoce el % de gastos

                    contenido_reconst.append(goma_obj)
                except Exception as e_reconst:
                    print(f"    * Error reconstruyendo item Goma desde stock ID {item_stock_dict.get('id')}: {e_reconst}")

            # 4. Crear instancia de ContenedorGoma
            try:
                # Crear objeto ContenedorGoma pasando datos generales y gastos reconstruidos
                # El contenido es la lista de objetos Goma simplificados
                contenedor = ContenedorGoma(
                    fecha_pedido=pedido_dict.get('fecha_pedido'),
                    fecha_llegada=pedido_dict.get('fecha_llegada'),
                    proveedor=pedido_dict.get('proveedor'),
                    numero_factura=pedido_dict.get('numero_factura'),
                    observaciones=pedido_dict.get('observaciones'),
                    gastos=gastos_dict_reconst, # Usar gastos reconstruidos
                    valor_conversion=pedido_dict.get('valor_conversion'),
                    contenido_goma=contenido_reconst # Usar contenido reconstruido (simplificado)
                )
                # Opcional: Recalcular precios basados en el contenido reconstruido (será aproximado)
                # contenedor.calcular_precios_finales()
                contenedores_cargados.append(contenedor)
                print(f"    - Objeto ContenedorGoma creado para Factura: {num_factura}")
            except Exception as e_create:
                print(f"Error creando objeto ContenedorGoma para Factura {num_factura}: {e_create}")
                traceback.print_exc()

    except sqlite3.Error as e:
        print(f"Error SQLite cargando contenedores Goma: {e}")
    except Exception as e_gen:
        print(f"Error inesperado cargando contenedores Goma: {e_gen}")
        traceback.print_exc()
    finally:
        if conn:
            conn.close()
            print("Conexión DB cerrada después de cargar contenedores Goma.")

    print(f"--- Carga DB Contenedores Goma finalizada: {len(contenedores_cargados)} objetos creados ---")
    return contenedores_cargados

# ... (resto del archivo si hay más funciones) ...
