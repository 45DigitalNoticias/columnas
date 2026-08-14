# -*- coding: utf-8 -*-
"""
Miniaturas de las portadas para el panel de la portada del sitio.

POR QUÉ EXISTE
El collage del hero carga ~100 piezas. Las portadas originales pesan
88.6 MB entre las 93: así el panel no termina de cargar nunca y el
lector ve un hueco negro. En webp de 420px las 93 pesan 3.85 MB, un
95.7% menos, y cada pieza se muestra a ~80px, o sea que sobra
resolución de todas formas.

CUÁNDO SE CORRE
Cada vez que se publica una columna nueva. `_publicar_columna.py` lo
llama solo; también se puede correr a mano:

    python _generar_miniaturas.py            # solo las que faltan
    python _generar_miniaturas.py --todas    # rehace todas

Si una portada nueva no tiene miniatura, el panel deja un hueco y no
avisa. Por eso conviene que corra siempre, no cuando uno se acuerde.
"""
import io, os, sys, json, shutil, pathlib

AQUI  = pathlib.Path(__file__).resolve().parent
THUMB = AQUI / "thumbs"
ANCHO = 420
CALID = 76


def portadas():
    """Las portadas que el sitio realmente usa, declaradas en _columnas.json.
    No se busca por nombre de archivo: 48 de las 93 no llevan 'portada'
    en el nombre y un glob por patrón se las come. Tampoco se leen de las
    tarjetas de index/todas: esas páginas las escriben los generadores
    (dependencia circular) y su markup ya no trae card-img."""
    mf = AQUI / "_columnas.json"
    if not mf.exists():
        print("Falta _columnas.json. Corre antes:  python _generar_manifiesto.py")
        return []
    usadas = [c.get("img", "") for c in json.loads(io.open(mf, encoding="utf-8").read())]
    return [u for u in dict.fromkeys(usadas) if u and not u.startswith("http")]


def main(rehacer=False):
    try:
        from PIL import Image
    except ImportError:
        print("Falta Pillow:  pip install Pillow"); return 1

    THUMB.mkdir(exist_ok=True)
    antes = despues = 0
    nuevas = saltadas = copiadas = perdidas = 0

    for rel in portadas():
        src = AQUI / rel
        if not src.exists():
            print("  FALTA la portada:", rel); perdidas += 1; continue

        # los svg se copian tal cual: ya pesan nada y escalan solos
        if src.suffix.lower() == ".svg":
            dst = THUMB / src.name
            if rehacer or not dst.exists():
                shutil.copy(src, dst); copiadas += 1
            despues += dst.stat().st_size; antes += src.stat().st_size
            continue

        dst = THUMB / (src.stem + ".webp")
        antes += src.stat().st_size
        if dst.exists() and not rehacer and dst.stat().st_mtime >= src.stat().st_mtime:
            saltadas += 1; despues += dst.stat().st_size; continue

        im = Image.open(src).convert("RGB")
        w, h = im.size
        im = im.resize((ANCHO, max(1, round(h * ANCHO / w))), Image.LANCZOS)
        im.save(dst, "WEBP", quality=CALID, method=6)
        nuevas += 1; despues += dst.stat().st_size

    print(f"miniaturas: {nuevas} nuevas, {copiadas} svg copiados, {saltadas} al dia"
          + (f", {perdidas} portadas FALTANTES" if perdidas else ""))
    if antes:
        print(f"peso: {antes/1048576:.1f} MB de origen -> {despues/1048576:.2f} MB "
              f"({100 - despues/antes*100:.1f}% menos)")
    return 0


if __name__ == "__main__":
    sys.exit(main("--todas" in sys.argv))
