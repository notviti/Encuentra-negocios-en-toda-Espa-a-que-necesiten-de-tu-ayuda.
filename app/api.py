import io
import zipfile

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse

from app.overpass import (
    buscar_negocios,
    obtener_ciudades_españa,
    obtener_categorias
)

from app.analyzer import generar_estadisticas
from app.excel_export import (
    exportar_negocios_excel,
    exportar_estadisticas_excel
)

app = FastAPI()


# -------------------------
# FRONTEND
# -------------------------
@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Business Tracker</title>

<style>

h1 {
    text-align: center;
}

h3 {
    text-align: center;
}

body{
    font-family: Trebuchet MS;
    background: linear-gradient(to right, #f2f2f2, #dbdbdb);
    height: 100vh;
    margin: 0;
    padding:40px;
}

.container{
    max-width:700px;
    margin:auto;
    background: white;
    padding:30px;
    border-radius:12px;
    box-shadow:0 0 20px rgba(0,0,0,0.1);
}

select, input{
    width:100%;
    padding:12px;
    margin-top:10px;
    margin-bottom:15px;
}

button{
    width:100%;
    padding:12px;
    background:#2563eb;
    color:white;
    border:none;
    border-radius:20px;
    cursor:pointer;
}

button:hover{
    background:#1d4ed8;
}

#resultado{
    margin-top:20px;
    padding:15px;
    background:#eef2ff;
    border-radius:8px;
}
</style>

</head>

<body>

<h1>Business Tracker</h1>
<h3>Encuentra negocios en toda España que necesiten de tu ayuda.</h3>

<div class="container">

<label><b>Ciudad</b></label>
<select id="ciudad"></select>

<label><b>Categoría</b></label>
<select id="categoria"></select>

<button onclick="descargar()"><b>Descargar análisis ZIP</b></button>

<div id="resultado"></div>

</div>

<script>

// CIUDADES
async function cargarCiudades(){

    let res = await fetch("/ciudades");
    let data = await res.json();

    let select = document.getElementById("ciudad");

    select.innerHTML = "";

    data.ciudades.forEach(c => {

        let option = document.createElement("option");

        option.value = c;
        option.textContent = c;

        select.appendChild(option);

    });
}


// CATEGORÍAS
async function cargarCategorias(){

    let res = await fetch("/categorias");
    let data = await res.json();

    let select = document.getElementById("categoria");
    select.innerHTML = "";

    data.categorias.forEach((c, index) => {

        let option = document.createElement("option");

        option.value = c.startsWith("*") ? "*" : c;
        option.textContent = c;

        // Seleccionar automáticamente la primera opción (* TODAS)
        if(index === 0){
            option.selected = true;
        }

        select.appendChild(option);
    });
}


// DESCARGA ZIP
function descargar(){

    let ciudad = document.getElementById("ciudad").value;

    let categoria =
        document.getElementById("categoria").value || "*";

    window.location.href =
        `/descargar?ciudad=${encodeURIComponent(ciudad)}&categoria=${encodeURIComponent(categoria)}`;
}


// INIT
cargarCiudades();
cargarCategorias();

</script>

</body>
</html>
"""

@app.get("/ciudades")
def ciudades():
    return {
        "ciudades": obtener_ciudades_españa()
    }


# -------------------------
# ZIP DOWNLOAD
# -------------------------
@app.get("/descargar")
def descargar(ciudad: str, categoria: str = "*"):

    negocios = buscar_negocios(ciudad, categoria)

    archivo_negocios = exportar_negocios_excel(negocios)

    estadisticas = generar_estadisticas(negocios)

    archivo_estadisticas = exportar_estadisticas_excel(estadisticas)

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:

        zip_file.write(
            archivo_negocios,
            arcname=f"{ciudad}_negocios.xlsx"
        )

        zip_file.write(
            archivo_estadisticas,
            arcname=f"{ciudad}_analisis.xlsx"
        )

    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition":
            f'attachment; filename="{ciudad}_analisis.zip"'
        }
    )


# -------------------------
# API SIMPLE
# -------------------------
@app.get("/buscar")
def buscar(ciudad: str, categoria: str = "*"):

    negocios = buscar_negocios(ciudad, categoria)

    return {
        "ciudad": ciudad,
        "categoria": categoria,
        "total_negocios": len(negocios)
    }


@app.get("/categorias")
def categorias():
    return {
        "categorias": obtener_categorias()
    }


