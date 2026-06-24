from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"


def exportar_negocios_excel(negocios):

    OUTPUT_DIR.mkdir(exist_ok=True)

    archivo = OUTPUT_DIR / "negocios.xlsx"

    pd.DataFrame(negocios).to_excel(archivo, index=False)

    return archivo


def exportar_estadisticas_excel(df):

    OUTPUT_DIR.mkdir(exist_ok=True)

    archivo = OUTPUT_DIR / "estadisticas.xlsx"

    df.to_excel(archivo, index=False)

    return archivo