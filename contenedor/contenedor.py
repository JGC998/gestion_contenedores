# contenedor/contenedor.py (CORREGIDO)
from abc import ABC
import json # Mantener si se usa from_json en algún sitio, aunque parece no usarse para cargar

class Contenedor(ABC):
    def __init__(self, fecha_pedido, fecha_llegada, proveedor, numero_factura, observaciones, gastos, valor_conversion):
        self.fecha_pedido = fecha_pedido
        self.fecha_llegada = fecha_llegada
        self.proveedor = proveedor
        self.numero_factura = numero_factura
        self.observaciones = observaciones
        # --- CORRECCIÓN: Asignar el argumento 'gastos' ---
        # Asumimos que 'gastos' llega como el diccionario esperado
        self.gastos = gastos
        self.valor_conversion = valor_conversion
        # --- CORRECCIÓN: Eliminar la inicialización de self.contenido aquí ---
        # self.contenido = [] # Las subclases se encargan de esto

    # --- MÉTODOS EXISTENTES (agregar_gasto, calcular_total_gastos, etc.) ---
    # Estos métodos ya esperan que self.gastos sea el diccionario, así que deberían funcionar bien.

    def agregar_gasto(self, tipo, descripcion, coste):
        # Asegurarse que self.gastos es un dict si viene de una fuente inesperada
        if not isinstance(self.gastos, dict):
             self.gastos = {"SUPLIDOS": [], "EXENTO": [], "SUJETO": []} # Inicializar si es necesario
        if tipo not in self.gastos:
             self.gastos[tipo] = [] # Asegurar que la clave existe

        # Validar tipo antes de añadir
        if tipo in ["SUPLIDOS", "EXENTO", "SUJETO"]:
             self.gastos[tipo].append({"descripcion": descripcion, "coste": coste})
        else:
             raise ValueError(f"Tipo de gasto '{tipo}' no válido. Debe ser SUPLIDOS, EXENTO o SUJETO.")


    # En contenedor.py, dentro de la clase Contenedor
    def calcular_total_gastos(self, tipos=None):
        if not isinstance(self.gastos, dict):
            print("Advertencia: self.gastos no es un diccionario en calcular_total_gastos.")
            return 0

        total_gastos = 0.0 # Inicializar como float
        tipos_a_sumar = tipos if tipos is not None else self.gastos.keys()

        for tipo in tipos_a_sumar:
            if tipo in self.gastos and isinstance(self.gastos[tipo], list):
                for gasto in self.gastos[tipo]:
                    if isinstance(gasto, dict):
                        try:
                            coste = gasto.get("coste")
                            if coste is not None:
                                # --- Intenta convertir a float ---
                                total_gastos += float(coste)
                            else:
                                print(f"Advertencia: Gasto sin 'coste' en tipo '{tipo}': {gasto}")
                        except (ValueError, TypeError) as e:
                            print(f"Advertencia: No se pudo convertir 'coste' a número para el gasto {gasto} en tipo '{tipo}': {e}")
                            # Decidir si continuar o parar
        return total_gastos

    def eliminar_gasto(self, tipo, indice):
         if isinstance(self.gastos, dict) and tipo in self.gastos and isinstance(self.gastos[tipo], list):
             try:
                 del self.gastos[tipo][indice]
             except IndexError:
                  print(f"Error: Índice {indice} fuera de rango para gastos de tipo {tipo}.")
             except Exception as e:
                  print(f"Error inesperado al eliminar gasto: {e}")
         else:
             # Manejar el caso donde la estructura no es la esperada
             print(f"Error: No se pueden eliminar gastos. Tipo '{tipo}' no válido o estructura de gastos incorrecta.")


    def editar_gasto(self, tipo, indice, descripcion, coste):
        if isinstance(self.gastos, dict) and tipo in self.gastos and isinstance(self.gastos[tipo], list):
            try:
                 # Validar datos antes de asignar
                 if not isinstance(descripcion, str) or not isinstance(coste, (int, float)):
                     raise ValueError("Descripción debe ser texto y coste debe ser número.")
                 self.gastos[tipo][indice] = {"descripcion": descripcion, "coste": coste}
            except IndexError:
                 print(f"Error: Índice {indice} fuera de rango para gastos de tipo {tipo}.")
            except ValueError as ve:
                 print(f"Error al editar gasto: {ve}")
            except Exception as e:
                 print(f"Error inesperado al editar gasto: {e}")
        else:
             print(f"Error: No se pueden editar gastos. Tipo '{tipo}' no válido o estructura de gastos incorrecta.")


    # from_json probablemente no se usa y podría eliminarse si la carga se hace como hasta ahora
    # @classmethod
    # def from_json(cls, data):
    #     return cls(**json.loads(data))