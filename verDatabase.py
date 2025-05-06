# ver_contenido_db.py
# Script para mostrar el contenido de las tablas principales de la base de datos almacen.db

import sqlite3
import os
import traceback

# --- Configuración (Asegúrate que coincida con database.py) ---
DB_FILENAME = 'almacen.db'
# Construye la ruta a la DB asumiendo que este script está en la raíz del proyecto
# y 'almacen' es una subcarpeta.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'almacen', DB_FILENAME)

def conectar_db_local():
    """Establece conexión con la base de datos SQLite localmente."""
    try:
        print(f"Intentando conectar a: {DB_PATH}")
        if not os.path.exists(DB_PATH):
            print(f"ERROR: El archivo de base de datos no existe en la ruta: {DB_PATH}")
            print("      Asegúrate de que la ruta es correcta y de que has ejecutado")
            print("      primero 'almacen/database.py' para crear la base de datos.")
            return None
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row # Para acceder a las columnas por nombre
        print("Conexión a DB establecida.")
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos SQLite: {e}")
        return None
    except Exception as ex:
        print(f"Error inesperado al conectar a la DB: {ex}")
        return None

def mostrar_tabla(cursor: sqlite3.Cursor, nombre_tabla: str):
    """Selecciona todos los datos de una tabla y los imprime."""
    print(f"\n--- Contenido de la Tabla: {nombre_tabla} ---")
    try:
        cursor.execute(f"SELECT * FROM {nombre_tabla}")
        filas = cursor.fetchall()

        if not filas:
            print("   (La tabla está vacía o no existe)")
            return

        # Obtener nombres de columnas
        nombres_columnas = [description[0] for description in cursor.description]
        print(" | ".join(nombres_columnas))
        print("-" * (sum(len(col) for col in nombres_columnas) + (len(nombres_columnas) - 1) * 3)) # Separador

        for fila in filas:
            valores_fila = [str(fila[col] if fila[col] is not None else 'NULL') for col in nombres_columnas]
            print(" | ".join(valores_fila))

    except sqlite3.Error as e:
        print(f"   Error al leer la tabla {nombre_tabla}: {e}")
    except Exception as ex:
        print(f"   Error inesperado leyendo la tabla {nombre_tabla}: {ex}")

if __name__ == "__main__":
    print("="*50)
    print("===== VISOR DE CONTENIDO DE LA BASE DE DATOS =====")
    print("="*50)

    conn = conectar_db_local()

    if conn:
        cursor = conn.cursor()
        tablas_a_mostrar = [
            "PedidosProveedores",
            "GastosPedido",
            "StockMateriasPrimas",
            "StockComponentes",
            "Configuracion"
            # Añade aquí otras tablas que quieras ver, como las de Presupuestos si las mantuviste
        ]

        for tabla in tablas_a_mostrar:
            mostrar_tabla(cursor, tabla)

        print("\n" + "="*50)
        print("Visualización completada.")
        print("="*50)
        conn.close()
        print("Conexión a DB cerrada.")
    else:
        print("\nNo se pudo establecer conexión con la base de datos.")
        print("Verifica la ruta y que el archivo 'almacen.db' existe y es accesible.")

