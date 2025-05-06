# nacional/mercanciaNacional.py (Versión Revisada con Gastos Simplificados)

import json
from abc import ABC, abstractmethod

class MercanciaNacional(ABC):
    """Clase base abstracta para registros de mercancía nacional (gastos simplificados)."""
    def __init__(self, fecha_pedido, fecha_llegada, proveedor, numero_factura, observaciones):
        """Inicializador base."""
        self.fecha_pedido = fecha_pedido
        self.fecha_llegada = fecha_llegada
        self.proveedor = proveedor
        self.numero_factura = numero_factura # Usaremos como ID único
        self.observaciones = observaciones
        # Los gastos son una lista simple de diccionarios {"descripcion": ..., "coste": ...}
        self.gastos = []
        self.contenido = [] # Lista estándar para los items

    # --- Métodos de Gastos (Simplificados) ---

    def agregar_gasto(self, descripcion, coste):
        """Añade un gasto a la lista de gastos."""
        try:
            coste_float = float(coste)
            if not descripcion: # Simple validación para descripción
                 print("Error: La descripción del gasto no puede estar vacía.")
                 return
            gasto_nuevo = {"descripcion": descripcion, "coste": coste_float}
            self.gastos.append(gasto_nuevo)
            print(f"  + Gasto Nacional añadido: {descripcion} - {coste_float:.2f}€ (Factura: {self.numero_factura})")
        except (ValueError, TypeError):
             print(f"Error: Coste inválido ('{coste}') para el gasto '{descripcion}'. No añadido.")
        except Exception as e:
             print(f"Error inesperado al añadir gasto nacional: {e}")


    def calcular_total_gastos(self):
        """Calcula la suma de TODOS los costes en la lista de gastos."""
        # Suma el valor de 'coste' de cada diccionario en la lista self.gastos
        # Usa 0 si 'coste' no existe o no es un número válido (aunque agregar_gasto intenta prevenirlo)
        total = sum(g.get("coste", 0) for g in self.gastos if isinstance(g.get("coste"), (int, float)))
        return total

    def eliminar_gasto(self, indice):
        """Elimina un gasto por su índice en la lista."""
        try:
            gasto_eliminado = self.gastos.pop(indice) # pop() elimina y devuelve el elemento
            print(f"Gasto Nacional eliminado: {gasto_eliminado.get('descripcion', '[sin descripción]')} (Índice original: {indice}, Factura: {self.numero_factura})")
        except IndexError:
            print(f"Error: Índice {indice} fuera de rango para la lista de gastos.")
        except Exception as e:
             print(f"Error inesperado al eliminar gasto nacional: {e}")


    def editar_gasto(self, indice, descripcion, coste):
        """Edita un gasto existente por su índice en la lista."""
        try:
            coste_float = float(coste)
            if not descripcion:
                 print("Error: La descripción del gasto no puede estar vacía al editar.")
                 return
            # Accede al diccionario en el índice y modifica sus valores
            self.gastos[indice]["descripcion"] = descripcion
            self.gastos[indice]["coste"] = coste_float
            print(f"Gasto Nacional editado (Índice {indice}): -> {descripcion} - {coste_float:.2f}€ (Factura: {self.numero_factura})")
        except IndexError:
            print(f"Error: Índice {indice} fuera de rango para la lista de gastos.")
        except (ValueError, TypeError):
             print(f"Error: Coste inválido ('{coste}') al editar gasto '{descripcion}'. No modificado.")
        except Exception as e:
             print(f"Error inesperado al editar gasto nacional: {e}")


    # --- Métodos Abstractos (Obligatorios para subclases, se mantienen igual) ---

    @abstractmethod
    def agregar_contenido(self, item):
        pass

    @abstractmethod
    def eliminar_contenido(self, indice):
        pass

    @abstractmethod
    def editar_contenido(self, indice, item):
        pass

    # --- Métodos de Cálculo ---
    # La lógica específica de reparto (calcular_precio_total_euro_gastos)
    # y el cálculo final (calcular_precios_finales) la implementaremos
    # en las subclases (como MercanciaNacionalGoma), ya que dependen del contenido.
    # Podríamos añadir aquí el método de reparto si fuera *absolutamente idéntico*
    # para todos los tipos de mercancía nacional, pero es más seguro en la subclase.