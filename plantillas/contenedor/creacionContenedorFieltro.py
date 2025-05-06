# plantilla_crear_fieltro.py
import datetime
import os

# --- Importaciones ---
# Asegúrate que las rutas y nombres son correctos según tu proyecto
try:
    # Intenta importar la clase y la función de guardado específicas de Fieltro
    from contenedor.contenedorFieltro import ContenedorFieltro, guardar_contenedores_fieltro
except ImportError:
    print("WARN: No se encontró 'guardar_contenedores_fieltro'. Verifica el nombre en contenedorFieltro.py.")
    exit() # Salir si no se puede importar lo necesario

# --- 1. DEFINE AQUÍ LOS DATOS DEL CONTENEDOR FIELTRO ---
fecha_hoy_str = datetime.date.today().strftime('%Y-%m-%d') # Fecha actual: 2025-04-10

datos_contenedor_fieltro = {
    "fecha_pedido": "2025-04-10",
    "fecha_llegada": fecha_hoy_str,
    "proveedor": "Textiles Industriales Felt",
    "numero_factura": "FEL-PLANT-00Z", # ¡Cambia esto por uno único!
    "observaciones": "Contenedor Fieltro creado desde plantilla",
    "valor_conversion": 0.912, # Cambia según el tipo de cambio real
    # 'gastos' y 'contenido_fieltro' se inicializan vacíos en la clase
}

# --- 2. DEFINE AQUÍ LA LISTA DE GASTOS ---
lista_gastos_fieltro = [
    {"tipo": "SUPLIDOS", "descripcion": "Tasa Textil", "coste": 77.80},
    {"tipo": "EXENTO", "descripcion": "Transporte Contenedor Fieltro", "coste": 390.00},
    {"tipo": "SUJETO", "descripcion": "Seguro Mercancía Fieltro", "coste": 65.25},
    # Añade más diccionarios de gastos aquí si es necesario
]

# --- 3. DEFINE AQUÍ LA LISTA DE ROLLOS DE FIELTRO ---
lista_rollos_fieltro = [
    {
        "espesor": 3, "ancho": 1000, "largo": 55, "n_bobinas": 40,
        "metro_lineal_usd": 2.95
    },
    {
        "espesor": 5, "ancho": 1500, "largo": 35, "n_bobinas": 22,
        "metro_lineal_usd": 4.15
    },
    # Añade más diccionarios de rollos aquí si es necesario
]

# --- Ejecución ---
print(f"--- Creando Contenedor Fieltro: {datos_contenedor_fieltro['numero_factura']} ---")

# 4. Crear instancia (pasando los datos generales)
try:
    contenedor = ContenedorFieltro(gastos={}, contenido_fieltro=[], **datos_contenedor_fieltro)
except TypeError as e:
     print(f"Error al crear ContenedorFieltro. ¿Faltan argumentos o sobran?: {e}")
     exit()

# 5. Agregar Gastos (desde la lista)
print("Agregando gastos...")
for gasto in lista_gastos_fieltro:
    try:
        contenedor.agregar_gasto(gasto["tipo"], gasto["descripcion"], gasto["coste"])
        print(f"  + Gasto: {gasto['descripcion']}")
    except Exception as e:
        print(f"Error agregando gasto {gasto}: {e}")

# 6. Agregar Rollos (desde la lista, usando el método específico de Fieltro)
print("Agregando rollos de fieltro...")
# Asegúrate que el método para añadir rollos se llame así en ContenedorFieltro.py
agregar_rollo_method_name = 'agregar_rollo_fieltro' # Ajusta si lo llamaste diferente

if not hasattr(contenedor, agregar_rollo_method_name):
    print(f"Error: No se encontró el método '{agregar_rollo_method_name}' en ContenedorFieltro.")
else:
    agregar_rollo_func = getattr(contenedor, agregar_rollo_method_name)
    for rollo_data in lista_rollos_fieltro:
        try:
            agregar_rollo_func(
                espesor=rollo_data["espesor"],
                ancho=rollo_data["ancho"],
                largo=rollo_data["largo"],
                n_bobinas=rollo_data["n_bobinas"],
                metro_lineal_usd=rollo_data["metro_lineal_usd"],
                # Fieltro no tiene 'color' como PVC en este ejemplo
                valor_conversion=contenedor.valor_conversion # Pasar el valor del contenedor
            )
            print(f"  + Rollo: {rollo_data['espesor']}mm")
        except Exception as e:
             print(f"Error agregando rollo Fieltro {rollo_data}: {e}")


# 7. Calcular Precios Finales
print("Calculando precios finales...")
try:
    contenedor.calcular_precios_finales()
except Exception as e:
     print(f"Error calculando precios finales: {e}")

# 8. Guardar el Contenedor
print(f"\nGuardando contenedor {contenedor.numero_factura}...")
try:
    # Llama a la función específica de guardado para Fieltro
    guardar_contenedores_fieltro([contenedor])
    print("¡Contenedor Fieltro guardado!")
except Exception as e:
    print(f"Error al guardar el contenedor Fieltro: {e}")

print(f"--- Proceso Terminado para {datos_contenedor_fieltro['numero_factura']} ---")