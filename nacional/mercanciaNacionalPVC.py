# nacional/mercanciaNacionalPVC.py
# ACTUALIZADO: guardar_o_actualizar usa DB. cargar_mercancias_pvc ahora lee de DB.

# --- Imports Necesarios ---
import sqlite3
import os
import traceback
from typing import List, Dict, Any
from abc import ABC

# Clases Base/Modelo
try:
    from .mercanciaNacional import MercanciaNacional
except ImportError:
    from nacional.mercanciaNacional import MercanciaNacional
try:
    from modelos import PVCNacional
except ImportError:
    print("Error: No se pudo importar 'PVCNacional' desde 'modelos'.")
    class PVCNacional: pass # Dummy

# Funciones de Base de Datos y Almacén
try:
    from almacen.database import conectar_db
    from almacen.gestion_almacen import registrar_entrada_almacen
except ImportError as e:
    print(f"ERROR CRÍTICO [mercanciaNacionalPVC]: No se pueden importar funciones de almacen: {e}")
    def conectar_db(): return None
    def registrar_entrada_almacen(obj, pid): pass

# --- Clase MercanciaNacionalPVC (Sin cambios) ---
class MercanciaNacionalPVC(MercanciaNacional, ABC):
    def __init__(self, fecha_pedido, fecha_llegada, proveedor, numero_factura, observaciones, contenido_pvc_nacional=None):
        super().__init__(fecha_pedido, fecha_llegada, proveedor, numero_factura, observaciones)
        self.contenido = contenido_pvc_nacional if contenido_pvc_nacional is not None else []

    def agregar_bobina_pvc(self, espesor, ancho, largo, n_bobinas, metro_lineal_eur, color):
        try:
            pvc_nac_obj = PVCNacional(
                espesor=espesor, ancho=ancho, largo=largo,
                n_bobinas=n_bobinas, metro_lineal_eur=metro_lineal_eur,
                color=color
            )
            self.contenido.append(pvc_nac_obj)
            print(f"  + Bobina PVC Nac. añadida: {espesor} {color} (Factura: {self.numero_factura})")
        except (ValueError, TypeError) as e:
             print(f"Error al crear objeto PVCNacional: {e}. Datos: {locals()}")
        except Exception as e_gen:
             print(f"Error inesperado al crear PVCNacional: {e_gen}. Datos: {locals()}")

    def calcular_precio_total_euro_gastos(self):
        items = self.contenido
        if not hasattr(self, 'calcular_total_gastos') or not callable(self.calcular_total_gastos):
             print("Error: Método 'calcular_total_gastos' no encontrado.");
             for item in items: item.precio_total_euro_gastos = None
             return
        gastos_repercutibles = self.calcular_total_gastos()
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

    def agregar_contenido(self, item_pvc_nacional: PVCNacional):
        if isinstance(item_pvc_nacional, PVCNacional): self.contenido.append(item_pvc_nacional)
        else: print(f"Error: Se intentó añadir un objeto que no es PVCNacional: {type(item_pvc_nacional)}")

    def eliminar_contenido(self, indice):
        try: del self.contenido[indice]
        except IndexError: print(f"Error: Índice {indice} fuera de rango al intentar eliminar PVCNac.")

    def editar_contenido(self, indice, item_pvc_nacional: PVCNacional):
        try:
            if not isinstance(item_pvc_nacional, PVCNacional): raise TypeError("El item proporcionado no es PVCNacional")
            self.contenido[indice] = item_pvc_nacional
        except IndexError: print(f"Error: Índice {indice} fuera de rango al intentar editar PVCNac.")
        except TypeError as e: print(f"Error al editar contenido PVCNac.: {e}")

# ==============================================================================
# FUNCIÓN GUARDAR/ACTUALIZAR MERCANCIA PVC NACIONAL (DB)
# ==============================================================================
def guardar_o_actualizar_mercancias_pvc(lista_pedidos: List[MercanciaNacionalPVC]):
    """
    Guarda o actualiza una lista de objetos MercanciaNacionalPVC en la base de datos.
    """
    print(f"\n--- Iniciando guardado/actualización DB para {len(lista_pedidos)} Pedido(s) PVC Nacional ---")
    pedidos_procesados = 0
    pedidos_fallidos = 0

    for pedido_obj in lista_pedidos:
        if not isinstance(pedido_obj, MercanciaNacionalPVC):
             print(f"Error: Objeto no es MercanciaNacionalPVC. Tipo: {type(pedido_obj)}. Saltando...")
             pedidos_fallidos += 1; continue
        if not hasattr(pedido_obj, 'numero_factura') or not pedido_obj.numero_factura:
            print("Error: Pedido nacional sin número de factura. Saltando...")
            pedidos_fallidos += 1; continue

        num_factura = pedido_obj.numero_factura
        print(f"\nProcesando Pedido PVC Nacional - Factura: {num_factura}")
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
                registrar_entrada_almacen(pedido_obj, pedido_id)
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
            print(f"ERROR procesando pedido PVC Nac - Factura: {num_factura}. Error: {e}")
            traceback.print_exc()
            if conn: print(f"  - Realizando rollback para Factura: {num_factura}..."); conn.rollback()
            pedidos_fallidos += 1
        finally:
            if conn: conn.close(); print(f"  - Conexión DB cerrada para Factura: {num_factura}.")

    print(f"\n--- Finalizado guardado/actualización DB Pedidos PVC Nacional ---")
    print(f"    Procesados con éxito: {pedidos_procesados}")
    print(f"    Fallidos: {pedidos_fallidos}")
    print("-" * 60)

# ==============================================================================
# FUNCIÓN CARGAR MERCANCIAS PVC NACIONAL (Refactorizada para DB)
# ==============================================================================
def cargar_mercancias_pvc() -> List[MercanciaNacionalPVC]:
    """
    Carga TODOS los Pedidos de PVC Nacional desde la base de datos.
    Reconstruye los objetos MercanciaNacionalPVC, incluyendo gastos y
    una representación SIMPLIFICADA del contenido basada en StockMateriasPrimas.
    """
    print("\n--- Cargando Pedidos PVC Nacional desde la DB ---")
    pedidos_cargados = []
    conn = None
    try:
        conn = conectar_db()
        if conn is None:
            print("Error: No se pudo conectar a la DB para cargar Pedidos PVC Nacional.")
            return []
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 1. Obtener pedidos de tipo NACIONAL
        cursor.execute("SELECT * FROM PedidosProveedores WHERE origen_tipo = 'NACIONAL'")
        pedidos_db = cursor.fetchall()
        print(f"  - Encontrados {len(pedidos_db)} pedidos de tipo NACIONAL.")

        for pedido_row in pedidos_db:
            pedido_dict = dict(pedido_row)
            pedido_id = pedido_dict['id']
            num_factura = pedido_dict['numero_factura']
            print(f"  - Procesando Pedido ID: {pedido_id}, Factura: {num_factura}")

            # 2. Obtener Gastos
            cursor.execute("SELECT descripcion, coste_eur FROM GastosPedido WHERE pedido_id = ?", (pedido_id,))
            gastos_db = cursor.fetchall()
            gastos_lista_reconst = [{'descripcion': g['descripcion'], 'coste': g['coste_eur']} for g in gastos_db]

            # 3. Obtener Items de Stock (PVC)
            cursor.execute("""
                SELECT id, referencia_stock, espesor, ancho, largo_actual, color,
                       coste_unitario_final, unidad_medida, status
                FROM StockMateriasPrimas
                WHERE pedido_id = ? AND material_tipo = 'PVC'
            """, (pedido_id,))
            items_stock_db = cursor.fetchall()
            contenido_reconst = []
            es_pvc_nacional = False

            if items_stock_db:
                es_pvc_nacional = True
                print(f"    - Encontrados {len(items_stock_db)} items de PVC en stock para este pedido.")
                for item_stock_row in items_stock_db:
                    item_stock_dict = dict(item_stock_row)
                    try:
                        pvc_nac_obj = PVCNacional(
                            espesor=item_stock_dict.get('espesor', '?'),
                            ancho=item_stock_dict.get('ancho', 0.0),
                            largo=item_stock_dict.get('largo_actual', 0.0),
                            n_bobinas=1, # Asumir 1
                            metro_lineal_eur=item_stock_dict.get('coste_unitario_final', 0.0), # Aproximación
                            color=item_stock_dict.get('color', '?')
                        )
                        pvc_nac_obj.metro_lineal_euro_mas_gastos = item_stock_dict.get('coste_unitario_final')
                        if pvc_nac_obj.largo and pvc_nac_obj.metro_lineal_euro_mas_gastos:
                             pvc_nac_obj.precio_total_euro_gastos = pvc_nac_obj.largo * pvc_nac_obj.metro_lineal_euro_mas_gastos
                        else: pvc_nac_obj.precio_total_euro_gastos = None
                        pvc_nac_obj.precio_total_euro = None
                        contenido_reconst.append(pvc_nac_obj)
                    except Exception as e_reconst:
                        print(f"    * Error reconstruyendo item PVCNacional desde stock ID {item_stock_dict.get('id')}: {e_reconst}")
            else:
                print(f"    - No se encontraron items de PVC en stock para el pedido nacional {num_factura}. Se omite como PVC Nacional.")
                continue

            # 4. Crear instancia de MercanciaNacionalPVC
            if es_pvc_nacional:
                try:
                    pedido = MercanciaNacionalPVC(
                        fecha_pedido=pedido_dict.get('fecha_pedido'),
                        fecha_llegada=pedido_dict.get('fecha_llegada'),
                        proveedor=pedido_dict.get('proveedor'),
                        numero_factura=pedido_dict.get('numero_factura'),
                        observaciones=pedido_dict.get('observaciones'),
                        contenido_pvc_nacional=contenido_reconst
                    )
                    pedido.gastos = gastos_lista_reconst
                    if pedido.contenido:
                         for item_cont in pedido.contenido:
                              if not hasattr(item_cont, 'precio_total_euro') or item_cont.precio_total_euro is None:
                                   if item_cont.metro_lineal_eur and item_cont.largo and item_cont.n_bobinas:
                                        item_cont.precio_total_euro = item_cont.metro_lineal_eur * item_cont.largo * item_cont.n_bobinas
                         pedido.calcular_precios_finales()
                    pedidos_cargados.append(pedido)
                    print(f"    - Objeto MercanciaNacionalPVC creado para Factura: {num_factura}")
                except Exception as e_create:
                    print(f"Error creando objeto MercanciaNacionalPVC para Factura {num_factura}: {e_create}")
                    traceback.print_exc()

    except sqlite3.Error as e:
        print(f"Error SQLite cargando mercancías PVC Nacional: {e}")
    except Exception as e_gen:
        print(f"Error inesperado cargando mercancías PVC Nacional: {e_gen}")
        traceback.print_exc()
    finally:
        if conn:
            conn.close()
            print("Conexión DB cerrada después de cargar mercancías PVC Nacional.")

    print(f"--- Carga DB Pedidos PVC Nacional finalizada: {len(pedidos_cargados)} objetos creados ---")
    return pedidos_cargados
