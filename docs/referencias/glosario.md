# Glosario de Silente

> Vocabulario de producto: cómo llamamos a cada cosa en la app, en los manuales, en el libro de Silente y en los textos legales. Decisión del usuario del 2026-09-30 (ROADMAP P-14).

## Regla general

Cada concepto tiene **un solo nombre**, y ese nombre se usa siempre igual en la interfaz (`lib/l10n/app_es.arb`), en los manuales, en el libro de Silente (`tool/silente_book/`) y en los textos legales (`assets/legal/`). Si aparece un concepto nuevo, se añade aquí antes de escribir los textos.

## Términos

| Concepto | Término | Ejemplos en la app | Evitar |
|---|---|---|---|
| El espacio donde se guarda lo que escribes sobre tus libros | **Diario** (el de un libro: **Diario del libro**) | Pestaña «Diario», «Diario del libro», «Proteger mi diario» | Bitácora, notas, «Ver diario» |
| Cada texto que escribes | **reflexión** | «Escribir una reflexión», «Añadir reflexión», «Guardar reflexión», «Borrar todas las reflexiones» | entrada, nota, apunte, «Borrar diario» |
| Texto breve asociado a un marcador | **nota** (del marcador) | «Añadir nota», «Editar nota» | reflexión |
| Poner un libro en Silente | **añadir** (un libro) | «Añadir un libro», «Añadir mi primer libro», «Añadiendo libro…» | importar (un libro) |
| El archivo con todos tus datos | **copia** (se **exporta** y se **importa**) | «Exportar mis datos», «Importar una copia», «Crear copia» | respaldo, backup |
| Donde están tus libros | **Biblioteca** | Pestaña «Biblioteca», «Mis libros» | estantería |
| Guardar una página | **marcador** | «Índice y marcadores» | favorito |
| Dónde vas en un libro | **progreso** (… % leído) | «16 % leído», «Continuar leyendo» | avance |
| La versión ampliada | **Silente+** | «Diario+», «Silente+» | premium, pro |

## Notas

- «Diario» también nombra el conjunto de tus reflexiones cuando se habla de tus datos en general («tus libros y tu diario»). Las **acciones** siempre hablan de reflexiones: añadir, guardar, eliminar o borrar reflexiones.
- En el código se mantienen los identificadores en inglés (`journal`, `JournalEntry`, `backup`, `import`). Este glosario solo rige los textos que ve la persona.
- `docs/spec.md` (en inglés) usa *journal*, *entry* e *import*; sus ejemplos de texto en español se sustituyen por los términos de este glosario.
