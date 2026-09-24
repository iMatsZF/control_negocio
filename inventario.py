from pathlib import Path

import pandas as pd


RAIZ = Path(__file__).resolve().parent

ENTRADA = RAIZ / "datos" / "entrada"

SALIDA = RAIZ / "datos" / "salida"

EVIDENCIAS = RAIZ / "evidencias"


for carpeta in (ENTRADA, SALIDA, EVIDENCIAS):

    carpeta.mkdir(parents=True, exist_ok=True)


RUTA_INVENTARIO = ENTRADA / "Inventario_Mercado_La_Cosecha.xlsx"

RUTA_VENTAS = ENTRADA / "Ventas_Mercado_La_Cosecha.xlsx"


if not RUTA_INVENTARIO.exists():

    raise FileNotFoundError(
        "No se encontró Inventario_Mercado_La_Cosecha.xlsx "
        "dentro de datos/entrada."
    )


if not RUTA_VENTAS.exists():

    raise FileNotFoundError(
        "No se encontró Ventas_Mercado_La_Cosecha.xlsx "
        "dentro de datos/entrada."
    )


print("Carpeta del proyecto:", RAIZ)

print("Inventario:", RUTA_INVENTARIO.name)

print("Ventas:", RUTA_VENTAS.name)
print("\nESTRUCTURA DEL PROYECTO")

print("📁", RAIZ.name)


for ruta in sorted(RAIZ.rglob("*")):

    nivel = len(ruta.relative_to(RAIZ).parts)

    marca = "📁" if ruta.is_dir() else "📄"

    print("    " * nivel + marca, ruta.name)
    inventario = pd.read_excel(
    RUTA_INVENTARIO,
    sheet_name="Inventario"
)

ventas = pd.read_excel(
    RUTA_VENTAS,
    sheet_name="Ventas"
)


print(
    "Inventario:",
    inventario.shape[0],
    "filas y",
    inventario.shape[1],
    "columnas"
)

print(
    "Ventas:",
    ventas.shape[0],
    "filas y",
    ventas.shape[1],
    "columnas"
)
print("\nPRIMERAS CINCO FILAS DEL INVENTARIO")

print(inventario.head().to_string(index=False))


print("\nPRIMERAS CINCO FILAS DE LAS VENTAS")

print(ventas.head().to_string(index=False))
print("Columnas del inventario:")
print(inventario.columns.tolist())
print("\nColumnas de las ventas:")
print(ventas.columns.tolist())
print("\nColumnas compartidas:")
print(sorted(set(inventario.columns) & set(ventas.columns)))
def diagnostico(nombre, tabla):

    return pd.DataFrame({

        "archivo": [nombre],

        "filas": [len(tabla)],

        "columnas": [len(tabla.columns)],

        "celdas_vacias": [
            int(tabla.isna().sum().sum())
        ],

        "filas_duplicadas": [
            int(tabla.duplicated().sum())
        ],

        "columnas_tipo_objeto": [
            int((tabla.dtypes == "object").sum())
        ]

    })


resumen_calidad = pd.concat(

    [

        diagnostico("inventario", inventario),

        diagnostico("ventas", ventas)

    ],

    ignore_index=True

)


print("\nRESUMEN INICIAL DE CALIDAD")

print(resumen_calidad.to_string(index=False))
print("\nVALORES FALTANTES EN INVENTARIO")

faltantes_inventario = (
    inventario
    .isna()
    .sum()
    .sort_values(ascending=False)
)

print(faltantes_inventario.to_string())


print("\nVALORES FALTANTES EN VENTAS")

faltantes_ventas = (
    ventas
    .isna()
    .sum()
    .sort_values(ascending=False)
)

print(faltantes_ventas.to_string())
print("\nTIPOS DE DATOS DEL INVENTARIO")

print(
    inventario
    .dtypes
    .astype(str)
    .to_string()
)


print("\nTIPOS DE DATOS DE LAS VENTAS")

print(
    ventas
    .dtypes
    .astype(str)
    .to_string()
)
ruta_evidencia = EVIDENCIAS / "diagnostico_inicial.csv"

resumen_calidad.to_csv(
    ruta_evidencia,
    index=False
)

print(
    "\nEvidencia guardada en:",
    ruta_evidencia
)
from datetime import datetime


registro = inventario.loc[
    inventario["codigo_producto"] == "P-001"
].iloc[0]


codigo_producto = str(registro["codigo_producto"])

producto = str(registro["producto"])

stock_inicial = int(registro["stock_actual"])

stock_minimo = int(registro["stock_minimo"])

costo_unitario = float(registro["costo_unitario"])

precio_venta = float(registro["precio_venta"])


print("\nPRODUCTO SELECCIONADO")

print("Código:", codigo_producto)

print("Producto:", producto)

print("Stock inicial:", stock_inicial)

print("Stock mínimo:", stock_minimo)

print("Costo unitario:", costo_unitario)

print("Precio de venta:", precio_venta)
print("\nMOVIMIENTO DE INVENTARIO")


entradas = int(
    input("Cantidad que llegó al negocio: ")
)

salidas = int(
    input("Cantidad vendida: ")
)


stock_actual = stock_inicial + entradas - salidas


print("Entradas:", entradas)

print("Salidas:", salidas)

print("Stock actualizado:", stock_actual)
if stock_actual <= 0:

    estado = "AGOTADO"

    recomendacion = "Realizar una compra urgente"

elif stock_actual < stock_minimo:

    estado = "STOCK BAJO"

    recomendacion = "Programar una compra"

elif stock_actual == stock_minimo:

    estado = "EN EL LÍMITE"

    recomendacion = (
        "Revisar las ventas antes de la siguiente compra"
    )

else:

    estado = "STOCK SUFICIENTE"

    recomendacion = "No comprar todavía"


print("\nEVALUACIÓN DEL STOCK")

print("Estado:", estado)

print("Recomendación:", recomendacion)
ventas_semana = [4, 6, 3, 8, 5, 10, 7]


total_vendido = sum(ventas_semana)

promedio_diario = total_vendido / len(ventas_semana)

venta_maxima = max(ventas_semana)

venta_minima = min(ventas_semana)


print("\nVENTAS DE LA SEMANA")

print("Ventas registradas:", ventas_semana)

print("Total vendido:", total_vendido)

print("Promedio diario:", round(promedio_diario, 2))

print("Venta máxima:", venta_maxima)

print("Venta mínima:", venta_minima)
margen_preventivo = round(
    promedio_diario * 2
)

objetivo_stock = stock_minimo + margen_preventivo

cantidad_comprar = objetivo_stock - stock_actual


if cantidad_comprar < 0:

    cantidad_comprar = 0


costo_estimado = cantidad_comprar * costo_unitario

valor_venta_estimado = cantidad_comprar * precio_venta


print("\nPROPUESTA DE COMPRA")

print("Margen preventivo:", margen_preventivo)

print("Objetivo de stock:", objetivo_stock)

print("Cantidad sugerida:", cantidad_comprar)

print("Costo estimado: $", round(costo_estimado, 2))

print(
    "Valor estimado de venta: $",
    round(valor_venta_estimado, 2)
)
fecha_reporte = datetime.now().strftime(
    "%Y-%m-%d %H:%M"
)


reporte = f"""MERCADO LA COSECHA
REPORTE DE INVENTARIO

Fecha: {fecha_reporte}
Código: {codigo_producto}
Producto: {producto}
Stock inicial: {stock_inicial}
Entradas: {entradas}
Salidas: {salidas}
Stock actualizado: {stock_actual}
Stock mínimo: {stock_minimo}
Estado: {estado}
Recomendación: {recomendacion}
Promedio diario: {promedio_diario:.2f}
Cantidad sugerida: {cantidad_comprar}
Costo estimado: ${costo_estimado:.2f}
Valor estimado de venta: ${valor_venta_estimado:.2f}
"""


ruta_reporte = (
    SALIDA / "reporte_programacion_1.txt"
)

ruta_reporte.write_text(
    reporte,
    encoding="utf-8"
)


print("\nREPORTE GENERADO")

print(reporte)

print("Archivo guardado en:", ruta_reporte)
