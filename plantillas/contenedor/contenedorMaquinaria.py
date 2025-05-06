# plantilla_crear_maquinaria.py
import datetime
import os

# --- Importaciones ---
# Asegúrate que las rutas y nombres son correctos según tu proyecto
try:
    # Intenta importar la clase y la función de guardado específicas de Maquinaria
    from contenedor.contenedorMaquinaria import ContenedorMaquinaria, guardar_contenedores_maquinaria
except ImportError:
    print("WARN: No se encontró 'guardar_contenedores_maquinaria'. Verifica el nombre en contenedorMaquinaria.py.")
    exit() # Salir si no se puede importar lo necesario

# --- 1. DEFINE AQUÍ LOS DATOS DEL CONTENEDOR MAQUINARIA ---
fecha_hoy_str = datetime.date.today().strftime('%Y-%m-%d') # Fecha actual: 2025-04-10

datos_contenedor_maq = {
    "fecha_pedido": "2025-03-25",
    "fecha_llegada": fecha_hoy_str,
    "proveedor": "Global Machine Tools",
    "numero_factura": "MAQ-PLANT-00W", # ¡Cambia esto por uno único!
    "observaciones": "Contenedor Maquinaria creado desde plantilla",
    "valor_conversion": 0.921, # Cambia según el tipo de cambio real
    # 'gastos' y 'contenido_maquinaria' se inicializan vacíos en la clase
}

# --- 2. DEFINE AQUÍ LA LISTA DE GASTOS ---
lista_gastos_maq = [
    {"tipo": "SUPLIDOS", "descripcion": "Tasa Importación Maquinaria", "coste": 850.00},
    {"tipo": "EXENTO", "descripcion": "Transporte Pesado Especial", "coste": 1400.00},
    {"tipo": "SUJETO", "descripcion": "Seguro Alto Valor", "coste": 450.00},
    {"tipo": "SUJETO", "descripcion": "Instalación Base", "coste": 980.00},
    # Añade más diccionarios de gastos aquí si es necesario
]

# --- 3. DEFINE AQUÍ LA LISTA DE MÁQUINAS ---
lista_maquinas = [
    {
        "codigo": "TORNO-CNC-08", "modelo": "LatheMaster 5000", "marca": "PreciseTurn",
        "precio_total_usd": 55750.00
    },
    {
        "codigo": "FRES-CNC-12", "modelo": "MillPro XZ", "marca": "RoboMill",
        "precio_total_usd": 72300.50
    },
    # Añade más diccionarios de máquinas aquí si es necesario
]

# --- Ejecución ---
print(f"--- Creando Contenedor Maquinaria: {datos_contenedor_maq['numero_factura']} ---")

# 4. Crear instancia (pasando los datos generales)
try:
    # Pasamos 'contenido_maquinaria' aunque esté vacío, si __init__ lo espera
    contenedor = ContenedorMaquinaria(gastos={}, contenido_maquinaria=[], **datos_contenedor_maq)
except TypeError as e:
     print(f"Error al crear ContenedorMaquinaria. ¿Faltan argumentos o sobran?: {e}")
     exit()

# 5. Agregar Gastos (desde la lista)
print("Agregando gastos...")
for gasto in lista_gastos_maq:
    try:
        contenedor.agregar_gasto(gasto["tipo"], gasto["descripcion"], gasto["coste"])
        print(f"  + Gasto: {gasto['descripcion']}")
    except Exception as e:
        print(f"Error agregando gasto {gasto}: {e}")

# 6. Agregar Máquinas (desde la lista, usando el método específico de Maquinaria)
print("Agregando máquinas...")
# Asegúrate que el método para añadir máquinas se llame así en ContenedorMaquinaria.py
agregar_maq_method_name = 'agregar_maquina' # Ajusta si lo llamaste diferente

if not hasattr(contenedor, agregar_maq_method_name):
    print(f"Error: No se encontró el método '{agregar_maq_method_name}' en ContenedorMaquinaria.")
else:
    agregar_maq_func = getattr(contenedor, agregar_maq_method_name)
    for maq_data in lista_maquinas:
        try:
            agregar_maq_func(
                codigo=maq_data["codigo"],
                modelo=maq_data["modelo"],
                marca=maq_data["marca"],
                precio_total_usd=maq_data["precio_total_usd"],
                # Maquinaria solo necesita estos datos base
                valor_conversion=contenedor.valor_conversion # Pasar el valor del contenedor
            )
            print(f"  + Máquina: {maq_data['codigo']} - {maq_data['modelo']}")
        except Exception as e:
             print(f"Error agregando máquina {maq_data}: {e}")


# 7. Calcular Precios Finales
#    Para maquinaria, esto calcula principalmente el precio_total_euro_gastos
print("Calculando precios finales...")
try:
    contenedor.calcular_precios_finales()
except Exception as e:
     print(f"Error calculando precios finales: {e}")

# 8. Guardar el Contenedor
print(f"\nGuardando contenedor {contenedor.numero_factura}...")
try:
    # Llama a la función específica de guardado para Maquinaria
    guardar_contenedores_maquinaria([contenedor])
    print("¡Contenedor Maquinaria guardado!")
except Exception as e:
    print(f"Error al guardar el contenedor Maquinaria: {e}")

print(f"--- Proceso Terminado para {datos_contenedor_maq['numero_factura']} ---")