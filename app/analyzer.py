import pandas as pd


def generar_estadisticas(negocios):

    df = pd.DataFrame(negocios)

    if df.empty:
        return pd.DataFrame(columns=[
            "categoria",
            "total_negocios",
            "con_web",
            "sin_web",
            "porcentaje_sin_web"
        ])

    resultados = []

    for categoria, grupo in df.groupby("categoria"):

        total = len(grupo)
        con_web = len(grupo[grupo["estado_web"] == "Tiene web"])
        sin_web = len(grupo[grupo["estado_web"] == "No tiene web"])

        porcentaje = round((sin_web / total) * 100, 2)

        resultados.append({
            "categoria": categoria,
            "total_negocios": total,
            "con_web": con_web,
            "sin_web": sin_web,
            "porcentaje_sin_web": porcentaje
        })

    return pd.DataFrame(resultados).sort_values(
        by="porcentaje_sin_web",
        ascending=False
    )