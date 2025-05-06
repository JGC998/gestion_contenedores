# plantilla_crear_goma.py
import datetime
import os

# --- Importaciones ---
# Asegúrate que las rutas y nombres son correctos según tu proyecto
try:
    from contenedor.contenedorGoma import ContenedorGoma, guardar_contenedores_goma
except ImportError:
    print("WARN: No se encontró 'guardar_contenedores_goma', intentando 'guardar_contenedores'")
    from contenedor.contenedorGoma import ContenedorGoma, guardar_contenedores as guardar_contenedores_goma

# --- 1. DEFINE AQUÍ LOS DATOS DEL CONTENEDOR ---
fecha_hoy_str = datetime.date.today().strftime('%Y-%m-%d') # Fecha actual: 2025-04-10

datos_contenedor = {
    "fecha_pedido": "2025-04-08",
    "fecha_llegada": fecha_hoy_str,
    "proveedor": "Proveedor Goma Plantilla",
    "numero_factura": "NEFD-25", # ¡Cambia esto por uno único!
    "observaciones": "Contenedor Goma creado desde plantilla",
    "valor_conversion": 0.89, # Cambia según el tipo de cambio real
    # 'gastos' y 'contenido_goma' se inicializan vacíos en la clase
}

# --- 2. DEFINE AQUÍ LA LISTA DE GASTOS ---
lista_gastos = [
    {"tipo": "SUPLIDOS", "descripcion": "Arancel Plantilla", "coste": 165.0},
    {"tipo": "EXENTO", "descripcion": "Flete Plantilla", "coste": 350.50},
    {"tipo": "SUJETO", "descripcion": "Seguro Plantilla", "coste": 95.0},
    {"tipo": "SUJETO", "descripcion": "THC Plantilla", "coste": 110.0},
    # Añade más diccionarios de gastos aquí si es necesario
]

# --- 3. DEFINE AQUÍ LA LISTA DE BOBINAS ---
lista_bobinas = [
    {
        "espesor": 6, "ancho": 1450, "largo": 110, "n_bobinas": 2,
        "metro_lineal_usd": 16.20
    },
    {
        "espesor": 4, "ancho": 1100, "largo": 180, "n_bobinas": 1,
        "metro_lineal_usd": 10.75
    },
    # Añade más diccionarios de bobinas aquí si es necesario
]

# --- Ejecución ---
print(f"--- Creando Contenedor Goma: {datos_contenedor['numero_factura']} ---")

# 4. Crear instancia (pasando los datos generales)
#    Se usan los valores por defecto de __init__ para gastos y contenido
try:
    contenedor = ContenedorGoma(gastos={}, contenido_goma=[], **datos_contenedor)
except TypeError as e:
     print(f"Error al crear ContenedorGoma. ¿Faltan argumentos o sobran?: {e}")
     exit() # Salir si no se puede crear

# 5. Agregar Gastos (desde la lista)
print("Agregando gastos...")
for gasto in lista_gastos:
    try:
        contenedor.agregar_gasto(gasto["tipo"], gasto["descripcion"], gasto["coste"])
        print(f"  + Gasto: {gasto['descripcion']}")
    except Exception as e:
        print(f"Error agregando gasto {gasto}: {e}")

# 6. Agregar Bobinas (desde la lista, usando el método específico)
print("Agregando bobinas...")
# Determinar el nombre correcto del método para añadir bobinas
agregar_bobina_method_name = None
if hasattr(contenedor, 'agregar_bobina_goma'):
    agregar_bobina_method_name = 'agregar_bobina_goma'
elif hasattr(contenedor, 'agregar_bobina'):
     agregar_bobina_method_name = 'agregar_bobina'

if not agregar_bobina_method_name:
    print("Error: No se encontró el método 'agregar_bobina_goma' o 'agregar_bobina' en ContenedorGoma.")
else:
    # Obtener el método real
    agregar_bobina_func = getattr(contenedor, agregar_bobina_method_name)
    for bobina_data in lista_bobinas:
        try:
            agregar_bobina_func(
                espesor=bobina_data["espesor"],
                ancho=bobina_data["ancho"],
                largo=bobina_data["largo"],
                n_bobinas=bobina_data["n_bobinas"],
                metro_lineal_usd=bobina_data["metro_lineal_usd"],
                valor_conversion=contenedor.valor_conversion # Pasar el valor del contenedor
            )
            print(f"  + Bobina: {bobina_data['espesor']}mm")
        except Exception as e:
             print(f"Error agregando bobina {bobina_data}: {e}")


# 7. Calcular Precios Finales
print("Calculando precios finales...")
try:
    contenedor.calcular_precios_finales()
except Exception as e:
     print(f"Error calculando precios finales: {e}")

# 8. Guardar el Contenedor
print(f"\nGuardando contenedor {contenedor.numero_factura}...")
try:
    guardar_contenedores_goma([contenedor]) # Guarda la instancia en una lista
    print("¡Contenedor guardado!")
except Exception as e:
    print(f"Error al guardar el contenedor: {e}")

print(f"--- Proceso Terminado para {datos_contenedor['numero_factura']} ---")