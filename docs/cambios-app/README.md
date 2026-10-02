# Cambios de la app para la web

Notas que llegan desde el repositorio de la app (`DeartDev/silente`) cada vez que hay un avance o una funcionalidad nueva (convención del ROADMAP de la app, §14, 2026-10-02).

**Para qué sirven:** que la landing solo anuncie lo que la app ya hace. Cada nota dice qué cambia para la persona lectora y qué partes de la web habría que tocar. No son un blog ni un *changelog* público: el spec deja eso fuera de alcance (§2).

## Cómo se usan

1. La sesión que trabaja en la app escribe la nota con la [plantilla](_plantilla.md), en `AAAA-MM-DD-<tema>.md`, y abre un PR en este repositorio.
2. Al trabajar en la web, se revisan las notas con estado **⏳ pendiente en la web**.
3. Se aplican los cambios (textos del §5, FAQ, capturas…) solo si la nota dice que la funcionalidad está **disponible** en la versión publicada.
4. La nota se marca como **✅ aplicada en la web**, con el PR que la aplicó, o **— sin impacto**.

## Reglas

- Lenguaje de la persona lectora y [glosario](../referencias/glosario.md): sin tecnicismos.
- Distinguir siempre entre **disponible en Google Play**, **disponible en una build de prueba** y **en desarrollo**. La web solo anuncia lo publicado; lo planificado no se anuncia.
- Nada de datos privados, rutas personales ni contenido con copyright, tampoco en las capturas.

## Notas

| Fecha | Nota | Estado en la web |
|---|---|---|
| 2026-10-02 | [Estado de la app 0.1.0 y plan de formatos](2026-10-02-estado-0.1.0-y-plan-de-formatos.md) | — sin impacto (línea base; no anunciar el PDF) |
