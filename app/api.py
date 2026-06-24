from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.overpass import buscar_negocios, obtener_ciudades_españa
from app.analyzer import generar_estadisticas
from app.excel_export import exportar_negocios_excel, exportar_estadisticas_excel

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


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
<select id="ciudad">
    <option>Cargando ciudades...</option>
</select>

<label><b>Categoría</b></label>
<select id="categoria">
    <option>Cargando categorías...</option>
</select>

<button onclick="buscar()"><b>Buscar negocios</b></button>

<div id="resultado"></div>

</div>

<script>

async function cargarCategorias(){

    let res = await fetch("/categorias");
    let data = await res.json();

    let select = document.getElementById("categoria");

    select.innerHTML = "";

    data.categorias.forEach(c => {
        let option = document.createElement("option");
        option.value = c.startsWith("*") ? "*" : c;
        option.textContent = c;
        select.appendChild(option);
    });
}

// 🔥 cargar ciudades al iniciar
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

async function buscar(){

    let ciudad = document.getElementById("ciudad").value;
    let categoria = document.getElementById("categoria").value;

    let res = await fetch(`/buscar?ciudad=${encodeURIComponent(ciudad)}&categoria=${encodeURIComponent(categoria)}`);
    let data = await res.json();

    document.getElementById("resultado").innerHTML = `
        <h3>Resultado</h3>
        <p><b>Ciudad:</b> ${data.ciudad}</p>
        <p><b>Categoría:</b> ${data.categoria}</p>
        <p><b>Total negocios:</b> ${data.total_negocios}</p>
        <p>Excel generado en /output</p>
    `;
}

// iniciar
cargarCiudades();
cargarCategorias();

</script>

</body>
</html>
"""


@app.get("/buscar")
def buscar(ciudad: str, categoria: str = "*"):

    negocios = buscar_negocios(ciudad, categoria)

    archivo_negocios = exportar_negocios_excel(negocios)

    estadisticas = generar_estadisticas(negocios)

    archivo_estadisticas = exportar_estadisticas_excel(estadisticas)

    return {
        "ciudad": ciudad,
        "categoria": categoria,
        "total_negocios": len(negocios)
    }


@app.get("/ciudades")
def ciudades():
    return {
        "ciudades": obtener_ciudades_españa()
    }


from app.overpass import obtener_categorias

@app.get("/categorias")
def categorias():
    return {
        "categorias": obtener_categorias()
    }