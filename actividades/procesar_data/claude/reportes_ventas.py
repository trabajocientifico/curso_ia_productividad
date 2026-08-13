# -*- coding: utf-8 -*-
"""Reportes por ciudad y resumen por categoria desde datos_ventas_limpio.xlsx"""
import os
import re
import pandas as pd

datos = pd.read_excel("datos_ventas_limpio.xlsx")

# Utilidad por fila = total_venta - (costo_unitario * cantidad)
datos["utilidad"] = datos["total_venta"] - datos["costo_unitario"] * datos["cantidad"]


def nombre_archivo(texto):
    """Nombre seguro para archivo (sin espacios ni caracteres raros)."""
    return re.sub(r"[^\w]+", "_", str(texto).strip()).lower()


# (1) Un Excel por cada ciudad dentro de reportes_por_ciudad/
carpeta = "reportes_por_ciudad"
os.makedirs(carpeta, exist_ok=True)
for ciudad, grupo in datos.groupby("ciudad"):
    ruta = os.path.join(carpeta, f"ventas_{nombre_archivo(ciudad)}.xlsx")
    grupo.to_excel(ruta, index=False)
    print(f"  {ruta}: {len(grupo)} filas")

# (2) resumen_ventas.xlsx: una hoja por categoria + hoja Resumen
resumen = (
    datos.groupby("ciudad")[["total_venta", "utilidad"]]
    .sum()
    .sort_values("total_venta", ascending=False)
    .reset_index()
)

with pd.ExcelWriter("resumen_ventas.xlsx", engine="openpyxl") as writer:
    # Hoja Resumen primero
    resumen.to_excel(writer, sheet_name="Resumen", index=False)
    # Una hoja por categoria
    for categoria, grupo in datos.groupby("categoria"):
        hoja = str(categoria)[:31]  # Excel limita el nombre de hoja a 31 caracteres
        grupo.to_excel(writer, sheet_name=hoja, index=False)
        print(f"  hoja '{hoja}': {len(grupo)} filas")

print("\nGuardado resumen_ventas.xlsx")
print(resumen.to_string(index=False))
