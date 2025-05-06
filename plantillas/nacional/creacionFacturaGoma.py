# plantilla_crear_goma_nacional.py
import datetime
import os

# --- Importaciones ---
try:
    from nacional.mercanciaNacionalGoma import MercanciaNacionalGoma, guardar_o_actualizar_mercancias_goma
except ImportError as e:
    print(f"Error importando: {e}. Verifica nombres/rutas en nacional/mercanciaNacionalGoma.py")
    exit()

# --- 1. DATOS DEL PEDIDO NACIONAL ---
fecha_hoy_str = datetime.date.today().strftime('%Y-%m-%d') # 2025-04-11

datos_pedido = {
    "fecha_pedido": "2025-04-11",
    "fecha_llegada": fecha_hoy_str,
    "proveedor": "Gomas del Ebro S.L.",
    "numero_factura": "NAC-GOM-001", # ¡Asegúrate que sea único!
    "observaciones": "Pedido nacional Goma plantilla"
    # 'gastos' y 'contenido' se inicializan en la clase
}

# --- 2. LISTA DE GASTOS (Formato simple) ---
lista_gastos = [
    {"descripcion": "Portes Goma Nac.", "coste": 65.00},
    {"descripcion": "Embalaje Especial", "coste": 15.50}
    # Añade más gastos si es necesario
]

# --- 3. LISTA DE BOBINAS (Precio en EUR) ---
lista_bobinas = [
    {"espesor": 5, "ancho": 1200, "largo": 80, "n_bobinas": 3, "metro_lineal_eur": 18.50},
    {"espesor": 8, "ancho": 1000, "largo": 50, "n_bobinas": 2, "metro_lineal_eur": 25.75}
]

# --- Ejecución ---
print(f"--- Creando Pedido Goma Nacional: {datos_pedido['numero_factura']} ---")

# 4. Crear instancia
try:
    pedido = MercanciaNacionalGoma(contenido_goma_nacional=[], **datos_pedido)
except Exception as e:
    print(f"Error al crear MercanciaNacionalGoma: {e}")
    exit()

# 5. Agregar Gastos
print("Agregando gastos...")
for gasto in lista_gastos:
    pedido.agregar_gasto(gasto["descripcion"], gasto["coste"])

# 6. Agregar Bobinas
print("Agregando bobinas...")
# Asegúrate que el método se llame así
agregar_bobina_method = getattr(pedido, 'agregar_bobina', None)
if agregar_bobina_method:
    for bobina in lista_bobinas:
        agregar_bobina_method(**bobina)
else:
    print("Error: Método 'agregar_bobina' no encontrado.")

# 7. Calcular Precios Finales
print("Calculando precios finales...")
try:
    pedido.calcular_precios_finales()
except Exception as e:
    print(f"Error calculando precios finales: {e}")

# 8. Guardar/Actualizar
print(f"\nGuardando/Actualizando pedido {pedido.numero_factura}...")
try:
    guardar_o_actualizar_mercancias_goma([pedido])
    print("¡Pedido Goma Nacional guardado/actualizado!")
except Exception as e:
    print(f"Error al guardar: {e}")

# Al final de plantilla_crear_goma.py, por ejemplo:
from almacen.gestion_almacen import registrar_entrada_almacen # Importar la función
# ... (después de guardar_o_actualizar_...)
print("Registrando entrada en almacén...")
registrar_entrada_almacen(pedido) # Pasar el objeto ya calculado


print(f"--- Proceso Terminado para {datos_pedido['numero_factura']} ---")
print("-" * 30)