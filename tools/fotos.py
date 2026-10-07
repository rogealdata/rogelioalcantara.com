#!/usr/bin/env python3
"""Prepara fotos para publicar: borra TODOS los metadatos (EXIF, GPS, XMP, IPTC),
corrige la orientación y genera AVIF + WebP + JPG en dos anchos.

Uso:
    python3 tools/fotos.py ORIGEN DESTINO_SIN_EXTENSION [ancho_chico ancho_grande]

Ejemplo:
    python3 tools/fotos.py ~/Fotos/IMG_1234.HEIC assets/img/terreno/altos/001 800 1600

Requisitos (sólo para este script, no para el sitio):
    pip install pillow pillow-heif

Al final verifica que ningún archivo generado conserve EXIF y lo informa.
"""
import os
import sys

from PIL import Image, ImageOps

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pass


def limpia(im):
    """Copia sólo los píxeles: nada de metadatos viaja con la imagen nueva."""
    im = ImageOps.exif_transpose(im).convert("RGB")
    return Image.frombytes("RGB", im.size, im.tobytes())


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    origen, destino = sys.argv[1], sys.argv[2]
    anchos = [int(a) for a in sys.argv[3:5]] or [800, 1600]
    os.makedirs(os.path.dirname(destino) or ".", exist_ok=True)

    im = limpia(Image.open(origen))
    salidas = []
    for ancho in anchos:
        ancho = min(ancho, im.width)
        alto = round(im.height * ancho / im.width)
        r = im.resize((ancho, alto), Image.LANCZOS)
        base = f"{destino}-{ancho}"
        r.save(base + ".jpg", "JPEG", quality=82, optimize=True, progressive=True)
        r.save(base + ".webp", "WEBP", quality=80, method=6)
        r.save(base + ".avif", "AVIF", quality=60)
        salidas += [base + ext for ext in (".jpg", ".webp", ".avif")]

    for ruta in salidas:
        with Image.open(ruta) as comprobar:
            sucio = len(comprobar.getexif()) or any(k in comprobar.info for k in ("exif", "xmp", "XML:com.adobe.xmp"))
        if sucio:
            sys.exit(f"ERROR: {ruta} conserva metadatos")
        print(f"ok  {ruta}  ({os.path.getsize(ruta) // 1024} KB)")
    print(f"tamaño final: {anchos[-1]} x {round(im.height * min(anchos[-1], im.width) / im.width)} px")


if __name__ == "__main__":
    main()
