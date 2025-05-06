# plantilla_crear_fieltro_nacional.py
import datetime
import os

# --- Importaciones ---
try:
    from nacional.mercanciaNacionalFieltro import MercanciaNacionalFieltro, guardar_o_actualizar_mercancias_fieltro
except ImportError as e:
    print(f"Error importando: {e}. Verifica nombres/rutas en nacional/mercanciaNacionalFieltro.py")
    exit()

# --- 1. DATOS DEL PEDIDO NACIONAL ---
fecha_hoy_str = datetime.date.today().strftime('%Y-%m-%d') # 2025-04-11

datos_pedido = {
    "fecha_pedido": "2025-04-11",
    "fecha_llegada": fecha_hoy_str,
    "proveedor": "Fieltros Artesanos S.A.",
    "numero_factura": "NAC-FIE-001", # ¡Asegúrate que sea único!
    "observaciones": "Pedido nacional Fieltro plantilla"
}

# --- 2. LISTA DE GASTOS ---
lista_gastos = [
    {"descripcion": "Envío Fieltro", "coste": 40.00}
]

# --- 3. LISTA DE ROLLOS (Precio en EUR) ---
lista_rollos = [
    {"espesor": 2, "ancho": 900, "largo": 45, "n_bobinas": 15, "metro_lineal_eur": 3.50},
    {"espesor": 4, "ancho": 1100, "largo": 30, "n_bobinas": 10, "metro_lineal_eur": 5.20}
]

# --- Ejecución ---
print(f"--- Creando Pedido Fieltro Nacional: {datos_pedido['numero_factura']} ---")

# 4. Crear instancia
try:
    pedido = MercanciaNacionalFieltro(contenido_fieltro_nacional=[], **datos_pedido)
except Exception as e:
    print(f"Error al crear MercanciaNacionalFieltro: {e}")
    exit()

# 5. Agregar Gastos
print("Agregando gastos...")
for gasto in lista_gastos:
    pedido.agregar_gasto(gasto["descripcion"], gasto["coste"])

# 6. Agregar Rollos
print("Agregando rollos...")
# Asegúrate que el método se llame así
agregar_rollo_method = getattr(pedido, 'agregar_rollo_fieltro', None)
if agregar_rollo_method:
    for rollo in lista_rollos:
        agregar_rollo_method(**rollo)
else:
    print("Error: Método 'agregar_rollo_fieltro' no encontrado.")

# 7. Calcular Precios Finales
print("Calculando precios finales...")
try:
    pedido.calcular_precios_finales()
except Exception as e:
    print(f"Error calculando precios finales: {e}")

# 8. Guardar/Actualizar
print(f"\nGuardando/Actualizando pedido {pedido.numero_factura}...")
try:
    guardar_o_actualizar_mercancias_fieltro([pedido])
    print("¡Pedido Fieltro Nacional guardado/actualizado!")
except Exception as e:
    print(f"Error al guardar: {e}")

print(f"--- Proceso Terminado para {datos_pedido['numero_factura']} ---")
print("-" * 30)