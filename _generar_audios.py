# -*- coding: utf-8 -*-
# Genera el mp3 del lector (Jorge/Dalia alternados) para las columnas que
# no lo tengan. La lista sale de _columnas.json: el manifiesto es la fuente
# de datos del sitio, no las tarjetas de index.html (los generadores las
# reescriben y su markup cambió con el rediseño).
#
#     python _generar_audios.py                  # todas las que falten
#     python _generar_audios.py <slug.html>      # solo esa
#
# NO toca las páginas: el reproductor del formato editorial lo pone
# _convertir_columna.py cuando el mp3 existe. (La versión anterior insertaba
# un bloque <audio> con regex sobre el markup viejo; ese markup ya no existe.)
import asyncio, io, os, re, sys, json

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
TXT_DIR = os.path.join(ROOT, "..", "_audio_textos_sitio")
os.makedirs(TXT_DIR, exist_ok=True)

VOICES = ["es-MX-DaliaNeural", "es-MX-JorgeNeural"]
# columnas que por decisión editorial NO llevan audio
SIN_AUDIO = {"la-silla-del-acusado.html"}


def adapt(path):
    """El texto leíble de una columna, desde su HTML publicado. Entiende el
    formato editorial nuevo (div .prosa) y el fuente (div .prose)."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(io.open(path, encoding="utf-8").read(), "html.parser")
    title = soup.find("h1").get_text(" ", strip=True)
    prose = soup.find("div", class_="prosa") or soup.find("div", class_="prose")
    parts = []
    for el in prose.find_all(["p", "h2", "li"]):
        if "pull" in (el.get("class") or []):
            continue
        t = el.get_text(" ", strip=True)
        if not t:
            continue
        if el.name == "h2":
            t = t.rstrip(".") + "."
        parts.append(t)
    text = "\n\n".join(parts)
    text = re.sub(r"\barts\.\s", "artículos ", text)
    text = re.sub(r"\bart\.\s", "artículo ", text)
    text = text.replace("fr. ", "fracción ")
    text = text.replace("EE.UU.", "Estados Unidos")
    text = re.sub(r"\s+([.,;:)])", r"\1", text)
    text = re.sub(r"  +", " ", text)
    intro = f"{title}. Columna de opinión de 45 Digital Noticias.\n\n"
    outro = "\n\n45 Digital Noticias. La columna completa, con sus fuentes enlazadas, está en nuestro sitio de columnas."
    return title, intro + text + outro


async def main(solo=None):
    import edge_tts
    cols = json.loads(io.open("_columnas.json", encoding="utf-8").read())
    # la voz alterna conforme se acumulan columnas con audio
    hechos = sum(1 for c in cols if os.path.exists("audio-" + c["href"][:-5] + ".mp3"))
    n = 0
    for c in cols:
        href = c["href"]
        if solo and href != solo:
            continue
        if href in SIN_AUDIO:
            if solo: print("SIN AUDIO por decisión editorial:", href, flush=True)
            continue
        slug = href[:-5]
        mp3 = f"audio-{slug}.mp3"
        if os.path.exists(mp3):
            if solo: print("YA EXISTE:", mp3, flush=True)
            continue
        if not os.path.exists(href):
            print("SIN PÁGINA:", href, flush=True)
            continue
        voice = VOICES[(hechos + n) % 2]
        try:
            title, text = adapt(href)
        except Exception as e:
            print("ERROR extrayendo", href, "->", e, flush=True)
            continue
        io.open(os.path.join(TXT_DIR, slug + ".txt"), "w", encoding="utf-8", newline="\n").write(text)
        try:
            await edge_tts.Communicate(text, voice, rate="+4%").save(mp3)
        except Exception as e:
            print("ERROR tts", href, "->", e, flush=True)
            continue
        n += 1
        v = "Dalia" if "Dalia" in voice else "Jorge"
        print(f"OK {href} -> {mp3} ({v})", flush=True)
    print(f"FIN: {n} audios nuevos", flush=True)


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else None))
