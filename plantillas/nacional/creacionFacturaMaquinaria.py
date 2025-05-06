# plantilla_crear_maq_nacional.py
import datetime
import os

# --- Importaciones ---
try:
    from nacional.mercanciaNacionalMaquinaria import MercanciaNacionalMaquinaria, guardar_o_actualizar_mercancias_maquinaria
except ImportError as e:
    print(f"Error importando: {e}. Verifica nombres/rutas en nacional/mercanciaNacionalMaquinaria.py")
    exit()

# --- 1. DATOS DEL PEDIDO NACIONAL ---
fecha_hoy_str = datetime.date.today().strftime('%Y-%m-%d') # 2025-04-11

datos_pedido = {
    "fecha_pedido": "2025-04-11",
    "fecha_llegada": fecha_hoy_str,
    "proveedor": "Maquinaria Industrial Local",
    "numero_factura": "NAC-MAQ-001", # ¡Asegúrate que sea único!
    "observaciones": "Pedido nacional Maquinaria plantilla"
}

# --- 2. LISTA DE GASTOS ---
lista_gastos = [
    {"descripcion": "Transporte Especial Maq Nac", "coste": 350.00},
    {"descripcion": "Instalación y Pruebas", "coste": 600.00}
]

# --- 3. LISTA DE MÁQUINAS (Precio Total en EUR, Consumo opcional) ---
lista_maquinas = [
    {"codigo": "PREN-LOC-01", "modelo": "Prensa Taller 20T", "marca": "Marca Local", "precio_total_eur": 18500.00, "consumo_kw": 7.5},
    {"codigo": "SOLD-LOC-02", "modelo": "Soldadora Puntos", "marca": "Marca Local", "precio_total_eur": 5200.00} # Sin consumo especificado
]

# --- Ejecución ---
print(f"--- Creando Pedido Maquinaria Nacional: {datos_pedido['numero_factura']} ---")

# 4. Crear instancia
try:
    pedido = MercanciaNacionalMaquinaria(contenido_maquinaria_nacional=[], **datos_pedido)
except Exception as e:
    print(f"Error al crear MercanciaNacionalMaquinaria: {e}")
    exit()

# 5. Agregar Gastos
print("Agregando gastos...")
for gasto in lista_gastos:
    pedido.agregar_gasto(gasto["descripcion"], gasto["coste"])

# 6. Agregar Máquinas
print("Agregando máquinas...")
# Asegúrate que el método se llame así
agregar_maq_method = getattr(pedido, 'agregar_maquina', None)
if agregar_maq_method:
    for maq in lista_maquinas:
        agregar_maq_method(**maq) # Desempaqueta todo el diccionario
else:
    print("Error: Método 'agregar_maquina' no encontrado.")

# 7. Calcular Precios Finales (Solo calcula total con gastos)
print("Calculando precios finales...")
try:
    pedido.calcular_precios_finales()
except Exception as e:
    print(f"Error calculando precios finales: {e}")

# 8. Guardar/Actualizar
print(f"\nGuardando/Actualizando pedido {pedido.numero_factura}...")
try:
    guardar_o_actualizar_mercancias_maquinaria([pedido])
    print("¡Pedido Maquinaria Nacional guardado/actualizado!")
except Exception as e:
    print(f"Error al guardar: {e}")

print(f"--- Proceso Terminado para {datos_pedido['numero_factura']} ---")
print("-" * 30)