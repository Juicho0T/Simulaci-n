---
name: publicaciones-aws-sbg
description: Crea publicaciones de Instagram para el AWS Student Builder Group (ITD) — posts sueltos, carruseles 3:4 e historias 9:16 — con la identidad visual del grupo (morado + chip). Úsalo para anuncios de evento, recaps de eventos, resúmenes de taller, tutoriales, agradecimientos a patrocinadores y captions.
---

# Publicaciones AWS Student Builder Group

Todo el trabajo se hace en español. Las imágenes se generan con Python + Pillow (`pip install -r requirements.txt`).

## 1. Flujo de trabajo

1. **Fotos:** el usuario suele mandar las fotos de 5 en 5. Cuéntalas en voz alta en cada envío ("llevo 12 fotos"), descríbelas en una línea y **no empieces a diseñar hasta que diga "listo"**. Guarda cada foto en `fotos/<evento>/` (carpeta ignorada por git) en cuanto llegue.
2. **Datos:** con el "listo", pide solo lo que falte: fecha, lugar, ponentes, qué se vio/hizo, ganadores, número de slides. Si el usuario dice "tú propón", propón tú (normalmente 5 slides para un recap corto, 1 slide por momento del evento).
3. **No inventes datos.** Si algo se deduce de una foto (texto de una diapositiva, un reconocimiento, un logo), úsalo y dilo. Si es suposición, márcalo para que el usuario lo revise.
4. **Genera, verifica y muestra:** ejecuta el script, abre cada slide para revisarla (no basta con que el script termine) y envía las imágenes al usuario. Después escribe el caption.
5. **Iteraciones:** cuando pida un cambio puntual ("quita X", "pon Y"), cambia solo eso y reenvía solo las slides afectadas. Antes de cambiar el estilo completo, respalda la versión anterior.

## 2. Identidad visual (por defecto)

Usa siempre esta paleta salvo que el usuario pida otra para una publicación concreta:

| Uso | Color |
|---|---|
| Fondo | `#151C26` (21, 28, 38) — en carruseles se usa un degradado oscuro algo más morado `(24, 19, 44)` |
| Acento principal | morado `#AE5CFF` (174, 92, 255) |
| Morado claro (texto pequeño, etiquetas) | `#C698FF` (198, 152, 255) |
| Texto principal | blanco `(240, 242, 247)` |
| Texto de apoyo | gris claro `(180, 188, 204)` |

- **Logo del grupo:** `assets/logo.png` (chip morado). Va en la cabecera de cada slide.
- **Colaboraciones:** si el evento es con otra organización, usa "chip × logo del aliado" en la cabecera. Con ACISTI: `assets/acisti.png`, y su paleta es azul `#00BEE2` / `#86DCEE` sobre fondo `(4, 28, 56)`.
- **Logo de AWS:** no lo dibujes ni lo recrees. Solo úsalo si el usuario entrega el archivo oficial.
- **Colores de AWS** (`#232F3E` + naranja `#FF9900`): solo si el usuario lo pide expresamente para esa publicación. Ojo: después de usarlos, el usuario volvió a preferir el morado.

### Estilo que más le gusta: editorial oscuro

- Titulares en serif **Caladea Bold** con la segunda línea en *Caladea Bold Italic* morada (p. ej. "Lo que / *vimos*"), o en **Inter Display Black** cuando el tema es más tech.
- Texto en **Inter**. Etiquetas pequeñas en MAYÚSCULAS con Inter Bold en morado claro.
- Cabecera: logo(s) + "AWS STUDENT BUILDER GROUP" a la izquierda, sección a la derecha, doble filete (claro + morado) debajo.
- Pie: "Evento — fecha" a la izquierda y "n / total →" a la derecha, sobre un filete fino.
- Cuadrícula sutil de fondo (líneas cada 60 px) y resplandores morados difusos.
- Fotos completas (sin recortes) con marco fino; números grandes en contorno morado para datos ("23 equipos", "1–4 integrantes").
- Cierre editorial: frase grande + lista numerada con filetes (01, 02, 03), sin tarjetas tipo botón.

### Estilos que NO le gustaron (evitar)

- Polaroids inclinadas con cinta, stickers y look scrapbook: "se ve desordenado".
- Fotos pequeñas con mucho espacio vacío.
- Diseños que se parezcan demasiado a la publicación anterior: si pide "otro estilo", cambia el concepto completo, no solo colores.
- Tarjeta de llamada a la acción con botón repetida en cada carrusel ("muy repetitivo").

## 3. Formatos

| Formato | Tamaño | Notas |
|---|---|---|
| Post / slide de carrusel | **1080 × 1440 (3:4)** | Margen mínimo de 80 px para todo el texto. |
| Historia | **1080 × 1920 (9:16)** | Texto solo entre y = 250 y y = 1670 (Instagram tapa arriba y abajo). |
| Carrusel continuo | panorama de `N × 1080` × 1440 cortado en N slides | Las fotos pueden cruzar las divisiones (nunca dejar un trozo < 110 px); el texto **nunca** cruza una división. |

Dibuja al doble de resolución (`S = 2`) y reduce al final con LANCZOS para bordes suaves.

## 4. Scripts

Todos importan `_comun.py`, que hace que las fuentes de `assets/fonts/` y los logos funcionen en cualquier computadora.

- `crear_post.py` — imagen suelta 3:4 (anuncio, resultado, taller, tutorial).
  `python .claude/skills/publicaciones-aws-sbg/crear_post.py --titulo "..." --fecha "..." --lugar "..." --tipo anuncio`
- `plantillas/` — los diseños aprobados, listos para copiar y adaptar. **Los nombres de las fotos y los textos están escritos dentro del script** (son del evento original): copia la plantilla, cambia fotos, textos y posiciones, y ejecútala.
  - `carrusel_slides.py` — slides independientes, estilo editorial con titulares Inter Display ("Explorando Skill Builder", 5 slides). Buena base para recaps cortos.
  - `carrusel_editorial.py` — editorial oscuro con titulares serif, fotos con pie "Fig. n", árbol de texto monoespaciado (taller "Claude Code en Amazon Bedrock", 5 slides).
  - `carrusel_panoramico.py` — collage continuo de 11 slides con cambio de paleta (morado → azul ACISTI) y haz de luz en la unión; incluye slide de patrocinadores con logos en tarjetas blancas (Hackathon 24H ITD 2026).
  - `historias_patrocinadores.py` — una historia 9:16 por patrocinador ("Patrocinador *oficial*" + logo + agradecimiento) y una portada sin logos con el número total de aliados.

Uso típico: `python .claude/skills/publicaciones-aws-sbg/plantillas/<script>.py <carpeta_fotos> salida`

### Patrocinadores guardados (`assets/patrocinadores/`)

DICOM.MX, PACS Computación, Print Company, CSNI (solo ícono: añadir el nombre debajo), Caja Hipódromo, República Coffee Roasters, Cosmo Carrier, XIXIM, CESA (versión horizontal) y el Departamento de Sistemas y Computación (es una foto redonda, no un logo: mostrar en círculo con halo). Los logos de CSNI y República necesitan limpieza de fondo; la función `limpiar()` de `historias_patrocinadores.py` ya lo hace.

## 5. Verificación obligatoria antes de entregar

Cada script debe comprobar automáticamente, y fallar con un mensaje claro si no se cumple:

- Ningún texto a menos de 80 px del borde (historias: dentro de la zona segura).
- Ningún texto encima o pegado a una foto o tarjeta de logo; ninguna foto encima de otra.
- Fotos completas, sin recortar; cada foto se usa una sola vez.
- En carruseles continuos: ningún texto cruza una división ni cae en la franja del degradado, y al volver a unir las slides el resultado es idéntico al panorama.

Además **abre las imágenes** (hoja de contactos con todas las slides en miniatura) y revisa a ojo: textos repetidos, títulos pegados al párrafo, decoraciones que chocan con el pie, huecos grandes. Si Pillow no está instalado y no se puede instalar, dilo y no des el trabajo por probado.

## 6. Caption para Instagram

- Abre con un gancho en la primera línea (pregunta, dato o frase con energía). Nunca "Hola a todos".
- Tono de recap cercano, de builder a builder, con emojis sin exagerar.
- Lista corta "Lo que vivimos 👇 / Lo que nos llevamos 👇".
- Agradece a participantes, ponentes, jueces y patrocinadores (por nombre).
- Llamada a la acción al final. El usuario prefiere **"Síguenos en Instagram"** como CTA.
- Hashtags: `#AWS #StudentBuilderGroup #AWSCommunity` + 1 o 2 del tema (p. ej. `#Hackathon`, `#CloudComputing`, `#ClaudeCode`, `#AWSSkillBuilder`).
- Máximo ~150 palabras. Entrégalo en un bloque de código para copiar.

## 7. Salida

- Las imágenes van en `salida/` (git ignora los `.png`). Usa nombres por publicación para no sobrescribir otra (`skillbuilder_slide_1.png`, `historia_dicom.png`…).
- Al terminar, muestra al usuario las rutas, envíale las imágenes y da el caption.
