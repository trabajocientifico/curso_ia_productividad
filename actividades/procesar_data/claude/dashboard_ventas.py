# -*- coding: utf-8 -*-
"""Dashboard de ventas a partir de datos_ventas_limpio.xlsx -> dashboard_ventas.png"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

datos = pd.read_excel("datos_ventas_limpio.xlsx")

# Normalizar metodo_pago (Efectivo / Tarjeta / Transferencia; "Transf." -> Transferencia)
mapa_pago = {"transf.": "Transferencia", "transf": "Transferencia"}
datos["metodo_pago"] = (
    datos["metodo_pago"].str.strip().str.lower()
    .map(lambda x: mapa_pago.get(x, x)).str.title()
)

# Orden cronologico de los meses
orden_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
               "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# --- Figura con 4 paneles ---
fig, axes = plt.subplots(2, 2, figsize=(15, 10))
fig.suptitle("Dashboard de Ventas 2025", fontsize=20, fontweight="bold")
COLOR = "#0e7490"

# (1) Ventas totales por ciudad - barras
ventas_ciudad = datos.groupby("ciudad")["total_venta"].sum().sort_values(ascending=False)
ax = axes[0, 0]
barras = ax.bar(ventas_ciudad.index, ventas_ciudad.values / 1e6, color=COLOR)
ax.set_title("Ventas totales por ciudad", fontweight="bold")
ax.set_ylabel("Ventas (millones $)")
ax.bar_label(barras, fmt="%.1f", padding=2, fontsize=9)
ax.tick_params(axis="x", rotation=20)

# (2) Participacion por categoria - dona
part_categoria = datos.groupby("categoria")["total_venta"].sum().sort_values(ascending=False)
ax = axes[0, 1]
ax.pie(part_categoria.values, labels=part_categoria.index, autopct="%1.1f%%",
       startangle=90, pctdistance=0.8, wedgeprops=dict(width=0.4))
ax.set_title("Participacion por categoria", fontweight="bold")

# (3) Tendencia de total_venta por mes - linea
ventas_mes = datos.groupby("mes")["total_venta"].sum().reindex(orden_meses)
ax = axes[1, 0]
ax.plot(ventas_mes.index, ventas_mes.values / 1e6, marker="o", color=COLOR, linewidth=2)
ax.set_title("Tendencia de ventas por mes", fontweight="bold")
ax.set_ylabel("Ventas (millones $)")
ax.tick_params(axis="x", rotation=45)
ax.grid(True, alpha=0.3)

# (4) Satisfaccion promedio por metodo_pago - barras
sat_pago = datos.groupby("metodo_pago")["satisfaccion"].mean().sort_values(ascending=False)
ax = axes[1, 1]
barras = ax.bar(sat_pago.index, sat_pago.values, color=COLOR)
ax.set_title("Satisfaccion promedio por metodo de pago", fontweight="bold")
ax.set_ylabel("Satisfaccion (1-5)")
ax.set_ylim(0, 5)
ax.bar_label(barras, fmt="%.2f", padding=2, fontsize=9)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig("dashboard_ventas.png", dpi=150, bbox_inches="tight")
print("Guardado dashboard_ventas.png")
