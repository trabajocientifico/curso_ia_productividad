# -*- coding: utf-8 -*-
"""Carga y limpieza de datos_ventas.xlsx -> datos_ventas_limpio.xlsx"""
import re
import unicodedata
import pandas as pd

# --- Cargar ---
datos = pd.read_excel("datos_ventas.xlsx")
print(f"Filas iniciales: {len(datos)}")

# (1) Eliminar filas duplicadas
datos = datos.drop_duplicates().reset_index(drop=True)
print(f"Tras quitar duplicados: {len(datos)}")


# (2) Limpiar texto en ciudad y categoria: quitar espacios y unificar mayus/acentos
def normaliza_texto(valor):
    if pd.isna(valor):
        return valor
    texto = str(valor).strip()
    # Reparar acentos que llegaron corruptos (caracter de reemplazo U+FFFD)
    corregir = {
        "medell�n": "medellin",
        "bogot�": "bogota",
        "tecnolog�a": "tecnologia",
    }
    texto = corregir.get(texto.lower(), texto)
    # Quitar acentos y colapsar espacios internos
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto.title()  # unifica mayus/minus (Title Case)


datos["ciudad"] = datos["ciudad"].apply(normaliza_texto)
datos["categoria"] = datos["categoria"].apply(normaliza_texto)
print("Ciudades:", sorted(datos["ciudad"].dropna().unique()))
print("Categorias:", sorted(datos["categoria"].dropna().unique()))


# (3) Convertir a numero: quitar "$" y puntos de miles
def a_numero(valor):
    if pd.isna(valor):
        return pd.NA
    texto = str(valor).strip()
    # Deja solo digitos y signo negativo (elimina $, puntos de miles, espacios)
    texto = re.sub(r"[^\d-]", "", texto)
    if texto in ("", "-"):
        return pd.NA
    return int(texto)


for col in ["cantidad", "precio_unitario", "total_venta"]:
    datos[col] = datos[col].apply(a_numero).astype("Float64")

# (4) Recalcular total_venta = cantidad * precio_unitario donde falte
faltan = datos["total_venta"].isna()
datos.loc[faltan, "total_venta"] = datos.loc[faltan, "cantidad"] * datos.loc[faltan, "precio_unitario"]
print(f"total_venta recalculados: {int(faltan.sum())}")

# (5) Eliminar filas con cantidad <= 0
antes = len(datos)
datos = datos[datos["cantidad"] > 0].reset_index(drop=True)
print(f"Filas con cantidad <= 0 eliminadas: {antes - len(datos)}")

# (6) Rellenar satisfaccion vacia con la mediana
mediana_sat = datos["satisfaccion"].median()
n_vacias = int(datos["satisfaccion"].isna().sum())
datos["satisfaccion"] = datos["satisfaccion"].fillna(mediana_sat)
print(f"satisfaccion vacias rellenadas con mediana={mediana_sat}: {n_vacias}")

# Tipos enteros donde aplica (ya sin nulos)
datos["cantidad"] = datos["cantidad"].astype("int64")
datos["total_venta"] = datos["total_venta"].astype("int64")

# --- Guardar ---
datos.to_excel("datos_ventas_limpio.xlsx", index=False)
print(f"\nGuardado datos_ventas_limpio.xlsx con {len(datos)} filas.")
print(datos.dtypes)
print("Nulos restantes:\n", datos.isnull().sum())
