# -*- coding: utf-8 -*-
"""
Construye _columnas.json: el catálogo de columnas publicadas.

POR QUÉ EXISTE
Antes los generadores leían las tarjetas de index.html y todas.html.
Eso creaba una dependencia circular: al regenerar index.html con el
formato nuevo desaparecían las tarjetas viejas y el siguiente generador
se quedaba sin datos (así se perdió una columna en la primera pasada).

El manifiesto rompe el círculo: es un archivo propio, versionado, que
declara qué columnas hay y con qué portada. Los generadores lo leen a
él, no a las páginas que ellos mismos escriben.

    python _generar_manifiesto.py            # actualiza _columnas.json
    python _generar_manifiesto.py --revisar  # solo informa, no escribe

Al publicar una columna nueva basta con volver a correrlo.
"""
import io, re, sys, json, pathlib, subprocess

AQUI = pathlib.Path(__file__).resolve().parent
MANIF = AQUI / "_columnas.json"
META = {"index.html", "todas.html", "acerca.html", "expedientes.html", "privacidad.html"}
BORRADORES = {"columna-ejemplo.html", "_template.html"}


def tarjetas(html):
    """Saca de un HTML todas las tarjetas de columna que encuentre."""
    out = {}
    for b in re.findall(r'<a class="card[^"]*".*?</a>', html, re.S):
        h  = re.search(r'href="([^"]+)"', b)
        im = re.search(r'card-img"><img src="([^"]+)"', b)
        ca = re.search(r'<span class="date">([^<]*)</span>', b)
        t  = re.search(r"<h3>(.*?)</h3>", b, re.S)
        p  = re.search(r"<p>(.*?)</p>", b, re.S)
        dc = re.search(r'data-cat="([^"]*)"', b)
        dt = re.search(r'data-title="([^"]*)"', b)
        if not (h and im and t) or h.group(1).startswith("http"):
            continue
        out[h.group(1)] = {
            "href": h.group(1), "img": im.group(1),
            "cat": ca.group(1).strip() if ca else "",
            "dcat": dc.group(1).split() if dc else [],
            "claves": dt.group(1) if dt else "",
            "titulo": t.group(1).strip(),
            "dek": re.sub(r"<[^>]+>", "", p.group(1)).strip() if p else "",
        }
    return out


def desde_git(archivo):
    """La versión de un archivo tal como está en el último commit.
    Sirve para rescatar las tarjetas del index.html anterior al rediseño."""
    try:
        r = subprocess.run(["git", "show", f"HEAD:{archivo}"], cwd=AQUI,
                           capture_output=True, timeout=20)
        return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else ""
    except Exception:
        return ""


def construir():
    fichas = {}
    # las fuentes se leen de la MENOS a la MÁS confiable: la última gana
    for origen in (desde_git("index.html"), desde_git("todas.html")):
        fichas.update(tarjetas(origen))
    for pag in ("todas.html", "index.html"):
        f = AQUI / pag
        if f.exists():
            fichas.update(tarjetas(io.open(f, encoding="utf-8").read()))
    if MANIF.exists():   # lo ya declarado no se pierde por un HTML regenerado
        previo = {c["href"]: c for c in json.loads(io.open(MANIF, encoding="utf-8").read())}
        for h, c in previo.items():
            fichas.setdefault(h, c)

    vivas = []
    for h, c in fichas.items():
        if h in META or h in BORRADORES or not (AQUI / h).exists():
            continue
        s = io.open(AQUI / h, encoding="utf-8").read()
        d = re.search(r'"datePublished":\s*"([0-9-]{10})"', s)
        m = re.search(r'<div class="article-meta">\s*<span>(.*?)</span>', s, re.S) \
            or re.search(r'<span class="meta">(\d+ min)', s)
        # si la página aún no declara fecha o minutos (una recién generada
        # trae el JSON-LD hasta que corre el SEO), lo ya sabido NO se borra
        c["iso"] = d.group(1) if d else c.get("iso", "")
        c["min"] = (m.group(1).strip().replace(" de lectura", "") if m else c.get("min", ""))
        au = AQUI / ("audio-" + h.replace(".html", "") + ".mp3")
        c["audio"] = au.name if au.exists() else ""
        vivas.append(c)
    vivas.sort(key=lambda c: c["iso"], reverse=True)
    return vivas


def main(revisar=False):
    cols = construir()
    sin_img = [c["href"] for c in cols if not c["img"]]
    sin_fec = [c["href"] for c in cols if not c["iso"]]
    huerf = [p.name for p in sorted(AQUI.glob("*.html"))
             if p.name not in META and p.name not in BORRADORES
             and p.name not in {c["href"] for c in cols}]

    print("columnas en el manifiesto: %d" % len(cols))
    print("  con audio : %d" % sum(1 for c in cols if c["audio"]))
    if sin_img: print("  SIN portada:", ", ".join(sin_img))
    if sin_fec: print("  SIN fecha  :", ", ".join(sin_fec))
    if huerf:   print("  no publicadas (fuera):", ", ".join(huerf))

    if revisar:
        print("  (--revisar: no se escribió nada)")
        return 0
    io.open(MANIF, "w", encoding="utf-8").write(
        json.dumps(cols, ensure_ascii=False, indent=1))
    print("escrito: _columnas.json")
    return 0


if __name__ == "__main__":
    sys.exit(main("--revisar" in sys.argv))
