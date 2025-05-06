# probar_dar_baja.py

import sqlite3 # Importar sqlite3 por si acaso para row_factory o errores específicos
# Importar las funciones necesarias del módulo de almacén

    # Usamos la ruta correcta ahora que confirmamos que la carpeta es 'almacen'
# Importación recomendada en probar_dar_baja.py (si está en la carpeta raíz)
from almacen.gestion_almacen import consultar_stock, marcar_item_agotado



def imprimir_resumen_stock(items, titulo):
    """Función auxiliar para imprimir los resultados de forma legible."""
    print(f"\n--- {titulo} ({len(items)} item(s)) ---")
    if not items:
        print("   (No hay items)")
        return
    # Imprimir cabecera
    print(f"  {'ID':<4} | {'Tipo':<10} | {'Factura Origen':<15} | {'Largo (m)':<10} | {'Status':<10}")
    print(f"  {'-'*4}-+-{'-'*10}-+-{'-'*15}-+-{'-'*10}-+-{'-'*10}")
    for item in items:
        # Obtener valores usando .get() para seguridad
        id_stock = item.get('id_stock', 'N/A')
        mat_tipo = item.get('material_tipo', 'N/A')
        factura = item.get('origen_factura', 'N/A')
        largo = item.get('largo')
        largo_str = f"{largo:.1f}" if isinstance(largo, (int, float)) else "N/A"
        status = item.get('status', 'N/A')

        # Imprimir fila formateada
        print(f"  {id_stock:<4} | {mat_tipo:<10} | {factura:<15} | {largo_str:<10} | {status:<10}")
    print("-" * (len(titulo) + 4))


if __name__ == "__main__":
    print("--- INICIO PRUEBA: Marcar Item como Agotado ---")

    # 1. Buscar un item disponible para marcar
    print("\n1. Buscando items disponibles...")
    # Usamos try-except por si la consulta falla por alguna razón
    try:
        items_disponibles = consultar_stock(status='DISPONIBLE')
    except Exception as e:
        print(f"Error al consultar stock disponible: {e}")
        items_disponibles = [] # Asegurarse de que es una lista vacía si falla

    imprimir_resumen_stock(items_disponibles, "Items Disponibles ANTES")

    if not items_disponibles:
        print("\nNo hay items disponibles en el almacén para marcar como agotados.")
        print("Ejecuta primero un script de creación (ej: plantilla_crear_...) que registre entradas.")
        exit()

    # Seleccionar el primer item disponible de la lista
    item_a_marcar = items_disponibles[0]
    id_a_marcar = item_a_marcar.get('id_stock')

    if id_a_marcar is None:
        print("\nError: El primer item disponible no tiene un ID de Stock válido.")
        exit()

    print(f"\n2. Intentando marcar como AGOTADO el item con ID de Stock: {id_a_marcar}")

    # 2. Llamar a la función para marcar como agotado
    exito = False # Inicializar
    try:
        exito = marcar_item_agotado(id_a_marcar)
    except Exception as e:
         print(f"Error inesperado al llamar a marcar_item_agotado: {e}")


    if not exito:
        print("\nFallo al intentar marcar el item como agotado. Revisa los mensajes de error anteriores.")
        # Podríamos decidir salir o continuar para ver el estado actual
        # exit()

    # 3. Verificar los resultados volviendo a consultar
    print("\n3. Verificando estado del stock DESPUÉS de la operación:")

    # Consultar de nuevo los disponibles (el item marcado ya no debería estar)
    try:
        items_disponibles_despues = consultar_stock(status='DISPONIBLE')
    except Exception as e:
        print(f"Error al consultar stock disponible después: {e}")
        items_disponibles_despues = []
    imprimir_resumen_stock(items_disponibles_despues, "Items Disponibles DESPUÉS")

    # Consultar los agotados (el item marcado debería estar aquí)
    try:
        items_agotados = consultar_stock(status='AGOTADO')
    except Exception as e:
        print(f"Error al consultar stock agotado después: {e}")
        items_agotados = []
    imprimir_resumen_stock(items_agotados, "Items Agotados DESPUÉS")

    # Verificación final
    item_marcado_esta_agotado = any(item.get('id_stock') == id_a_marcar for item in items_agotados)
    item_marcado_sigue_disponible = any(item.get('id_stock') == id_a_marcar for item in items_disponibles_despues)

    print("\n--- RESULTADO DE LA PRUEBA ---")
    if item_marcado_esta_agotado and not item_marcado_sigue_disponible:
        print(f"¡ÉXITO! El item con ID {id_a_marcar} se marcó correctamente como AGOTADO.")
    elif not item_marcado_esta_agotado and not item_marcado_sigue_disponible:
         print(f"¡FALLO! El item con ID {id_a_marcar} DESAPARECIÓ o no se marcó como AGOTADO.")
    elif item_marcado_sigue_disponible:
         print(f"¡FALLO! El item con ID {id_a_marcar} TODAVÍA aparece como DISPONIBLE.")
    else:
        print(f"Resultado INCONCLUSO para el item con ID {id_a_marcar}. Revisa las listas manualmente.")
    print("-" * 30)