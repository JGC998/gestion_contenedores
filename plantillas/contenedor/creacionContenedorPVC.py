# plantilla_crear_pvc.py
import datetime
import os

# --- Importaciones ---
# Asegúrate que las rutas y nombres son correctos según tu proyecto
try:
    # Intenta importar la clase y la función de guardado específicas de PVC
    from contenedor.contenedorPVC import ContenedorPVC, guardar_contenedores_pvc
except ImportError:
    print("WARN: No se encontró 'guardar_contenedores_pvc'. Verifica el nombre en contenedorPVC.py.")
    # Si tienes una función genérica o un nombre diferente, ajústalo aquí
    # from contenedor.contenedorPVC import ContenedorPVC, guardar_contenedores # Ejemplo si fuera genérico
    exit() # Salir si no se puede importar lo necesario

# --- 1. DEFINE AQUÍ LOS DATOS DEL CONTENEDOR PVC ---
fecha_hoy_str = datetime.date.today().strftime('%Y-%m-%d') # Fecha actual: 2025-04-10

datos_contenedor_pvc = {
    "fecha_pedido": "2025-04-09",
    "fecha_llegada": fecha_hoy_str,
    "proveedor": "Plásticos del Mundo SA",
    "numero_factura": "PVC-PLANT-00Y", # ¡Cambia esto por uno único!
    "observaciones": "Contenedor PVC creado desde plantilla",
    "valor_conversion": 0.928, # Cambia según el tipo de cambio real
    # 'gastos' y 'contenido_pvc' se inicializan vacíos en la clase
}

# --- 2. DEFINE AQUÍ LA LISTA DE GASTOS ---
lista_gastos_pvc = [
    {"tipo": "EXENTO", "descripcion": "Flete PVC Plantilla", "coste": 510.00},
    {"tipo": "SUJETO", "descripcion": "Gestión Aduana PVC", "coste": 130.50},
    {"tipo": "SUJETO", "descripcion": "Movilización Puerto PVC", "coste": 175.00},
    # Añade más diccionarios de gastos aquí si es necesario
]

# --- 3. DEFINE AQUÍ LA LISTA DE BOBINAS DE PVC ---
lista_bobinas_pvc = [
    {
        "espesor": 1, "ancho": 1600, "largo": 250, "n_bobinas": 6,
        "metro_lineal_usd": 6.95, "color": "Verde Botella"
    },
    {
        "espesor": 2, "ancho": 1350, "largo": 175, "n_bobinas": 9,
        "metro_lineal_usd": 8.40, "color": "Amarillo Tráfico"
    },
    # Añade más diccionarios de bobinas aquí si es necesario
]

# --- Ejecución ---
print(f"--- Creando Contenedor PVC: {datos_contenedor_pvc['numero_factura']} ---")

# 4. Crear instancia (pasando los datos generales)
try:
    contenedor = ContenedorPVC(gastos={}, contenido_pvc=[], **datos_contenedor_pvc)
except TypeError as e:
     print(f"Error al crear ContenedorPVC. ¿Faltan argumentos o sobran?: {e}")
     exit()

# 5. Agregar Gastos (desde la lista)
print("Agregando gastos...")
for gasto in lista_gastos_pvc:
    try:
        contenedor.agregar_gasto(gasto["tipo"], gasto["descripcion"], gasto["coste"])
        print(f"  + Gasto: {gasto['descripcion']}")
    except Exception as e:
        print(f"Error agregando gasto {gasto}: {e}")

# 6. Agregar Bobinas (desde la lista, usando el método específico de PVC)
print("Agregando bobinas de PVC...")
# Asegúrate que el método para añadir bobinas se llame así en ContenedorPVC.py
agregar_bobina_pvc_method_name = 'agregar_bobina_pvc' # Ajusta si lo llamaste diferente

if not hasattr(contenedor, agregar_bobina_pvc_method_name):
    print(f"Error: No se encontró el método '{agregar_bobina_pvc_method_name}' en ContenedorPVC.")
else:
    agregar_bobina_func = getattr(contenedor, agregar_bobina_pvc_method_name)
    for bobina_data in lista_bobinas_pvc:
        try:
            agregar_bobina_func(
                espesor=bobina_data["espesor"],
                ancho=bobina_data["ancho"],
                largo=bobina_data["largo"],
                n_bobinas=bobina_data["n_bobinas"],
                metro_lineal_usd=bobina_data["metro_lineal_usd"],
                color=bobina_data["color"], # Argumento extra para PVC
                valor_conversion=contenedor.valor_conversion # Pasar el valor del contenedor
            )
            print(f"  + Bobina: {bobina_data['espesor']}mm {bobina_data['color']}")
        except Exception as e:
             print(f"Error agregando bobina PVC {bobina_data}: {e}")


# 7. Calcular Precios Finales
print("Calculando precios finales...")
try:
    contenedor.calcular_precios_finales()
except Exception as e:
     print(f"Error calculando precios finales: {e}")

# 8. Guardar el Contenedor
print(f"\nGuardando contenedor {contenedor.numero_factura}...")
try:
    # Llama a la función específica de guardado para PVC
    guardar_contenedores_pvc([contenedor])
    print("¡Contenedor PVC guardado!")
except Exception as e:
    print(f"Error al guardar el contenedor PVC: {e}")

print(f"--- Proceso Terminado para {datos_contenedor_pvc['numero_factura']} ---")