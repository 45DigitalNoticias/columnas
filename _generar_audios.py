# Genera el lector de audio (Jorge/Dalia alternados) para todas las columnas del sitio.
# Fuente del texto: el HTML publicado (versión evergreen corregida). Inserta el bloque
# reproductor tras los botones de compartir. Idempotente: salta páginas con audio-col.
import asyncio, io, os, re, sys
from bs4 import BeautifulSoup
import edge_tts

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
TXT_DIR = os.path.join(ROOT, "..", "_audio_textos_sitio")
os.makedirs(TXT_DIR, exist_ok=True)

idx = io.open("index.html", encoding="utf-8").read()
order = re.findall(r'data-date="([\d-]+)"[^>]*href="([^"]+)"', idx)
order = sorted(set(order), key=lambda t: (t[0], t[1]), reverse=True)
local = [(d, h) for d, h in order if not h.startswith("http")]

VOICES = ["es-MX-DaliaNeural", "es-MX-JorgeNeural"]

def adapt(path):
    soup = BeautifulSoup(io.open(path, encoding="utf-8").read(), "html.parser")
    title = soup.find("h1").get_text(" ", strip=True)
    prose = soup.find("div", class_="prose")
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

BLOCK = '''      <button class="share-btn" type="button" data-net="copy">Copiar enlace</button>
    </div>

    <div class="audio-col" style="max-width:var(--measure);margin:0 auto 38px;padding:16px 18px;border:1px solid rgba(204,161,90,.3);border-radius:12px;background:rgba(204,161,90,.05);">
      <div style="font-family:'Inter',system-ui,sans-serif;font-size:.74rem;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:#cca15a;margin-bottom:10px;">🎧 Escuchar la columna · {mins} min</div>
      <audio controls preload="none" style="width:100%;display:block;">
        <source src="{mp3}" type="audio/mpeg">
        Tu navegador no soporta audio HTML5.
      </audio>
      <div style="font-family:'Inter',system-ui,sans-serif;font-size:.72rem;color:rgba(243,241,232,.55);margin-top:8px;">Lectura automática con voz sintética.</div>
    </div>
'''

async def main():
    i = 0
    for date, href in local:
        if href == "la-silla-del-acusado.html":
            continue
        voice = VOICES[i % 2]
        i += 1
        html = io.open(href, encoding="utf-8").read()
        if "audio-col" in html:
            print("SALTADA (ya tiene):", href, flush=True)
            continue
        slug = href[:-5]
        mp3 = f"audio-{slug}.mp3"
        try:
            title, text = adapt(href)
        except Exception as e:
            print("ERROR extrayendo", href, "->", e, flush=True)
            continue
        io.open(os.path.join(TXT_DIR, slug + ".txt"), "w", encoding="utf-8", newline="\n").write(text)
        try:
            tts = edge_tts.Communicate(text, voice, rate="+4%")
            await tts.save(mp3)
        except Exception as e:
            print("ERROR tts", href, "->", e, flush=True)
            continue
        mins = max(1, round(os.path.getsize(mp3) * 8 / 48000 / 60))
        anchor = '      <button class="share-btn" type="button" data-net="copy">Copiar enlace</button>\n    </div>\n'
        if anchor not in html:
            print("ERROR ancla no encontrada:", href, flush=True)
            continue
        html = html.replace(anchor, BLOCK.format(mins=mins, mp3=mp3), 1)
        io.open(href, "w", encoding="utf-8", newline="\n").write(html)
        v = "Dalia" if "Dalia" in voice else "Jorge"
        print(f"OK {href} -> {mp3} ({v}, ~{mins} min)", flush=True)

asyncio.run(main())
print("FIN", flush=True)
