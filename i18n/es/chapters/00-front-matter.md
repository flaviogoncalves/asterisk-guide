```{=latex}
\frontmatter
```

## Copyright {.unnumbered}

*Asterisk Guide* — Segunda edición (Asterisk 22 LTS)

Copyright © 2006–2026 Flavio E. Gonçalves. Todos los derechos reservados.

Ninguna parte de este libro puede ser reproducida, almacenada en un sistema de recuperación o transmitida en cualquier forma o por cualquier medio sin el consentimiento previo por escrito del autor, excepto para breves extractos utilizados en reseñas publicadas.

**Edición:** Segunda edición.
**ISBN:** *por asignar.*

> **[author TODO]** Asignar un nuevo ISBN para la segunda edición (no reutilizar el 9781796396973 de la primera edición) y establecer la fecha de publicación antes de la impresión.

Muchas de las designaciones utilizadas por fabricantes y vendedores para distinguir sus productos son reclamadas como marcas comerciales. Cuando esas designaciones aparecen en este libro y el autor tenía conocimiento de una reclamación de marca comercial, se han impreso en mayúsculas o con iniciales en mayúsculas. Asterisk, Digium, IAX y DUNDi son marcas comerciales de Sangoma Technologies (Digium fue adquirida por Sangoma en 2018; Asterisk ahora es patrocinado por Sangoma).

Aunque se han tomado todas las precauciones en la preparación de este libro, el autor no asume ninguna responsabilidad por errores u omisiones, ni por daños resultantes del uso de la información contenida en el mismo.

## Preface {.unnumbered}

Este libro es para cualquier persona que desee aprender a instalar y configurar una PBX (Private Branch Exchange) basada en Asterisk 22 LTS. Asterisk es una plataforma de telefonía de código abierto que conecta VoIP con canales TDM tradicionales.

Esta es la quinta generación de un libro que comenzó como *Asterisk Configuration Guide*. El material surgió del trabajo que realicé para prepararme para la certificación dCAP de Digium en 2006 —la cual aprobé en el primer intento— y desde entonces se ha enseñado a más de mil estudiantes.

El concepto de PBX de código abierto es revolucionario. Durante décadas, la telefonía estuvo dominada por un puñado de empresas que vendían costosos sistemas propietarios. Asterisk devolvió ese poder a manos de los usuarios: funciones que antes eran económicamente inalcanzables —CTI (integración de telefonía informática), IVR (respuesta de voz interactiva), ACD (distribución automática de llamadas), voicemail y mucho más— ahora están disponibles para cualquiera que tenga un equipo con Linux y la disposición para aprender.

Este libro no lo convertirá en un gurú por sí solo —ningún libro puede hacerlo—, pero al finalizarlo será capaz de construir y operar una PBX real con funciones avanzadas. El libro tiene un complemento —laboratorios prácticos y un curso en línea— en **VoIP School Blackbelt** (<https://voip.school>).

## Audience {.unnumbered}

Este libro está dirigido a lectores que son nuevos en Asterisk. Asumo que se siente cómodo con Linux: la shell, un editor de texto y la administración básica del sistema. Puede seguir los ejercicios en un escritorio Linux si le resulta más fácil mientras aprende, y una máquina virtual es adecuada para los laboratorios (espere una calidad de voz ligeramente inferior). Para sistemas de producción, no recomiendo ejecutar Asterisk en un entorno de escritorio o dentro de una máquina virtual con pocos recursos. Tener cierta familiaridad con redes IP, Voice over IP (VoIP) y conceptos básicos de telefonía será de ayuda.

## What's new in the second edition {.unnumbered}

La segunda edición es una modernización completa para **Asterisk 22 LTS** (lanzada en 2024, con soporte hasta octubre de 2028). Los cambios principales son:

- **PJSIP es el único canal SIP.** `chan_sip` fue eliminado en Asterisk 21 y no existe en la versión 22. Cada ejemplo de SIP ahora utiliza PJSIP (`pjsip.conf`); el material heredado de `sip.conf` se mantiene solo como referencia de migración.
- **Administración de Sangoma.** Digium fue adquirida por Sangoma en 2018; el proyecto ahora es desarrollado y patrocinado por Sangoma, y el texto refleja esto en todo su contenido.
- **Tres capítulos nuevos.** *WebRTC with Asterisk* (teléfonos de navegador sobre WSS/DTLS-SRTP), *SIP trunking, DID & the PSTN*, y *Deployment, monitoring & scaling*.
- **Un laboratorio reproducible.** Cada configuración y comando en el libro está verificado contra un laboratorio Docker de Asterisk 22 que usted mismo puede ejecutar.
- **Funciones modernizadas.** ConfBridge reemplaza a la antigua conferencia MeetMe, se introduce ARI junto a AMI/AGI, se cubre PJSIP Realtime (Sorcery), y los capítulos de instalación, seguridad y CDR han sido actualizados.
- **Una nueva estructura.** El libro ahora está organizado en cuatro partes: Fundamentos, Canales y Conectividad, Dialplan y Funciones de Llamada, e Integración y Operaciones.

## About the author {.unnumbered}

Flavio E. Gonçalves nació en 1966 en Brasil. Ha tenido un fuerte interés en las computadoras desde que obtuvo su primera PC en 1983, y obtuvo un título en ingeniería en 1989 con enfoque en diseño y fabricación asistidos por computadora. Es el CEO de SipPulse en Brasil, una empresa dedicada a softswitches, session border controllers y PBXs multi-inquilino.

A lo largo de su carrera ha obtenido una larga lista de certificaciones: Novell MCNE/MCNI, Microsoft MCSE/MCT, Cisco CCSP/CCNP/CCDP y Asterisk dCAP, entre otras. Comenzó a escribir sobre software de código abierto porque cree que la forma estructurada en que las certificaciones enseñaban su material es una excelente manera de aprender, y ha aprovechado más de 25 años de experiencia docente para escribir pensando en cómo aprende la gente realmente, en lugar de hacerlo solo desde un punto de vista técnico.

Flavio es padre de dos hijos y vive en Florianópolis, Brasil —uno de los lugares más hermosos del mundo—, donde pasa su tiempo libre surfeando y navegando.

## Feedback, credits & training {.unnumbered}

Me esfuerzo mucho por encontrar y eliminar errores, pero algunos siempre se escapan. Si encuentra algo incorrecto, por favor hágamelo saber y tomaré medidas al respecto.

Este libro también se utiliza como material de capacitación. Si desea utilizarlo en su propio centro de formación, o tomar el curso en línea y los laboratorios complementarios, visite **VoIP School Blackbelt** en <https://voip.school> o envíe un correo electrónico a <flavio@voip.school>.

**Créditos.** Diseño de portada: Karla Braga. Revisores: Luis F. Gonçalves, Guilherme Goes (dCAP) y correctores profesionales. Mi agradecimiento también a los muchos estudiantes cuyos comentarios a lo largo de los años han dado forma a este material, y a mi familia por su apoyo.

```{=latex}
\cleardoublepage
```
