# contenedor/contenedorPVC.py
# ACTUALIZADO: guardar_o_actualizar usa DB. Carga desde JSON eliminada.

# --- Imports Necesarios ---
import sqlite3
import os
import traceback
from typing import List, Dict, Any
from abc import ABC

# Clases de Contenedor/Modelo
try:
    from .contenedor import Contenedor
except ImportError:
    from contenedor import Contenedor
try:
    from modelos import PVC # Modelo específico
except ImportError:
    print("Error: No se pudo importar 'PVC' desde 'modelos'.")
    class PVC: pass

# Funciones de Base de Datos y Almacén
try:
    from almacen.database import conectar_db
    from almacen.gestion_almacen import registrar_entrada_almacen
except ImportError as e:
    print(f"ERROR CRÍTICO [contenedorPVC]: No se pueden importar funciones de almacen: {e}")
    def conectar_db(): return None
    def registrar_entrada_almacen(obj, pid): pass

# --- Clase ContenedorPVC (Sin cambios en lógica interna) ---
class ContenedorPVC(Contenedor, ABC):
    def __init__(self, fecha_pedido, fecha_llegada, proveedor, numero_factura, observaciones, gastos, valor_conversion, contenido_pvc=None):
        super().__init__(fecha_pedido, fecha_llegada, proveedor, numero_factura, observaciones, gastos, valor_conversion)
        self.contenido = contenido_pvc if contenido_pvc is not None else []

    def agregar_bobina_pvc(self, espesor, ancho, largo, n_bobinas, metro_lineal_usd, color, valor_conversion):
        pvc_obj = PVC(espesor=espesor, ancho=ancho, largo=largo,
                      n_bobinas=n_bobinas, metro_lineal_usd=metro_lineal_usd,
                      color=color)
        try:
            if pvc_obj.metro_lineal_usd is not None and valor_conversion is not None:
                 pvc_obj.metro_lineal_euro = float(pvc_obj.metro_lineal_usd) * float(valor_conversion)
            else: pvc_obj.metro_lineal_euro = None
            if pvc_obj.metro_lineal_euro is not None and pvc_obj.largo is not None and pvc_obj.n_bobinas is not None:
                 pvc_obj.precio_total_euro = pvc_obj.metro_lineal_euro * float(pvc_obj.largo) * int(pvc_obj.n_bobinas)
            else: pvc_obj.precio_total_euro = None
        except (ValueError, TypeError) as e:
            print(f"Error calculando precios base para PVC: {e}. Datos: {pvc_obj.__dict__}")
            pvc_obj.metro_lineal_euro = None; pvc_obj.precio_total_euro = None
        self.contenido.append(pvc_obj)
        print(f"  + Bobina PVC añadida: {espesor}mm {color} (Factura: {self.numero_factura})")

    def calcular_precio_total_euro_gastos(self):
        items = self.contenido
        if not hasattr(self, 'calcular_total_gastos') or not callable(self.calcular_total_gastos):
             print("Error: Método 'calcular_total_gastos' no encontrado.");
             for item in items: item.precio_total_euro_gastos = None
             return
        gastos_repercutibles = self.calcular_total_gastos(tipos=["EXENTO", "SUJETO"])
        total_coste_items = sum(getattr(item, 'precio_total_euro', 0) or 0 for item in items)
        porcentaje_gastos = (gastos_repercutibles / total_coste_items) if total_coste_items > 0 else 0
        for item in items:
            precio_base = getattr(item, 'precio_total_euro', None)
            item.precio_total_euro_gastos = precio_base * (1 + porcentaje_gastos) if isinstance(precio_base, (int, float)) else None

    def calcular_precios_finales(self):
         self.calcular_precio_total_euro_gastos()
         for item in self.contenido:
             coste_unitario_con_gastos = None
             precio_total_gastos = getattr(item, 'precio_total_euro_gastos', None)
             n_bobinas = getattr(item, 'n_bobinas', None)
             largo = getattr(item, 'largo', None)
             if isinstance(precio_total_gastos, (int, float)) and isinstance(n_bobinas, int) and n_bobinas > 0:
                  coste_unitario_con_gastos = precio_total_gastos / n_bobinas
             if isinstance(coste_unitario_con_gastos, (int, float)) and isinstance(largo, (int, float)) and largo != 0:
                 item.metro_lineal_euro_mas_gastos = coste_unitario_con_gastos / largo
             else: item.metro_lineal_euro_mas_gastos = None

    def agregar_contenido(self, item_pvc: PVC):
        if isinstance(item_pvc, PVC): self.contenido.append(item_pvc)
        else: print(f"Error: Se intentó añadir un objeto que no es PVC: {type(item_pvc)}")

    def eliminar_contenido(self, indice):
        try: del self.contenido[indice]
        except IndexError: print(f"Error: Índice {indice} fuera de rango al intentar eliminar PVC.")

    def editar_contenido(self, indice, item_pvc: PVC):
        try:
            if not isinstance(item_pvc, PVC): raise TypeError("El item proporcionado no es de tipo PVC")
            self.contenido[indice] = item_pvc
        except IndexError: print(f"Error: Índice {indice} fuera de rango al intentar editar PVC.")
        except TypeError as e: print(f"Error al editar contenido PVC: {e}")

# ==============================================================================
# FUNCIÓN GUARDAR/ACTUALIZAR CONTENEDOR PVC (Refactorizada para DB)
# ==============================================================================
def guardar_o_actualizar_contenedores_pvc(lista_contenedores: List[ContenedorPVC]):
    """
    Guarda o actualiza una lista de objetos ContenedorPVC en la base de datos.
    (Lógica idéntica a Goma, adaptada para PVC).
    """
    print(f"\n--- Iniciando guardado/actualización DB para {len(lista_contenedores)} Contenedor(es) PVC ---")
    contenedores_procesados = 0
    contenedores_fallidos = 0

    for contenedor_obj in lista_contenedores:
        if not isinstance(contenedor_obj, ContenedorPVC):
             print(f"Error: Objeto no es ContenedorPVC. Tipo: {type(contenedor_obj)}. Saltando...")
             contenedores_fallidos += 1; continue
        if not hasattr(contenedor_obj, 'numero_factura') or not contenedor_obj.numero_factura:
            print("Error: Contenedor sin número de factura. Saltando...")
            contenedores_fallidos += 1; continue

        num_factura = contenedor_obj.numero_factura
        print(f"\nProcesando Contenedor PVC - Factura: {num_factura}")
        conn = None; pedido_id = None; commit_necesario = False

        try:
            conn = conectar_db()
            if conn is None: raise Exception("No se pudo conectar a la base de datos.")
            cursor = conn.cursor()

            # 1. Buscar/Insertar/Actualizar Cabecera
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
            try:
                if datos_pedido["valor_conversion"] is not None:
                    datos_pedido["valor_conversion"] = float(datos_pedido["valor_conversion"])
            except (ValueError, TypeError) as e_type:
                raise ValueError(f"Valor de conversión inválido: {e_type}")

            if resultado: # Actualizar
                pedido_id = resultado[0]
                print(f"  - Factura '{num_factura}' encontrada (ID: {pedido_id}). Actualizando...")
                # Borrar datos antiguos
                print(f"  - Borrando datos antiguos para pedido ID: {pedido_id}...")
                cursor.execute("DELETE FROM GastosPedido WHERE pedido_id = ?", (pedido_id,))
                cursor.execute("DELETE FROM StockMateriasPrimas WHERE pedido_id = ?", (pedido_id,))
                # Actualizar cabecera
                sql_update = "UPDATE PedidosProveedores SET proveedor = ?, fecha_pedido = ?, fecha_llegada = ?, origen_tipo = ?, observaciones = ?, valor_conversion = ? WHERE id = ?"
                cursor.execute(sql_update, (datos_pedido['proveedor'], datos_pedido['fecha_pedido'], datos_pedido['fecha_llegada'], datos_pedido['origen_tipo'], datos_pedido['observaciones'], datos_pedido['valor_conversion'], pedido_id))
            else: # Insertar
                print(f"  - Factura '{num_factura}' no encontrada. Insertando nuevo pedido...")
                columnas = list(datos_pedido.keys())
                placeholders = ', '.join('?' * len(columnas))
                sql_insert = f"INSERT INTO PedidosProveedores ({', '.join(columnas)}) VALUES ({placeholders})"
                cursor.execute(sql_insert, tuple(datos_pedido.values()))
                pedido_id = cursor.lastrowid
                print(f"  - Nuevo pedido insertado con ID: {pedido_id}")
            commit_necesario = True

            if pedido_id is None: raise Exception(f"No se pudo obtener ID para factura {num_factura}")

            # 2. Insertar Gastos
            if hasattr(contenedor_obj, 'gastos') and isinstance(contenedor_obj.gastos, dict):
                print(f"  - Insertando gastos para pedido ID: {pedido_id}...")
                gastos_insertados = 0
                for tipo_gasto, lista_gastos_tipo in contenedor_obj.gastos.items():
                    if isinstance(lista_gastos_tipo, list):
                        for gasto_data in lista_gastos_tipo:
                            if isinstance(gasto_data, dict):
                                desc = gasto_data.get('descripcion'); coste = gasto_data.get('coste')
                                if desc and coste is not None:
                                    try:
                                        coste_float = float(coste)
                                        cursor.execute("INSERT INTO GastosPedido (pedido_id, tipo_gasto, descripcion, coste_eur) VALUES (?, ?, ?, ?)", (pedido_id, tipo_gasto, desc, coste_float))
                                        gastos_insertados += 1
                                    except (ValueError, TypeError): print(f"    * Advertencia: Coste inválido gasto '{desc}'.")
                                    except sqlite3.Error as e_gasto: print(f"    * Error insertando gasto '{desc}': {e_gasto}")
                print(f"  - {gastos_insertados} gastos insertados.")
            else: print("  - No se encontraron gastos válidos para insertar.")

            # 3. Registrar Items en Stock
            print(f"  - Llamando a registrar_entrada_almacen para pedido ID: {pedido_id}...")
            try:
                registrar_entrada_almacen(cursor, contenedor_obj, pedido_id) # Pasar pedido_id
            except TypeError as te:
                 if 'pedido_id' in str(te) or ('positional argument' in str(te) and '2' in str(te)):
                      print("ERROR FATAL: 'registrar_entrada_almacen' no acepta 'pedido_id'. Modificar 'almacen/gestion_almacen.py'.")
                      raise
                 else: raise
            except Exception as e_stock:
                print(f"  - Error durante registrar_entrada_almacen: {e_stock}"); raise

            # 4. Commit
            if commit_necesario:
                print(f"  - Realizando commit para Factura: {num_factura} (ID: {pedido_id})...")
                conn.commit(); print(f"  - Commit exitoso.")
                contenedores_procesados += 1
            else:
                print(f"  - No se realizaron cambios que requieran commit para Factura: {num_factura}.")
                contenedores_procesados += 1

        except Exception as e:
            print(f"ERROR procesando contenedor PVC - Factura: {num_factura}. Error: {e}")
            traceback.print_exc()
            if conn: print(f"  - Realizando rollback para Factura: {num_factura}..."); conn.rollback()
            contenedores_fallidos += 1
        finally:
            if conn: conn.close(); print(f"  - Conexión DB cerrada para Factura: {num_factura}.")

    print(f"\n--- Finalizado guardado/actualización DB Contenedores PVC ---")
    print(f"    Procesados con éxito: {contenedores_procesados}")
    print(f"    Fallidos: {contenedores_fallidos}")
    print("-" * 60)

# contenedor/contenedorPVC.py
# ... (imports y clase ContenedorPVC como estaban antes) ...

# --- Imports ADICIONALES para Carga DB ---
import sqlite3
from typing import List, Dict, Any # Asegúrate que está
try:
    from almacen.database import conectar_db
except ImportError as e:
    print(f"ERROR CRÍTICO [cargar_contenedores_pvc]: No se puede importar conectar_db: {e}")
    def conectar_db(): return None
try:
    from modelos import PVC
except ImportError:
    print("Error: No se pudo importar 'PVC' desde 'modelos'.")
    class PVC: pass # Dummy

# ==============================================================================
# FUNCIÓN CARGAR CONTENEDORES PVC (Refactorizada para DB)
# ==============================================================================
def cargar_contenedores_pvc() -> List[ContenedorPVC]:
    """
    Carga TODOS los Contenedores de PVC desde la base de datos.
    Reconstruye los objetos ContenedorPVC, incluyendo gastos y una
    representación SIMPLIFICADA del contenido basada en StockMateriasPrimas.
    """
    print("\n--- Cargando Contenedores PVC desde la DB ---")
    contenedores_cargados = []
    conn = None
    try:
        conn = conectar_db()
        if conn is None:
            print("Error: No se pudo conectar a la DB para cargar Contenedores PVC.")
            return []
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 1. Obtener pedidos de tipo CONTENEDOR
        cursor.execute("SELECT * FROM PedidosProveedores WHERE origen_tipo = 'CONTENEDOR'")
        pedidos_db = cursor.fetchall()
        print(f"  - Encontrados {len(pedidos_db)} pedidos de tipo CONTENEDOR.")

        for pedido_row in pedidos_db:
            pedido_dict = dict(pedido_row)
            pedido_id = pedido_dict['id']
            num_factura = pedido_dict['numero_factura']
            print(f"  - Procesando Pedido ID: {pedido_id}, Factura: {num_factura}")

            # 2. Obtener Gastos
            cursor.execute("SELECT tipo_gasto, descripcion, coste_eur FROM GastosPedido WHERE pedido_id = ?", (pedido_id,))
            gastos_db = cursor.fetchall()
            gastos_dict_reconst = {}
            for g_row in gastos_db:
                g_dict = dict(g_row); tipo = g_dict['tipo_gasto']
                if tipo not in gastos_dict_reconst: gastos_dict_reconst[tipo] = []
                gastos_dict_reconst[tipo].append({'descripcion': g_dict['descripcion'], 'coste': g_dict['coste_eur']})

            # 3. Obtener Items de Stock (PVC)
            cursor.execute("""
                SELECT id, referencia_stock, espesor, ancho, largo_actual, color,
                       coste_unitario_final, unidad_medida, status
                FROM StockMateriasPrimas
                WHERE pedido_id = ? AND material_tipo = 'PVC'
            """, (pedido_id,))
            items_stock_db = cursor.fetchall()
            contenido_reconst = []
            print(f"    - Encontrados {len(items_stock_db)} items de PVC en stock para este pedido.")

            # Reconstruir objetos PVC simplificados desde el stock
            for item_stock_row in items_stock_db:
                item_stock_dict = dict(item_stock_row)
                try:
                    pvc_obj = PVC(
                        espesor=item_stock_dict.get('espesor', '?'),
                        ancho=item_stock_dict.get('ancho', 0.0),
                        largo=item_stock_dict.get('largo_actual', 0.0),
                        n_bobinas=1, # Asumir 1
                        metro_lineal_usd=None,
                        color=item_stock_dict.get('color', '?') # Obtener color del stock
                    )
                    # Asignar costes calculados del stock
                    pvc_obj.metro_lineal_euro_mas_gastos = item_stock_dict.get('coste_unitario_final')
                    pvc_obj.precio_total_euro = None
                    pvc_obj.precio_total_euro_gastos = None
                    pvc_obj.metro_lineal_euro = None
                    contenido_reconst.append(pvc_obj)
                except Exception as e_reconst:
                    print(f"    * Error reconstruyendo item PVC desde stock ID {item_stock_dict.get('id')}: {e_reconst}")

            # 4. Crear instancia de ContenedorPVC
            try:
                contenedor = ContenedorPVC(
                    fecha_pedido=pedido_dict.get('fecha_pedido'),
                    fecha_llegada=pedido_dict.get('fecha_llegada'),
                    proveedor=pedido_dict.get('proveedor'),
                    numero_factura=pedido_dict.get('numero_factura'),
                    observaciones=pedido_dict.get('observaciones'),
                    gastos=gastos_dict_reconst,
                    valor_conversion=pedido_dict.get('valor_conversion'),
                    contenido_pvc=contenido_reconst # Contenido simplificado
                )
                contenedores_cargados.append(contenedor)
                print(f"    - Objeto ContenedorPVC creado para Factura: {num_factura}")
            except Exception as e_create:
                print(f"Error creando objeto ContenedorPVC para Factura {num_factura}: {e_create}")
                traceback.print_exc()

    except sqlite3.Error as e:
        print(f"Error SQLite cargando contenedores PVC: {e}")
    except Exception as e_gen:
        print(f"Error inesperado cargando contenedores PVC: {e_gen}")
        traceback.print_exc()
    finally:
        if conn:
            conn.close()
            print("Conexión DB cerrada después de cargar contenedores PVC.")

    print(f"--- Carga DB Contenedores PVC finalizada: {len(contenedores_cargados)} objetos creados ---")
    return contenedores_cargados

# ... (resto del archivo si hay más funciones) ...
