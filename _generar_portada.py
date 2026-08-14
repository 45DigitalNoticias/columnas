# -*- coding: utf-8 -*-
"""
Genera la portada (index.html) con el formato editorial.

NO se edita index.html a mano: se genera. La portada muestra las 87
columnas publicadas y eso cambia cada vez que sale una nueva.

    python _generar_portada.py            # escribe index.html
    python _generar_portada.py --prueba   # escribe _portada-prueba.html

Conserva del index.html actual TODO el andamio de publicación
(description, og, canonical, JSON-LD, favicon, GA4, aviso de cookies y
beacon de Cloudflare): se toma el <head> tal cual y se le quita solo lo
que la plantilla nueva repone.
"""
import io, re, sys, json, pathlib, colorsys

from _portada_tpl import (PLANTILLA, EXPEDIENTES, FB,
                          SVG_FB, SVG_WA, SVG_X, SVG_CP, SVG_RSS, SVG_SALIR)

AQUI = pathlib.Path(__file__).resolve().parent
DESTACADAS = 5          # cuántas rotan en el hero
CARRIL     = 3          # cuántas van en el carril lateral

CATS = [  # etiqueta, filtro data-cat, icono
 ("Seguridad", "seguridad", '<path d="M12 3l7 3v6c0 4.2-2.8 7.6-7 9-4.2-1.4-7-4.8-7-9V6l7-3z"/>'),
 ("Morelos", "morelos", '<path d="M12 21s6-5.7 6-10a6 6 0 10-12 0c0 4.3 6 10 6 10z"/><circle cx="12" cy="11" r="2.2"/>'),
 ("Economía", "economia", '<path d="M3 19h18"/><path d="M4 15l5-5 3.5 3.5L20 6"/><path d="M20 10V6h-4"/>'),
 ("Justicia", "justicia", '<path d="M12 4v16M8 20h8M5 7h14M12 5.5L5 7l-2 5a3.2 3.2 0 004 0zM12 5.5L19 7l2 5a3.2 3.2 0 01-4 0z"/>'),
 ("Mundial 2026", "mundial", '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17"/><path d="M12 3.5c2.4 2.4 2.4 14.6 0 17M12 3.5c-2.4 2.4-2.4 14.6 0 17"/>'),
 ("Cultura", "cultura", '<path d="M12 7.5C10.3 6 8 5.5 4 5.5v12c4 0 6.3.5 8 2 1.7-1.5 4-2 8-2v-12c-4 0-6.3.5-8 2z"/><path d="M12 7.5v12"/>'),
 ("Democracia", "democracia", '<path d="M3 20h18M4 20V9.5M20 20V9.5M8 20V9.5M12 20V9.5M16 20V9.5M2.5 9.5L12 4l9.5 5.5z"/>'),
 ("Poder", "poder", '<circle cx="12" cy="5" r="2.1"/><circle cx="5" cy="17" r="2.1"/><circle cx="19" cy="17" r="2.1"/><path d="M10.4 6.6L6.6 15M13.6 6.6L17.4 15M7.1 17h9.8"/>'),
]
MES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
       "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


# ------------------------------------------------------------------ datos
def columnas():
    """Las publicadas, desde _columnas.json.

    NO se leen las tarjetas de index.html ni todas.html: esos archivos
    los escribe este mismo generador, así que usarlos como fuente crea
    una dependencia circular. En la primera pasada eso costó una columna:
    al regenerar index.html sus tarjetas viejas desaparecieron y con
    ellas el único registro de una pieza que no estaba en todas.html.

    El manifiesto lo construye _generar_manifiesto.py."""
    import json
    m = AQUI / "_columnas.json"
    if not m.exists():
        raise SystemExit("Falta _columnas.json. Corre antes:  python _generar_manifiesto.py")
    cols = json.loads(io.open(m, encoding="utf-8").read())
    return [c for c in cols if (AQUI / c["href"]).exists()]


def orden_panel():
    """Las portadas intercaladas por familia de color.

    Alfabéticamente los matices se agrupan y el muro se ve de un solo
    color: 28 de las 93 caen en la familia cian. Este orden nunca repite
    familia en piezas seguidas."""
    from PIL import Image

    def fam(h):
        return ("ambar" if h < 60 else "verde" if h < 160 else
                "cian" if h < 225 else "violeta" if h < 300 else "magenta")

    grupos = {}
    for t in sorted((AQUI / "thumbs").iterdir()):
        if t.suffix == ".svg":            # a los svg no se les puede medir el matiz
            grupos.setdefault("ambar", []).append(t.name)
            continue
        im = Image.open(t).convert("RGB").resize((40, 40))
        tot = [0, 0, 0]
        peso = 0.0
        for r, g, b in im.getdata():
            hh, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            w = s * v + .05
            tot[0] += r * w; tot[1] += g * w; tot[2] += b * w; peso += w
        hh, _, _ = colorsys.rgb_to_hsv(*[c / peso / 255 for c in tot])
        grupos.setdefault(fam(int(hh * 360)), []).append(t.name)

    orden, prev = [], None
    while any(grupos.values()):
        cand = sorted([k for k, v in grupos.items() if v and k != prev],
                      key=lambda k: -len(grupos[k])) or [k for k, v in grupos.items() if v]
        k = cand[0]
        orden.append(grupos[k].pop(0))
        prev = k
    return orden


def fecha_larga(iso):
    try:
        a, m, d = iso.split("-")
        return "%d de %s de %s" % (int(d), MES[int(m) - 1], a)
    except Exception:
        return ""


def fecha_corta(iso):
    try:
        a, m, d = iso.split("-")
        return "%d %s %s" % (int(d), MES[int(m) - 1][:3], a)
    except Exception:
        return ""


def conservar(s):
    """El andamio de publicación de la página actual, tal cual."""
    head = s[s.index("<head>") + 6: s.index("</head>")]
    for pat in (r"<title>.*?</title>", r"<meta charset[^>]*>",
                r'<meta name="viewport"[^>]*>', r'<link rel="preconnect"[^>]*>',
                r'<link href="https://fonts\.googleapis[^>]*>',
                r'<link rel="stylesheet"[^>]*>'):
        head = re.sub(pat, "", head, flags=re.S)
    piezas = []
    ck = (re.search(r"<style>\s*#ck-consent.*?<!--\s*/Cookie consent.*?-->", s, re.S)
          or re.search(r"<style>\s*#ck-consent.*?\)\(\);\s*</script>", s, re.S))
    if ck:
        piezas.append(ck.group(0).strip())
    bc = re.search(r"<!--\s*Cloudflare Web Analytics\s*-->.*?<!--\s*End Cloudflare Web Analytics\s*-->", s, re.S)
    if bc:
        piezas.append(bc.group(0).strip())
    return re.sub(r"\n\s*\n+", "\n", head).strip(), "\n".join(piezas)


# ------------------------------------------------------------------ armado
def esc(t):
    return re.sub(r"<[^>]+>", "", t).replace('"', "&quot;").strip()


FILA = """      <div class="fila" data-t="{dcat}" data-href="{href}" data-date="{iso}"{au}>
        <span class="num">{num:03d}</span><span class="fecha">{fecha}</span>
        <div><h3>{titulo}</h3><p class="dek">{dek}</p></div>
        <span class="tema">{cat}</span><span class="min">{min}</span>
        {boton}<span class="pista"></span>
      </div>"""

BOTON_OIR = ('<button class="oir" type="button" aria-label="Escuchar la columna">'
             '<svg class="play" viewBox="0 0 10 12" fill="currentColor" aria-hidden="true">'
             '<path d="M0 0l10 6-10 6z"/></svg>'
             '<svg class="pausa" viewBox="0 0 10 12" fill="currentColor" aria-hidden="true">'
             '<path d="M0 0h3.4v12H0zM6.6 0H10v12H6.6z"/></svg></button>')

CAT = """      <a class="cat" href="todas.html?s={clave}">
        <svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ico}</svg>
        <span class="nom">{nombre}</span><span class="n">{n}</span>
      </a>"""

LATERAL = """      <a href="{href}">
        <span class="meta">{cat}</span>
        <h3>{titulo}</h3>
        <p>{dek}</p>
      </a>"""

EXP = """      <a class="exp" href="{url}" target="_blank" rel="noopener">
        <div class="exp-img"><img src="{img}" alt=""></div>
        <span class="meta">{cat}</span>
        <h3>{titulo}</h3>
        <p>{dek}</p>
        <span class="abrir">Abrir el tablero {salir}</span>
      </a>"""


OIR = """      <article class="oir-t" data-audio="{audio}" data-href="{href}">
        <div class="oir-marco">
          <img src="{img}" alt="" loading="lazy">
          <button class="oir-btn" type="button" aria-label="Escuchar {titulo}">
            <svg class="play" viewBox="0 0 10 12" aria-hidden="true"><path d="M0 0l10 6-10 6z"/></svg>
            <svg class="pausa" viewBox="0 0 10 12" aria-hidden="true"><path d="M0 0h3.4v12H0zM6.6 0H10v12H6.6z"/></svg>
          </button>
          <span class="oir-dur">{dur}</span>
          <div class="oir-pie">
            <p class="m">{cat}</p>
            <a class="t" href="{href}">{titulo}</a>
          </div>
          <span class="oir-pista"></span>
        </div>
      </article>"""


def dur_mp3(f):
    try:
        from mutagen.mp3 import MP3
        m, s = divmod(int(MP3(str(AQUI / f)).info.length), 60)
        return "%d:%02d" % (m, s)
    except Exception:
        return ""

MURAL = """    <a class="mural-t{grande}" href="{href}">
      <img src="thumbs/{thumb}" alt="" loading="lazy" decoding="async">
      <figcaption><span class="tema">{cat}</span>{titulo}</figcaption>
    </a>"""


def thumb_de(img):
    """La miniatura que le toca a una portada. Los svg van tal cual."""
    return img if img.endswith(".svg") else img.rsplit(".", 1)[0] + ".webp"



def main(prueba=False):
    cols = columnas()
    if not cols:
        print("No se encontró ninguna columna. ¿Cambió el marcado de las tarjetas?")
        return 1

    orig = io.open(AQUI / "index.html", encoding="utf-8").read()
    head, cola = conservar(orig)
    n = len(cols)
    con_audio = sum(1 for c in cols if c["audio"])

    dest = cols[:DESTACADAS]
    js_cols = []
    for i, c in enumerate(dest):
        d = {"t": c["titulo"], "d": esc(c["dek"]), "img": c["img"], "href": c["href"],
             "fecha": fecha_larga(c["iso"]), "min": c["min"] + " de lectura",
             "tema": c["cat"]}
        if i == 0:
            d["nueva"] = True
        js_cols.append(d)

    # "También esta semana" arranca DESPUÉS de las del hero, para no repetir
    resto = cols[DESTACADAS:DESTACADAS + 1 + CARRIL]
    prin, lat = resto[0], resto[1:]

    filas = "\n".join(
        FILA.format(dcat=" ".join(c["dcat"]), href=c["href"], iso=c["iso"],
                    au=(' data-audio="%s"' % c["audio"]) if c["audio"] else "",
                    num=n - i, fecha=fecha_corta(c["iso"]), titulo=c["titulo"],
                    dek=esc(c["dek"]), cat=c["cat"], min=c["min"],
                    boton=BOTON_OIR if c["audio"] else "<span></span>")
        for i, c in enumerate(cols))

    cuenta = {}
    for c in cols:
        for d in c["dcat"]:
            cuenta[d] = cuenta.get(d, 0) + 1
    cats = "\n".join(CAT.format(clave=cl, ico=ic, nombre=nm, n=cuenta[cl])
                     for nm, cl, ic in CATS if cuenta.get(cl))

    salida = PLANTILLA.format(
        head=head, cola=cola, hoy=fecha_larga(cols[0]["iso"]),
        total=n, con_audio=con_audio, cats=cats,
        botones="\n".join('      <button class="f" data-t="%s">%s</button>' % (cl, nm)
                          for nm, cl, _ in CATS[:4]),
        p_href=prin["href"], p_img=prin["img"], p_cat=prin["cat"],
        p_tit=prin["titulo"], p_dek=esc(prin["dek"]),
        carril="\n".join(LATERAL.format(href=c["href"], cat=c["cat"],
                                        titulo=c["titulo"], dek=esc(c["dek"])) for c in lat),
        exps="\n".join(EXP.format(url=u, img=im, cat=ca, titulo=ti, dek=de, salir=SVG_SALIR)
                       for u, im, ca, ti, de in EXPEDIENTES),
        fb=FB, svg_fb=SVG_FB, svg_wa=SVG_WA, svg_x=SVG_X, svg_cp=SVG_CP, svg_rss=SVG_RSS,
        js_cols=json.dumps(js_cols, ensure_ascii=False),
        js_port=json.dumps(orden_panel(), ensure_ascii=False))

    destino = AQUI / ("_portada-prueba.html" if prueba else "index.html")
    io.open(destino, "w", encoding="utf-8").write(salida)
    print("escrito:", destino.name)
    print("  columnas: %d  ·  con audio: %d" % (n, con_audio))
    print("  hero:", " | ".join(c["titulo"][:24] for c in dest))
    return 0


if __name__ == "__main__":
    sys.exit(main("--prueba" in sys.argv))
