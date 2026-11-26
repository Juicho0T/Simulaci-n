# Proyecto: publicaciones del AWS Student Builder Group (ITD)

Este repositorio se usa para diseñar publicaciones de Instagram del AWS Student Builder Group del Instituto Tecnológico de Durango (ITD).

## Cómo trabajar aquí

- Responde siempre en **español**, en tono cercano y directo.
- Para cualquier publicación (post, carrusel, historia o caption) usa el skill **`publicaciones-aws-sbg`** (`.claude/skills/publicaciones-aws-sbg/SKILL.md`). Ahí está la identidad visual, los estilos aprobados y rechazados, las plantillas y las comprobaciones obligatorias.
- Requisito: Python 3 con Pillow → `pip install -r requirements.txt`.

## Preferencias del usuario

- Paleta por defecto: fondo oscuro `#151C26` + morado `#AE5CFF`, con el chip morado del grupo (`assets/logo.png`). Solo usa otros colores si lo pide para esa publicación.
- Estilo favorito: **editorial oscuro** (titulares serif o Inter Display con la segunda línea en morado, fotos grandes y completas, cuadrícula sutil).
- Manda las fotos de 5 en 5: cuéntalas en cada envío y espera a que diga **"listo"** antes de diseñar.
- Cambios puntuales: cambia solo lo pedido y reenvía solo las slides afectadas.
- Siempre revisa visualmente las imágenes antes de entregarlas y envíaselas.

## Carpetas

- `fotos/<evento>/` — fotos de cada evento (no se suben a git: tienen personas).
- `salida/` — imágenes generadas (los `.png` no se suben a git).
- `.claude/skills/publicaciones-aws-sbg/` — skill, scripts, plantillas, logos y fuentes.

## Git

- No hagas commit de fotos de eventos ni de imágenes generadas.
- Haz commit solo cuando el usuario lo pida.
