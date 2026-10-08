# rogelioalcantara.com

Sitio estático en tres idiomas (inglés en la raíz, español en `es/`, francés en `fr/`). GitHub Pages sirve el HTML tal cual: no hay build en el servidor ni CMS.

## Cómo se edita

Todo el contenido vive en `data/`:

| Archivo | Qué contiene |
| --- | --- |
| `data/obra.json` | Escritos, tesis, ponencias y organización académica (un solo archivo para el índice de Escritos y la portada) |
| `data/textos.json` | Todos los textos de las páginas, por idioma (en, es, fr), y los enlaces externos |
| `data/terreno.json` | Proyectos y fotos de Trabajo de campo |

Después de editar, regenera las páginas:

```
python3 tools/build.py
```

Sólo necesita Python 3 (sin instalar nada). Si encuentra Google Chrome, además regenera los PDF del CV (`assets/cv/rogelio-alcantara-cv-*.pdf`) con los mismos datos, así que el CV descargable siempre coincide con el sitio. Escribe los `.html` de los tres idiomas, el `sitemap.xml` y las etiquetas `hreflang`/Open Graph. Los `.html` generados se versionan; no los edites a mano porque el siguiente build los sobrescribe.

### Añadir una obra

Copia una entrada en `data/obra.json` y cambia los campos. `fecha` es `AAAA-MM` (o sólo `AAAA`); `tipo` es `articulo`, `entrevista`, `tesis`, `ponencia` u `organizacion`. Los títulos no se traducen; `medio`, `lugar` y `nota` pueden ser texto simple o `{ "en": …, "es": …, "fr": … }`.

### Añadir fotos de terreno

1. Procesa cada foto (borra EXIF y GPS, corrige orientación, genera AVIF, WebP y JPG):

   ```
   pip install pillow pillow-heif   # una sola vez
   python3 tools/fotos.py ORIGEN.jpg assets/img/terreno/PROYECTO/001
   ```

2. Añade la foto en `data/terreno.json` (hay un `_ejemplo`) con `"publicar": true` sólo después de revisar rostros, ubicación, fecha y consentimiento.

Nunca subas la foto original al repositorio.

## Estructura

```
index.html, escritos.html, docencia.html, proyectos.html, teatro-politico.html,
editorial.html, trabajo-de-campo.html, acerca.html            → inglés
es/…, fr/…                                                     → mismos archivos
escritos/cartografia-chiapas.html, cv.html                     → redirecciones (rutas antiguas)
assets/style.css      → estilos (modo claro/oscuro incluido)
assets/script.js      → lámpara, correo protegido, filtro de Escritos
assets/fonts/         → EB Garamond (licencia OFL)
assets/img/           → imágenes ya limpias de metadatos
data/, tools/         → contenido y generador
```

## Previsualizar

```
python3 -m http.server 8000
```

y abre http://localhost:8000.

## Correo

La dirección no aparece en el HTML: va invertida en `data-e` y `assets/script.js` arma el `mailto:` en el navegador. Si el dominio pasa por Cloudflare, su Email Obfuscation añade otra capa.

## Publicación

GitHub Pages, rama `main`, carpeta raíz. El dominio está en `CNAME`.
