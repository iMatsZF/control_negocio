# 1. IMPORTACIONES Y RUTAS
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import re
import unicodedata
import pandas as pd

try:
    from IPython.display import display
except ImportError:
    def display(objeto):
        print(objeto.to_string(index=False) if hasattr(objeto, "to_string") else objeto)

def localizar_raiz_control_negocio():
    candidatos = [Path.cwd(), Path.cwd() / "control_negocio", Path.cwd().parent]
    for candidato in candidatos:
        if (candidato / "datos" / "entrada").exists():
            return candidato.resolve()
    raise FileNotFoundError(
        "No se encontró datos/entrada. Abre control_negocio como carpeta en VS Code."
    )

RAIZ = localizar_raiz_control_negocio()
ENTRADA = RAIZ / "datos" / "entrada"
SALIDA = RAIZ / "datos" / "salida"
EVIDENCIAS = RAIZ / "evidencias"
SALIDA.mkdir(parents=True, exist_ok=True)
EVIDENCIAS.mkdir(parents=True, exist_ok=True)

print("Raíz del proyecto:", RAIZ)

# 2. CARGA INDEPENDIENTE Y RECUPERACIÓN SEGURA
inventario_limpio = SALIDA / "Inventario_Limpio.xlsx"
inventario_original = ENTRADA / "Inventario_Mercado_La_Cosecha.xlsx"

if inventario_limpio.exists():
    inventario = pd.read_excel(inventario_limpio)
    fuente_inventario = inventario_limpio
elif inventario_original.exists():
    inventario = pd.read_excel(inventario_original)
    fuente_inventario = inventario_original
else:
    raise FileNotFoundError("No se encontró un inventario para iniciar la Práctica 4.")

inventario = inventario.copy()
if inventario.empty:
    raise ValueError(f"El archivo {fuente_inventario.name} no contiene productos.")
print("Fuente utilizada:", fuente_inventario.name)
display(inventario.head())

# 3. COLUMNAS DEL INVENTARIO
def normalizar_nombre(texto):
    texto = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    texto = re.sub(r"[^a-zA-Z0-9]+", "_", texto.strip().lower())
    return texto.strip("_")

columnas_inv = {normalizar_nombre(col): col for col in inventario.columns}

def buscar_columna(mapa, alias, obligatoria=True):
    for nombre in alias:
        if nombre in mapa:
            return mapa[nombre]
    if obligatoria:
        raise KeyError(f"No se encontró {alias}. Disponibles: {list(mapa.values())}")
    return None

COL_CODIGO = buscar_columna(
    columnas_inv, ["codigo_producto", "codigo", "id_producto", "producto_id", "clave", "sku"]
)
COL_STOCK = buscar_columna(
    columnas_inv, ["stock_actual", "stock", "stock_inicial", "existencia", "existencias", "cantidad"]
)
COL_NOMBRE = buscar_columna(
    columnas_inv, ["nombre_producto", "producto", "nombre", "descripcion"], obligatoria=False
)

inventario[COL_CODIGO] = inventario[COL_CODIGO].astype(str).str.strip()
inventario[COL_STOCK] = pd.to_numeric(inventario[COL_STOCK], errors="coerce").fillna(0)

print("Código:", COL_CODIGO, "| Stock:", COL_STOCK)

# 4. INTEGRAR VENTAS CUANDO EL ARCHIVO ESTÁ DISPONIBLE
ruta_ventas = ENTRADA / "Ventas_Mercado_La_Cosecha.xlsx"
inventario["ventas_acumuladas_p4"] = 0.0

if ruta_ventas.exists():
    ventas = pd.read_excel(ruta_ventas).copy()
    columnas_ventas = {normalizar_nombre(col): col for col in ventas.columns}
    col_codigo_ventas = buscar_columna(
        columnas_ventas,
        ["codigo_producto", "codigo", "id_producto", "producto_id", "clave", "sku"],
        obligatoria=False,
    )
    col_cantidad_ventas = buscar_columna(
        columnas_ventas,
        ["cantidad_vendida", "unidades_vendidas", "cantidad", "unidades", "ventas"],
        obligatoria=False,
    )

    if col_codigo_ventas and col_cantidad_ventas:
        ventas[col_codigo_ventas] = ventas[col_codigo_ventas].astype(str).str.strip()
        ventas[col_cantidad_ventas] = pd.to_numeric(
            ventas[col_cantidad_ventas], errors="coerce"
        ).fillna(0)
        acumulado = ventas.groupby(col_codigo_ventas)[col_cantidad_ventas].sum()
        inventario["ventas_acumuladas_p4"] = (
            inventario[COL_CODIGO].map(acumulado).fillna(0)
        )
        print("Ventas integradas correctamente.")
    else:
        print("El archivo de ventas no tiene columnas reconocibles; se continuará con ventas = 0.")
else:
    print("No se encontró el archivo de ventas; se continuará con ventas = 0.")

display(inventario[[COL_CODIGO, COL_STOCK, "ventas_acumuladas_p4"]].head())

# 5. ÁRBOL DE DECISIÓN REPRESENTADO CON DICCIONARIOS ANIDADOS
UMBRAL_STOCK = 10
mediana_ventas = float(inventario["ventas_acumuladas_p4"].median())

arbol_decision = {
    "campo": "stock",
    "operador": "<=",
    "valor": 0,
    "si": "CRÍTICA: producto agotado",
    "no": {
        "campo": "stock",
        "operador": "<=",
        "valor": UMBRAL_STOCK,
        "si": {
            "campo": "ventas",
            "operador": ">=",
            "valor": mediana_ventas,
            "si": "ALTA: stock bajo y venta relevante",
            "no": "MEDIA: stock bajo y venta menor",
        },
        "no": {
            "campo": "stock",
            "operador": "<=",
            "valor": UMBRAL_STOCK * 2,
            "si": "VIGILAR: stock cercano al umbral",
            "no": "ESTABLE: sin alerta inmediata",
        },
    },
}

def comparar(valor_actual, operador, referencia):
    if operador == "<=":
        return valor_actual <= referencia
    if operador == ">=":
        return valor_actual >= referencia
    raise ValueError(f"Operador no soportado: {operador}")

def evaluar_arbol(nodo, contexto):
    # Caso base: llegamos a una hoja de texto.
    if isinstance(nodo, str):
        return nodo

    valor_actual = contexto[nodo["campo"]]
    resultado = comparar(valor_actual, nodo["operador"], nodo["valor"])
    siguiente = nodo["si"] if resultado else nodo["no"]
    return evaluar_arbol(siguiente, contexto)  # llamada recursiva
