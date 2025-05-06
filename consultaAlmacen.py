# probar_consulta_almacen.py

# Importar la función de consulta
from almacen.gestion_almacen import consultar_stock

def mostrar_resultados(items_stock):
    """Función auxiliar para imprimir los resultados de forma legible."""
    if not items_stock:
        print(">> No se encontraron items de stock con los filtros aplicados.")
        return

    print(f"\n--- {len(items_stock)} Item(s) Encontrado(s) ---")
    for item in items_stock:
        print("-" * 20)
        print(f"ID Stock: {item.get('id_stock')}")
        print(f"Material: {item.get('material_tipo')} (Status: {item.get('status')})")
        print(f"Origen: {item.get('origen_tipo')} - Factura: {item.get('origen_factura')}")
        print(f"Entrada: {item.get('fecha_entrada_almacen')}")

        # Mostrar detalles según el tipo
        if item.get('material_tipo') in ['GOMA', 'PVC', 'FIELTRO']:
            print(f"  Espesor: {item.get('espesor')}")
            print(f"  Ancho: {item.get('ancho')}mm")
            print(f"  Largo: {item.get('largo')}m ")
            print(f"  Nº Bobinas: {item.get('n_bobinas_lote')}")
            
            if item.get('color'): print(f"  Color: {item.get('color')}")

            coste_m = item.get('coste_metro_lineal_final')
            print(f"  Coste/m Final: {coste_m:.4f} €" if coste_m is not None else "  Coste/m Final: N/A")

            coste_total = item.get('coste_total_final')
            print(f"  Total bobinas: {coste_total:.4f} €" if coste_total is not None else "  Total bobinas Final: N/A")
            
        #Maquinaria
        elif item.get('material_tipo') == 'MAQUINARIA':
            print(f"  Máquina: {item.get('codigo_maq')} - {item.get('modelo_maq')} ({item.get('marca_maq')})")
            consumo = item.get('consumo_kw')
            print(f"  Consumo: {consumo:.2f} kW" if consumo is not None else "  Consumo: N/A")
            coste_t = item.get('coste_total_final')
            print(f"  Coste Total Final: {coste_t:.2f} €" if coste_t is not None else "  Coste Total Final: N/A")



    print("-" * 20)


if __name__ == "__main__":
    # --- PRUEBAS ---
    # (Descomenta las llamadas que quieras probar)

    # 1. Ver TODO el stock
    print("\n*** CONSULTANDO TODO EL STOCK ***")
    todo_stock = consultar_stock()
    mostrar_resultados(todo_stock)

    # 2. Ver solo Goma DISPONIBLE
    # print("\n*** CONSULTANDO GOMA DISPONIBLE ***")
    # goma_disponible = consultar_stock(material_tipo='GOMA', status='DISPONIBLE')
    # mostrar_resultados(goma_disponible)

    # 3. Ver items de una factura específica
    # factura_origen = "PCV-DEMO-557" # Cambia por una factura que sepas que existe
    # print(f"\n*** CONSULTANDO ITEMS DE FACTURA: {factura_origen} ***")
    # items_factura = consultar_stock(origen_factura=factura_origen)
    # mostrar_resultados(items_factura)

    # 4. Ver Maquinaria Agotada (si tuvieras alguna)
    # print("\n*** CONSULTANDO MAQUINARIA AGOTADA ***")
    # maq_agotada = consultar_stock(material_tipo='MAQUINARIA', status='AGOTADO')
    # mostrar_resultados(maq_agotada)