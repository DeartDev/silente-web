# Plan de monetización de Silente

- **Estado:** Propuesta para validar con el usuario. **No se implementan pagos en el MVP** (spec §3 y §25).
- **Fase del ROADMAP:** F8 (planificación); la implementación es posterior al MVP (ROADMAP §15).
- **Última actualización:** 2026-10-01

## Objetivo

Definir cómo podría financiarse Silente **sin traicionar lo que la hace distinta**:
- es local-first;
- no tiene anuncios ni seguimiento;
- nunca vende datos;
- el diario es privado.

Este documento sirve para decidir antes de escribir código. No compromete precios ni fechas.

## Principios (no negociables)

1. **Sin publicidad y sin SDK de terceros que rastreen.** Esto excluye los anuncios recompensados y los «modelos híbridos» con anuncios.
2. **Nunca vender ni compartir datos**, tampoco agregados ni «anónimos». La política de privacidad lo dice y seguirá siendo cierto.
3. **El diario es de la persona.** Nada de lo que escribió queda bloqueado detrás de un pago: siempre puede leerlo, exportar su copia y borrarlo. Lo mismo vale para sus libros y su progreso.
4. **Lo gratuito es útil por sí mismo** (spec §25: «The free MVP must remain useful without these features»). Silente+ añade; no recorta lo que ya existe.
5. **Sin patrones oscuros:**
   - nada de muros de pago a mitad de lectura;
   - nada de cuentas atrás falsas;
   - la suscripción se cancela tan fácil como se contrata.
6. **Pagar no abre la red sin aviso.** Las funciones sin red (temas, fuentes, organización) se desbloquean sin enviar nada. Solo la sincronización usa red, y la persona la activa de forma explícita.

## Qué es siempre gratis

Todo lo que hace hoy el MVP, sin límites artificiales:

| Área | Gratis para siempre |
|---|---|
| Biblioteca | Añadir EPUB sin límite de libros, portadas, estados de lectura y orden básico |
| Lector | Todos los modos de desplazamiento, incluida la animación de pasar página; temas claro, oscuro y sepia; fuentes incluidas; marcadores, índice y reanudación exacta |
| Diario | Reflexiones sin límite, Diario del libro, Diario global y «Proteger mi diario» |
| Datos | Exportar e importar la copia cifrada; borrar todo |
| Privacidad | Sin cuenta, sin red y sin anuncios |

**Regla para el futuro:** una función que ya es gratis **no pasa** a Silente+.

## Qué ofrece Silente+

Se modela como **entitlements** (arquitectura §45), no como un `isPremium` repartido por el código:

| Entitlement | Contenido (spec §25) | ¿Necesita red? | Coste recurrente para NordirWork |
|---|---|---|---|
| `advancedJournal` (Diario+) | Búsqueda y filtros avanzados, exportar a Markdown y PDF | No | Ninguno |
| `unlimitedCollections` (Biblioteca+) | Etiquetas, colecciones y más formas de ordenar | No | Ninguno |
| `advancedCustomization` (Personalización+) | Más temas, más fuentes y más opciones de lectura | No | Ninguno |
| `cloudSync` (Sincronización) | Progreso, marcadores, diario y biblioteca en varios dispositivos | **Sí** | Servidores, almacenamiento y soporte |

Diseño previsto:

```text
EntitlementService (domain)          ← la UI pregunta por capacidades
  ├── LocalEntitlementStore           ← estado verificado, sin red al consultar
  └── PlayBillingEntitlementSource    ← compra y restauración (data)
```

La pantalla actual de Silente+ ya muestra estos cuatro bloques con el aviso «No hay pagos ni suscripciones en esta versión».

## Opciones de modelo

| Opción | Cómo funciona | A favor | En contra |
|---|---|---|---|
| **A. Compra única «Silente+ local»** | Un pago desbloquea para siempre Diario+, Biblioteca+ y Personalización+ | Coherente con local-first: lo que no cuesta mantener no se alquila. Sencillo de explicar | Ingreso puntual; no financia servidores |
| **B. Suscripción a la sincronización** | Mensual o anual, solo para `cloudSync` | El precio sigue al coste real (servidores); cancelar no quita nada local | Requiere backend, cuenta y un modelo de amenazas nuevo (ROADMAP §15) |
| **C. Suscripción única a todo** | Todo Silente+ por suscripción | Ingreso recurrente máximo | Alquilar funciones locales choca con los principios 3 y 4, y genera rechazo |
| **D. Donación** («Apoya Silente») | Compra opcional sin contenido a cambio | Cero fricción ética | Ingreso imprevisible; Play exige que el contenido digital se cobre con su facturación |

### Recomendación

**A + B, en dos etapas:**

1. **Primera etapa (sin backend):**
   - compra única de Silente+ local (opción A), cuando existan al menos dos de los tres bloques locales;
   - opcionalmente, la donación (D) como compra integrada.
2. **Segunda etapa (con backend):** suscripción **solo** a la sincronización (opción B). Se activa de forma explícita, se explica qué viaja (cifrado de extremo a extremo como objetivo) y, al cancelar, todo sigue en el teléfono.

Se descarta la opción C.

## Precios orientativos

Son solo para dimensionar; se revisarán con el mercado y con los impuestos de cada país. Play permite precios locales por país.

| Producto | Rango orientativo (USD) |
|---|---|
| Silente+ local (compra única) | 4,99 – 9,99 |
| Sincronización (suscripción) | 1,49 – 2,99 al mes, o 14,99 – 24,99 al año |
| Donación | 1,99 / 4,99 / 9,99 |

Comisiones de Google Play consultadas el 2026-10-01:
- **suscripciones:** 15 %;
- **resto de compras:** 15 % sobre el primer millón de USD anual (más un 5 % de facturación en algunas regiones tras el cambio de tarifas: Australia, EEE, Japón, Reino Unido y EE. UU.).

Hay que revisarlas antes de fijar precios.

## Impacto en privacidad y seguridad

| Tema | Impacto | Control |
|---|---|---|
| **Biblioteca de facturación de Play** | Añade el permiso `com.android.vending.BILLING` y habla con la app de Play Store. Es la **primera excepción** a «sin permisos» | ADR propio; actualizar `tool/check_apk_manifest.py` con una lista blanca explícita; ⚪ verificar que la app sigue sin el permiso `INTERNET` (la red la gestiona Play Store) |
| **Comprobar compras** | Sin backend, la verificación es local (Play la cachea). Con backend, se valida en el servidor | No guardar tokens de compra en logs (`AppLogger`); tratarlos como secretos |
| **Seguridad de los datos (Play)** | Una compra **no** obliga a declarar recogida de datos por parte de Silente; la sincronización **sí** | Rehacer el formulario y la política de privacidad **antes** de publicar la versión con sincronización |
| **Sin puertas traseras** | Nada de «modo pro» por flag, código secreto o configuración remota | El entitlement solo se concede con una compra verificada; un test comprueba que en release no hay otra vía |
| **Cuenta** | La compra única no necesita cuenta de Silente (se restaura con la cuenta de Google) | La cuenta llega solo con la sincronización |

## Requisitos de Google Play Billing

- El contenido digital que se desbloquea dentro de la app debe cobrarse con **Google Play Billing**.
- Desde el 31 de agosto de 2026, las apps nuevas y las actualizaciones deben usar la **biblioteca de facturación 8 o posterior**, con extensión posible hasta el 1 de noviembre de 2026. Cada versión tiene dos años de ciclo de obsolescencia.
- Cuenta de comerciante (pagos) vinculada a la cuenta de desarrollador, con datos fiscales.
- Hay que ofrecer **restaurar compras** y gestionar los reembolsos y las revocaciones: si Play revoca, el entitlement se retira, pero los datos no se tocan.
- La integración en Flutter se elegirá con el checklist de dependencias (ROADMAP §8.3). El candidato natural es el plugin oficial `in_app_purchase`.

## Decisiones pendientes (usuario)

| ID | Pregunta | Recomendación |
|---|---|---|
| M-01 | ¿Modelo A + B en dos etapas? | Sí |
| M-02 | ¿Incluir donación en la primera etapa? | Opcional; solo si no confunde con Silente+ |
| M-03 | ¿Cuándo empezar? | Después de publicar el MVP gratuito y validar su uso |
| M-04 | ¿Tipo de cuenta de Play (personal u organización)? | Organización ([guía de publicación](../guias/publicacion-play-store.md)) |

## Fuera de alcance

- Implementar cualquier pago en el MVP.
- Publicidad, venta de datos, ofertas de terceros y tienda de libros (spec §3).
