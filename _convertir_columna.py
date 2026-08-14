# -*- coding: utf-8 -*-
"""
Convierte una columna al formato editorial del sitio.

Se escribe como SCRIPT y no a mano porque son 89 páginas: el molde
tiene que ser uno solo y reproducible. El CSS vive en columna.css,
enlazado, NO incrustado 89 veces.

    python _convertir_columna.py <slug>            # una, a preview
    python _convertir_columna.py --todas           # todas, a columnas-nuevas/
    python _convertir_columna.py --publicar <slug> # una, EN SU LUGAR (publicación)

Los dos primeros modos no tocan el sitio: escriben a la carpeta de
salida. El tercero es el que usa _publicar_columna.py: toma la página
recién generada en formato fuente y la deja en formato editorial.
"""
import io, os, re, sys, html, json, pathlib

SITIO  = pathlib.Path(__file__).resolve().parent.parent / "SITIO_COLUMNAS"
SALIDA = pathlib.Path(__file__).resolve().parent
META   = {"index.html","todas.html","acerca.html","expedientes.html","privacidad.html"}


# ---------------------------------------------------------------- datos
def catalogo():
    """Portada, categoría, fecha y minutos de cada columna, desde
    _columnas.json. El manifiesto es LA fuente de datos del sitio: las
    tarjetas de index.html y todas.html las escriben los generadores, así
    que leerlas de vuelta era la dependencia circular que ya costó una
    columna perdida."""
    mf = SITIO / "_columnas.json"
    if not mf.exists():
        raise SystemExit("Falta _columnas.json. Corre antes:  python _generar_manifiesto.py")
    fichas = {}
    for c in json.loads(io.open(mf, encoding="utf-8").read()):
        fichas[c["href"]] = {"fecha": c.get("iso", ""), "img": c.get("img", ""),
                             "cat": c.get("cat", ""), "min": c.get("min", "")}
    return fichas


BORRADORES = {"columna-ejemplo.html", "_template.html"}

def publicadas():
    """Solo lo PUBLICADO = lo que declara _columnas.json y existe en disco.
    El criterio no es 'hay un .html en la carpeta': eso incluye plantillas
    y columnas escritas que aún no salen."""
    cols = json.loads(io.open(SITIO / "_columnas.json", encoding="utf-8").read())
    vistas, fuera = [], []
    for c in cols:
        (vistas if (SITIO / c["href"]).exists() else fuera).append(c["href"])
    if fuera:
        print("  AVISO en el manifiesto sin archivo:", ", ".join(fuera))
    sin_enlazar = [p.name for p in sorted(SITIO.glob("*.html"))
                   if p.name not in META and p.name not in BORRADORES and p.name not in vistas]
    if sin_enlazar:
        print("  NO publicadas (quedan fuera):", ", ".join(sin_enlazar))
    return vistas


MES = ["enero","febrero","marzo","abril","mayo","junio","julio",
       "agosto","septiembre","octubre","noviembre","diciembre"]

def fecha_larga(iso):
    try:
        a, m, d = iso.split("-")
        return f"{int(d)} de {MES[int(m)-1]} de {a}"
    except Exception:
        return ""


URL = re.compile(r'(?<![">=])(https?://[^\s<)"\']+?)(?=[.,;)]?(?:\s|<|$))')

def enlazar(fragmento):
    """Convierte en liga las URL que quedaron como texto plano.

    Cuatro columnas listaban sus fuentes con la dirección escrita a mano,
    sin <a>. La casa dice que las fuentes van enlazadas, así que se
    enlazan aquí y no se deja al lector copiando y pegando. Se respeta
    lo que YA es liga: se parte por las anclas existentes y solo se
    toca el texto de en medio."""
    partes = re.split(r'(<a\b.*?</a>)', fragmento, flags=re.S)
    for i, p in enumerate(partes):
        if p.startswith("<a"):
            continue
        partes[i] = URL.sub(
            lambda m: '<a href="%s" target="_blank" rel="noopener">%s</a>' % (
                m.group(1),
                re.sub(r'^https?://(www\.)?', '', m.group(1)).rstrip('/')),
            p)
    return "".join(partes)


def duracion(mp3):
    """Duración real del audio. Si no se puede leer, se devuelve vacío:
    antes que poner un número inventado, no se pone nada."""
    try:
        from mutagen.mp3 import MP3
        m, s = divmod(int(MP3(str(mp3)).info.length), 60)
        return f"{m}:{s:02d}"
    except Exception:
        return ""


def conservar(s):
    """Todo lo que la página ya traía y NO se debe perder: description,
    og, twitter, canonical, JSON-LD, favicon, GA4, aviso de cookies y
    beacon de Cloudflare.

    El criterio es quedarse con el <head> ENTERO y quitar solo las cuatro
    cosas que la plantilla nueva pone por su cuenta. Reconstruirlo a mano
    era la vía segura para perder un canonical sin darse cuenta."""
    head = s[s.index("<head>") + 6 : s.index("</head>")]
    for pat in (r'<title>.*?</title>',
                r'<meta charset[^>]*>',
                r'<meta name="viewport"[^>]*>',
                r'<link rel="preconnect"[^>]*>',
                r'<link href="https://fonts\.googleapis[^>]*>',
                r'<link rel="stylesheet"[^>]*>'):
        head = re.sub(pat, '', head, flags=re.S)
    head = re.sub(r'\n\s*\n+', '\n', head).strip()

    # La cola: aviso de cookies + beacon, cada uno por su cuenta.
    # OJO: el orden entre ambos CAMBIA de página a página (en unas el
    # beacon va antes del aviso, en otras después). Cortar "del aviso
    # hasta </body>" perdía el beacon en 3 de las 87. Se extraen por
    # separado para no depender del orden.
    piezas = []
    ck = (re.search(r'<style>\s*#ck-consent.*?<!--\s*/Cookie consent.*?-->', s, re.S)
          or re.search(r'<style>\s*#ck-consent.*?\)\(\);\s*</script>', s, re.S))
    if ck: piezas.append(ck.group(0).strip())
    bc = re.search(r'<!--\s*Cloudflare Web Analytics\s*-->.*?<!--\s*End Cloudflare Web Analytics\s*-->', s, re.S)
    if bc: piezas.append(bc.group(0).strip())
    return head, "\n".join(piezas)


def extraer(archivo):
    s = io.open(archivo, encoding="utf-8").read()
    g = lambda p, d="": (re.search(p, s, re.S).group(1).strip()
                         if re.search(p, s, re.S) else d)
    d = {
        "titulo":  g(r'<header class="article-head">.*?<h1>(.*?)</h1>'),
        "dek":     g(r'<p class="dek">(.*?)</p>'),
        "kicker":  g(r'<span class="kicker">(.*?)</span>', "Columna de opinión"),
        "minutos": g(r'<div class="article-meta">\s*<span>(.*?)</span>'),
        "prosa":   g(r'<div class="prose">(.*?)(?:<section class="fuentes"|</article>)'),
        "fuentes": g(r'<section class="fuentes">(.*?)</section>'),
        "canon":   g(r'<link rel="canonical" href="([^"]+)"'),
        # todas.html NO trae la fecha (solo data-cat y data-title): la
        # autoridad para la fecha es el JSON-LD de la propia columna.
        "iso":     g(r'"datePublished":\s*"([0-9-]{10})"'),
    }
    d["head"], d["cola"] = conservar(s)
    # La prosa vieja arrastra dos cosas que rompen el molde nuevo:
    #  1. <p class="signoff">SRVO</p>, que vive FUERA del div de la prosa.
    #     La firma la pone la plantilla, así que se corta aquí.
    #  2. el </div> que cerraba el contenedor viejo. Si se cuela, cierra
    #     antes de tiempo el contenedor nuevo y todo lo que sigue se sale
    #     de la medida de lectura. Fue justo lo que pasó.
    p = re.split(r'<p class="signoff"', d["prosa"])[0]
    p = re.sub(r'(?:\s*</div>)+\s*$', '', p)
    d["prosa"] = p.strip()
    # el h2 de "Fuentes" ya lo pone la plantilla nueva
    d["fuentes"] = re.sub(r'<h2>.*?</h2>', '', d["fuentes"], flags=re.S).strip()
    d["fuentes"] = enlazar(d["fuentes"])
    return d


# ---------------------------------------------------------------- plantilla
PAGINA = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{titulo} · 45 Digital Noticias</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;1,6..72,300;1,6..72,400&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="columna.css">
{head}
</head>
<body>

<header class="masthead">
  <div class="wrap">
    <span class="fecha">{fecha_larga}</span>
    <a href="index.html">
      <div class="logo">45 Digital <span class="n">Noticias</span></div>
      <div class="hilo"></div>
    </a>
    <nav>
      <a href="index.html">Columnas</a>
      <a href="expedientes.html">Expedientes</a>
      <a href="acerca.html">Acerca</a>
    </nav>
  </div>
</header>

<!-- barra de avance de lectura -->
<div class="avance" id="avance"></div>

<article>
  <header class="cabeza">
    <div class="wrap-medida">
      <div class="eyebrow">
        <span class="tick"></span>
        <span class="label">{cat}</span>
      </div>
      <h1>{titulo}</h1>
      <p class="entrada">{dek}</p>

      <div class="firma">
        <span class="autor">SRVO</span>
        <span class="sep"></span>
        <span class="meta">{fecha_larga}</span>
        <span class="sep"></span>
        <span class="meta">{minutos}</span>
      </div>

      {audio}
    </div>
  </header>

  {portada}

  <div class="wrap-medida prosa">
{prosa}
  </div>

  <section class="fuentes">
    <div class="wrap-medida">
      <div class="sec-head"><span class="label">Fuentes y referencias</span></div>
      {fuentes}
      <p class="cotejo">Las ligas van a la vista para que cualquiera compruebe por su cuenta. Si alguna dejó de resolver, escríbenos y la reponemos.</p>
    </div>
  </section>

  <section class="cierre wrap-medida">
    <p class="firma-final">SRVO</p>
    <div class="btns">
      <a class="btn-red" data-red="facebook" href="#" aria-label="Compartir en Facebook"><span class="tip">Facebook</span><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M14 9h3V6h-3c-2.2 0-4 1.8-4 4v2H8v3h2v7h3v-7h2.5l.5-3h-3v-2c0-.6.4-1 1-1z"/></svg></a>
      <a class="btn-red" data-red="whatsapp" href="#" aria-label="Compartir por WhatsApp"><span class="tip">WhatsApp</span><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 00-8.6 15L2 22l5.2-1.4A10 10 0 1012 2zm0 18a8 8 0 01-4.1-1.1l-.3-.2-3 .8.8-2.9-.2-.3A8 8 0 1112 20zm4.4-5.8c-.2-.1-1.4-.7-1.6-.8-.2-.1-.4-.1-.5.1l-.7.9c-.1.2-.3.2-.5.1a6.5 6.5 0 01-3.2-2.8c-.1-.2 0-.4.1-.5l.4-.5c.1-.2.1-.3 0-.5l-.7-1.6c-.2-.4-.4-.4-.5-.4h-.5c-.2 0-.5.1-.7.3-.7.7-.9 1.6-.6 2.6.5 1.6 1.6 3 3.1 3.9 1.4.9 2.5 1 3.4.9.7-.1 1.4-.6 1.6-1.2.1-.3.1-.6 0-.7z"/></svg></a>
      <a class="btn-red" data-red="x" href="#" aria-label="Compartir en X"><span class="tip">X</span><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.5 3h3l-6.6 7.5L21.7 21h-6l-4.7-6.1L5.6 21h-3l7-8L2.6 3h6.2l4.3 5.6zm-1 16h1.6L8.1 4.6H6.4z"/></svg></a>
      <button class="btn-red" type="button" data-red="copiar" aria-label="Copiar enlace"><span class="tip">Copiar enlace</span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10 13a4 4 0 006 .4l2.4-2.4a4 4 0 00-5.7-5.7l-1.4 1.4"/><path d="M14 11a4 4 0 00-6-.4l-2.4 2.4a4 4 0 005.7 5.7l1.4-1.4"/></svg></button>
    </div>
  </section>
</article>

<footer class="pie-sitio">
  <div class="wrap">
    <div class="pie-top">
      <div class="pie-marca">
        <p class="marca-n">45 Digital Noticias</p>
        <div class="hilo"></div>
        <p class="lema">Columnas de opinión con lectura sistémica. Lo verificable, separado de la lectura.</p>
      </div>
      <nav class="pie-col"><h4>Leer</h4>
        <a href="index.html">Portada</a><a href="todas.html">Todas las columnas</a><a href="expedientes.html">Expedientes</a></nav>
      <nav class="pie-col"><h4>Temas</h4>
        <a href="#">Seguridad</a><a href="#">Morelos</a><a href="#">Economía</a><a href="#">Justicia</a></nav>
      <nav class="pie-col"><h4>La casa</h4>
        <a href="acerca.html">Acerca</a><a href="mailto:s.rvaldespin8@gmail.com">Escríbenos</a>
        <a href="https://facebook.com/45DigitalMx" target="_blank" rel="noopener">Facebook</a></nav>
    </div>
    <div class="pie-bajo">
      <p>© 2026 · 45 Digital Noticias. Textos de SRVO.<br>El programa se transmite en vivo de 9 a 10 de la mañana.</p>
    </div>
  </div>
</footer>

<script>
(() => {{
  // barra de avance de lectura
  const barra = document.getElementById('avance'), art = document.querySelector('article');
  addEventListener('scroll', () => {{
    const t = art.offsetTop, h = art.offsetHeight - innerHeight;
    const p = Math.min(1, Math.max(0, (scrollY - t) / (h > 0 ? h : 1)));
    barra.style.transform = 'scaleX(' + p + ')';
  }}, {{passive:true}});

  // audio
  const bt = document.querySelector('.oir-barra');
  if (bt) {{
    const au = new Audio(bt.dataset.src);
    const pista = bt.querySelector('.pista-audio');
    bt.addEventListener('click', () => {{
      if (au.paused) {{ au.play().catch(()=>{{}}); bt.classList.add('suena'); }}
      else {{ au.pause(); bt.classList.remove('suena'); }}
    }});
    au.addEventListener('timeupdate', () => {{
      if (au.duration) pista.style.width = (au.currentTime / au.duration * 100) + '%';
    }});
    au.addEventListener('ended', () => bt.classList.remove('suena'));
  }}

  // compartir
  const U = encodeURIComponent(location.href);
  const T = encodeURIComponent(document.querySelector('h1').textContent + ' · 45 Digital Noticias');
  const D = {{facebook:`https://www.facebook.com/sharer/sharer.php?u=${{U}}`,
             whatsapp:`https://api.whatsapp.com/send?text=${{T}}%20${{U}}`,
             x:`https://twitter.com/intent/tweet?text=${{T}}&url=${{U}}`}};
  document.querySelectorAll('.btn-red').forEach(b => {{
    const r = b.dataset.red;
    if (D[r]) {{ b.href = D[r]; b.target = '_blank'; b.rel = 'noopener'; return; }}
    b.addEventListener('click', async () => {{
      const tip = b.querySelector('.tip');
      try {{ await navigator.clipboard.writeText(location.href); }} catch {{ return; }}
      const a = tip.textContent; tip.textContent = 'Copiado'; b.classList.add('copiado');
      setTimeout(() => {{ tip.textContent = a; b.classList.remove('copiado'); }}, 1800);
    }});
  }});
}})();
</script>

{cola}
</body>
</html>
"""

AUDIO = """<button class="oir-barra" type="button" data-src="{src}">
        <span class="ico"><svg class="play" viewBox="0 0 10 12" fill="currentColor"><path d="M0 0l10 6-10 6z"/></svg><svg class="pausa" viewBox="0 0 10 12" fill="currentColor"><path d="M0 0h3.4v12H0zM6.6 0H10v12H6.6z"/></svg></span>
        <span class="txt">Escuchar la columna</span>
        <span class="dur">{minutos}</span>
        <span class="pista-audio"></span>
      </button>"""

PORTADA = """<figure class="portada wrap-medida">
    <img src="{src}" alt="">
    <figcaption>{cat} · Ilustración de la columna</figcaption>
  </figure>"""


def convertir(slug, fichas, destino):
    origen = SITIO / slug
    if 'class="article-head"' not in io.open(origen, encoding="utf-8").read():
        # ya está en formato editorial: volver a convertirla la destruiría
        # (extraer() no encontraría ni título ni prosa)
        print("  YA CONVERTIDA (la salto):", slug)
        return None
    d = extraer(origen)
    ficha = fichas.get(slug, {})
    audio_f = "audio-" + slug.replace(".html", "") + ".mp3"

    d["cat"] = ficha.get("cat") or d["kicker"]
    d["fecha_larga"] = fecha_larga(d["iso"] or ficha.get("fecha", ""))
    if not d["minutos"] and ficha.get("min"):
        d["minutos"] = ficha["min"] + " de lectura"
    # La barra decía "9 min de lectura", que es el tiempo de LEER, no el de
    # escuchar. Confundía dos cosas distintas. Ahora va la duración real del
    # mp3, leída del archivo.
    # Las rutas van PLANAS (audio-x.mp3, portada.jpg): la página vive en la
    # raíz del sitio, junto a sus assets. El prefijo ../SITIO_COLUMNAS/ era
    # para previsualizar desde fuera y en el sitio publicado daba 404.
    d["audio"] = (AUDIO.format(src=audio_f, minutos=duracion(SITIO / audio_f))
                  if (SITIO / audio_f).exists() else "")
    d["portada"] = (PORTADA.format(src=ficha["img"], cat=d["cat"])
                    if ficha.get("img") else "")
    # la prosa se re-indenta para que el HTML de salida sea legible
    d["prosa"] = "\n".join("    " + l.strip() for l in d["prosa"].splitlines() if l.strip())
    # newline="\n": las páginas publicadas van con LF; sin esto Windows mete
    # CRLF y cada republicación ensucia el diff completo en git
    io.open(destino, "w", encoding="utf-8", newline="\n").write(PAGINA.format(**d))
    return d


if __name__ == "__main__":
    fichas = catalogo()
    args = sys.argv[1:]
    if not args:
        print("uso: python _convertir_columna.py <slug.html> | --todas | --publicar <slug.html>"); sys.exit(1)

    if args[0] == "--todas":
        dest = SALIDA / "columnas-nuevas"; dest.mkdir(exist_ok=True)
        todas = publicadas()
        ok = fallo = 0
        for slug in todas:
            try:
                d = convertir(slug, fichas, dest / slug)
                if d is None:
                    continue
                if not d["titulo"] or not d["prosa"]:
                    print("  AVISO sin título o sin prosa:", slug); fallo += 1
                else: ok += 1
            except Exception as e:
                print("  ERROR", slug, e); fallo += 1
        print(f"convertidas {ok}, con aviso {fallo}, de {len(todas)}")
    else:
        # --publicar escribe EN SU LUGAR (SITIO/slug); a secas, a preview
        publicar = args[0] == "--publicar"
        if publicar and len(args) < 2:
            print("uso: python _convertir_columna.py --publicar <slug.html>"); sys.exit(1)
        slug = args[1] if publicar else args[0]
        destino = (SITIO / slug) if publicar else (SALIDA / "propuesta-columna.html")
        d = convertir(slug, fichas, destino)
        if d is None:
            sys.exit(0)
        if not d["titulo"] or not d["prosa"]:
            print("  ERROR: sin título o sin prosa; revisa la página fuente."); sys.exit(1)
        print("lista:", destino.name)
        print("  titulo :", d["titulo"][:60])
        print("  cat    :", d["cat"], "|", d["fecha_larga"], "|", d["minutos"])
        print("  audio  :", "sí" if d["audio"] else "NO")
        print("  portada:", "sí" if d["portada"] else "NO")
        print("  fuentes:", len(re.findall(r'<a ', d["fuentes"])), "ligas")
