# crear_contenedor_goma_completo.py
# Script para crear un contenedor de Goma detallado y guardarlo en la DB.

import datetime
import os
import sys
import traceback
from typing import List, Dict, Any

# --- Añadir la carpeta raíz del proyecto al sys.path ---
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = current_dir
    if project_root not in sys.path:
        sys.path.append(project_root)
    print(f"Ruta del proyecto añadida a sys.path: {project_root}")
except NameError:
    print("Advertencia: No se pudo determinar la ruta del proyecto automáticamente.")
    current_dir = "."
    if current_dir not in sys.path:
         sys.path.append(current_dir)

# --- Importaciones Necesarias ---
try:
    # Clase y función de guardado para ContenedorGoma (versión DB)
    from contenedor.contenedorGoma import ContenedorGoma, guardar_o_actualizar_contenedores_goma
    # Para inicializar la DB
    from almacen.database import inicializar_database, conectar_db
    # Modelo Goma (para los items del contenido)
    from modelos import Goma
except ImportError as e:
    print(f"\n--- ERROR CRÍTICO DE IMPORTACIÓN ---")
    print(f"No se pudieron importar módulos necesarios: {e}")
    print("Asegúrate de que la estructura de carpetas es correcta y que los archivos")
    print("están en las ubicaciones esperadas (ej: 'almacen/database.py', 'modelos.py').")
    print("Verifica también que estás ejecutando el script desde la carpeta raíz 'gestion_contenedores'.")
    traceback.print_exc()
    exit()
except Exception as e_inesperado:
    print(f"\n--- ERROR INESPERADO DURANTE IMPORTACIONES ---")
    print(f"{e_inesperado}")
    traceback.print_exc()
    exit()

# --- DATOS DE EJEMPLO PARA UN CONTENEDOR DE GOMA COMPLETO ---
today = datetime.date.today()
fecha_llegada_estimada = today + datetime.timedelta(days=5) # Llegada en 5 días
fecha_pedido_realizado = today - datetime.timedelta(days=20) # Pedido hace 20 días

datos_contenedor_goma_detallado = {
    "fecha_pedido": fecha_pedido_realizado.strftime('%Y-%m-%d'),
    "fecha_llegada": fecha_llegada_estimada.strftime('%Y-%m-%d'),
    "proveedor": "Global Rubber Supplies Co.",
    "numero_factura": "GRS-CG-2025-007", # Número de factura único
    "observaciones": "Contenedor de goma variada para stock. Incluye tipos especiales. Revisar calidad al llegar.",
    "valor_conversion": 0.915, # Ejemplo de tipo de cambio USD a EUR
    "gastos": { # Diccionario de gastos, como se espera en la clase Contenedor
        "SUPLIDOS": [
            {"descripcion": "Arancel de importación Goma", "coste": 250.75},
            {"descripcion": "Tasa portuaria especial", "coste": 85.20}
        ],
        "EXENTO": [
            {"descripcion": "Flete marítimo principal", "coste": 1250.00},
            {"descripcion": "Seguro de transporte internacional", "coste": 110.50}
        ],
        "SUJETO": [
            {"descripcion": "Transporte terrestre a almacén", "coste": 320.00},
            {"descripcion": "Gastos de despacho de aduanas", "coste": 180.00},
            {"descripcion": "Manipulación y descarga en puerto", "coste": 95.00}
        ]
    }
    # 'contenido_goma' se añadirá dinámicamente
}

bobinas_goma_detalladas = [
    {
        "espesor": "6mm", "ancho": 1200, "largo": 100, "n_bobinas": 5,
        "metro_lineal_usd": 15.50, "subtipo": "NORMAL"
    },
    {
        "espesor": "8mm Reforzada", "ancho": 1000, "largo": 50, "n_bobinas": 3,
        "metro_lineal_usd": 22.75, "subtipo": "CARAMELO"
    },
    {
        "espesor": "3mm Lisa Fina", "ancho": 1500, "largo": 150, "n_bobinas": 8,
        "metro_lineal_usd": 10.20, "subtipo": "NORMAL"
    },
    {
        "espesor": "10mm Antideslizante", "ancho": 1200, "largo": 30, "n_bobinas": 4,
        "metro_lineal_usd": 28.90, "subtipo": "NERVADA"
    },
    {
        "espesor": "5mm (Oferta)", "ancho": 1000, "largo": 120, "n_bobinas": 10,
        "metro_lineal_usd": 12.00, "subtipo": "NORMAL"
    }
]

# --- FUNCIÓN PRINCIPAL DEL SCRIPT ---
if __name__ == "__main__":
    print("="*60)
    print("===== SCRIPT PARA CREAR CONTENEDOR DE GOMA COMPLETO EN DB =====")
    print("="*60)

    # 1. Inicializar/Verificar Base de Datos
    print("\n--- 1. Inicializando/Verificando Base de Datos Almacén ---")
    try:
        inicializar_database()
        conn_test = conectar_db()
        if conn_test:
            print("   Conexión a DB verificada.")
            conn_test.close()
        else:
            print("   ERROR FATAL: No se pudo conectar a la DB. Abortando.")
            exit()
    except Exception as e_db:
        print(f"   ERROR FATAL inicializando DB: {e_db}")
        traceback.print_exc()
        exit()

    # --- Procesar y Guardar el Contenedor de Goma ---
    print("\n--- 2. Procesando y Guardando Contenedor de Goma Detallado ---")

    try:
        # Crear la instancia del ContenedorGoma
        # Los gastos se pasan directamente al constructor de la clase base Contenedor
        contenedor_goma = ContenedorGoma(
            fecha_pedido=datos_contenedor_goma_detallado["fecha_pedido"],
            fecha_llegada=datos_contenedor_goma_detallado["fecha_llegada"],
            proveedor=datos_contenedor_goma_detallado["proveedor"],
            numero_factura=datos_contenedor_goma_detallado["numero_factura"],
            observaciones=datos_contenedor_goma_detallado["observaciones"],
            gastos=datos_contenedor_goma_detallado["gastos"], # Pasar el dict de gastos
            valor_conversion=datos_contenedor_goma_detallado["valor_conversion"]
            # contenido_goma se inicializa vacío y se llena con agregar_bobina
        )
        print(f"   Objeto ContenedorGoma creado para factura: {contenedor_goma.numero_factura}")

        # Añadir las bobinas al contenedor
        print("   Añadiendo bobinas al contenedor...")
        for bobina_data in bobinas_goma_detalladas:
            contenedor_goma.agregar_bobina(
                espesor=bobina_data["espesor"],
                ancho=bobina_data["ancho"],
                largo=bobina_data["largo"],
                n_bobinas=bobina_data["n_bobinas"],
                metro_lineal_usd=bobina_data["metro_lineal_usd"],
                valor_conversion=contenedor_goma.valor_conversion, # Usar el del contenedor
                subtipo=bobina_data["subtipo"]
            )
        print(f"   {len(contenedor_goma.contenido)} lotes de bobinas añadidas.")

        # Calcular precios finales
        print("   Calculando precios finales...")
        contenedor_goma.calcular_precios_finales()
        print("   Precios finales calculados.")

        # Guardar en la base de datos
        print("   Intentando guardar en la base de datos...")
        guardar_o_actualizar_contenedores_goma([contenedor_goma])
        # La función guardar_o_actualizar_contenedores_goma ya imprime logs detallados.

        print(f"\n   -> Contenedor de Goma '{contenedor_goma.numero_factura}' procesado y guardado en la DB.")

    except ValueError as ve:
        print(f"     -> ERROR DE VALIDACIÓN al procesar Contenedor Goma: {ve}")
        traceback.print_exc(limit=2)
    except TypeError as te:
        print(f"     -> ERROR DE TIPO al procesar Contenedor Goma: {te}")
        print(f"     Asegúrate que 'registrar_entrada_almacen' acepta 'cursor' y 'pedido_id'.")
        traceback.print_exc(limit=2)
    except Exception as e:
        print(f"     -> ERROR INESPERADO procesando Contenedor Goma: {e}")
        traceback.print_exc()

    # --- Resumen Final ---
    print("\n" + "="*60)
    print("===== SCRIPT DE CREACIÓN DE CONTENEDOR DE GOMA FINALIZADO =====")
    print("Revisa los mensajes anteriores para detalles y posibles errores.")
    print("Verifica el contenido de la base de datos 'almacen.db' para la factura:")
    print(f"  '{datos_contenedor_goma_detallado['numero_factura']}' en PedidosProveedores, GastosPedido y StockMateriasPrimas.")
    print("="*60)

