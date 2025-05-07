# borrar_contenido_almacen.py
import sqlite3
import os
import traceback

# Asume que este script está en la raíz del proyecto y 'almacen/database.py' existe
try:
    from almacen.database import DB_PATH, conectar_db
except ImportError:
    print("Error: No se pudo importar DB_PATH o conectar_db desde almacen.database.")
    print("Asegúrate de que el script se ejecuta desde la raíz del proyecto y que la SI,ruta a almacen/database.py es correcta.")
    # Fallback por si la importación falla, aunque es mejor que falle el script.
    # Esto es solo para que el resto del script no dé error de NameError inmediatamente.
    BASE_DIR_FALLBACK = os.path.dirname(os.path.abspath(__file__))
    DB_PATH_FALLBACK = os.path.join(BASE_DIR_FALLBACK, 'almacen', 'almacen.db')
    DB_PATH = DB_PATH_FALLBACK
    def conectar_db():
        print(f"ADVERTENCIA: Usando conexión de fallback a {DB_PATH}")
        if not os.path.exists(DB_PATH):
            print(f"ERROR CRÍTICO: El archivo de base de datos NO EXISTE en {DB_PATH}")
            return None
        try:
            return sqlite3.connect(DB_PATH)
        except sqlite3.Error as e:
            print(f"Error de fallback al conectar: {e}")
            return None
    # exit() # Podrías salir aquí si la importación es crítica

def borrar_todo_el_contenido():
    """
    Elimina todos los registros de las tablas de Pedidos, Gastos y Stock.
    La tabla Configuracion NO se toca.
    """
    tablas_a_vaciar = [
        "StockMateriasPrimas",
        "StockComponentes",
        "GastosPedido",
        "LineasPedido",       # Aunque su utilidad esté en evaluación, la vaciamos
        "PedidosProveedores"  # Esta es la "raíz" de muchos datos de stock
    ]

    print("="*60)
    print("¡¡¡ADVERTENCIA MUY IMPORTANTE!!!")
    print("Este script borrará TODOS los datos de las siguientes tablas:")
    for tabla in tablas_a_vaciar:
        print(f"  - {tabla}")
    print("La tabla 'Configuracion' (márgenes, etc.) NO será modificada.")
    print("Esta acción es IRREVERSIBLE.")
    print("Asegúrate de tener una COPIA DE SEGURIDAD de 'almacen.db' si los datos son valiosos.")
    print("="*60)

    confirmacion = input("Escribe 'SI, ESTOY SEGURO DE BORRAR' para continuar: ")

    if confirmacion != "SI, ESTOY SEGURO DE BORRAR":
        print("\nOperación cancelada por el usuario.")
        return

    print(f"\nProcediendo con el borrado de datos en: {DB_PATH}")
    conn = None
    try:
        conn = conectar_db()
        if conn is None:
            print("No se pudo establecer la conexión con la base de datos. Abortando.")
            return

        cursor = conn.cursor()
        total_filas_afectadas = 0

        for tabla in tablas_a_vaciar:
            try:
                print(f"  Borrando datos de la tabla: {tabla}...")
                cursor.execute(f"DELETE FROM {tabla}")
                filas_afectadas_tabla = cursor.rowcount
                print(f"    -> Se eliminaron {filas_afectadas_tabla if filas_afectadas_tabla != -1 else 'N/A'} filas de {tabla}.")
                if filas_afectadas_tabla > 0:
                    total_filas_afectadas += filas_afectadas_tabla
            except sqlite3.Error as e_tabla:
                print(f"    Error al borrar datos de la tabla {tabla}: {e_tabla}")
                # Podrías decidir si continuar con otras tablas o detener todo
                # conn.rollback()
                # return
            except Exception as e_inesperado_tabla:
                print(f"    Error inesperado borrando tabla {tabla}: {e_inesperado_tabla}")


        conn.commit()
        print("\n¡Borrado completado y cambios guardados (commit)!")
        if total_filas_afectadas > 0 :
             print(f"Total de filas eliminadas en todas las tablas afectadas: {total_filas_afectadas}")
        else:
             print("No se eliminaron filas (las tablas podrían haber estado ya vacías o hubo errores).")

    except sqlite3.Error as e:
        print(f"\nError de SQLite durante la operación de borrado: {e}")
        if conn:
            print("Se realizará rollback de los cambios no guardados.")
            conn.rollback()
        traceback.print_exc()
    except Exception as e_gen:
        print(f"\nError inesperado durante la operación de borrado: {e_gen}")
        if conn:
            print("Se realizará rollback de los cambios no guardados.")
            conn.rollback()
        traceback.print_exc()
    finally:
        if conn:
            conn.close()
            print("Conexión a la base de datos cerrada.")

if __name__ == "__main__":
    # Pequeña verificación de que DB_PATH parece correcto
    if not os.path.exists(DB_PATH):
        print(f"ERROR: No se encuentra el archivo de base de datos en la ruta esperada:")
        print(f"  {DB_PATH}")
        print("Asegúrate de que la ruta es correcta y de que el script se ejecuta")
        print("desde la carpeta raíz de 'gestion_contenedores'.")
    else:
        borrar_todo_el_contenido()