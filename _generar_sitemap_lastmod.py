"""
Añade <lastmod> a cada URL del sitemap.xml, tomando la fecha de "dateModified"
del JSON-LD de cada página. Mejora el rastreo (los crawlers priorizan lo fresco).
Idempotente: reescribe el lastmod si ya existía. Preserva loc y priority.

Uso: python _generar_sitemap_lastmod.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent
SITEMAP = ROOT / "sitemap.xml"
PREFIX = "https://45digitalnoticias.github.io/columnas/"

def file_for(loc):
    rel = loc[len(PREFIX):] if loc.startswith(PREFIX) else ""
    if rel == "" or rel.endswith("/"):
        rel = rel + "index.html"
    return ROOT / rel

def datemod(loc):
    f = file_for(loc)
    if not f.exists():
        return None
    m = re.search(r'"dateModified"\s*:\s*"([\d-]+)"', f.read_text(encoding="utf-8"))
    return m.group(1) if m else None

def fix(line):
    m = re.search(r"<loc>([^<]+)</loc>", line)
    if not m:
        return line
    line = re.sub(r"<lastmod>[^<]*</lastmod>", "", line)  # idempotencia
    d = datemod(m.group(1))
    if not d:
        return line
    return line.replace("</loc>", f"</loc><lastmod>{d}</lastmod>")

text = SITEMAP.read_text(encoding="utf-8")
out = "\n".join(fix(l) for l in text.splitlines())
if not out.endswith("\n"):
    out += "\n"
SITEMAP.write_text(out, encoding="utf-8")
con = sum(1 for l in out.splitlines() if "<lastmod>" in l)
print(f"sitemap.xml actualizado: {con} URLs con <lastmod>")
