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

- Emojis relevantes, sin exagerar.
- Hashtags #AWS, #StudentBuilderGroup y #AWSCommunity, más uno o dos del tema.
- Una llamada a la acción al final (registrarse, seguirnos, comentar, compartir).
- Máximo unas 150 palabras.

## 4. Generar la imagen

Ejecuta el script con los datos recopilados (en un tutorial o taller, usa el tema como título):

    python .claude/skills/publicaciones-aws-sbg/crear_post.py --titulo "..." --fecha "..." --lugar "..."

Genera una imagen de 1080 × 1440 píxeles (formato 3:4) en la carpeta `salida/`, con un nombre que incluye la fecha y hora de creación.

## 5. Entregar el resultado

Muestra al usuario la ruta de la imagen y el texto de la publicación, listos para copiar.
