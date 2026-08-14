# -*- coding: utf-8 -*-
"""
Genera todas.html: la vista visual del archivo.

REPARTO DE PAPELES
  index.html  -> índice denso, para escanear 87 títulos de un vistazo
  todas.html  -> rejilla con portadas, para recorrer con la vista

Las dos listan lo mismo; cambia cómo se recorre. Por eso todas.html
NO repite el índice: sería la misma página dos veces.

    python _generar_todas.py            # escribe todas.html
    python _generar_todas.py --prueba   # escribe _todas-prueba.html

Reutiliza columnas() y conservar() de _generar_portada.py: una sola
fuente de datos para todo el sitio.
"""
import io, re, sys, pathlib

from _generar_portada import columnas, conservar, fecha_corta, fecha_larga, CATS
from _portada_tpl import FB, SVG_FB, SVG_RSS

AQUI = pathlib.Path(__file__).resolve().parent


def esc(t):
    return re.sub(r"<[^>]+>", "", t).replace('"', "&quot;").strip()


TARJETA = """    <a class="mural-t{grande}" href="{href}" data-cat="{dcat}" data-date="{iso}" data-title="{busca}">
      <img src="thumbs/{thumb}" alt="" loading="lazy" decoding="async">
      <figcaption><span class="tema">{cat}</span>{titulo}</figcaption>
    </a>"""


def thumb_de(img):
    """La miniatura que le toca. Los svg van tal cual."""
    return img if img.endswith(".svg") else img.rsplit(".", 1)[0] + ".webp"

PAGINA = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Todas las columnas · 45 Digital Noticias</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;1,6..72,300&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="todas.css">
{head}
</head>
<body>

<header class="masthead">
  <div class="wrap">
    <span class="fecha">{hoy}</span>
    <a href="index.html">
      <div class="logo">45 Digital <span class="n">Noticias</span></div>
      <div class="hilo"></div>
    </a>
    <nav>
      <a href="index.html" aria-current="page">Columnas</a>
      <a href="expedientes.html">Expedientes</a>
      <a href="acerca.html">Acerca</a>
    </nav>
  </div>
</header>

<section class="lead">
  <div class="wrap">
    <div class="lead-kicker"><span class="tick"></span><span class="label">El archivo completo</span></div>
    <h1>Todas las columnas</h1>
    <p class="entrada">Las {total} columnas publicadas, cada una por su portada. Filtra por tema o busca por palabra: títulos, entradas y palabras clave entran en la búsqueda.</p>
  </div>
</section>

<div class="wrap">
  <div class="filtros">
    <button class="f on" data-c="all">Todas</button>
{botones}
    <input class="busca" type="search" placeholder="Buscar columna" aria-label="Buscar columna">
  </div>
  <p class="cuantas" id="cuantas"></p>
  <div class="mural-grid" id="rejilla">
{tarjetas}
  </div>
  <p class="vacio" id="vacio" hidden>Ninguna columna coincide con esa búsqueda.</p>
</div>

<section class="hacia">
  <div class="wrap">
    <div>
      <h3>¿Buscas los tableros?</h3>
      <p>Los expedientes con datos interactivos viven en su propia sección.</p>
    </div>
    <a class="chev" href="expedientes.html">Ver expedientes <i>›</i></a>
  </div>
</section>

<footer class="pie-sitio">
  <div class="wrap">
    <div class="pie-top">
      <div class="pie-marca">
        <p class="marca">45 Digital Noticias</p>
        <div class="hilo"></div>
        <p class="lema">Columnas de opinión con lectura sistémica. Lo verificable, separado de la lectura.</p>
      </div>
      <nav class="pie-col"><h4>Leer</h4>
        <a href="index.html">Portada</a><a href="todas.html">Todas las columnas</a><a href="expedientes.html">Expedientes</a></nav>
      <nav class="pie-col"><h4>Temas</h4>
        <a href="todas.html?s=seguridad">Seguridad</a><a href="todas.html?s=morelos">Morelos</a>
        <a href="todas.html?s=economia">Economía</a><a href="todas.html?s=justicia">Justicia</a></nav>
      <nav class="pie-col"><h4>La casa</h4>
        <a href="acerca.html">Acerca</a><a href="mailto:s.rvaldespin8@gmail.com">Escríbenos</a>
        <a href="{fb}" target="_blank" rel="noopener">Facebook</a></nav>
    </div>
    <div class="pie-bajo">
      <p>© 2026 · 45 Digital Noticias. Textos de SRVO.<br>El programa se transmite en vivo de 9 a 10 de la mañana.</p>
      <div class="redes">
        <a href="{fb}" target="_blank" rel="noopener" aria-label="Facebook">{svg_fb}</a>
        <a href="feed.xml" aria-label="RSS">{svg_rss}</a>
      </div>
    </div>
  </div>
</footer>

<script>
(() => {{
  const tarjetas = [...document.querySelectorAll('.mural-t')];
  const botones  = [...document.querySelectorAll('.f')];
  const busca    = document.querySelector('.busca');
  const cuantas  = document.getElementById('cuantas');
  const vacio    = document.getElementById('vacio');
  let tema = 'all';

  function aplicar() {{
    const q = busca.value.trim().toLowerCase();
    let n = 0;
    tarjetas.forEach(t => {{
      // data-cat trae varias categorías separadas por espacio
      const cats = (t.dataset.cat || '').split(' ');
      const okT = tema === 'all' || cats.includes(tema);
      const okQ = !q || (t.dataset.title || '').toLowerCase().includes(q)
                     || t.textContent.toLowerCase().includes(q);
      t.hidden = !(okT && okQ);
      if (!t.hidden) n++;
    }});
    cuantas.textContent = n === tarjetas.length
      ? `${{n}} columnas`
      : `${{n}} de ${{tarjetas.length}} columnas`;
    vacio.hidden = n > 0;
  }}

  botones.forEach(b => b.addEventListener('click', () => {{
    botones.forEach(x => x.classList.remove('on'));
    b.classList.add('on'); tema = b.dataset.c; aplicar();
    // la dirección refleja el filtro, para poder compartirla
    const u = new URL(location);
    tema === 'all' ? u.searchParams.delete('s') : u.searchParams.set('s', tema);
    history.replaceState(null, '', u);
  }}));
  busca.addEventListener('input', aplicar);

  // ?s=morelos llega desde la portada y desde el pie
  const s = new URLSearchParams(location.search).get('s');
  const b = s && botones.find(x => x.dataset.c === s);
  if (b) {{ botones.forEach(x => x.classList.remove('on')); b.classList.add('on'); tema = s; }}
  aplicar();
}})();
</script>
{cola}
</body>
</html>
"""


def main(prueba=False):
    cols = columnas()
    if not cols:
        print("No se encontró ninguna columna."); return 1
    orig = io.open(AQUI / "todas.html", encoding="utf-8").read()
    head, cola = conservar(orig)


    # una de cada siete al doble de tamaño: le da ritmo al muro
    tarjetas = "\n".join(
        TARJETA.format(grande=" grande" if i % 7 == 0 else "", href=c["href"],
                       dcat=" ".join(c["dcat"]), iso=c["iso"],
                       busca=esc(c.get("claves") or c["titulo"]),
                       thumb=thumb_de(c["img"]),
                       cat=c["cat"].split(" · ")[-1], titulo=c["titulo"])
        for i, c in enumerate(cols))

    usadas = {d for c in cols for d in c["dcat"]}
    botones = "\n".join('    <button class="f" data-c="%s">%s</button>' % (cl, nm)
                        for nm, cl, _ in CATS if cl in usadas)

    salida = PAGINA.format(
        head=head, cola=cola, hoy=fecha_larga(cols[0]["iso"]),
        total=len(cols), con_audio=sum(1 for c in cols if c["audio"]),
        botones=botones, tarjetas=tarjetas,
        fb=FB, svg_fb=SVG_FB, svg_rss=SVG_RSS)

    destino = AQUI / ("_todas-prueba.html" if prueba else "todas.html")
    io.open(destino, "w", encoding="utf-8").write(salida)
    print("escrito:", destino.name)
    print("  tarjetas: %d · filtros: %d" % (len(cols), len(usadas)))
    return 0


if __name__ == "__main__":
    sys.exit(main("--prueba" in sys.argv))
