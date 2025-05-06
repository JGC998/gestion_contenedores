# plantilla_crear_pvc_nacional.py
import datetime
import os

# --- Importaciones ---
try:
    from nacional.mercanciaNacionalPVC import MercanciaNacionalPVC, guardar_o_actualizar_mercancias_pvc
except ImportError as e:
    print(f"Error importando: {e}. Verifica nombres/rutas en nacional/mercanciaNacionalPVC.py")
    exit()

# --- 1. DATOS DEL PEDIDO NACIONAL ---
fecha_hoy_str = datetime.date.today().strftime('%Y-%m-%d') # 2025-04-11

datos_pedido = {
    "fecha_pedido": "2025-04-11",
    "fecha_llegada": fecha_hoy_str,
    "proveedor": "Plasticos Iberia",
    "numero_factura": "NAC-PVC-001", # ¡Asegúrate que sea único!
    "observaciones": "Pedido nacional PVC plantilla"
}

# --- 2. LISTA DE GASTOS ---
lista_gastos = [
    {"descripcion": "Transporte Urgente PVC", "coste": 95.00},
    {"descripcion": "Manipulación PVC", "coste": 30.00}
]

# --- 3. LISTA DE BOBINAS (Precio en EUR, incluye color) ---
lista_bobinas = [
    {"espesor": 1, "ancho": 1500, "largo": 200, "n_bobinas": 5, "metro_lineal_eur": 8.10, "color": "Rojo"},
    {"espesor": 2, "ancho": 1300, "largo": 150, "n_bobinas": 4, "metro_lineal_eur": 9.75, "color": "Azul"}
]

# --- Ejecución ---
print(f"--- Creando Pedido PVC Nacional: {datos_pedido['numero_factura']} ---")

# 4. Crear instancia
try:
    pedido = MercanciaNacionalPVC(contenido_pvc_nacional=[], **datos_pedido)
except Exception as e:
    print(f"Error al crear MercanciaNacionalPVC: {e}")
    exit()

# 5. Agregar Gastos
print("Agregando gastos...")
for gasto in lista_gastos:
    pedido.agregar_gasto(gasto["descripcion"], gasto["coste"])

# 6. Agregar Bobinas
print("Agregando bobinas...")
# Asegúrate que el método se llame así
agregar_bobina_method = getattr(pedido, 'agregar_bobina_pvc', None)
if agregar_bobina_method:
    for bobina in lista_bobinas:
        agregar_bobina_method(**bobina)
else:
    print("Error: Método 'agregar_bobina_pvc' no encontrado.")

# 7. Calcular Precios Finales
print("Calculando precios finales...")
try:
    pedido.calcular_precios_finales()
except Exception as e:
    print(f"Error calculando precios finales: {e}")

# 8. Guardar/Actualizar
print(f"\nGuardando/Actualizando pedido {pedido.numero_factura}...")
try:
    guardar_o_actualizar_mercancias_pvc([pedido])
    print("¡Pedido PVC Nacional guardado/actualizado!")
except Exception as e:
    print(f"Error al guardar: {e}")

print(f"--- Proceso Terminado para {datos_pedido['numero_factura']} ---")
print("-" * 30)