import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def construir_direccion(tags):
    return " ".join([
        tags.get("addr:street", ""),
        tags.get("addr:housenumber", ""),
        tags.get("addr:postcode", ""),
        tags.get("addr:city", "")
    ]).strip()


def buscar_negocios(ciudad, categoria="*"):

    filtro = f'["amenity"="{categoria}"]' if categoria != "*" else '["amenity"]'

    query = f"""
    [out:json][timeout:25];

    area["name"="{ciudad}"]["boundary"="administrative"]->.searchArea;

    (
      node{filtro}(area.searchArea);
    );

    out tags 500;
    """

    response = requests.post(
        OVERPASS_URL,
        data=query,
        timeout=40,
        headers={"User-Agent": "NegociosAPI/1.0"}
    )

    data = response.json()

    negocios = []

    for el in data.get("elements", []):

        tags = el.get("tags", {})

        nombre = tags.get("name")
        if not nombre:
            continue

        website = tags.get("website") or tags.get("contact:website", "")

        negocios.append({
            "nombre": nombre,
            "categoria": tags.get("amenity", "sin_categoria"),
            "direccion": construir_direccion(tags),
            "telefono": tags.get("phone", ""),
            "website": website,
            "estado_web": "Tiene web" if website else "No tiene web"
        })

    return negocios

def obtener_ciudades_españa():

    query = """
    [out:json][timeout:25];

    area["name"="España"]->.a;

    relation["boundary"="administrative"]["admin_level"="8"](area.a);

    out tags;
    """

    response = requests.post(
        OVERPASS_URL,
        data=query,
        timeout=40,
        headers={"User-Agent": "NegociosAPI/1.0"}
    )

    data = response.json()

    ciudades = []

    for el in data.get("elements", []):

        tags = el.get("tags", {})

        nombre = tags.get("name")

        # ❌ FILTRO 1: eliminar vacíos
        if not nombre:
            continue

        # ❌ FILTRO 2: eliminar nombres con números al inicio
        if nombre[0].isdigit():
            continue

        # ❌ FILTRO 3: eliminar nombres técnicos raros
        if "relation" in nombre.lower():
            continue

        if "faza" in nombre.lower():
            continue

        ciudades.append(nombre.strip())

    # 🔥 eliminar duplicados y ordenar
    ciudades = sorted(list(set(ciudades)))

    return ciudades

def obtener_categorias():

    return [
        "* (TODAS)",
        "restaurant",
        "cafe",
        "bar",
        "fast_food",
        "bank",
        "pharmacy",
        "dentist",
        "school",
        "hospital",
        "hotel",
        "car_repair",
        "supermarket"
    ]