
class Goma:
    def __init__(self, espesor, ancho, largo, n_bobinas, metro_lineal_usd, subtipo="NORMAL"):
        self.espesor = str(espesor)
        self.ancho = float(ancho)
        self.largo = float(largo)
        self.n_bobinas = int(n_bobinas)
        self.metro_lineal_usd = float(metro_lineal_usd)
        self.subtipo = str(subtipo).upper()
        self.metro_lineal_euro = None
        self.precio_total_euro = None
        self.precio_total_euro_gastos = None
        self.metro_lineal_euro_mas_gastos= None

    def __str__(self):
        return (f"Goma ({self.subtipo}) (Esp: {self.espesor}, Ancho: {self.ancho:.1f}, "
                f"Largo: {self.largo:.1f}, N: {self.n_bobinas})")

class GomaNacional:
    def __init__(self, espesor, ancho, largo, n_bobinas, metro_lineal_eur, subtipo="NORMAL"):
        self.espesor = str(espesor)
        self.ancho = float(ancho) if ancho is not None else None
        self.largo = float(largo) if largo is not None else None
        self.n_bobinas = int(n_bobinas) if n_bobinas is not None else None
        self.metro_lineal_eur = float(metro_lineal_eur) if metro_lineal_eur is not None else None
        self.subtipo = str(subtipo).upper()
        self.precio_total_euro = None
        if self.metro_lineal_eur is not None and self.largo is not None and self.n_bobinas is not None:
            try: self.precio_total_euro = self.metro_lineal_eur * self.largo * self.n_bobinas
            except TypeError: print(f"Error calc precio base GomaNacional {self.subtipo}")
        self.precio_total_euro_gastos = None
        self.metro_lineal_euro_mas_gastos = None
        self.metro_lineal_usd = None

    def __str__(self):
        return (f"GomaNacional ({self.subtipo}) (Esp: {self.espesor}, Ancho: {self.ancho:.1f}, "
                f"Largo: {self.largo:.1f}, N: {self.n_bobinas})")

class PVC:
    # ... (como estaba antes) ...
    def __init__(self, espesor, ancho, largo, n_bobinas, metro_lineal_usd, color):
        try: self.espesor = int(espesor)
        except (ValueError, TypeError): self.espesor = None
        try: self.ancho = float(ancho)
        except (ValueError, TypeError): self.ancho = None
        try: self.largo = float(largo)
        except (ValueError, TypeError): self.largo = None
        try: self.n_bobinas = int(n_bobinas)
        except (ValueError, TypeError): self.n_bobinas = None
        try: self.metro_lineal_usd = float(metro_lineal_usd)
        except (ValueError, TypeError): self.metro_lineal_usd = None
        self.color = str(color)
        self.metro_lineal_euro = None
        self.precio_total_euro = None
        self.precio_total_euro_gastos = None
        self.metro_lineal_euro_mas_gastos= None

    def __str__(self):
        return f"PVC (Color: {self.color}, Esp: {self.espesor}, Ancho: {self.ancho}, Largo: {self.largo})"


class PVCNacional:
     # ... (como estaba antes) ...
    def __init__(self, espesor, ancho, largo, n_bobinas, metro_lineal_eur, color):
        self.espesor = str(espesor) if espesor is not None else None
        self.color = str(color) if color is not None else None
        try: self.ancho = float(ancho) if ancho is not None else None
        except (ValueError, TypeError): self.ancho = None
        try: self.largo = float(largo) if largo is not None else None
        except (ValueError, TypeError): self.largo = None
        try: self.n_bobinas = int(n_bobinas) if n_bobinas is not None else None
        except (ValueError, TypeError): self.n_bobinas = None
        try: self.metro_lineal_eur = float(metro_lineal_eur) if metro_lineal_eur is not None else None
        except (ValueError, TypeError): self.metro_lineal_eur = None
        self.precio_total_euro = None
        if self.metro_lineal_eur is not None and self.largo is not None and self.n_bobinas is not None:
            try: self.precio_total_euro = self.metro_lineal_eur * self.largo * self.n_bobinas
            except TypeError: print(f"Error calc precio base PVCNacional")
        self.precio_total_euro_gastos = None
        self.metro_lineal_euro_mas_gastos = None
        self.metro_lineal_usd = None

    def __str__(self):
         return f"PVCNacional (Color: {self.color}, Esp: {self.espesor}, Ancho: {self.ancho})"


class Fieltro:
    # ... (como estaba antes) ...
    def __init__(self, espesor, ancho, largo, n_bobinas, metro_lineal_usd):
        try: self.espesor = int(espesor)
        except (ValueError, TypeError): self.espesor = None
        try: self.ancho = float(ancho)
        except (ValueError, TypeError): self.ancho = None
        try: self.largo = float(largo)
        except (ValueError, TypeError): self.largo = None
        try: self.n_bobinas = int(n_bobinas)
        except (ValueError, TypeError): self.n_bobinas = None
        try: self.metro_lineal_usd = float(metro_lineal_usd)
        except (ValueError, TypeError): self.metro_lineal_usd = None
        self.metro_lineal_euro = None
        self.precio_total_euro = None
        self.precio_total_euro_gastos = None
        self.metro_lineal_euro_mas_gastos= None

    def __str__(self):
        return f"Fieltro (Esp: {self.espesor}, Ancho: {self.ancho}, Largo: {self.largo})"


class FieltroNacional:
    # ... (como estaba antes) ...
    def __init__(self, espesor, ancho, largo, n_bobinas, metro_lineal_eur):
        self.espesor = str(espesor) if espesor is not None else None
        try: self.ancho = float(ancho) if ancho is not None else None
        except (ValueError, TypeError): self.ancho = None
        try: self.largo = float(largo) if largo is not None else None
        except (ValueError, TypeError): self.largo = None
        try: self.n_bobinas = int(n_bobinas) if n_bobinas is not None else None
        except (ValueError, TypeError): self.n_bobinas = None
        try: self.metro_lineal_eur = float(metro_lineal_eur) if metro_lineal_eur is not None else None
        except (ValueError, TypeError): self.metro_lineal_eur = None
        self.precio_total_euro = None
        if self.metro_lineal_eur is not None and self.largo is not None and self.n_bobinas is not None:
            try: self.precio_total_euro = self.metro_lineal_eur * self.largo * self.n_bobinas
            except TypeError: print(f"Error calc precio base FieltroNacional")
        self.precio_total_euro_gastos = None
        self.metro_lineal_euro_mas_gastos = None
        self.metro_lineal_usd = None

    def __str__(self):
         return f"FieltroNacional (Esp: {self.espesor}, Ancho: {self.ancho}, N: {self.n_bobinas})"


