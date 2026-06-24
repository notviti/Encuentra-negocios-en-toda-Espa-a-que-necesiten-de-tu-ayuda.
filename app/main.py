from app.overpass import buscar_negocios
from app.analyzer import generar_estadisticas
from app.excel_export import (
    exportar_negocios_excel,
    exportar_estadisticas_excel
)

print("Buscando negocios...")

negocios = buscar_negocios("Oviedo")

print("Total:", len(negocios))

exportar_negocios_excel(negocios)

estadisticas = generar_estadisticas(negocios)

exportar_estadisticas_excel(estadisticas)

print("FIN")