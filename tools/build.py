#!/usr/bin/env python3
"""Genera las páginas HTML del sitio a partir de data/*.json.

Uso:  python3 tools/build.py

Sin dependencias (sólo la biblioteca estándar de Python 3.8+). El HTML generado
se versiona tal cual, así que el sitio se sirve sin build: este script sólo hace
falta cuando cambias algo en data/.
"""
import html
import json
import os
import shutil
import subprocess
from urllib.parse import unquote

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL_BASE = "https://rogelioalcantara.com/"
IDIOMAS = ["en", "es", "fr"]
CARPETA = {"en": "", "es": "es/", "fr": "fr/"}
LOCALE = {"en": "en_US", "es": "es_MX", "fr": "fr_FR"}
NOMBRE_IDIOMA = {"en": "English", "es": "Español", "fr": "Français"}

# clave -> archivo. El orden es el del menú.
PAGINAS = [
    ("escritos", "escritos.html"),
    ("docencia", "docencia.html"),
    ("teatro", "teatro-politico.html"),
    ("editorial", "editorial.html"),
    ("terreno", "trabajo-de-campo.html"),
    ("proyectos", "proyectos.html"),
    ("acerca", "acerca.html"),
]
ARCHIVO = dict(PAGINAS, inicio="index.html")

# Rutas antiguas que ya no existen: se redirigen para no romper enlaces.
REDIRECCIONES = {"escritos/cartografia-chiapas.html": "escritos.html", "cv.html": "acerca.html#cv"}


def cargar(nombre):
    with open(os.path.join(RAIZ, "data", nombre), encoding="utf-8") as f:
        return json.load(f)


T = cargar("textos.json")
OBRA = cargar("obra.json")["obra"]
TERRENO = cargar("terreno.json")["proyectos"]
e = html.escape


def loc(valor, idioma):
    """Texto simple o diccionario {en, es, fr}."""
    if isinstance(valor, dict):
        return valor.get(idioma, "")
    return valor or ""


def pendiente(valor):
    return not valor or str(valor).startswith("TODO")


def url_pagina(idioma, clave):
    archivo = ARCHIVO[clave]
    ruta = CARPETA[idioma] + ("" if archivo == "index.html" else archivo)
    return URL_BASE + ruta


def fecha(item, idioma):
    if item.get("fecha_texto"):
        return item["fecha_texto"]
    partes = item["fecha"].split("-")
    if len(partes) == 1:
        return partes[0]
    c = T["comun"][idioma]
    return c["fecha_formato"].format(mes=c["meses"][int(partes[1]) - 1], anio=partes[0])


# ---------------------------------------------------------------- piezas

LAMPARA = """<svg class="lamp-icon" viewBox="0 0 40 40" aria-hidden="true" focusable="false">
        <ellipse class="glow" cx="20" cy="14" rx="10" ry="8"/>
        <path class="shade" d="M13 14 L27 14 L23 6 L17 6 Z"/>
        <circle class="bulb" cx="20" cy="17" r="2.2"/>
        <line class="arm" x1="8" y1="34" x2="8" y2="22"/>
        <line class="arm" x1="8" y1="22" x2="20" y2="14"/>
        <line class="base" x1="3" y1="34" x2="13" y2="34"/>
      </svg>"""

_SVG = '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{}</svg>'
ICONOS = {
    "instagram": _SVG.format(
        '<rect x="3.5" y="3.5" width="17" height="17" rx="5" fill="none" stroke="currentColor" stroke-width="1.4"/>'
        '<circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="1.4"/>'
        '<circle cx="17.2" cy="6.8" r="1" fill="currentColor"/>'),
    "linkedin": _SVG.format(
        '<rect x="3.5" y="3.5" width="17" height="17" rx="2.5" fill="none" stroke="currentColor" stroke-width="1.4"/>'
        '<path d="M8 10.5v6M8 7.6v.1M11.5 16.5v-6M11.5 13c0-1.6 1-2.6 2.3-2.6s2.2.9 2.2 2.6v3.5" '
        'fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>'),
    "youtube": _SVG.format(
        '<rect x="2.5" y="5.5" width="19" height="13" rx="3.5" fill="none" stroke="currentColor" stroke-width="1.4"/>'
        '<path d="M10 9.2v5.6l4.8-2.8z" fill="currentColor"/>'),
    "academia": _SVG.format(
        '<path d="M2.5 9.5 12 5l9.5 4.5L12 14z" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>'
        '<path d="M6.5 11.6v4c1.4 1.5 3.3 2.3 5.5 2.3s4.1-.8 5.5-2.3v-4M21.5 9.5v5" '
        'fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>'),
}

# Fija el tema antes de pintar, para que no parpadee.
TEMA_INLINE = ('<script>try{var t=localStorage.getItem("ra_theme");'
               'if(t==="light"||t==="dark")document.documentElement.setAttribute("data-theme",t)}catch(e){}</script>')


def head(idioma, clave, titulo, descripcion, rel, tipo_og="website"):
    alternos = "\n".join(
        f'<link rel="alternate" hreflang="{l}" href="{url_pagina(l, clave)}">' for l in IDIOMAS
    )
    otros_locales = "\n".join(
        f'<meta property="og:locale:alternate" content="{LOCALE[l]}">' for l in IDIOMAS if l != idioma
    )
    return f"""<!doctype html>
<html lang="{idioma}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)}</title>
<meta name="description" content="{e(descripcion)}">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#f4f0e6" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#15130f" media="(prefers-color-scheme: dark)">
<link rel="canonical" href="{url_pagina(idioma, clave)}">
{alternos}
<link rel="alternate" hreflang="x-default" href="{url_pagina('en', clave)}">
<meta property="og:type" content="{tipo_og}">
<meta property="og:site_name" content="Rogelio Alcántara">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(descripcion)}">
<meta property="og:url" content="{url_pagina(idioma, clave)}">
<meta property="og:image" content="{URL_BASE}assets/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Rogelio Alcántara">
<meta property="og:locale" content="{LOCALE[idioma]}">
{otros_locales}
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{rel}assets/favicon.svg" type="image/svg+xml">
<link rel="preload" href="{rel}assets/fonts/eb-garamond-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{rel}assets/style.css">
{TEMA_INLINE}
</head>"""


def cabecera(idioma, clave, rel):
    nav = T["nav"][idioma]
    c = T["comun"][idioma]
    enlaces = []
    for k, archivo in PAGINAS:
        actual = ' aria-current="page"' if k == clave else ""
        enlaces.append(f'<a href="{archivo}"{actual}>{e(nav[k])}</a>')
    idiomas = []
    for l in IDIOMAS:
        destino = rel_entre(idioma, l) + ARCHIVO[clave]
        actual = ' aria-current="true"' if l == idioma else ""
        idiomas.append(f'<a href="{destino}" hreflang="{l}" lang="{l}"{actual} title="{NOMBRE_IDIOMA[l]}">{l.upper()}</a>')
    return f"""<body>
<a class="skip" href="#contenido">{e(c['saltar'])}</a>
<header class="site">
  <div class="site-top">
    <a class="brand" href="index.html">Rogelio Alcántara</a>
    <div class="header-controls">
      <nav class="lang-switch" aria-label="{e(c['idiomas'])}">
        {'<span class="sep" aria-hidden="true">·</span>'.join(idiomas)}
      </nav>
      <button class="lamp-btn" type="button" data-lamp aria-label="{e(c['lampara'])}">
      {LAMPARA}
      </button>
    </div>
  </div>
  <nav class="site-nav" aria-label="{e(c['menu'])}">
    {chr(10).join('    ' + a for a in enlaces).strip()}
  </nav>
</header>
"""


def rel_entre(origen, destino):
    """Prefijo relativo desde la carpeta de un idioma a la de otro."""
    subir = "../" if CARPETA[origen] else ""
    return subir + CARPETA[destino]


def correo(idioma, clase="", texto=None):
    c = T["comun"][idioma]
    etiqueta = texto or c["contacto_boton"]
    clase = f' class="{clase}"' if clase else ""
    return (f'<a{clase} data-e="{T["enlaces"]["correo_invertido"]}" '
            f'href="#contacto">{e(etiqueta)}</a>')


def iconos_perfiles(idioma):
    items = []
    for p in T["enlaces"]["perfiles"]:
        if pendiente(p["url"]):
            # Sin URL todavía: icono visible pero sin enlace.
            if p["icono"] == "youtube":
                pronto = e(T["comun"][idioma]["youtube_pronto"])
                items.append(f'<li><span class="soon" role="img" aria-label="{pronto}" title="{pronto}">'
                             f'{ICONOS["youtube"]}</span></li>')
            else:
                items.append(f"<!-- {e(p['url'])} ({e(p['nombre'])}) -->")
            continue
        items.append(f'<li><a href="{e(p["url"])}" rel="me noopener" aria-label="{e(p["nombre"])}" '
                     f'title="{e(p["nombre"])}">{ICONOS[p["icono"]]}</a></li>')
    return "\n    ".join(items)


def pie(idioma, rel):
    c = T["comun"][idioma]
    cara = rel + "assets/img/cara"
    return f"""<footer class="site" id="contacto">
  <div class="card">
    <picture>
      <source type="image/avif" srcset="{cara}-160.avif 1x, {cara}-320.avif 2x">
      <source type="image/webp" srcset="{cara}-160.webp 1x, {cara}-320.webp 2x">
      <img class="avatar" src="{cara}-320.jpg" width="80" height="80" alt="" loading="lazy" decoding="async">
    </picture>
    <div class="card-text">
      <p class="card-name">Rogelio Alcántara</p>
      <p class="card-note">{e(c['contacto_texto'])}</p>
      <p class="card-mail"><span data-e-texto="{T["enlaces"]["correo_invertido"]}"></span></p>
      <noscript><p class="small">{e(c['correo_sin_js'])}</p></noscript>
    </div>
    {correo(idioma, "btn")}
  </div>
  <ul class="social" aria-label="{e(c['redes'])}">
    {iconos_perfiles(idioma)}
  </ul>
</footer>
<script src="{rel}assets/script.js" defer></script>
</body>
</html>
"""


def pagina(idioma, clave, titulo, descripcion, cuerpo, tipo_og="website"):
    rel = "../" if CARPETA[idioma] else ""
    return (head(idioma, clave, titulo, descripcion, rel, tipo_og) + "\n"
            + cabecera(idioma, clave, rel)
            + '<main id="contenido">\n' + cuerpo + "\n</main>\n"
            + pie(idioma, rel))


def titulo_pagina(idioma, clave):
    return f"{T['nav'][idioma][clave]} — Rogelio Alcántara"


# ---------------------------------------------------------------- obra

def obra_ordenada():
    return sorted(OBRA, key=lambda i: i["fecha"], reverse=True)


def item_obra(item, idioma, h="h3"):
    tipos = T["tipos"][idioma]
    titulo = e(item["titulo"])
    if item.get("url"):
        titulo = f'<a href="{e(item["url"])}" rel="noopener">{titulo}</a>'
    meta = [e(loc(item.get("medio"), idioma)), e(loc(item.get("lugar"), idioma)), e(fecha(item, idioma))]
    meta = " · ".join(m for m in meta if m)
    lineas = [
        f'<p class="entry-kicker"><span class="kicker">{e(tipos[item["tipo"]][0])}</span>'
        f'<span class="lang-tag" title="{NOMBRE_IDIOMA.get(item["idioma"], "")}">{item["idioma"].upper()}</span></p>',
        f'<{h} class="entry-title" lang="{item["idioma"]}">{titulo}</{h}>',
        f'<p class="entry-meta">{meta}</p>',
    ]
    if item.get("nota"):
        lineas.append(f'<p class="entry-note">{loc(item["nota"], idioma)}</p>')
    if item.get("doi"):
        d = e(item["doi"])
        lineas.append(f'<p class="entry-note">{T["escritos"][idioma]["doi"]}: '
                      f'<a href="https://doi.org/{d}" rel="noopener">{d}</a></p>')
    return f'<li class="entry" data-tipo="{item["tipo"]}">\n  ' + "\n  ".join(lineas) + "\n</li>"


def pagina_escritos(idioma):
    s = T["escritos"][idioma]
    tipos = T["tipos"][idioma]
    presentes = [t for t in tipos if any(i["tipo"] == t for i in OBRA)]
    botones = [f'<button type="button" data-filtro="{t}" aria-pressed="false">{e(tipos[t][1])}</button>'
               for t in presentes]
    botones.append(f'<button type="button" class="all" data-filtro="todo" aria-pressed="true">{e(s["todo"])}</button>')
    grupos, actual = [], None
    for item in obra_ordenada():
        anio = item["fecha"][:4]
        if anio != actual:
            if actual:
                grupos.append("</ol>\n</section>")
            grupos.append(f'<section class="year" aria-labelledby="y{anio}">\n'
                          f'<h2 class="year-label" id="y{anio}">{anio}</h2>\n<ol class="entries">')
            actual = anio
        grupos.append(item_obra(item, idioma))
    grupos.append("</ol>\n</section>")
    cuerpo = f"""<div class="page-head">
  <h1>{e(T['nav'][idioma]['escritos'])}</h1>
  <p class="lede">{e(s['intro'])}</p>
</div>
<div class="filters" role="group" aria-label="{e(s['filtro'])}" hidden>
  {chr(10).join('  ' + b for b in botones).strip()}
</div>
<div class="archive" data-archivo>
{chr(10).join(grupos)}
</div>"""
    return pagina(idioma, "escritos", titulo_pagina(idioma, "escritos"), s["descripcion"], cuerpo)


# ---------------------------------------------------------------- inicio

def fila_enlaces(idioma):
    items = []
    for n in T["enlaces"]["newsletters"]:
        if pendiente(n["url"]):
            items.append(f"<!-- {e(n['url'])} ({e(n['nombre'])}) -->")
            continue
        items.append(f'<li><a href="{e(n["url"])}" rel="noopener">{e(n["nombre"])}</a></li>')
    return "\n    ".join(items)


def retrato(ruta, alt, sizes, prioridad=True):
    extra = ' fetchpriority="high"' if prioridad else ' loading="lazy"'
    return f"""<picture>
      <source type="image/avif" srcset="{ruta}-600.avif 600w, {ruta}-1200.avif 1200w" sizes="{sizes}">
      <source type="image/webp" srcset="{ruta}-600.webp 600w, {ruta}-1200.webp 1200w" sizes="{sizes}">
      <img src="{ruta}-1200.jpg" width="1200" height="1600" alt="{e(alt)}" decoding="async"{extra}>
    </picture>"""


def pagina_inicio(idioma):
    s = T["inicio"][idioma]
    rel = "../" if CARPETA[idioma] else ""
    cuerpo = f"""<section class="home" aria-labelledby="nombre">
  <figure class="frame">
    {retrato(rel + "assets/img/inicio", s['foto_alt'], "(max-width: 760px) 92vw, 340px")}
  </figure>
  <div class="home-text">
    <h1 id="nombre" class="sr-only">Rogelio Alcántara</h1>
    <p class="statement">{e(s['frase'])}</p>
    <div class="channels">
      <h2 class="kicker">{e(s['newsletters'])}</h2>
      <ul>
      {fila_enlaces(idioma)}
      </ul>
    </div>
  </div>
</section>"""
    return pagina(idioma, "inicio", s["titulo_meta"], s["descripcion"], cuerpo)


# ---------------------------------------------------------------- secciones

def pagina_en_preparacion(idioma, clave):
    s = T["secciones_en_preparacion"][idioma][clave]
    c = T["comun"][idioma]
    cuerpo = f"""<div class="page-head">
  <h1>{e(T['nav'][idioma][clave])}</h1>
  <p class="lede">{e(s)}</p>
</div>
<!-- TODO: contenido confirmado de esta sección (títulos, instituciones, fechas, descripciones). -->
<p class="placeholder">{e(c['en_preparacion'])}</p>"""
    return pagina(idioma, clave, titulo_pagina(idioma, clave), s, cuerpo)


def figura(foto, idioma, rel):
    s = T["terreno"][idioma]
    src = rel + foto["src"]
    detalles = " · ".join(x for x in [e(loc(foto.get("lugar"), idioma)), e(foto.get("anio", ""))] if x)
    aprendizaje = loc(foto.get("aprendizaje"), idioma)
    extra = f'<span class="learned"><span class="kicker">{e(s["aprendizaje"])}</span> {e(aprendizaje)}</span>' if aprendizaje else ""
    return f"""<figure class="photo">
  <picture>
    <source type="image/avif" srcset="{src}-800.avif 800w, {src}-1600.avif 1600w" sizes="(max-width: 760px) 100vw, 780px">
    <source type="image/webp" srcset="{src}-800.webp 800w, {src}-1600.webp 1600w" sizes="(max-width: 760px) 100vw, 780px">
    <img src="{src}-1600.jpg" width="{foto['ancho']}" height="{foto['alto']}" alt="{e(loc(foto['alt'], idioma))}" loading="lazy" decoding="async">
  </picture>
  <figcaption><span class="kicker">{detalles}</span> {e(loc(foto.get('pie'), idioma))} {extra}</figcaption>
</figure>"""


def pagina_terreno(idioma):
    s = T["terreno"][idioma]
    c = T["comun"][idioma]
    rel = "../" if CARPETA[idioma] else ""
    bloques = []
    for p in TERRENO:
        fotos = [f for f in p.get("fotos", []) if f.get("publicar") is True]
        if not fotos:
            continue
        bloques.append(f"""<section class="project" aria-labelledby="p-{e(p['id'])}">
  <h2 id="p-{e(p['id'])}">{e(loc(p['titulo'], idioma))} <span class="kicker">{e(p.get('periodo', ''))}</span></h2>
  <p class="project-intro">{e(loc(p.get('intro'), idioma))}</p>
  {chr(10).join(figura(f, idioma, rel) for f in fotos)}
</section>""")
    contenido = "\n".join(bloques) or (
        "<!-- TODO: fotos de terreno (ver data/terreno.json). -->\n"
        f'<p class="placeholder">{e(c["en_preparacion"])}</p>')
    cuerpo = f"""<div class="page-head">
  <h1>{e(T['nav'][idioma]['terreno'])}</h1>
  <p class="lede">{e(s['intro'])}</p>
</div>
{contenido}"""
    return pagina(idioma, "terreno", titulo_pagina(idioma, "terreno"), s["descripcion"], cuerpo)


def nombre_pdf(idioma):
    return f"assets/cv/rogelio-alcantara-cv-{idioma}.pdf"


def secciones_cv(idioma):
    """Secciones del CV, construidas desde data/: se actualizan solas."""
    cv = T["cv"][idioma]

    def lineas(clave):
        return [f'<span class="role">{e(rol)}</span> <span class="org">{e(org)}</span>'
                for rol, org in cv["lineas"][clave]]

    def obras(*tipos):
        filas = []
        for i in obra_ordenada():
            if i["tipo"] not in tipos:
                continue
            titulo = e(i["titulo"])
            if i.get("url"):
                titulo = f'<a href="{e(i["url"])}" rel="noopener">{titulo}</a>'
            meta = ", ".join(x for x in (e(loc(i.get("medio"), idioma)), e(loc(i.get("lugar"), idioma))) if x)
            anio = e(i.get("fecha_texto") or i["fecha"][:4])
            filas.append(f'<span class="cv-year">{anio}</span> '
                         f'<span><cite lang="{i["idioma"]}">{titulo}</cite>. {meta}.</span>')
        return filas

    return [
        ("formacion", cv["formacion"], lineas("formacion")),
        ("trayectoria", cv["trayectoria"], lineas("trayectoria")),
        ("publicaciones", cv["publicaciones"], obras("articulo", "entrevista")),
        ("tesis", cv["tesis"], obras("tesis")),
        ("ponencias", cv["ponencias"], obras("ponencia")),
        ("academico", cv["academico"], obras("organizacion")),
        ("areas", cv["areas"], [e(x.strip(" .")) for x in cv["areas_texto"].split("·")]),
    ]


def pagina_acerca(idioma):
    s = T["acerca"][idioma]
    cv = T["cv"][idioma]
    rel = "../" if CARPETA[idioma] else ""
    bloques = []
    for clave, titulo, filas in secciones_cv(idioma):
        if not filas:
            continue
        lis = "\n".join(f"    <li>{f}</li>" for f in filas)
        bloques.append(f"""<details class="cv-block" id="cv-{clave}" open>
  <summary><h2>{e(titulo)}</h2><span class="count">{len(filas)}</span></summary>
  <ul class="cv-lines">
{lis}
  </ul>
</details>""")
    cuerpo = f"""<h1 class="sr-only">{e(T['nav'][idioma]['acerca'])}</h1>
<div class="about">
  <figure class="frame">
    {retrato(rel + "assets/img/rogelio-alcantara", s['foto_alt'], "(max-width: 760px) 92vw, 340px")}
  </figure>
  <div class="about-text">
    <p class="statement">{e(s['frase'])}</p>
    <p class="about-actions"><a class="btn" href="{rel}{nombre_pdf(idioma)}" download>{e(cv['descargar'])}</a></p>
  </div>
</div>

<section class="cv" id="cv" aria-label="{e(cv['nombre_cv'])}">
{chr(10).join(bloques)}
</section>"""
    return pagina(idioma, "acerca", titulo_pagina(idioma, "acerca"), s["descripcion"], cuerpo, "profile")


def pagina_cv_imprimible(idioma):
    """Versión para PDF: una sola columna, sin menú. La imprime Chrome."""
    s = T["acerca"][idioma]
    cv = T["cv"][idioma]
    bloques = []
    for _, titulo, filas in secciones_cv(idioma):
        if filas:
            lis = "\n".join(f"<li>{f}</li>" for f in filas)
            bloques.append(f"<section><h2>{e(titulo)}</h2><ul>\n{lis}\n</ul></section>")
    perfiles = " · ".join(e(unquote(p["url"]).replace("https://", "").replace("www.", "").rstrip("/"))
                          for p in T["enlaces"]["perfiles"] if not pendiente(p["url"]))
    return f"""<!doctype html>
<html lang="{idioma}">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex">
<title>Rogelio Alcántara — {e(cv['nombre_cv'])}</title>
<style>
@font-face{{font-family:'EB Garamond';font-weight:400;src:url('../fonts/eb-garamond-latin-400-normal.woff2') format('woff2')}}
@font-face{{font-family:'EB Garamond';font-weight:400;font-style:italic;src:url('../fonts/eb-garamond-latin-400-italic.woff2') format('woff2')}}
@font-face{{font-family:'EB Garamond';font-weight:500;src:url('../fonts/eb-garamond-latin-500-normal.woff2') format('woff2')}}
@page{{size:A4;margin:18mm 20mm}}
body{{font-family:'EB Garamond',Georgia,serif;color:#241f18;font-size:10.5pt;line-height:1.45;margin:0}}
h1{{font-weight:400;font-size:24pt;margin:0}}
.sub{{font-style:italic;color:#5c5346;font-size:13pt;margin:2pt 0 8pt}}
.contact{{color:#5c5346;font-size:9.5pt;border-bottom:.5pt solid #b9b0a0;padding-bottom:10pt;margin:0 0 4pt}}
h2{{font-weight:400;font-style:italic;text-transform:lowercase;color:#6b2129;font-size:12pt;margin:14pt 0 4pt}}
ul{{list-style:none;margin:0;padding:0}}
li{{display:flex;gap:10pt;padding:2pt 0;break-inside:avoid}}
.cv-year{{flex:0 0 46pt;color:#5c5346}}
.role{{font-weight:500}} .org{{font-style:italic;color:#5c5346}}
a{{color:inherit;text-decoration:none}}
cite{{font-style:italic}}
</style>
</head>
<body>
<h1>Rogelio Alcántara</h1>
<p class="sub">{e(T['inicio'][idioma]['frase'])}</p>
<p class="contact"><span data-e-texto="{T["enlaces"]["correo_invertido"]}"></span> · rogelioalcantara.com · {perfiles}</p>
{chr(10).join(bloques)}
<script>document.querySelectorAll("[data-e-texto]").forEach(function(n){{n.textContent=n.getAttribute("data-e-texto").split("").reverse().join("")}});</script>
</body>
</html>
"""


def buscar_chrome():
    candidatos = [
        os.environ.get("CHROME"),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        shutil.which("google-chrome"), shutil.which("chromium"),
        shutil.which("chromium-browser"), shutil.which("chrome"),
    ]
    return next((c for c in candidatos if c and os.path.exists(c)), None)


def generar_pdfs():
    chrome = buscar_chrome()
    if not chrome:
        print("Aviso: no encontré Chrome; los PDF del CV no se actualizaron (usa CHROME=/ruta/al/navegador).")
        return
    for idioma in IDIOMAS:
        html_cv = os.path.join(RAIZ, "assets", "cv", f"{idioma}.html")
        destino = os.path.join(RAIZ, nombre_pdf(idioma))
        orden = [chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                 "--virtual-time-budget=3000", f"--print-to-pdf={destino}", "file://" + html_cv]
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            orden.insert(1, "--no-sandbox")
        subprocess.run(orden, check=True, capture_output=True)
    print("PDF del CV actualizados en assets/cv/")


def redireccion(destino):
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={destino}">
<link rel="canonical" href="{destino}">
<title>Rogelio Alcántara</title>
</head>
<body><p><a href="{destino}">{destino}</a></p></body>
</html>
"""


# ---------------------------------------------------------------- salida

def escribir(ruta, contenido):
    completa = os.path.join(RAIZ, ruta)
    os.makedirs(os.path.dirname(completa) or RAIZ, exist_ok=True)
    with open(completa, "w", encoding="utf-8") as f:
        f.write(contenido)
    return ruta


def main():
    hechas = []
    for idioma in IDIOMAS:
        base = CARPETA[idioma]
        hechas.append(escribir(base + "index.html", pagina_inicio(idioma)))
        hechas.append(escribir(base + "escritos.html", pagina_escritos(idioma)))
        for clave in ("docencia", "proyectos", "teatro", "editorial"):
            hechas.append(escribir(base + ARCHIVO[clave], pagina_en_preparacion(idioma, clave)))
        hechas.append(escribir(base + ARCHIVO["terreno"], pagina_terreno(idioma)))
        hechas.append(escribir(base + ARCHIVO["acerca"], pagina_acerca(idioma)))
        escribir(f"assets/cv/{idioma}.html", pagina_cv_imprimible(idioma))
        for viejo, nuevo in REDIRECCIONES.items():
            subir = "../" * viejo.count("/")
            hechas.append(escribir(base + viejo, redireccion(subir + nuevo)))
    escribir("sitemap.xml", sitemap())
    print(f"{len(hechas)} páginas generadas + sitemap.xml")
    generar_pdfs()


def sitemap():
    urls = []
    for clave in ["inicio"] + [k for k, _ in PAGINAS]:
        for l in IDIOMAS:
            alt = "".join(
                f'\n    <xhtml:link rel="alternate" hreflang="{o}" href="{url_pagina(o, clave)}"/>' for o in IDIOMAS
            )
            urls.append(f"  <url>\n    <loc>{url_pagina(l, clave)}</loc>{alt}\n  </url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(urls) + "\n</urlset>\n")


if __name__ == "__main__":
    main()
