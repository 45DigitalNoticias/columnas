# -*- coding: utf-8 -*-
"""Plantilla HTML de la portada. Solo texto: la lógica vive en
_generar_portada.py. Se separa para que el HTML se pueda leer y editar
sin pelearse con el código."""

EXPEDIENTES = [
 ("https://45digitalnoticias.github.io/Expediente-Hantavirus/", "thumb-brotes.jpg",
  "Salud · Geopolítica", "Expediente Brotes 2026",
  "Hantavirus y ébola como corredor del Mundial 2026: el mapa, los actores y la doctrina del shock."),
 ("https://45digitalnoticias.github.io/cementerio-transparencia/", "thumb-cementerio.jpg",
  "Morelos · Transparencia", "El Cementerio de la Transparencia",
  "El desmantelamiento del IMIPE y la auditoría de los sitios oficiales caídos del gobierno de Morelos."),
 ("https://45digitalnoticias.github.io/Inseguridad-Morelos/", "thumb-morelos.jpg",
  "Morelos · Seguridad", "Morelos: seguridad municipal",
  "Hub de datos de violencia y desapariciones por municipio: rankings, series y fichas de Cuautla, Cuernavaca, Ayala y más."),
]


# ============================================================
# REELS DE LA PORTADA  ·  se rotan cambiando esta lista
# ============================================================
# Los mp4 pesan de 47 a 198 MB y no hay ffmpeg para comprimirlos, así que
# NO se alojan en el sitio: la tarjeta muestra el cartel y la duración
# reales y manda a donde vive el video.
#
# "url" es lo único pendiente: pon el enlace de YouTube o de Facebook de
# cada reel. Mientras esté vacío, la tarjeta manda a la página de Facebook.
REELS = [
 {"titulo": "El país que no se cuenta",
  "pie": "Seguridad · México",
  "dur": "4:57",
  "cartel": "el-pais-que-no-se-cuenta-portada.png",
  "url": ""},
 {"titulo": "Las ratas del agua",
  "pie": "Morelos · SOAPSC",
  "dur": "1:31",
  "cartel": "cuenta-puente-portada.png",
  "url": ""},
 {"titulo": "¿Quién era Zapata?",
  "pie": "Zapata y la tierra · Episodio 1",
  "dur": "2:17",
  "cartel": "zapata-ep01-portada.png",
  "url": ""},
]

FB = "https://facebook.com/45DigitalMx"

SVG_FB = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M14 9h3V6h-3c-2.2 0-4 1.8-4 4v2H8v3h2v7h3v-7h2.5l.5-3h-3v-2c0-.6.4-1 1-1z"/></svg>'
SVG_WA = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 00-8.6 15L2 22l5.2-1.4A10 10 0 1012 2zm0 18a8 8 0 01-4.1-1.1l-.3-.2-3 .8.8-2.9-.2-.3A8 8 0 1112 20zm4.4-5.8c-.2-.1-1.4-.7-1.6-.8-.2-.1-.4-.1-.5.1l-.7.9c-.1.2-.3.2-.5.1a6.5 6.5 0 01-3.2-2.8c-.1-.2 0-.4.1-.5l.4-.5c.1-.2.1-.3 0-.5l-.7-1.6c-.2-.4-.4-.4-.5-.4h-.5c-.2 0-.5.1-.7.3-.7.7-.9 1.6-.6 2.6.5 1.6 1.6 3 3.1 3.9 1.4.9 2.5 1 3.4.9.7-.1 1.4-.6 1.6-1.2.1-.3.1-.6 0-.7z"/></svg>'
SVG_X  = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.5 3h3l-6.6 7.5L21.7 21h-6l-4.7-6.1L5.6 21h-3l7-8L2.6 3h6.2l4.3 5.6zm-1 16h1.6L8.1 4.6H6.4z"/></svg>'
SVG_CP = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10 13a4 4 0 006 .4l2.4-2.4a4 4 0 00-5.7-5.7l-1.4 1.4"/><path d="M14 11a4 4 0 00-6-.4l-2.4 2.4a4 4 0 005.7 5.7l1.4-1.4"/></svg>'
SVG_RSS = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="M5 18.5h.01M5 12a7 7 0 017 7M5 5.5a13 13 0 0113 13"/></svg>'
SVG_SALIR = '<svg viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 9L9 3M4.2 3H9v4.8"/></svg>'

PLANTILLA = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>45 Digital Noticias · Columnas</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;1,6..72,300&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="portada.css">
{head}
</head>
<body>

<div class="portada">
  <div class="mosaico" id="mgrid" aria-hidden="true"></div>
  <div class="tinte" aria-hidden="true"></div>
  <div class="luz"   aria-hidden="true"></div>
  <div class="velo"  aria-hidden="true"></div>
  <div class="grano" aria-hidden="true"></div>

  <header class="masthead">
    <div class="wrap">
      <span class="fecha">{hoy}</span>
      <div>
        <div class="logo">45 Digital <span class="n">Noticias</span></div>
        <div class="hilo"></div>
      </div>
      <nav><a href="index.html">Columnas</a><a href="expedientes.html">Expedientes</a><a href="acerca.html">Acerca</a></nav>
    </div>
  </header>

  <div class="portada-cuerpo">
    <div class="wrap">
      <div class="destacada" id="destacada"></div>
      <div class="activa" id="activa"></div>
    </div>
  </div>

  <div class="rotador" id="rotador">
    <div class="wrap" id="tabs" role="tablist" aria-label="Columnas destacadas"></div>
  </div>
</div>

<section class="cats">
  <div class="wrap">
    <div class="cats-head">
      <span class="label">Por tema</span>
      <span class="label label--soft">{total} columnas publicadas</span>
    </div>
    <div class="cats-grid">
{cats}
    </div>
  </div>
</section>

<section class="recientes">
  <div class="wrap">
    <div class="principal">
      <div class="sec-head">
        <span class="label">Recién publicadas</span>
        <a class="ver" href="todas.html">Ver todas</a>
      </div>
      <a href="{p_href}">
        <img src="{p_img}" alt="">
        <span class="meta">{p_cat}</span>
        <h2>{p_tit}</h2>
        <p>{p_dek}</p>
      </a>
    </div>
    <div class="divisor"></div>
    <div class="carril">
{carril}
    </div>
  </div>
</section>

<section class="expedientes">
  <div class="wrap">
    <div class="sec-head">
      <span class="label">Expedientes</span>
      <span class="label label--soft">Tableros interactivos</span>
      <a class="ver" href="expedientes.html">Ver todos</a>
    </div>
    <div class="exp-fila">
{exps}
    </div>
  </div>
</section>

<section class="declaracion">
  <svg class="vantage" viewBox="0 0 400 400" fill="none" aria-hidden="true">
    <circle cx="200" cy="200" r="190" stroke="#B08D4F" stroke-width=".8" opacity=".22"/>
    <circle cx="200" cy="200" r="140" stroke="#B08D4F" stroke-width=".8" opacity=".30"/>
    <circle cx="200" cy="200" r="90"  stroke="#B08D4F" stroke-width=".8" opacity=".38"/>
    <circle cx="200" cy="200" r="40"  stroke="#B08D4F" stroke-width="1"  opacity=".46"/>
    <path d="M200 10v380M10 200h380" stroke="#B08D4F" stroke-width=".6" opacity=".18"/>
  </svg>
  <div class="wrap">
    <div class="hilo"></div>
    <h2>Conjuntar lo que el día deja suelto.</h2>
    <p>Cada columna toma piezas que parecen no tener relación y las lee en su conjunto: quién gana, quién paga, qué se mueve detrás. Opinión fundada, fuentes citadas, lo verificable separado de la lectura. El lector siempre puede cotejar.</p>
    <span class="firma-decl">SRVO</span>
  </div>
</section>

<section class="compartir">
  <div class="wrap">
    <div class="txt">
      <h3>Comparte 45 Digital Noticias</h3>
      <p>Si una columna te sirvió, pásala. Es la única difusión que tenemos.</p>
    </div>
    <div class="btns" id="btns">
      <a class="btn-red" data-red="facebook" href="#" aria-label="Compartir en Facebook"><span class="tip">Facebook</span>{svg_fb}</a>
      <a class="btn-red" data-red="whatsapp" href="#" aria-label="Compartir por WhatsApp"><span class="tip">WhatsApp</span>{svg_wa}</a>
      <a class="btn-red" data-red="x" href="#" aria-label="Compartir en X"><span class="tip">X</span>{svg_x}</a>
      <button class="btn-red" type="button" data-red="copiar" aria-label="Copiar enlace"><span class="tip">Copiar enlace</span>{svg_cp}</button>
    </div>
  </div>
</section>

<footer class="pie-sitio">
  <div class="wrap">
    <div class="pie-top">
      <div class="pie-marca">
        <p class="marca">45 Digital Noticias</p>
        <div class="hilo" style="margin-left:0"></div>
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
const COLUMNAS = {js_cols};
const PORTADAS = {js_port};
</script>
<script src="portada.js"></script>
{cola}
</body>
</html>
"""
