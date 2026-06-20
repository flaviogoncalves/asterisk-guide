# Introducción a Asterisk PBX

La popularidad de distribuciones listas‑para‑usar como FreePBX e Issabel ha crecido recientemente. En este libro, cubriremos el Asterisk clásico, que es la base para entender estas distribuciones. Asterisk PBX es un software de código abierto capaz de transformar una PC ordinaria en una potente PBX multiprotocolo. En este capítulo, aprenderemos sobre las posibilidades de esta nueva tecnología y su arquitectura básica.

## Objectives

Al final de este capítulo deberías ser capaz de:

- Explicar qué es Asterisk y qué hace;
- Describir el papel de Digium™ y su sucesor Sangoma;
- Reconocer la arquitectura básica de Asterisk y sus componentes;
- Señalar varios escenarios de uso; y
- Identificar fuentes de información y ayuda.

## Qué es Asterisk

Asterisk es un software PBX de código abierto que convierte una computadora ordinaria en una PBX con todas las funciones para usuarios domésticos, empresas, proveedores de servicios VoIP y compañías telefónicas. Asterisk también es una comunidad de código abierto y un proyecto patrocinado por Sangoma Technologies (que adquirió Digium en 2018). Usted es libre de usar y modificar Asterisk para adaptarlo a sus necesidades. Asterisk permite la conectividad en tiempo real entre redes PSTN y VoIP. Dado que Asterisk es mucho más que una PBX, no solo obtiene una mejora excepcional para su PBX existente, sino que también puede hacer cosas nuevas en telefonía, como:

- Conectar a empleados que trabajan desde casa a una PBX de oficina a través de Internet de banda ancha;
- Conectar varias oficinas en diferentes lugares mediante una red IP, una red privada o incluso a través de Internet mismo;
- Proveer a sus empleados un buzón de voz integrado con la web y el correo electrónico;
- Construir aplicaciones como IVR que permitan conexiones a su sistema de pedidos u otras aplicaciones;
- Dar a los usuarios viajeros acceso a la PBX de la empresa desde cualquier lugar con una simple conexión de banda ancha o VPN; y
- mucho más....

Asterisk incluye varios recursos avanzados que antes solo se encontraban en sistemas de alta gama, tales como:

- Música para clientes en espera en colas de llamadas, con soporte para transmisión de medios y archivos MP3;
- Colas de llamadas, mediante las cuales un equipo de agentes puede contestar llamadas y monitorear colas;
- Integración con texto a voz y reconocimiento de voz;
- Registros detallados transferidos tanto a archivos de texto como a bases de datos SQL; y
- Conectividad PSTN a través de líneas digitales y analógicas.

## ¿Qué es AsteriskNOW (Histórico) y FreePBX

Asterisk en su forma más pura, también conocido como “classic asterisk” (denominación del paquete Debian) se considera más una herramienta de desarrollo que un producto terminado por sí mismo. AsteriskNOW fue una iniciativa para transformar Asterisk en un soft‑appliance. La distribución incluía CentOS como sistema operativo y FreePBX como la interfaz gráfica. AsteriskNOW ha sido descontinuado.

Hoy, la distribución estándar llave en mano de Asterisk es **FreePBX** (mantenida por Sangoma), que empaqueta Asterisk con una GUI de administración basada en web y un ecosistema de módulos. FreePBX está licenciado bajo la GPL y puede descargarse libremente desde www.freepbx.org. Para implementaciones comerciales, Sangoma también ofrece **FreePBX Distro** (una imagen Linux completa) y su producto comercial **PBXact**.

## Rol de Digium™ y Sangoma

Digium, una empresa ubicada en Huntsville, Alabama, fue la creadora y desarrolladora principal de Asterisk desde su fundación en 1999. Además de ser el patrocinador principal del desarrollo de Asterisk, Digium produjo tarjetas de interfaz telefónica y otro hardware para PBX Asterisk, y creó productos comerciales como Switchvox (dirigido al mercado de PyMEs). En 2018, Digium fue adquirida por **Sangoma Technologies**, una empresa canadiense de comunicaciones unificadas. Desde la adquisición, Sangoma ha continuado patrocinando el desarrollo de Asterisk y actúa como su principal responsable, manteniendo el proyecto de código abierto en www.asterisk.org.

Históricamente, Digium ofrecía Asterisk bajo tres tipos de acuerdos de licencia:

- General Public License (GPL) Asterisk. Esta es la versión más utilizada. Incluye todas las funciones y es libre de usar y modificar según los términos de la licencia GPL.
- Asterisk Business Edition era una versión comercial de Asterisk. Algunas empresas usaban la edición business porque no querían o no podían usar la licencia GPL—usualmente porque no deseaban publicar su código fuente junto con Asterisk. **Nota:** Asterisk Business Edition ha sido descontinuada; hoy Asterisk se distribuye únicamente bajo la GPL.
- Licenciamiento Asterisk OEM. Después de que Digium dejó de vender Asterisk Business Edition al por menor, continuó licenciando esa edición comercial a clientes OEM —proveedores de equipos que querían construir productos propietarios sobre Asterisk sin publicar su propio código fuente bajo la GPL.

### El proyecto Zapata y su relación con Asterisk

El proyecto Zapata fue desarrollado por Jim Dixon, quien también fue responsable del diseño revolucionario de hardware usado con Asterisk. El hardware también es de código abierto; como tal, puede ser usado por cualquier empresa, y hoy varios fabricantes producen tarjetas compatibles con esta arquitectura.

El proyecto Zapata produjo una arquitectura llamada Zaptel, luego renombrada DAHDI (Digium/Asterisk Hardware Device Interface). Uno de los principales beneficios de esta arquitectura es la capacidad de usar la CPU del PC para procesar la transmisión de medios, cancelación de eco y transcodificación. En contraste, la mayoría de las tarjetas existentes usan procesadores de señal digital (DSP) para realizar estas tareas. El uso de la CPU del PC en lugar de DSP dedicados reduce drásticamente el precio de la placa. Así, estas tarjetas son significativamente más baratas que las interfaces previamente disponibles de otros fabricantes. Por otro lado, estas tarjetas requieren mucha CPU; un uso inadecuado de la CPU del PC puede afectar notablemente la calidad de voz. Recientemente, Digium lanzó una tarjeta coprocesadora que usa DSP para codificar y decodificar G.729 y G.723, permitiendo mejor escalabilidad para un gran número de canales.

## ¿Por qué Asterisk?

Recuerdo mi primer contacto con Asterisk. Por lo general, la primera reacción ante algo nuevo—especialmente algo que compite con lo que ya conoces—es rechazarlo. ¡Exactamente eso fue lo que ocurrió en 2003! Asterisk competía con una solución que estaba vendiendo a un cliente (4 E1 VoIP Gateway), y era diez veces menos costosa que lo que estaba cobrando por la solución que ya conocía. Ese precio desproporcionado me llevó a comenzar a estudiar Asterisk para identificar posibles trampas y desventajas. Por ejemplo, descubrí que la CPU de la PC en ese momento no soportaba 120 sesiones simultáneas de g.729; al final del día, gané la propuesta con mi solución de Gateway.

Sin embargo, este ejercicio me llevó al descubrimiento de que Asterisk podía resolver una variedad de problemas muy costosos para mi base de clientes. Teníamos problemas con cotizaciones caras para IVR, mensajería unificada, grabación de llamadas y marcadores automáticos; con un dimensionamiento adecuado, los problemas de CPU podían mitigarse. De hecho, en solo tres años Asterisk se convirtió en el producto estrella de mi empresa (incluso decidí abrir otra compañía solo para el negocio de Asterisk). En mi opinión, Asterisk es una revolución en telecomunicaciones que representa a la telefonía IP lo que Apache representa a los servicios web.

### Reducción extrema de costos

Si comparas una PBX tradicional con Asterisk en cuanto a interfaces digitales y teléfonos, Asterisk es ligeramente más barato que esas PBX. Sin embargo, Asterisk realmente se paga cuando añades funciones avanzadas como buzón de voz, ACD, IVR y CTI. Con estas funciones avanzadas, Asterisk se vuelve significativamente menos costoso que las PBX tradicionales. De hecho, comparar PBX de Asterisk con PBX analógicas de bajo costo es injusto porque Asterisk ofrece tantas funciones que no están disponibles en los sistemas analógicos de bajo nivel.

### Control del sistema telefónico e independencia

Uno de los beneficios más citados por los clientes de Asterisk es la independencia que brinda. Algunos fabricantes actuales ni siquiera entregan al cliente la contraseña del sistema o la documentación de configuración. Con el enfoque “hazlo tú mismo” de Asterisk, el usuario logra total libertad; como bono, el usuario tiene acceso a una interfaz estándar.

### Entorno de desarrollo fácil y rápido

Asterisk puede extenderse usando lenguajes de script como PHP y Perl con interfaces AMI y AGI. Asterisk es de código abierto, y su código fuente puede ser modificado por el usuario. El código fuente está escrito mayormente en lenguaje de programación ANSI C.

### Rico en funciones

Asterisk tiene varias funciones que no se encuentran o son opcionales en PBX tradicionales (p. ej., buzón de voz, CTI, ACD, IVR, música en espera incorporada y grabación). Los costos de estas funciones en algunas plataformas superan el precio de la propia plataforma.

### Contenido dinámico en el teléfono

Asterisk está programado usando lenguaje C y otros lenguajes comunes en el entorno de desarrollo actual. La posibilidad de proporcionar contenido dinámico es prácticamente ilimitada.

### Plan de marcación flexible y potente

Otro avance de Asterisk es su potente plan de marcación. En PBX tradicionales, incluso funciones simples como enrutamiento de menor costo (LCR) son inviables o opcionales. Con Asterisk, elegir la mejor ruta es fácil y limpio.

### Código abierto ejecutándose sobre Linux

Una de las mayores virtudes de Asterisk es su comunidad. Hay varios recursos disponibles, incluyendo la documentación oficial de Asterisk (docs.asterisk.org), la wiki comunitaria VoIP-Info (www.voip-info.org <http://www.voip-info.org>), listas de distribución por correo electrónico y foros. A medida que Asterisk se adopta cada vez más, los errores se encuentran y corrigen rápidamente. Con una gran base de usuarios y un equipo de desarrollo activo, Asterisk está entre las plataformas PBX más ampliamente probadas en el mundo, lo que ayuda a mantener la base de código estable y madura.

### Limitaciones de la arquitectura de Asterisk

Algunas limitaciones en Asterisk provienen del uso del diseño telefónico Zapata. En este diseño, Asterisk usa la CPU de la PC para procesar canales de voz en lugar de procesadores de señal digital dedicados (DSP), que son comunes en otras plataformas. Aunque esto permite una enorme reducción de costos en la interfaz de hardware, el sistema se vuelve dependiente de la CPU de la PC. Mi recomendación es ejecutar Asterisk en una máquina dedicada y ser conserv

## Objeciones principales al PBX Asterisk

Es común escuchar objeciones a la adopción de Asterisk, que abordaremos aquí.

### La cuota de mercado de Asterisk es demasiado pequeña

La cuota de mercado suele medirse por el número de PBX vendidos. Estas estadísticas se obtienen generalmente de los distribuidores más grandes. Asterisk es software libre que puede descargarse e implementarse sin que se registre ninguna venta, por lo que se contabiliza sistemáticamente por debajo en esas cifras. Aun así, Asterisk impulsa una base instalada muy grande a nivel mundial —desde PBX de oficina de un solo servidor hasta despliegues de grandes operadores y centros de contacto— y sigue siendo el motor dominante detrás del ecosistema de PBX de código abierto (incluyendo distribuciones llave en mano como FreePBX).

### Si es gratuito, ¿cómo sobrevive el fabricante?

En realidad, no existe tal cosa como un fabricante de software de código abierto en el sentido tradicional. Digium desarrolló Asterisk desde 1999, sustentándose mediante la venta de tarjetas de interfaz telefónica, productos comerciales de PBX como Switchvox y software relacionado. En 2018, Sangoma Technologies adquirió Digium. Sangoma continúa financiando el desarrollo de Asterisk y genera ingresos a través de productos comerciales (módulos comerciales de FreePBX, PBXact, Switchvox), ventas de hardware y servicios profesionales.

### ¡Es difícil encontrar soporte técnico!

Sangoma brinda soporte técnico comercial para Asterisk a través de su ecosistema de socios y directamente mediante sus ofertas de productos. Una red global de profesionales certificados proporciona soporte de primera línea y servicios profesionales. El soporte comunitario sigue activo a través de los foros y listas de correo de Asterisk en www.asterisk.org.

### ¿Asterisk soporta más de 200 extensiones?

Sí, absolutamente. Un solo servidor Asterisk bien dimensionado puede manejar un gran número de extensiones, y Asterisk escala aún más distribuyendo usuarios entre varios servidores con balanceo de carga y conmutación por error, lo que permite despliegues multi‑sitio de gran envergadura.

### Sólo los “geeks” pueden instalar Asterisk

Con FreePBX (disponible como una distro independiente de Sangoma), incluso profesionales con conocimientos limitados de Linux pueden instalar y configurar un PBX de complejidad media. Con la ayuda de una GUI, es posible configurar un PBX completo en solo unas pocas horas.

### ¿Qué pasa si el servidor falla?

Una de las principales ventajas de Asterisk es su capacidad para ejecutarse en sistemas tolerantes a fallas. Es relativamente simple y económico tener dos servidores funcionando en paralelo. ¡Te reto a probar esto con un PBX convencional!

### Nuestra empresa no usa software de código abierto

Probablemente su empresa usa software de código abierto sin siquiera darse cuenta. Varios dispositivos utilizan Linux como su sistema operativo. Además, el soporte comercial y los despliegues gestionados están disponibles a través de Sangoma y su red de socios certificados.

### No se recomienda usar la CPU del PC para procesar señalización y medios

Asterisk usa la CPU del servidor para procesar señalización y medios de los canales de voz en lugar de contar con DSP dedicados. Aunque esto permite una reducción de costos de hasta cinco veces, hace que el sistema dependa del rendimiento de la CPU principal. Con el dimensionamiento correcto, Asterisk es capaz de manejar grandes volúmenes. Si aún desea liberar la CPU principal de estas tareas, también puede usar cancelación de eco por hardware e incluso tarjetas transcodificadoras, como la Sangoma (anteriormente Digium) TC400B basada en DSPs.

## Asterisk Architecture

Esta sección explicará cómo funciona la arquitectura de Asterisk. La figura a continuación muestra la arquitectura básica de Asterisk. A continuación, explicaremos conceptos relacionados con la arquitectura, incluidos canales, códecs y aplicaciones.

![The Asterisk architecture](../images/01-introduction-fig01.png)

### Channels

Un canal es el equivalente a una línea telefónica, pero en formato digital. Normalmente consiste en un sistema de señalización analógico o digital (TDM) o en una combinación de códec y protocolo de señalización (p. ej., SIP‑GSM, IAX‑uLaw). Inicialmente, todas las conexiones telefónicas eran analógicas y susceptibles al eco y al ruido. Más tarde, la mayoría de los sistemas se convirtieron a sistemas digitales, con el sonido analógico convertido a formato digital mediante modulación por código de pulsos (PCM) en la mayoría de los casos. Este formato permite la transmisión de voz a 64 kilobits/segundo sin compresión.

Canales que se interconectan con la Public Switched Telephone Network (PSTN):

- `chan_dahdi`: tarjetas TDM analógicas (FXO/FXS) y digitales (E1/T1/PRI) de Sangoma (antes Digium), Xorcom y otras. Construidas por separado contra DAHDI — ver el capítulo *Legacy channels*.

Canales que se interconectan con Voice over IP:

- `chan_pjsip`: SIP — el controlador de canal SIP principal y único en Asterisk 22 LTS. Cadena de marcación: `PJSIP/endpoint_name`. (**Note:** el antiguo `chan_sip` se eliminó en Asterisk 21 y no existe en Asterisk 22. Ver *Building your first PBX with PJSIP* para la configuración.)
- `chan_iax2`: el protocolo IAX2 — todavía incluido en Asterisk 22 pero es legado; se prefiere SIP/PJSIP para nuevas implementaciones. Cadena de marcación: `IAX2/peer`.
- `chan_unistim`: teléfonos Nortel/Avaya UNISTIM. Aún disponible (soporte extendido) pero raramente usado.

Los canales VoIP más antiguos ya no forman parte de una compilación estándar de Asterisk 22: `chan_h323` (H.323) sobrevive solo como el complemento comunitario `ooh323`, y `chan_mgcp` (MGCP) y `chan_skinny` (Cisco SCCP) fueron desaprobados y eliminados del conjunto de canales moderno. Si necesita interoperar con esos protocolos, lo habitual es colocar una pasarela frente a Asterisk.

Canales misceláneos:

- **Local**: un pseudo‑canal (integrado en el núcleo) que vuelve al dialplan en un contexto diferente — útil para enrutamiento recursivo y para distribuir una llamada a múltiples destinos. Cadena de marcación: `Local/extension@context`.

### Codec and codec translation

Normalmente intentamos colocar la mayor cantidad posible de conexiones de voz en una red de datos. Los códecs habilitan nuevas funciones en la voz digital, incluida la compresión, que es una de las características más importantes ya que permite tasas de compresión superiores a 8 a 1. Muchos códecs también definen funciones como detección de actividad de voz (supresión de silencio), ocultación de pérdida de paquetes y generación de ruido de confort, aunque Asterisk mismo no genera ruido de confort ni realiza supresión de silencio. Hay varios códecs disponibles para Asterisk y pueden traducirse de forma transparente de uno a otro. Internamente, Asterisk usa slinear como formato de flujo cuando necesita convertir de un códec a otro. Algunos códecs en Asterisk solo se admiten en modo paso‑a‑paso; esos códecs no pueden traducirse. Para verificar qué códecs están instalados en su sistema, puede usar el comando de consola:

```
CLI>core show translation
```

Los siguientes códecs son compatibles:

- G.711 ulaw (EE. UU.) - (64 Kbps).
- G.711 alaw (Europa) - (64 Kbps).
- G.722 (Alta Definición) – (64 Kbps)
- G.723.1 - Solo modo paso‑a‑paso
- G.726 - (16/24/32/40 kbps)
- G.729 - Módulo de códec binario distribuido por Sangoma; la descarga es gratuita, pero el uso legal requiere la compra de una licencia por canal (8 Kbps)
- GSM - (12‑13 Kbps)
- iLBC - (15 Kbps)
- LPC10 - (2.4 Kbps)
- Speex - (2.15‑44.2 Kbps)
- Opus - (6‑510 Kbps)

### Protocolos

Enviar datos de un teléfono a otro debería ser fácil siempre que los datos encuentren por sí mismos una ruta hacia el otro teléfono. Desafortunadamente, no ocurre así, y se necesita un protocolo de señalización para establecer conexiones entre teléfonos, descubrir dispositivos finales e implementar la señalización de telefonía. SIP es el protocolo de señalización dominante en implementaciones modernas y es el único canal SIP disponible en Asterisk 22 LTS (a través de chan_pjsip). IAX2 sigue estando disponible pero se considera heredado. Asterisk soporta los siguientes protocolos.

- SIP — a través de `chan_pjsip`
- IAX2 — heredado, aún incluido en Asterisk 22
- UNISTIM — teléfonos Nortel/Avaya (soporte extendido)
- H.323, MGCP y SCCP (Cisco Skinny) — protocolos heredados que ya no forman parte de una compilación estándar de Asterisk 22 (H.323 solo a través del complemento comunitario `ooh323`)

### Aplicaciones

Para interconectar llamadas de un teléfono a otro, se utiliza la aplicación dial(). La mayoría de las funciones de Asterisk (p. ej., voicemail y conferencias) están implementadas como aplicaciones. Puedes ver las aplicaciones disponibles de Asterisk usando el comando de consola core show applications.

```
CLI>core show applications
```

Puede agregar aplicaciones de complementos de Asterisk, proveedores externos, o incluso aquellas que desarrolle usted mismo.

## Visión general de un sistema Asterisk

Asterisk es una PBX de código abierto que actúa como una PBX híbrida, integrando tecnologías como TDM y telefonía IP. Asterisk está preparada para implementar funcionalidades como respuesta de voz interactiva (IVR) y distribución automática de llamadas (ACD); además, como se mencionó anteriormente, está abierta al desarrollo de nuevas aplicaciones. Esta figura muestra cómo Asterisk se conecta a la PSTN y a PBX existentes mediante interfaces analógicas y digitales, así como también soporta teléfonos analógicos e IP. Puede actuar como un soft‑switch, pasarela de medios, buzón de voz y conferencia de audio, y también incluye música en espera integrada.

![Visión general de un sistema Asterisk](../images/01-introduction-fig02.png)

## Comparando el mundo antiguo y el nuevo

En el modelo de soft‑switch antiguo, todos los componentes se vendían por separado, lo que significaba que debías adquirir cada componente individualmente y luego integrarlo al entorno PBX o soft‑switch. Los costos y riesgos eran altos y la mayor parte del equipo era propietario.

![The old world: components bought and integrated separately](../images/01-introduction-fig03.png)

### Telefonía usando Asterisk

Todas las funciones están integradas en la plataforma Asterisk en la misma o en diferentes cajas según el dimensionamiento, y todas están bajo licencia GPL. A veces es más fácil instalar Asterisk que licenciar algunos de los IP‑PBX más populares

![Telephony using Asterisk: the functions are integrated](../images/01-introduction-fig04.png)

## Construyendo un sistema de pruebas

Al implementar una solución Asterisk, nuestro primer paso suele ser construir un sistema de pruebas. El objetivo es un **PBX 1×1** mínimo — un teléfono que pueda llamar a otro — para que puedas probar endpoints, dialplan y funciones antes de tocar la producción. Hoy en día todo es software: no necesitas ningún hardware de telefonía.

![A simple Asterisk test system](../images/01-introduction-fig05.png)

### La forma moderna: un laboratorio de software (recomendado)

El sistema de pruebas más rápido es Asterisk 22 ejecutándose en un contenedor o máquina virtual, con **softphones** para los endpoints y, opcionalmente, un **SIP trunk** para alcanzar la red pública:

- **Asterisk 22** en una pequeña caja Linux, VM o contenedor Docker. Este libro incluye un laboratorio Docker listo para usar (ver la guía del laboratorio) que arranca un Asterisk 22 totalmente configurado con un solo comando — sin compilación, sin hardware.
- **Dos softphones** registrados como endpoints PJSIP, para que puedas realizar una llamada real entre ellos. A lo largo de este libro usamos el **SipPulse Softphone** (descarga gratuita: <https://www.sippulse.com/produtos/softphone>), disponible para escritorio y móvil.
- **Un SIP trunk** (opcional) de un proveedor VoIP, para cuando quieras alcanzar la PSTN. Sin tarjeta y sin línea analógica — solo credenciales.

Así es como se construye y verifica cada ejemplo en este libro, y puedes reproducirlo en cualquier laptop.

### La forma tradicional: tarjetas analógicas/digitales

Antes del VoIP, un PBX de pruebas necesitaba interfaces físicas: un puerto **FXO** para conectar a una línea telefónica existente y un puerto **FXS** para conectar un teléfono analógico, que juntos te daban un PBX 1×1. Una sola tarjeta que llevaba una interfaz FXO y una FXS era el kit de inicio clásico. Estas tarjetas basadas en DAHDI (de Sangoma, antes Digium) aún existen para sitios que deben terminar líneas analógicas o T1/E1, pero hoy son de nicho — la mayoría de los despliegues son puro VoIP. Si solo necesitas conectar teléfonos o líneas analógicas, consulta el capítulo *Legacy Channels*; de lo contrario puedes omitir completamente el hardware de telefonía.

## Escenarios de Asterisk

Asterisk puede usarse en varios escenarios diferentes. Enumeraremos algunos de ellos y explicaremos las ventajas y posibles limitaciones de cada uno.

### IP PBX

El escenario más común es la instalación de una PBX nueva o el reemplazo de una PBX existente. Si comparas Asterisk con algunas otras alternativas, verás que es más barato y más rico en funciones que la mayoría de las PBX disponibles actualmente en el mercado. Varias empresas están cambiando sus especificaciones a Asterisk en lugar de otras PBX de marca.

![Asterisk as an IP PBX](../images/01-introduction-fig06.png)

### Habilitación IP de PBX heredadas

La siguiente imagen ilustra una de las configuraciones más usadas. Las grandes empresas generalmente no quieren asumir riesgos significativos al invertir en nuevas tecnologías y al mismo tiempo desean preservar sus inversiones en equipos heredados. Habilitar IP en una PBX heredada puede ser muy costoso; por lo tanto, conectar una PBX Asterisk usando líneas T1/E1 puede ser una buena alternativa para clientes sensibles al costo. Otro beneficio es la posibilidad de conectarse a un proveedor de servicios VoIP con tarifas de telefonía más favorables.

![IP-enabling a legacy PBX](../images/01-introduction-fig07.png)

### Bypass de peaje

Una aplicación muy útil para VoIP es conectar sucursales a través de Internet o una WAN. Usar una conexión de datos existente permite eludir los cargos de peaje incurridos en las conexiones de telecomunicaciones entre la sede central y las sucursales.

![Toll bypass between offices over a WAN](../images/01-introduction-fig08.png)

### Servidor de aplicaciones (IVR, Conferencia, Voicemail)

Asterisk puede usarse como servidor de aplicaciones para la PBX existente o estar conectado directamente a la PSTN. Asterisk ofrece servicios como voicemail, recepción de fax, grabación de llamadas, IVR conectado a una base de datos y un servidor de conferencias de audio. Si integras voicemail y fax en un servidor de correo electrónico existente, tendrás un sistema de mensajería unificado, que suele ser una solución costosa. Usar Asterisk como servidor de aplicaciones brinda una reducción de costos extrema comparada con otras soluciones.

![Asterisk as an application server](../images/01-introduction-fig09.png)

### Pasarela de medios

La mayoría de los proveedores de servicios de voz sobre IP usan un proxy SIP para alojar todo el registro, ubicación y autenticación de usuarios SIP. Aún deben enviar llamadas a la PSTN directamente o enrutarla a través de un proveedor mayorista de terminación de llamadas usando una conexión SIP o H.323 de voz sobre IP. Asterisk puede actuar como un agente de usuario back-to-back (B2BUA) o como pasarela de medios, reemplazando soft switches o pasarelas de medios muy costosos. Compara el precio de una pasarela de cuatro E1/T1 de los principales fabricantes del mercado con Asterisk. La solución Asterisk puede costar varias veces menos que otras soluciones y es capaz de traducir protocolos de señalización (H.323, SIP, IAX…) y códecs (G.711, G.729…).

![Asterisk as a media gateway](../images/01-introduction-fig10.png)

### Plataforma de centro de contacto

Un centro de contacto es una solución muy compleja que combina varias tecnologías, como distribución automática de llamadas (ACD), respuesta interactiva de voz (IVR) y supervisión de llamadas. Básicamente, hay tres tipos de centros de contacto disponibles: entrante, saliente y mixto.

Los centros de contacto entrantes son muy sofisticados y usualmente requieren ACD, IVR, CTI, grabación, supervisión e informes. Asterisk tiene un ACD incorporado para encolar las llamadas. El IVR puede implementarse usando Asterisk Gateway Interface (AGI) o mecanismos internos como la aplicación background(). La integración de telefonía informática (CTI) se logra usando Asterisk Manager Interface (AMI); la grabación y los informes están integrados en Asterisk.

Para un centro de contacto saliente, un marcador predictivo o de potencia es uno de los componentes principales. Aunque hay varios marcadores disponibles para el Asterisk de código abierto, no es difícil crear el propio para la plataforma si lo deseas. Un centro de contacto mixto permite operación simultánea entrante y saliente, ahorrando dinero al asegurar un mejor uso del tiempo del agente. Es posible usar Asterisk y su mecanismo ACD para implementar una solución mixta.

![An Asterisk contact-center platform](../images/01-introduction-fig11.png)

## Encontrar información y ayuda

Esta sección proporcionará algunas de las principales fuentes de información relacionadas con Asterisk.

- Sitio web oficial de Asterisk: <https://www.asterisk.org> Aquí puedes encontrar información sobre:
- Documentación y Wiki -> <https://docs.asterisk.org>
- Foro de la comunidad -> <https://community.asterisk.org>
- Seguimiento de errores -> <https://github.com/asterisk/asterisk/issues>
- Wiki (heredada, en gran parte reemplazada por docs.asterisk.org) -> <https://wiki.asterisk.org>

### Foro de la comunidad

El foro de la comunidad de Asterisk ha reemplazado en gran medida a las antiguas listas de correo y es el lugar para hacer preguntas. Trata de reunir la mayor cantidad de información posible antes de publicar. Nadie te ayudará si no has hecho tu tarea — intenta al menos una vez resolver el problema por tu cuenta.

- <https://community.asterisk.org>

## Resumen

Asterisk es un software licenciado bajo la GPL que permite que una PC ordinaria actúe como una potente plataforma IP PBX. Mark Spencer de Digium creó Asterisk a finales de la década de 1990, y Digium se mantuvo vendiendo hardware relacionado con Asterisk y productos comerciales. Digium fue adquirida por Sangoma Technologies en 2018; Sangoma ahora patrocina el desarrollo de Asterisk. El diseño de la interfaz de hardware se originó en el proyecto Zapata desarrollado por Jim Dixon, que dio origen a DAHDI.

La arquitectura de Asterisk tiene los siguientes componentes principales:

- CHANNELS: Analógico, digital o voz sobre IP. En Asterisk 22 LTS, SIP es manejado exclusivamente por `chan_pjsip`.
- PROTOCOLS: Protocolos de comunicación, que son responsables de señalizar las llamadas, incluyendo SIP (a través de PJSIP), H.323, MGCP e IAX2.
- CODECS: Traducen formatos digitales de voz permitiendo compresión y ocultación de pérdida de paquetes. Tenga en cuenta que el propio Asterisk no realiza supresión de silencio (detección de actividad de voz) ni generación de ruido de confort; cuando los endpoints usan VAD, el ruido de confort debe desactivarse en el lado del cliente.
- APPLICATIONS: Responsables de la funcionalidad del PBX de Asterisk. Conferencia, buzón de voz y fax son ejemplos de aplicaciones de Asterisk.

Asterisk puede usarse en varios escenarios, desde una pequeña IP PBX hasta un centro de contacto sofisticado. Puede encontrar ayuda fácilmente en www.asterisk.org y docs.asterisk.org.

## Quiz

1. ¿Qué empresa adquirió Digium en 2018 y ahora actúa como el principal responsable del proyecto de código abierto Asterisk?
   - A. Cisco Systems
   - B. Sangoma Technologies
   - C. Nortel Networks
   - D. Red Hat

2. En Asterisk 22 LTS, ¿qué controlador de canal proporciona conectividad SIP?
   - A. `chan_sip`
   - B. `chan_skinny`
   - C. `chan_pjsip`
   - D. `chan_h323`

3. Verdadero o Falso: El controlador de canal `chan_sip` fue eliminado en Asterisk 21 y no está presente en una compilación estándar de Asterisk 22.

4. ¿Cuál de los siguientes canales/protocolos **ya no** forman parte de una compilación estándar de Asterisk 22? (Elija todas las que correspondan.)
   - A. MGCP (`chan_mgcp`)
   - B. SCCP / Cisco Skinny (`chan_skinny`)
   - C. IAX2 (`chan_iax2`)
   - D. H.323 (`chan_h323`, sobreviviendo solo como el complemento comunitario `ooh323`)

5. La arquitectura de hardware del proyecto Zapata, originalmente llamada Zaptel, fue renombrada posteriormente a ____.
   - A. DAHDI
   - B. PJSIP
   - C. PRI
   - D. mISDN

6. Cuando Asterisk debe convertir audio de un códec a otro, ¿a través de qué formato interno de flujo traduce?
   - A. G.711 ulaw
   - B. GSM
   - C. slinear (signed linear)
   - D. Opus

7. Según el capítulo, ¿cuál es la situación de licenciamiento del módulo de códec G.729 distribuido por Sangoma?
   - A. Es GPL y completamente gratuito para cualquier uso.
   - B. La descarga es gratuita, pero su uso legal requiere la compra de una licencia por canal.
   - C. No se puede obtener en absoluto sin comprar Asterisk Business Edition.
   - D. Solo funciona en modo de paso directo y no puede instalarse.

8. ¿Qué aplicación de Asterisk se usa para conectar una llamada de un teléfono a otro?
   - A. `Background()`
   - B. `Dial()`
   - C. `Queue()`
   - D. `Goto()`

9. ¿Qué es el canal `Local` en Asterisk?
   - A. Una interfaz de hardware FXS para teléfonos analógicos.
   - B. Un trunk SIP a un proveedor de servicios local.
   - C. Un pseudo‑canal que devuelve una llamada al dialplan en un contexto diferente.
   - D. Un códec usado para llamadas dentro de la red.

10. ¿En qué escenario de uso Asterisk actúa como un agente de usuario back‑to‑back (B2BUA), traduciendo entre protocolos de señalización y códecs para reemplazar soft switches costosos?
    - A. Habilitación IP de una PBX heredada
    - B. Bypass de peaje
    - C. Media Gateway
    - D. Plataforma de Contact Center

**Answers:** 1 — B · 2 — C · 3 — True · 4 — A, B, D · 5 — A · 6 — C · 7 — B · 8 — B · 9 — C · 10 — C
