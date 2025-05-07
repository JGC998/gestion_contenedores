# poblar_almacen_debug.py
import datetime
import os
import sys
import traceback

# --- Añadir la carpeta raíz del proyecto al sys.path ---
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = current_dir # Asume que el script está en la raíz
    if project_root not in sys.path:
        sys.path.append(project_root)
    print(f"SCRIPT: Ruta del proyecto añadida a sys.path: {project_root}")
except NameError:
    print("SCRIPT: Advertencia: No se pudo determinar la ruta del proyecto automáticamente.")
    current_dir = "."
    if current_dir not in sys.path:
         sys.path.append(current_dir)

# --- Importaciones Necesarias ---
print("\nSCRIPT: Iniciando importaciones...")
try:
    from almacen.database import inicializar_database, conectar_db
    print("SCRIPT: IMPORTADO almacen.database (inicializar_database, conectar_db)")

    from modelos import Goma, PVC, Fieltro, GomaNacional, PVCNacional, FieltroNacional
    print("SCRIPT: IMPORTADO modelos (Goma, PVC, Fieltro, GomaNacional, PVCNacional, FieltroNacional)")

    from contenedor.contenedorGoma import ContenedorGoma, guardar_o_actualizar_contenedores_goma
    print("SCRIPT: IMPORTADO contenedor.contenedorGoma (ContenedorGoma, guardar_o_actualizar_contenedores_goma)")
    from contenedor.contenedorPVC import ContenedorPVC, guardar_o_actualizar_contenedores_pvc
    print("SCRIPT: IMPORTADO contenedor.contenedorPVC (ContenedorPVC, guardar_o_actualizar_contenedores_pvc)")
    from contenedor.contenedorFieltro import ContenedorFieltro, guardar_o_actualizar_contenedores_fieltro
    print("SCRIPT: IMPORTADO contenedor.contenedorFieltro (ContenedorFieltro, guardar_o_actualizar_contenedores_fieltro)")

    from nacional.mercanciaNacionalGoma import MercanciaNacionalGoma, guardar_o_actualizar_mercancias_goma
    print("SCRIPT: IMPORTADO nacional.mercanciaNacionalGoma (MercanciaNacionalGoma, guardar_o_actualizar_mercancias_goma)")
    from nacional.mercanciaNacionalPVC import MercanciaNacionalPVC, guardar_o_actualizar_mercancias_pvc
    print("SCRIPT: IMPORTADO nacional.mercanciaNacionalPVC (MercanciaNacionalPVC, guardar_o_actualizar_mercancias_pvc)")
    from nacional.mercanciaNacionalFieltro import MercanciaNacionalFieltro, guardar_o_actualizar_mercancias_fieltro
    print("SCRIPT: IMPORTADO nacional.mercanciaNacionalFieltro (MercanciaNacionalFieltro, guardar_o_actualizar_mercancias_fieltro)")
    print("SCRIPT: Todas las importaciones principales parecen correctas.\n")

except ImportError as e:
    print(f"\n--- SCRIPT: ERROR CRÍTICO DE IMPORTACIÓN ---")
    print(f"No se pudieron importar módulos necesarios: {e}")
    print("Asegúrate de que la estructura de carpetas es correcta y que los archivos")
    print("están en las ubicaciones esperadas (ej: 'almacen/database.py', 'modelos.py').")
    print("Verifica también que estás ejecutando el script desde la carpeta raíz 'gestion_contenedores'.")
    traceback.print_exc()
    exit()
except Exception as e_inesperado:
    print(f"\n--- SCRIPT: ERROR INESPERADO DURANTE IMPORTACIONES ---")
    print(f"{e_inesperado}")
    traceback.print_exc()
    exit()

# --- Datos Comunes de Ejemplo ---
today = datetime.date.today()
fecha_pedido_str = (today - datetime.timedelta(days=10)).strftime('%Y-%m-%d')
fecha_llegada_str = today.strftime('%Y-%m-%d')

# --- Funciones de Creación Detalladas ---

def crear_contenedor_goma_debug():
    print("\n" + "="*30 + " INICIO DEBUG: Contenedor Goma " + "="*30)
    datos_contenedor = {
        "fecha_pedido": fecha_pedido_str, "fecha_llegada": fecha_llegada_str,
        "proveedor": "Proveedor Goma Debug", "numero_factura": "CG-DEBUG-001",
        "observaciones": "Contenedor Goma para depuración", "valor_conversion": 0.92,
        "gastos": {} # Se inicializa vacío, se añaden después
    }
    print(f"SCRIPT_CG: Datos iniciales para ContenedorGoma: {datos_contenedor}")
    
    try:
        cg = ContenedorGoma(**datos_contenedor)
        print(f"SCRIPT_CG: Objeto ContenedorGoma creado para factura: {cg.numero_factura}")

        # Añadir Gastos
        print("SCRIPT_CG: Añadiendo gastos...")
        cg.agregar_gasto("SUPLIDOS", "Arancel Goma Debug", 150.0)
        cg.agregar_gasto("EXENTO", "Flete Goma Debug", 400.0)
        cg.agregar_gasto("SUJETO", "Transporte Local Goma Debug", 120.0)
        print(f"SCRIPT_CG: Gastos añadidos: {cg.gastos}")

        # Añadir Bobinas
        print("SCRIPT_CG: Añadiendo bobinas...")
        bobina1_data = {"espesor": "6mm", "ancho": 1200, "largo": 100, "n_bobinas": 2, "metro_lineal_usd": 10.50, "subtipo": "NORMAL"}
        print(f"SCRIPT_CG: Datos Bobina 1 a añadir: {bobina1_data}")
        cg.agregar_bobina(**bobina1_data, valor_conversion=cg.valor_conversion)
        
        bobina2_data = {"espesor": "8mm", "ancho": 1000, "largo": 50, "n_bobinas": 1, "metro_lineal_usd": 12.75, "subtipo": "CARAMELO"}
        print(f"SCRIPT_CG: Datos Bobina 2 a añadir: {bobina2_data}")
        cg.agregar_bobina(**bobina2_data, valor_conversion=cg.valor_conversion)
        
        print(f"SCRIPT_CG: Contenido después de añadir bobinas ({len(cg.contenido)} items):")
        for i, item_goma in enumerate(cg.contenido):
            print(f"  Item {i+1}: {item_goma.__dict__}")


        # Calcular Precios
        print("SCRIPT_CG: Llamando a calcular_precios_finales()...")
        cg.calcular_precios_finales()
        print("SCRIPT_CG: calcular_precios_finales() ejecutado.")
        print(f"SCRIPT_CG: Contenido después de calcular_precios_finales ({len(cg.contenido)} items):")
        for i, item_goma in enumerate(cg.contenido):
            print(f"  Item {i+1} (post-cálculo): {item_goma.__dict__}")


        # Guardar
        print(f"SCRIPT_CG: Llamando a guardar_o_actualizar_contenedores_goma para factura {cg.numero_factura}...")
        guardar_o_actualizar_contenedores_goma([cg])
        print(f"SCRIPT_CG: guardar_o_actualizar_contenedores_goma ejecutado para {cg.numero_factura}.")

    except Exception as e:
        print(f"SCRIPT_CG: !!! ERROR DURANTE LA CREACIÓN DEL CONTENEDOR GOMA DEBUG: {e} !!!")
        traceback.print_exc()
    print("="*30 + " FIN DEBUG: Contenedor Goma " + "="*30 + "\n")

def crear_contenedor_pvc_debug():
    print("\n" + "="*30 + " INICIO DEBUG: Contenedor PVC " + "="*30)
    datos_contenedor = {
        "fecha_pedido": fecha_pedido_str, "fecha_llegada": fecha_llegada_str,
        "proveedor": "Proveedor PVC Debug", "numero_factura": "CPVC-DEBUG-001",
        "observaciones": "Contenedor PVC para depuración", "valor_conversion": 0.93,
        "gastos": {}
    }
    print(f"SCRIPT_CPVC: Datos iniciales para ContenedorPVC: {datos_contenedor}")

    try:
        cpvc = ContenedorPVC(**datos_contenedor)
        print(f"SCRIPT_CPVC: Objeto ContenedorPVC creado para factura: {cpvc.numero_factura}")

        cpvc.agregar_gasto("EXENTO", "Flete PVC Debug", 500.0)
        cpvc.agregar_gasto("SUJETO", "Aduana PVC Debug", 200.0)
        print(f"SCRIPT_CPVC: Gastos añadidos: {cpvc.gastos}")

        bobina1_data = {"espesor": "1", "ancho": 1500, "largo": 200, "n_bobinas": 3, "metro_lineal_usd": 7.20, "color": "Azul"}
        print(f"SCRIPT_CPVC: Datos Bobina 1 a añadir: {bobina1_data}")
        cpvc.agregar_bobina_pvc(**bobina1_data, valor_conversion=cpvc.valor_conversion)
        print(f"SCRIPT_CPVC: Contenido después de añadir bobinas ({len(cpvc.contenido)} items):")
        for i, item_pvc_obj in enumerate(cpvc.contenido): # Renombrado para evitar conflicto
            print(f"  Item {i+1}: {item_pvc_obj.__dict__}")

        print("SCRIPT_CPVC: Llamando a calcular_precios_finales()...")
        cpvc.calcular_precios_finales()
        print("SCRIPT_CPVC: calcular_precios_finales() ejecutado.")
        print(f"SCRIPT_CPVC: Contenido después de calcular_precios_finales ({len(cpvc.contenido)} items):")
        for i, item_pvc_obj in enumerate(cpvc.contenido): # Renombrado para evitar conflicto
            print(f"  Item {i+1} (post-cálculo): {item_pvc_obj.__dict__}")

        print(f"SCRIPT_CPVC: Llamando a guardar_o_actualizar_contenedores_pvc para factura {cpvc.numero_factura}...")
        guardar_o_actualizar_contenedores_pvc([cpvc])
        print(f"SCRIPT_CPVC: guardar_o_actualizar_contenedores_pvc ejecutado para {cpvc.numero_factura}.")

    except Exception as e:
        print(f"SCRIPT_CPVC: !!! ERROR DURANTE LA CREACIÓN DEL CONTENEDOR PVC DEBUG: {e} !!!")
        traceback.print_exc()
    print("="*30 + " FIN DEBUG: Contenedor PVC " + "="*30 + "\n")

def crear_contenedor_fieltro_debug():
    print("\n" + "="*30 + " INICIO DEBUG: Contenedor Fieltro " + "="*30)
    datos_contenedor = {
        "fecha_pedido": fecha_pedido_str, "fecha_llegada": fecha_llegada_str,
        "proveedor": "Proveedor Fieltro Debug", "numero_factura": "CFIE-DEBUG-001",
        "observaciones": "Contenedor Fieltro para depuración", "valor_conversion": 0.91,
        "gastos": {}
    }
    print(f"SCRIPT_CFIE: Datos iniciales para ContenedorFieltro: {datos_contenedor}")
    try:
        cfie = ContenedorFieltro(**datos_contenedor)
        print(f"SCRIPT_CFIE: Objeto ContenedorFieltro creado para factura: {cfie.numero_factura}")

        cfie.agregar_gasto("SUJETO", "Tasa Textil Debug", 70.0)
        print(f"SCRIPT_CFIE: Gastos añadidos: {cfie.gastos}")

        rollo1_data = {"espesor": "3", "ancho": 1000, "largo": 50, "n_bobinas": 5, "metro_lineal_usd": 2.50}
        print(f"SCRIPT_CFIE: Datos Rollo 1 a añadir: {rollo1_data}")
        cfie.agregar_rollo_fieltro(**rollo1_data, valor_conversion=cfie.valor_conversion)
        print(f"SCRIPT_CFIE: Contenido después de añadir rollos ({len(cfie.contenido)} items):")
        for i, item_fieltro_obj in enumerate(cfie.contenido): # Renombrado
             print(f"  Item {i+1}: {item_fieltro_obj.__dict__}")

        print("SCRIPT_CFIE: Llamando a calcular_precios_finales()...")
        cfie.calcular_precios_finales()
        print("SCRIPT_CFIE: calcular_precios_finales() ejecutado.")
        print(f"SCRIPT_CFIE: Contenido después de calcular_precios_finales ({len(cfie.contenido)} items):")
        for i, item_fieltro_obj in enumerate(cfie.contenido): # Renombrado
             print(f"  Item {i+1} (post-cálculo): {item_fieltro_obj.__dict__}")

        print(f"SCRIPT_CFIE: Llamando a guardar_o_actualizar_contenedores_fieltro para factura {cfie.numero_factura}...")
        guardar_o_actualizar_contenedores_fieltro([cfie])
        print(f"SCRIPT_CFIE: guardar_o_actualizar_contenedores_fieltro ejecutado para {cfie.numero_factura}.")

    except Exception as e:
        print(f"SCRIPT_CFIE: !!! ERROR DURANTE LA CREACIÓN DEL CONTENEDOR FIELTRO DEBUG: {e} !!!")
        traceback.print_exc()
    print("="*30 + " FIN DEBUG: Contenedor Fieltro " + "="*30 + "\n")

def crear_pedido_nacional_goma_debug():
    print("\n" + "="*30 + " INICIO DEBUG: Pedido Nacional Goma " + "="*30)
    datos_pedido = {
        "fecha_pedido": fecha_pedido_str, "fecha_llegada": fecha_llegada_str,
        "proveedor": "Gomas Nacionales Debug SL", "numero_factura": "NOMG-DEBUG-001",
        "observaciones": "Pedido Goma Nacional para depuración"
    }
    print(f"SCRIPT_NOMG: Datos iniciales para MercanciaNacionalGoma: {datos_pedido}")
    try:
        png = MercanciaNacionalGoma(**datos_pedido)
        print(f"SCRIPT_NOMG: Objeto MercanciaNacionalGoma creado para factura: {png.numero_factura}")

        print("SCRIPT_NOMG: Añadiendo gastos...")
        png.agregar_gasto("Portes Goma Nac Debug", 60.0)
        print(f"SCRIPT_NOMG: Gastos añadidos: {png.gastos}")

        print("SCRIPT_NOMG: Añadiendo bobinas...")
        bobina1_data = {"espesor": "5mm", "ancho": 1400, "largo": 80, "n_bobinas": 1, "metro_lineal_eur": 15.0, "subtipo": "NERVADA"}
        print(f"SCRIPT_NOMG: Datos Bobina 1 a añadir: {bobina1_data}")
        png.agregar_bobina(**bobina1_data)
        print(f"SCRIPT_NOMG: Contenido después de añadir bobinas ({len(png.contenido)} items):")
        for i, item_goma_nac in enumerate(png.contenido):
            print(f"  Item {i+1}: {item_goma_nac.__dict__}")

        print("SCRIPT_NOMG: Llamando a calcular_precios_finales()...")
        png.calcular_precios_finales()
        print("SCRIPT_NOMG: calcular_precios_finales() ejecutado.")
        print(f"SCRIPT_NOMG: Contenido después de calcular_precios_finales ({len(png.contenido)} items):")
        for i, item_goma_nac in enumerate(png.contenido):
            print(f"  Item {i+1} (post-cálculo): {item_goma_nac.__dict__}")

        print(f"SCRIPT_NOMG: Llamando a guardar_o_actualizar_mercancias_goma para factura {png.numero_factura}...")
        guardar_o_actualizar_mercancias_goma([png])
        print(f"SCRIPT_NOMG: guardar_o_actualizar_mercancias_goma ejecutado para {png.numero_factura}.")

    except Exception as e:
        print(f"SCRIPT_NOMG: !!! ERROR DURANTE LA CREACIÓN DEL PEDIDO GOMA NACIONAL DEBUG: {e} !!!")
        traceback.print_exc()
    print("="*30 + " FIN DEBUG: Pedido Nacional Goma " + "="*30 + "\n")

def crear_pedido_nacional_pvc_debug():
    print("\n" + "="*30 + " INICIO DEBUG: Pedido Nacional PVC " + "="*30)
    datos_pedido = {
        "fecha_pedido": fecha_pedido_str, "fecha_llegada": fecha_llegada_str,
        "proveedor": "PVC Nacional Debug Co.", "numero_factura": "NOPVC-DEBUG-001",
        "observaciones": "Pedido PVC Nacional para depuración"
    }
    print(f"SCRIPT_NOPVC: Datos iniciales para MercanciaNacionalPVC: {datos_pedido}")
    try:
        pnpvc = MercanciaNacionalPVC(**datos_pedido)
        print(f"SCRIPT_NOPVC: Objeto MercanciaNacionalPVC creado para factura: {pnpvc.numero_factura}")

        pnpvc.agregar_gasto("Transporte PVC Nac Debug", 45.0)
        print(f"SCRIPT_NOPVC: Gastos añadidos: {pnpvc.gastos}")

        bobina1_data = {"espesor": "2", "ancho": 1300, "largo": 150, "n_bobinas": 2, "metro_lineal_eur": 9.50, "color": "Rojo"}
        print(f"SCRIPT_NOPVC: Datos Bobina 1 a añadir: {bobina1_data}")
        pnpvc.agregar_bobina_pvc(**bobina1_data) # agregar_bobina_pvc para nacional
        print(f"SCRIPT_NOPVC: Contenido después de añadir bobinas ({len(pnpvc.contenido)} items):")
        for i, item_pvc_nac in enumerate(pnpvc.contenido):
             print(f"  Item {i+1}: {item_pvc_nac.__dict__}")

        print("SCRIPT_NOPVC: Llamando a calcular_precios_finales()...")
        pnpvc.calcular_precios_finales()
        print("SCRIPT_NOPVC: calcular_precios_finales() ejecutado.")
        print(f"SCRIPT_NOPVC: Contenido después de calcular_precios_finales ({len(pnpvc.contenido)} items):")
        for i, item_pvc_nac in enumerate(pnpvc.contenido):
             print(f"  Item {i+1} (post-cálculo): {item_pvc_nac.__dict__}")

        print(f"SCRIPT_NOPVC: Llamando a guardar_o_actualizar_mercancias_pvc para factura {pnpvc.numero_factura}...")
        guardar_o_actualizar_mercancias_pvc([pnpvc])
        print(f"SCRIPT_NOPVC: guardar_o_actualizar_mercancias_pvc ejecutado para {pnpvc.numero_factura}.")

    except Exception as e:
        print(f"SCRIPT_NOPVC: !!! ERROR DURANTE LA CREACIÓN DEL PEDIDO PVC NACIONAL DEBUG: {e} !!!")
        traceback.print_exc()
    print("="*30 + " FIN DEBUG: Pedido Nacional PVC " + "="*30 + "\n")


def crear_pedido_nacional_fieltro_debug():
    print("\n" + "="*30 + " INICIO DEBUG: Pedido Nacional Fieltro " + "="*30)
    datos_pedido = {
        "fecha_pedido": fecha_pedido_str, "fecha_llegada": fecha_llegada_str,
        "proveedor": "Fieltros Locales Debug", "numero_factura": "NOFIE-DEBUG-001",
        "observaciones": "Pedido Fieltro Nacional para depuración"
    }
    print(f"SCRIPT_NOFIE: Datos iniciales para MercanciaNacionalFieltro: {datos_pedido}")
    try:
        pnfie = MercanciaNacionalFieltro(**datos_pedido)
        print(f"SCRIPT_NOFIE: Objeto MercanciaNacionalFieltro creado para factura: {pnfie.numero_factura}")

        pnfie.agregar_gasto("Envío Fieltro Nac Debug", 30.0)
        print(f"SCRIPT_NOFIE: Gastos añadidos: {pnfie.gastos}")

        rollo1_data = {"espesor": "2", "ancho": 900, "largo": 40, "n_bobinas": 3, "metro_lineal_eur": 3.75}
        print(f"SCRIPT_NOFIE: Datos Rollo 1 a añadir: {rollo1_data}")
        pnfie.agregar_rollo_fieltro(**rollo1_data) # agregar_rollo_fieltro para nacional
        print(f"SCRIPT_NOFIE: Contenido después de añadir rollos ({len(pnfie.contenido)} items):")
        for i, item_fieltro_nac in enumerate(pnfie.contenido):
            print(f"  Item {i+1}: {item_fieltro_nac.__dict__}")


        print("SCRIPT_NOFIE: Llamando a calcular_precios_finales()...")
        pnfie.calcular_precios_finales()
        print("SCRIPT_NOFIE: calcular_precios_finales() ejecutado.")
        print(f"SCRIPT_NOFIE: Contenido después de calcular_precios_finales ({len(pnfie.contenido)} items):")
        for i, item_fieltro_nac in enumerate(pnfie.contenido):
            print(f"  Item {i+1} (post-cálculo): {item_fieltro_nac.__dict__}")

        print(f"SCRIPT_NOFIE: Llamando a guardar_o_actualizar_mercancias_fieltro para factura {pnfie.numero_factura}...")
        guardar_o_actualizar_mercancias_fieltro([pnfie])
        print(f"SCRIPT_NOFIE: guardar_o_actualizar_mercancias_fieltro ejecutado para {pnfie.numero_factura}.")

    except Exception as e:
        print(f"SCRIPT_NOFIE: !!! ERROR DURANTE LA CREACIÓN DEL PEDIDO FIELTRO NACIONAL DEBUG: {e} !!!")
        traceback.print_exc()
    print("="*30 + " FIN DEBUG: Pedido Nacional Fieltro " + "="*30 + "\n")

# --- Función Principal del Script de Depuración ---
if __name__ == "__main__":
    print("="*70)
    print("===== INICIO SCRIPT DE POBLACIÓN Y DEPURACIÓN DE ALMACÉN =====")
    print("="*70)

    # 1. Inicializar/Verificar Base de Datos
    print("\nSCRIPT: --- 1. Inicializando/Verificando Base de Datos Almacén ---")
    try:
        inicializar_database()
        conn_test = conectar_db()
        if conn_test:
            print("SCRIPT: Conexión a DB verificada después de inicializar.")
            conn_test.close()
        else:
            print("SCRIPT: ERROR FATAL: No se pudo conectar a la DB tras inicializar. Abortando.")
            exit()
    except Exception as e_db:
        print(f"SCRIPT: ERROR FATAL inicializando DB: {e_db}")
        traceback.print_exc()
        exit()
    print("SCRIPT: --- Base de Datos Lista ---")

    # 2. Crear y guardar ejemplos para cada tipo
    print("\nSCRIPT: --- 2. Creando y Guardando Datos de Prueba Detallados ---")
    
    crear_contenedor_goma_debug()
    crear_contenedor_pvc_debug()
    crear_contenedor_fieltro_debug()
    
    crear_pedido_nacional_goma_debug()
    crear_pedido_nacional_pvc_debug()
    crear_pedido_nacional_fieltro_debug()

    print("\n" + "="*70)
    print("===== FIN SCRIPT DE POBLACIÓN Y DEPURACIÓN DE ALMACÉN =====")
    print("Revisa todos los mensajes 'SCRIPT_XX:' y los mensajes de las funciones internas.")
    print("Verifica el contenido de la base de datos 'almacen.db' usando 'verDatabase.py'")
    print("o consultando directamente las tablas PedidosProveedores, GastosPedido y StockMateriasPrimas.")
    print("Busca específicamente los items con facturas 'CG-DEBUG-001', 'CPVC-DEBUG-001', etc.")
    print("="*70)