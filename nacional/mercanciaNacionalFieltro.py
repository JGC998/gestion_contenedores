# nacional/mercanciaNacionalFieltro.py
# ACTUALIZADO: guardar_o_actualizar usa DB. cargar_mercancias_fieltro ahora lee de DB.

# --- Imports Necesarios ---
import sqlite3
import os
import traceback
from typing import List, Dict, Any # Para type hints
from abc import ABC

# Clases Base/Modelo
try:
    # Asume que mercanciaNacional.py está en la misma carpeta
    from .mercanciaNacional import MercanciaNacional
except ImportError:
    # Si ejecutas desde la raíz del proyecto
    from nacional.mercanciaNacional import MercanciaNacional
try:
    # Asume que modelos.py está en la carpeta raíz
    from modelos import FieltroNacional
except ImportError:
    print("Error: No se pudo importar 'FieltroNacional' desde 'modelos'.")
    class FieltroNacional: pass # Dummy

# Funciones de Base de Datos y Almacén
try:
    # Asume que 'almacen' está al mismo nivel que 'nacional'
    # y que ejecutas desde la raíz del proyecto.
    from almacen.database import conectar_db
    # Aunque no se usa en cargar, es parte del módulo y podría serlo en el futuro
    from almacen.gestion_almacen import registrar_entrada_almacen
except ImportError as e:
    print(f"ERROR CRÍTICO [mercanciaNacionalFieltro]: No se pueden importar funciones de almacen: {e}")
    def conectar_db(): return None
    # Dummy que acepta dos argumentos ahora
    def registrar_entrada_almacen(obj, pid): pass

# --- Clase MercanciaNacionalFieltro (Sin cambios en lógica interna) ---
class MercanciaNacionalFieltro(MercanciaNacional, ABC):
    def __init__(self, fecha_pedido, fecha_llegada, proveedor, numero_factura, observaciones, contenido_fieltro_nacional=None):
        """Inicializa un registro de Fieltro Nacional."""
        super().__init__(fecha_pedido, fecha_llegada, proveedor, numero_factura, observaciones)
        self.contenido = contenido_fieltro_nacional if contenido_fieltro_nacional is not None else []

    def agregar_rollo_fieltro(self, espesor, ancho, largo, n_bobinas, metro_lineal_eur):
        """
        Crea un objeto FieltroNacional (que calcula su precio base en __init__)
        y lo añade a la lista de contenido.
        """
        try:
            # Crear instancia directamente del modelo FieltroNacional
            fieltro_nac_obj = FieltroNacional(
                espesor=espesor, ancho=ancho, largo=largo,
                n_bobinas=n_bobinas, metro_lineal_eur=metro_lineal_eur
                # No tiene color
            )
            self.contenido.append(fieltro_nac_obj)
            print(f"  + Rollo Fieltro Nac. añadido: {espesor} (Factura: {self.numero_factura})")
        except (ValueError, TypeError) as e:
             print(f"Error al crear objeto FieltroNacional: {e}. Datos: {locals()}")
        except Exception as e_gen:
             print(f"Error inesperado al crear FieltroNacional: {e_gen}. Datos: {locals()}")

    def calcular_precio_total_euro_gastos(self):
        """Calcula el precio total en euros con gastos para cada item FieltroNacional."""
        items = self.contenido
        if not hasattr(self, 'calcular_total_gastos') or not callable(self.calcular_total_gastos):
             print("Error: Método 'calcular_total_gastos' no encontrado en MercanciaNacional.");
             for item in items: item.precio_total_euro_gastos = None
             return

        gastos_repercutibles = self.calcular_total_gastos() # Suma TODOS los gastos simples
        total_coste_items = sum(getattr(item, 'precio_total_euro', 0) or 0 for item in items)

        if total_coste_items == 0:
            porcentaje_gastos = 0.0
        else:
            porcentaje_gastos = gastos_repercutibles / total_coste_items

        for item in items:
            precio_base = getattr(item, 'precio_total_euro', None)
            if isinstance(precio_base, (int, float)):
                item.precio_total_euro_gastos = precio_base * (1 + porcentaje_gastos)
            else:
                item.precio_total_euro_gastos = None

    def calcular_precios_finales(self):
       """Calcula TODOS los precios finales para Fieltro Nacional."""
       self.calcular_precio_total_euro_gastos()
       for item in self.contenido:
           coste_unitario_con_gastos = None
           precio_total_gastos = getattr(item, 'precio_total_euro_gastos', None)
           n_bobinas = getattr(item, 'n_bobinas', None) # n_bobinas se usa internamente aunque sean rollos
           largo = getattr(item, 'largo', None)

           if isinstance(precio_total_gastos, (int, float)) and \
              isinstance(n_bobinas, int) and n_bobinas > 0:
               coste_unitario_con_gastos = precio_total_gastos / n_bobinas

           if isinstance(coste_unitario_con_gastos, (int, float)) and \
              isinstance(largo, (int, float)) and largo != 0:
               item.metro_lineal_euro_mas_gastos = coste_unitario_con_gastos / largo
           else:
               item.metro_lineal_euro_mas_gastos = None

    def agregar_contenido(self, item_fieltro_nacional: FieltroNacional):
        """Añade un objeto FieltroNacional pre-creado al registro."""
        if isinstance(item_fieltro_nacional, FieltroNacional):
            self.contenido.append(item_fieltro_nacional)
        else:
            print(f"Error: Se intentó añadir un objeto que no es FieltroNacional: {type(item_fieltro_nacional)}")

    def eliminar_contenido(self, indice):
        """Elimina un item de Fieltro Nacional por su índice."""
        try:
            del self.contenido[indice]
        except IndexError:
            print(f"Error: Índice {indice} fuera de rango al intentar eliminar FieltroNac.")

    def editar_contenido(self, indice, item_fieltro_nacional: FieltroNacional):
        """Reemplaza un item de Fieltro Nacional en el índice dado."""
        try:
            if not isinstance(item_fieltro_nacional, FieltroNacional):
                 raise TypeError("El item proporcionado no es de tipo FieltroNacional")
            self.contenido[indice] = item_fieltro_nacional
        except IndexError:
            print(f"Error: Índice {indice} fuera de rango al intentar editar FieltroNac.")
        except TypeError as e:
             print(f"Error al editar contenido FieltroNac.: {e}")

# ==============================================================================
# FUNCIÓN GUARDAR/ACTUALIZAR MERCANCIA FIELTRO NACIONAL (DB)
# ==============================================================================
def guardar_o_actualizar_mercancias_fieltro(lista_pedidos: List[MercanciaNacionalFieltro]):
    """
    Guarda o actualiza una lista de objetos MercanciaNacionalFieltro en la base de datos.
    """
    print(f"\n--- Iniciando guardado/actualización DB para {len(lista_pedidos)} Pedido(s) Fieltro Nacional ---")
    pedidos_procesados = 0
    pedidos_fallidos = 0

    for pedido_obj in lista_pedidos:
        if not isinstance(pedido_obj, MercanciaNacionalFieltro):
             print(f"Error: Objeto no es MercanciaNacionalFieltro. Tipo: {type(pedido_obj)}. Saltando...")
             pedidos_fallidos += 1; continue
        if not hasattr(pedido_obj, 'numero_factura') or not pedido_obj.numero_factura:
            print("Error: Pedido nacional sin número de factura. Saltando...")
            pedidos_fallidos += 1; continue

        num_factura = pedido_obj.numero_factura
        print(f"\nProcesando Pedido Fieltro Nacional - Factura: {num_factura}")
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
            print(f"ERROR procesando pedido Fieltro Nac - Factura: {num_factura}. Error: {e}")
            traceback.print_exc()
            if conn: print(f"  - Realizando rollback para Factura: {num_factura}..."); conn.rollback()
            pedidos_fallidos += 1
        finally:
            if conn: conn.close(); print(f"  - Conexión DB cerrada para Factura: {num_factura}.")

    print(f"\n--- Finalizado guardado/actualización DB Pedidos Fieltro Nacional ---")
    print(f"    Procesados con éxito: {pedidos_procesados}")
    print(f"    Fallidos: {pedidos_fallidos}")
    print("-" * 60)



# FUNCIÓN CARGAR MERCANCIAS FIELTRO NACIONAL (Refactorizada para DB con Filtros/Orden)
# ==============================================================================
def cargar_mercancias_fieltro(filtros=None) -> List[MercanciaNacionalFieltro]:
    """
    Carga Pedidos Nacionales de Fieltro desde la DB, aplicando filtros y ordenando por fecha_pedido DESC.
    Reconstruye los objetos incluyendo gastos y contenido SIMPLIFICADO desde Stock.
    """
    print("\n--- Cargando Pedidos Fieltro Nacional desde la DB ---")
    if filtros and any(filtros.values()): print(f"  Aplicando filtros: {filtros}")

    pedidos_cargados = []
    conn = None
    try:
        conn = conectar_db()
        if conn is None:
            print("Error: No se pudo conectar a la DB para cargar Pedidos Fieltro Nacional.")
            return []
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # --- Construcción de la consulta SQL ---
        sql_base = "SELECT * FROM PedidosProveedores"
        where_clauses = ["origen_tipo = 'NACIONAL'"]
        params = []

        if filtros:
            if 'numero_factura' in filtros and filtros['numero_factura']:
                where_clauses.append("UPPER(numero_factura) LIKE ?")
                params.append(f"%{str(filtros['numero_factura']).upper()}%")
            if 'proveedor' in filtros and filtros['proveedor']:
                where_clauses.append("UPPER(proveedor) LIKE ?")
                params.append(f"%{str(filtros['proveedor']).upper()}%")
            # Filtro 'material' implícito

        sql_query = sql_base
        if where_clauses:
            sql_query += " WHERE " + " AND ".join(where_clauses)
        sql_query += " ORDER BY fecha_pedido DESC"
        # --- Fin construcción SQL ---

        print(f"  Ejecutando SQL: {sql_query} con params: {params}")
        cursor.execute(sql_query, tuple(params))
        pedidos_db = cursor.fetchall()
        print(f"  - Encontrados {len(pedidos_db)} pedidos tipo NACIONAL (Fieltro) con filtros aplicados.")

        for pedido_row in pedidos_db:
            pedido_dict = dict(pedido_row)
            pedido_id = pedido_dict['id']
            num_factura = pedido_dict['numero_factura']
            print(f"  - Procesando Pedido ID: {pedido_id}, Factura: {num_factura}")

            # 2. Obtener Gastos (Nacional)
            cursor.execute("SELECT descripcion, coste_eur FROM GastosPedido WHERE pedido_id = ?", (pedido_id,))
            gastos_db = cursor.fetchall()
            gastos_lista_reconst = [{'descripcion': g['descripcion'], 'coste': g['coste_eur']} for g in gastos_db]

            # 3. Obtener Items de Stock (FIELTRO)
            cursor.execute("""
                SELECT id, referencia_stock, espesor, ancho, largo_actual,
                       coste_unitario_final, unidad_medida, status
                FROM StockMateriasPrimas
                WHERE pedido_id = ? AND material_tipo = 'FIELTRO'
            """, (pedido_id,))
            items_stock_db = cursor.fetchall()
            contenido_reconst = []
            es_fieltro_nacional = bool(items_stock_db)

            if not es_fieltro_nacional:
                print(f"    - Advertencia: Pedido Nacional ID {pedido_id} ({num_factura}) no tiene items de FIELTRO en stock. Omitiendo.")
                continue

            print(f"    - Encontrados {len(items_stock_db)} items de Fieltro en stock para este pedido.")
            for item_stock_row in items_stock_db:
                item_stock_dict = dict(item_stock_row)
                try:
                    # Crear objeto FieltroNacional simplificado
                    fieltro_nac_obj = FieltroNacional(
                        espesor=item_stock_dict.get('espesor', '?'),
                        ancho=item_stock_dict.get('ancho', 0.0),
                        largo=item_stock_dict.get('largo_actual', 0.0),
                        n_bobinas=1, # Aproximación
                        metro_lineal_eur=item_stock_dict.get('coste_unitario_final', 0.0) or 0.0 # Aproximación
                    )
                    fieltro_nac_obj.metro_lineal_euro_mas_gastos = item_stock_dict.get('coste_unitario_final')
                    # precio_total_euro se calcula en __init__
                    fieltro_nac_obj.precio_total_euro_gastos = None # No reconstruible
                    fieltro_nac_obj.metro_lineal_usd = None
                    contenido_reconst.append(fieltro_nac_obj)
                except Exception as e_reconst:
                    print(f"    * Error reconstruyendo item FieltroNacional desde stock ID {item_stock_dict.get('id')}: {e_reconst}")

            # 4. Crear instancia de MercanciaNacionalFieltro
            if es_fieltro_nacional:
                try:
                    pedido = MercanciaNacionalFieltro(
                        fecha_pedido=pedido_dict.get('fecha_pedido'),
                        fecha_llegada=pedido_dict.get('fecha_llegada'),
                        proveedor=pedido_dict.get('proveedor'),
                        numero_factura=pedido_dict.get('numero_factura'),
                        observaciones=pedido_dict.get('observaciones'),
                        contenido_fieltro_nacional=contenido_reconst
                    )
                    pedido.gastos = gastos_lista_reconst
                    if pedido.contenido:
                        pedido.calcular_precios_finales()
                    pedidos_cargados.append(pedido)
                    print(f"    - Objeto MercanciaNacionalFieltro creado para Factura: {num_factura}")
                except Exception as e_create:
                    print(f"Error creando objeto MercanciaNacionalFieltro para Factura {num_factura}: {e_create}")
                    traceback.print_exc()

    except sqlite3.Error as e:
        print(f"Error SQLite cargando mercancías Fieltro Nacional: {e}")
    except Exception as e_gen:
        print(f"Error inesperado cargando mercancías Fieltro Nacional: {e_gen}")
        traceback.print_exc()
    finally:
        if conn:
            conn.close()
            print("Conexión DB cerrada después de cargar mercancías Fieltro Nacional.")

    print(f"--- Carga DB Pedidos Fieltro Nacional finalizada: {len(pedidos_cargados)} objetos creados ---")
    return pedidos_cargados