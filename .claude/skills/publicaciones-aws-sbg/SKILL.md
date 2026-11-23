---
name: publicaciones-aws-sbg
description: Crea publicaciones de Instagram para el AWS Student Builder Group, con texto e imagen en formato 3:4. Úsalo para anuncios de evento, resultados de evento, resúmenes de taller y tutoriales.
---

# Publicaciones AWS Student Builder Group

Sigue estos pasos en orden.

## 1. Preguntar el tipo de publicación

Pregunta al usuario qué tipo de publicación quiere:
- Anuncio de evento
- Resultado de evento
- Resumen de taller
- Tutorial

## 2. Pedir solo los datos de ese tipo

- **Anuncio de evento:** título, fecha, lugar, registro (enlace o forma de registrarse).
- **Resultado de evento:** título, fecha, lugar, número de asistentes, highlights.
- **Resumen de taller:** tema, fecha, lugar, 3 a 5 aprendizajes clave.
- **Tutorial:** tema, 3 a 6 pasos, enlace de referencia (opcional).

## 3. Escribir el texto para Instagram

Reglas fijas:
- Emojis relevantes, sin exagerar.
- Hashtags #AWS, #StudentBuilderGroup y #AWSCommunity, más uno o dos del tema.
- Una llamada a la acción al final (registrarse, seguirnos, comentar, compartir).
- Máximo unas 150 palabras.

Para que el texto sea creativo y no genérico:
- **Empieza con un gancho** en la primera línea, que es lo único que se ve antes del "más": una pregunta provocadora, un dato curioso, un reto o una frase corta con energía. Nunca empieces con "Hola a todos" ni "Les invitamos a…".
- **Habla como builder a builder:** tono cercano, frases cortas, verbos de acción (construye, despliega, rompe, lanza). Un toque de humor técnico está bien si encaja.
- **Usa una estructura según el tipo:**
  - Anuncio: gancho → qué vas a lograr (no solo el tema) → 📅 fecha / 📍 lugar / 🔗 registro → CTA con urgencia ("cupo limitado", "aparta tu lugar").
  - Resultado: el número protagonista (asistentes, proyectos, horas) → 2 o 3 highlights concretos → agradecimiento a ponentes o asistentes → CTA para el próximo evento.
  - Taller: "Lo que nos llevamos 👇" con los aprendizajes en lista corta → CTA para comentar cuál les sirvió más.
  - Tutorial: promesa del resultado final → pasos con 1️⃣ 2️⃣ 3️⃣ → CTA para guardar el post.
- **Ofrece dos versiones** con tono distinto (por ejemplo, una entusiasta y otra más técnica), salvo que el usuario ya haya indicado el tono. Cada una cumple las reglas fijas.

## 4. Generar la imagen

Elige para la imagen un **título corto y con punch** (idealmente 3 a 8 palabras). No tiene que ser el nombre oficial: "Despliega tu primera web en la nube" funciona mejor que "Taller introductorio de Amazon S3". La última línea del título se resalta en naranja, así que conviene terminar con las palabras más importantes.

Ejecuta el script con los datos recopilados:

    python .claude/skills/publicaciones-aws-sbg/crear_post.py --titulo "..." --fecha "..." --lugar "..." --tipo anuncio

- `--tipo`: `anuncio`, `resultado`, `taller` o `tutorial`. Define la etiqueta de la imagen y su estilo visual.
- `--estilo` (opcional): `orbitas`, `circuito`, `bloques` o `terminal`, para usar otro estilo distinto al del tipo. Las decoraciones cambian en cada ejecución; si al usuario no le gusta el resultado, vuelve a ejecutarlo o prueba otro estilo.
- En un tutorial o un post sin lugar físico, usa algo como "Online, enlace en la bio" en `--lugar`.

La imagen se genera de 1080 × 1440 píxeles (formato 3:4) en la carpeta `salida/`, con un nombre que incluye la fecha y hora de creación.

## 5. Entregar el resultado

Muestra al usuario la ruta de la imagen y el texto de la publicación, listos para copiar.
