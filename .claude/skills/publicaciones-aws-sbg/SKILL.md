---
name: publicaciones-aws-sbg
description: Crea publicaciones de Instagram para el AWS Student Builder Group, con texto e imagen en formato 3:4. Úsalo cuando el usuario pida una publicación de anuncio de evento, resultado de evento, resumen de taller o tutorial.
---

# Publicaciones AWS Student Builder Group

## Paso 1: Tipo de publicación

Pregunta primero qué tipo de publicación quiere el usuario:
- Anuncio de evento
- Resultado de evento
- Resumen de taller
- Tutorial

## Paso 2: Datos según el tipo

Pide solo los datos que correspondan:
- **Anuncio de evento:** título, fecha, lugar, enlace o forma de registro.
- **Resultado de evento:** título, fecha, lugar, número de asistentes, highlights.
- **Resumen de taller:** tema, fecha, lugar, aprendizajes clave (3 a 5).
- **Tutorial:** tema, pasos numerados (3 a 6), enlace de referencia si existe.

## Paso 3: Texto para Instagram

Escribe el texto de la publicación con:
- Emojis relevantes, sin exagerar.
- Hashtags como #AWS, #StudentBuilderGroup, #AWSCommunity y uno o dos del tema.
- Una llamada a la acción al final (registrarse, seguirnos, comentar, compartir).
- Máximo unas 150 palabras, salvo que el usuario pida más.

## Paso 4: Imagen en formato 3:4

Ejecuta el script `crear_post.py` con los datos recopilados:

    python .claude/skills/publicaciones-aws-sbg/crear_post.py --titulo "..." --fecha "..." --lugar "..."

La imagen debe generarse con:
- Formato 3:4, de **1080 × 1350 píxeles**.
- Guardarse en la carpeta `salida/`.

Al terminar, muestra al usuario la ruta de la imagen y el texto de la publicación, listos para copiar.
