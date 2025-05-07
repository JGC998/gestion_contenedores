# nacional/mercanciaNacionalGoma.py
# ACTUALIZADO: guardar_o_actualizar usa DB. cargar_mercancias_goma ahora lee de DB.

# --- Imports Necesarios ---
import sqlite3
import os
import traceback
from typing import List, Dict, Any # Para type hints
from abc import ABC

# Clases Base/Modelo
try:
    from .mercanciaNacional import MercanciaNacional
except ImportError:
    from nacional.mercanciaNacional import MercanciaNacional
try:
    from modelos import GomaNacional
except ImportError:
    print("Error: No se pudo importar 'GomaNacional' desde 'modelos'.")
    class GomaNacional: pass # Dummy

# Funciones de Base de Datos y Almacén
try:
    from almacen.database import conectar_db
    from almacen.gestion_almacen import registrar_entrada_almacen # Aunque no se usa en cargar, es parte del módulo
except ImportError as e:
    print(f"ERROR CRÍTICO [mercanciaNacionalGoma]: No se pueden importar funciones de almacen: {e}")
    def conectar_db(): return None
    def registrar_entrada_almacen(obj, pid): pass

# --- Clase MercanciaNacionalGoma (Sin cambios) ---
class MercanciaNacionalGoma(MercanciaNacional, ABC):
    def __init__(self, fecha_pedido, fecha_llegada, proveedor, numero_factura, observaciones, contenido_goma_nacional=None):
        super().__init__(fecha_pedido, fecha_llegada, proveedor, numero_factura, observaciones)
        self.contenido = contenido_goma_nacional if contenido_goma_nacional is not None else []

    def agregar_bobina(self, espesor, ancho, largo, n_bobinas, metro_lineal_eur, subtipo="NORMAL"):
        try:
            goma_nacional_obj = GomaNacional(
                espesor=espesor, ancho=ancho, largo=largo,
                n_bobinas=n_bobinas, metro_lineal_eur=metro_lineal_eur,
                subtipo=subtipo
            )
            self.contenido.append(goma_nacional_obj)
            print(f"  + Bobina Goma Nac. ({goma_nacional_obj.subtipo}) añadida: {espesor}mm (Factura: {self.numero_factura})")
        except (ValueError, TypeError) as e:
             print(f"Error al crear objeto GomaNacional: {e}. Datos: {locals()}")
        except Exception as e_gen:
             print(f"Error inesperado al crear GomaNacional: {e_gen}. Datos: {locals()}")

    def calcular_precio_total_euro_gastos(self):
        items = self.contenido
        if not hasattr(self, 'calcular_total_gastos') or not callable(self.calcular_total_gastos):
             print("Error: Método 'calcular_total_gastos' no encontrado en MercanciaNacional.");
             for item in items: item.precio_total_euro_gastos = None
             return
        gastos_repercutibles = self.calcular_total_gastos()
        total_coste_items = sum(getattr(item, 'precio_total_euro', 0) or 0 for item in items)
        porcentaje_gastos = (gastos_repercutibles / total_coste_items) if total_coste_items > 0 else 0
        for item in items:
            precio_base = getattr(item, 'precio_total_euro', None)
            if isinstance(precio_base, (int, float)):
                item.precio_total_euro_gastos = precio_base * (1 + porcentaje_gastos)
            else:
                item.precio_total_euro_gastos = None

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
             else:
                 item.metro_lineal_euro_mas_gastos = None

    def agregar_contenido(self, item_goma_nacional: GomaNacional):
        if isinstance(item_goma_nacional, GomaNacional):
            self.contenido.append(item_goma_nacional)
        else:
            print(f"Error: Se intentó añadir un objeto que no es GomaNacional: {type(item_goma_nacional)}")

    def eliminar_contenido(self, indice):
        try: del self.contenido[indice]
        except IndexError: print(f"Error: Índice {indice} fuera de rango al intentar eliminar GomaNac.")

    def editar_contenido(self, indice, item_goma_nacional: GomaNacional):
        try:
            if not isinstance(item_goma_nacional, GomaNacional):
                 raise TypeError("El item proporcionado no es de tipo GomaNacional")
            self.contenido[indice] = item_goma_nacional
        except IndexError: print(f"Error: Índice {indice} fuera de rango al intentar editar GomaNac.")
        except TypeError as e: print(f"Error al editar contenido GomaNac.: {e}")

# ==============================================================================
# FUNCIÓN GUARDAR/ACTUALIZAR MERCANCIA GOMA NACIONAL (DB)
# ==============================================================================
def guardar_o_actualizar_mercancias_goma(lista_pedidos: List[MercanciaNacionalGoma]):
    """
    Guarda o actualiza una lista de objetos MercanciaNacionalGoma en la base de datos.
    """
    print(f"\n--- Iniciando guardado/actualización DB para {len(lista_pedidos)} Pedido(s) Goma Nacional ---")
    pedidos_procesados = 0
    pedidos_fallidos = 0

    for pedido_obj in lista_pedidos:
        if not isinstance(pedido_obj, MercanciaNacionalGoma):
             print(f"Error: Objeto no es MercanciaNacionalGoma. Tipo: {type(pedido_obj)}. Saltando...")
             pedidos_fallidos += 1; continue
        if not hasattr(pedido_obj, 'numero_factura') or not pedido_obj.numero_factura:
            print("Error: Pedido nacional sin número de factura. Saltando...")
            pedidos_fallidos += 1; continue

        num_factura = pedido_obj.numero_factura
        print(f"\nProcesando Pedido Goma Nacional - Factura: {num_factura}")
        conn = None; pedido_id = None; commit_necesario = False

        try:
            conn = conectar_db()
            if conn is None: raise Exception("No se pudo conectar a la base de datos.")
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM PedidosProveedores WHERE numero_factura = ?", (num_factura,))
            resultado = cursor.fetchone()
            datos_pedido = {
                "numero_factura": num_factura,
                "proveedor": getattr(pedido_obj, 'proveedor', None),
                "fecha_pedido": getattr(pedido_obj, 'fecha_pedido', None),
                "fecha_llegada": getattr(pedido_obj, 'fecha_llegada', None),
                "origen_tipo": 'NACIONAL',
                "observaciones": getattr(pedido_obj, 'observaciones', None),
                "valor_conversion": None
            }

            if resultado: # Actualizar
                pedido_id = resultado[0]
                print(f"  - Factura '{num_factura}' encontrada (ID: {pedido_id}). Actualizando...")
                print(f"  - Borrando datos antiguos para pedido ID: {pedido_id}...")
                cursor.execute("DELETE FROM GastosPedido WHERE pedido_id = ?", (pedido_id,))
                cursor.execute("DELETE FROM StockMateriasPrimas WHERE pedido_id = ?", (pedido_id,))
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

            if hasattr(pedido_obj, 'gastos') and isinstance(pedido_obj.gastos, list):
                print(f"  - Insertando gastos para pedido ID: {pedido_id}...")
                gastos_insertados = 0
                for gasto_data in pedido_obj.gastos:
                    if isinstance(gasto_data, dict):
                        desc = gasto_data.get('descripcion'); coste = gasto_data.get('coste')
                        if desc and coste is not None:
                            try:
                                coste_float = float(coste)
                                cursor.execute("INSERT INTO GastosPedido (pedido_id, tipo_gasto, descripcion, coste_eur) VALUES (?, ?, ?, ?)", (pedido_id, 'NACIONAL', desc, coste_float))
                                gastos_insertados += 1
                            except (ValueError, TypeError): print(f"    * Advertencia: Coste inválido gasto '{desc}'.")
                            except sqlite3.Error as e_gasto: print(f"    * Error insertando gasto '{desc}': {e_gasto}")
                print(f"  - {gastos_insertados} gastos insertados.")
            else: print("  - No se encontraron gastos válidos para insertar.")

            print(f"  - Llamando a registrar_entrada_almacen para pedido ID: {pedido_id}...")
            try:
                registrar_entrada_almacen(cursor, pedido_obj, pedido_id)
            except TypeError as te:
                 if 'pedido_id' in str(te) or ('positional argument' in str(te) and '2' in str(te)):
                      print("ERROR FATAL: 'registrar_entrada_almacen' no acepta 'pedido_id'. Modificar 'almacen/gestion_almacen.py'.")
                      raise
                 else: raise
            except Exception as e_stock:
                print(f"  - Error durante registrar_entrada_almacen: {e_stock}"); raise

            if commit_necesario:
                print(f"  - Realizando commit para Factura: {num_factura} (ID: {pedido_id})...")
                conn.commit(); print(f"  - Commit exitoso.")
                pedidos_procesados += 1
            else:
                print(f"  - No se realizaron cambios que requieran commit para Factura: {num_factura}.")
                pedidos_procesados += 1

        except Exception as e:
            print(f"ERROR procesando pedido Goma Nac - Factura: {num_factura}. Error: {e}")
            traceback.print_exc()
            if conn: print(f"  - Realizando rollback para Factura: {num_factura}..."); conn.rollback()
            pedidos_fallidos += 1
        finally:
            if conn: conn.close(); print(f"  - Conexión DB cerrada para Factura: {num_factura}.")

    print(f"\n--- Finalizado guardado/actualización DB Pedidos Goma Nacional ---")
    print(f"    Procesados con éxito: {pedidos_procesados}")
    print(f"    Fallidos: {pedidos_fallidos}")
    print("-" * 60)

# ==============================================================================
# FUNCIÓN CARGAR MERCANCIAS GOMA NACIONAL (Refactorizada para DB)
# ==============================================================================
def cargar_mercancias_goma() -> List[MercanciaNacionalGoma]:
    """
    Carga TODOS los Pedidos de Goma Nacional desde la base de datos.
    Reconstruye los objetos MercanciaNacionalGoma, incluyendo gastos y
    una representación SIMPLIFICADA del contenido basada en StockMateriasPrimas.
    """
    print("\n--- Cargando Pedidos Goma Nacional desde la DB ---")
    pedidos_cargados = []
    conn = None
    try:
        conn = conectar_db()
        if conn is None:
            print("Error: No se pudo conectar a la DB para cargar Pedidos Goma Nacional.")
            return []
        conn.row_factory = sqlite3.Row # Para obtener resultados como diccionarios
        cursor = conn.cursor()

        # 1. Obtener todos los pedidos de tipo NACIONAL
        cursor.execute("SELECT * FROM PedidosProveedores WHERE origen_tipo = 'NACIONAL'")
        pedidos_db = cursor.fetchall()
        print(f"  - Encontrados {len(pedidos_db)} pedidos de tipo NACIONAL.")

        for pedido_row in pedidos_db:
            pedido_dict = dict(pedido_row)
            pedido_id = pedido_dict['id']
            num_factura = pedido_dict['numero_factura']

            # Filtrar para procesar solo aquellos que podrían ser Goma Nacional
            # (Podríamos añadir una columna 'material_principal' a PedidosProveedores o inferir)
            # Por ahora, intentaremos cargar todos los NACIONAL y luego filtrar por tipo de contenido
            print(f"  - Procesando Pedido ID: {pedido_id}, Factura: {num_factura}")

            # 2. Obtener Gastos asociados
            cursor.execute("SELECT descripcion, coste_eur FROM GastosPedido WHERE pedido_id = ?", (pedido_id,))
            gastos_db = cursor.fetchall()
            gastos_lista_reconst = [{'descripcion': g['descripcion'], 'coste': g['coste_eur']} for g in gastos_db]

            # 3. Obtener Items de Stock (Materias Primas GOMA) asociados
            cursor.execute("""
                SELECT id, referencia_stock, espesor, ancho, largo_actual, subtipo_material,
                       coste_unitario_final, unidad_medida, status
                FROM StockMateriasPrimas
                WHERE pedido_id = ? AND material_tipo = 'GOMA'
            """, (pedido_id,))
            items_stock_db = cursor.fetchall()
            contenido_reconst = []
            es_goma_nacional = False # Bandera para confirmar si este pedido es de Goma

            if items_stock_db: # Solo procesar si hay items de GOMA asociados
                es_goma_nacional = True
                print(f"    - Encontrados {len(items_stock_db)} items de Goma en stock para este pedido.")
                for item_stock_row in items_stock_db:
                    item_stock_dict = dict(item_stock_row)
                    try:
                        # Crear objeto GomaNacional usando datos del stock.
                        # metro_lineal_eur original no está en stock, usamos coste_unitario_final.
                        goma_nac_obj = GomaNacional(
                            espesor=item_stock_dict.get('espesor', '?'),
                            ancho=item_stock_dict.get('ancho', 0.0),
                            largo=item_stock_dict.get('largo_actual', 0.0),
                            n_bobinas=1, # Asumir 1 por entrada de stock
                            metro_lineal_eur=item_stock_dict.get('coste_unitario_final', 0.0), # Aproximación
                            subtipo=item_stock_dict.get('subtipo_material', 'NORMAL')
                        )
                        # Los precios ya calculados (con gastos) están en el item de stock
                        goma_nac_obj.metro_lineal_euro_mas_gastos = item_stock_dict.get('coste_unitario_final')
                        # precio_total_euro y precio_total_euro_gastos serían más difíciles de reconstruir
                        # sin el n_bobinas original del lote y el largo original.
                        # Podríamos calcular precio_total_euro_gastos si asumimos largo_actual * coste_unitario_final
                        if goma_nac_obj.largo and goma_nac_obj.metro_lineal_euro_mas_gastos:
                             goma_nac_obj.precio_total_euro_gastos = goma_nac_obj.largo * goma_nac_obj.metro_lineal_euro_mas_gastos
                        else:
                             goma_nac_obj.precio_total_euro_gastos = None
                        goma_nac_obj.precio_total_euro = None # No se puede obtener fácilmente de stock

                        contenido_reconst.append(goma_nac_obj)
                    except Exception as e_reconst:
                        print(f"    * Error reconstruyendo item GomaNacional desde stock ID {item_stock_dict.get('id')}: {e_reconst}")
            else:
                # Si no hay items de GOMA en stock para este pedido NACIONAL, no lo consideramos Goma Nacional.
                print(f"    - No se encontraron items de Goma en stock para el pedido nacional {num_factura}. Se omite como Goma Nacional.")
                continue # Saltar al siguiente pedido_db

            # 4. Crear instancia de MercanciaNacionalGoma si se confirmó que es de Goma
            if es_goma_nacional:
                try:
                    pedido = MercanciaNacionalGoma(
                        fecha_pedido=pedido_dict.get('fecha_pedido'),
                        fecha_llegada=pedido_dict.get('fecha_llegada'),
                        proveedor=pedido_dict.get('proveedor'),
                        numero_factura=pedido_dict.get('numero_factura'),
                        observaciones=pedido_dict.get('observaciones'),
                        contenido_goma_nacional=contenido_reconst
                    )
                    # Re-asignar gastos (ya que el constructor de MercanciaNacional los inicializa vacíos)
                    pedido.gastos = gastos_lista_reconst
                    # Opcional: Recalcular precios basados en el contenido reconstruido y gastos
                    # Esto es importante si los precios en stock son solo el coste final
                    # y necesitamos que el objeto MercanciaNacionalGoma tenga sus propios cálculos.
                    # Si GomaNacional ya tiene su precio_total_euro calculado en su __init__
                    # (basado en el coste_unitario_final del stock), entonces podemos recalcular.
                    if pedido.contenido: # Solo si hay contenido para calcular
                         for item_cont in pedido.contenido: # Asegurar que los items tienen precio_total_euro
                              if not hasattr(item_cont, 'precio_total_euro') or item_cont.precio_total_euro is None:
                                   if item_cont.metro_lineal_eur and item_cont.largo and item_cont.n_bobinas:
                                        item_cont.precio_total_euro = item_cont.metro_lineal_eur * item_cont.largo * item_cont.n_bobinas
                         pedido.calcular_precios_finales()

                    pedidos_cargados.append(pedido)
                    print(f"    - Objeto MercanciaNacionalGoma creado para Factura: {num_factura}")
                except Exception as e_create:
                    print(f"Error creando objeto MercanciaNacionalGoma para Factura {num_factura}: {e_create}")
                    traceback.print_exc()

    except sqlite3.Error as e:
        print(f"Error SQLite cargando mercancías Goma Nacional: {e}")
    except Exception as e_gen:
        print(f"Error inesperado cargando mercancías Goma Nacional: {e_gen}")
        traceback.print_exc()
    finally:
        if conn:
            conn.close()
            print("Conexión DB cerrada después de cargar mercancías Goma Nacional.")

    print(f"--- Carga DB Pedidos Goma Nacional finalizada: {len(pedidos_cargados)} objetos creados ---")
    return pedidos_cargados
