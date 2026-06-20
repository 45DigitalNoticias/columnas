"""
Avisa a IndexNow (Bing, Yandex, Seznam) de todas las URLs del sitemap para acelerar
la indexación del sitio de columnas. Google NO usa IndexNow (eso va por Search Console),
pero Bing alimenta a ChatGPT, así que ayuda a la citabilidad por LLM.

Requisito: el archivo de clave (45dca17b9e0f4c2a8d6b3f5e1a7c9d20.txt) debe estar ya
PUBLICADO (pusheado) y accesible antes de correr esto.

Uso: python _indexnow.py
"""
import json, re, urllib.request
from pathlib import Path

HOST = "45digitalnoticias.github.io"
KEY = "45dca17b9e0f4c2a8d6b3f5e1a7c9d20"
KEY_LOCATION = f"https://{HOST}/columnas/{KEY}.txt"
SITEMAP = Path(__file__).parent / "sitemap.xml"

urls = re.findall(r"<loc>([^<]+)</loc>", SITEMAP.read_text(encoding="utf-8"))
payload = {"host": HOST, "key": KEY, "keyLocation": KEY_LOCATION, "urlList": urls}
data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(
    "https://api.indexnow.org/indexnow",
    data=data,
    headers={"Content-Type": "application/json; charset=utf-8"},
)
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print("IndexNow:", r.status, "-", len(urls), "URLs enviadas")
except Exception as e:
    print("Error:", e)
