# rogelio alcántara — el consigliere

Sitio estático. Sin build step, sin dependencias, sin CMS: son puros archivos HTML/CSS/JS que puedes editar directamente.

## Estructura

```
index.html            → inglés (home)
escritos.html          → inglés (índice de escritos)
cv.html                 → inglés (CV)
escritos/               → artículos en inglés (uno por archivo)
es/                     → misma estructura, en español
fr/                     → misma estructura, en francés
assets/style.css        → todos los estilos, en un solo archivo
assets/script.js        → el toggle de la lamparita (claro/oscuro)
CNAME                   → tu dominio, para GitHub Pages
```

## Cómo agregar un nuevo escrito

1. Copia `escritos/cartografia-chiapas.html` (o su versión en `es/` o `fr/`) con un nombre nuevo, ej. `escritos/mi-nuevo-articulo.html`.
2. Cambia el `<title>`, el `kicker` (tipo · fecha · lugar), el `<h1>` y el cuerpo del artículo.
3. Agrega una fila nueva en `escritos.html` (y en `index.html` si quieres que aparezca en la portada) apuntando a tu archivo nuevo.
4. Repite en `es/` y `fr/` si quieres las tres versiones — o deja el escrito solo en un idioma, no pasa nada si por ahora no lo traduces.

No hay base de datos ni panel de administración: el archivo HTML *es* el contenido, como en un WordPress muy simplificado donde cada post es su propio archivo.

## Cómo publicarlo en GitHub Pages con tu dominio

1. Crea un repositorio nuevo en GitHub (puede llamarse como quieras, ej. `rogelio-alcantara`).
2. Sube todo el contenido de esta carpeta a la raíz del repositorio (arrastra los archivos en la interfaz web de GitHub, o usa `git add . && git commit -m "sitio inicial" && git push`).
3. Abre el archivo `CNAME` en GitHub y reemplaza `tu-dominio.com` por tu dominio real (ej. `rogelioalcantara.com`), sin `https://` ni barra final.
4. En el repositorio: Settings → Pages → Source → selecciona la rama `main` y la carpeta `/ (root)`.
5. En el panel de tu proveedor de dominio, agrega:
   - Un registro `A` apuntando a las IPs de GitHub Pages (185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153), o
   - Un registro `CNAME` apuntando a `tu-usuario.github.io` si prefieres usar un subdominio (ej. `www`).
6. Espera unos minutos a que se propague el DNS y activa "Enforce HTTPS" en Settings → Pages una vez que GitHub lo permita.

## La lamparita

El botón de la lámpara en el header cambia entre modo claro y oscuro. Guarda tu preferencia en el navegador de cada visitante (no es una configuración del sitio, sino de quien lo visita).
