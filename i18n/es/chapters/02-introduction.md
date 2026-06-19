# Introducción a Asterisk PBX

La popularidad de las distribuciones listas para usar, como FreePBX e Issabel, ha crecido recientemente. En este libro, cubriremos el Asterisk clásico, que es la base para comprender dichas distribuciones. Asterisk PBX es un software de código abierto capaz de transformar una PC común en una potente PBX multiprotocolo. En este capítulo, aprenderemos sobre las posibilidades de esta nueva tecnología y su arquitectura básica.

## Objetivos

Al finalizar este capítulo, usted debería ser capaz de:

- Explicar qué es Asterisk y qué hace;
- Describir el papel de Digium™ y su sucesor Sangoma;
- Reconocer la arquitectura básica de Asterisk y sus componentes;
- Señalar varios escenarios de uso; y
- Identificar fuentes de información y ayuda.

## Qué es Asterisk

Asterisk es un software de PBX de código abierto que, una vez instalado en el hardware de una PC junto con las interfaces correctas, puede utilizarse como una PBX con todas las funciones para usuarios domésticos, empresas, proveedores de servicios VoIP y compañías telefónicas. Asterisk es también tanto una comunidad de código abierto como un proyecto patrocinado por Sangoma Technologies (que adquirió Digium en 2018). Usted es libre de usar y modificar Asterisk para satisfacer sus necesidades. Asterisk permite la conectividad en tiempo real entre redes PSTN y VoIP. Dado que Asterisk es mucho más que una PBX, no solo tiene una actualización excepcional para su PBX existente, sino que también puede realizar cosas nuevas en telefonía, tales como:

- Conectar a empleados que trabajan desde casa a una PBX de oficina a través de Internet de banda ancha;
- Conectar varias oficinas en diferentes lugares a través de una red IP, red privada o incluso a través de Internet mismo;
- Dar a sus empleados un correo de voz integrado con la web y el correo electrónico;
- Construir aplicaciones como IVRs que permitan conexiones a su sistema de pedidos u otras aplicaciones;
- Dar a los usuarios viajeros acceso a la PBX de la empresa desde cualquier lugar con una simple conexión de banda ancha o VPN; y
- mucho más...

Asterisk incluye varios recursos avanzados que antes solo se encontraban en sistemas de gama alta, tales como:

- Música para clientes en espera en colas de llamadas, con soporte para transmisión de medios y archivos MP3;
- Colas de llamadas, mediante las cuales un equipo de agentes puede responder llamadas y monitorear las colas;
- Integración con texto a voz y reconocimiento de voz;
- Registros detallados transferidos tanto a archivos de texto como a bases de datos SQL; y
- Conectividad PSTN a través de líneas digitales y analógicas.

## Qué es AsteriskNOW (Histórico) y FreePBX

Asterisk en su forma más pura, también conocido como "asterisk clásico" (denominación del paquete de Debian), se considera más una herramienta de desarrollo que un producto terminado por sí mismo. AsteriskNOW fue una iniciativa para transformar Asterisk en un soft-appliance. La distribución incluía CentOS como sistema operativo y FreePBX como interfaz gráfica. AsteriskNOW ha sido descontinuado desde entonces.

Hoy en día, la distribución estándar llave en mano de Asterisk es **FreePBX** (mantenida por Sangoma), que agrupa Asterisk con una GUI de administración basada en web y un ecosistema de módulos. FreePBX tiene licencia bajo la GPL y puede descargarse libremente desde www.freepbx.org. Para implementaciones comerciales, Sangoma también ofrece **FreePBX Distro** (una imagen completa de Linux) y su producto comercial **PBXact**.

## Papel de Digium™ y Sangoma

Digium, una empresa ubicada en Huntsville, Alabama, fue el creador y desarrollador principal de Asterisk desde su fundación en 1999. Además de ser el principal patrocinador del desarrollo de Asterisk, Digium producía tarjetas de interfaz de telefonía y otro hardware para PBX Asterisk, y creó productos comerciales como Switchvox (dirigido al mercado de las PYMES). En 2018, Digium fue adquirida por **Sangoma Technologies**, una empresa canadiense de comunicaciones unificadas. Desde la adquisición, Sangoma ha continuado patrocinando el desarrollo de Asterisk y sirve como su administrador principal, manteniendo el proyecto de código abierto en www.asterisk.org.

Históricamente, Digium ofrecía Asterisk bajo tres tipos de acuerdos de licencia:

- Licencia Pública General (GPL) Asterisk. Esta es la versión más utilizada. Incluye todas las funciones y es gratuita para ser utilizada y modificada de acuerdo con los términos de la licencia GPL.
- Asterisk Business Edition era una versión comercial de Asterisk. Algunas empresas utilizaban la edición empresarial porque no querían o no podían utilizar la licencia GPL, generalmente porque no deseaban publicar su código fuente junto con Asterisk. **Nota:** Asterisk Business Edition ha sido descontinuado; hoy en día Asterisk se distribuye únicamente bajo la GPL.
- Licencia OEM de Asterisk. Después de que Digium dejara de vender Asterisk Business Edition al por menor, continuó licenciando esa edición comercial a clientes OEM: proveedores de equipos que deseaban construir productos propietarios sobre Asterisk sin publicar su propio código fuente bajo la GPL.

### El proyecto Zapata y su relación con Asterisk

El proyecto Zapata fue desarrollado por Jim Dixon, quien también fue responsable del revolucionario diseño de hardware utilizado con Asterisk. El hardware también es de código abierto; como tal, puede ser utilizado por cualquier empresa, y hoy en día varios fabricantes producen tarjetas compatibles con esta arquitectura.

El proyecto Zapata produjo una arquitectura llamada Zaptel, renombrada más tarde como DAHDI (Digium/Asterisk Hardware Device Interface). Uno de los principales beneficios de esta arquitectura es la capacidad de utilizar la CPU de la PC para procesar la transmisión de medios, la cancelación de eco y la transcodificación. Por el contrario, la mayoría de las tarjetas existentes utilizan procesadores de señal digital (DSP) para realizar estas tareas. El uso de la CPU de la PC en lugar de DSP dedicados reduce drásticamente el precio de la placa. Por lo tanto, estas tarjetas son significativamente más baratas que las interfaces disponibles anteriormente de otros fabricantes. Por otro lado, estas tarjetas requieren mucha CPU; un mal uso de la CPU de la PC puede afectar significativamente la calidad de la voz. Recientemente, Digium lanzó una tarjeta coprocesadora que utiliza DSP para codificar y decodificar G.729 y G.723, permitiendo una mejor escalabilidad para un gran número de canales.

## ¿Por qué Asterisk?

Recuerdo mi primer contacto con Asterisk. Por lo general, la primera reacción ante algo nuevo, especialmente algo que compite con lo que ya conoces, ¡es rechazarlo! Esto es exactamente lo que sucedió en 2003. Asterisk estaba compitiendo con una solución que yo estaba vendiendo a un cliente (Gateway VoIP de 4 E1), y era diez veces menos costosa que lo que yo estaba cobrando por la solución que ya conocía. Este precio desproporcionado me llevó a comenzar a estudiar Asterisk para identificar posibles trampas y desventajas. Por ejemplo, descubrí que la CPU de la PC en ese momento no soportaría 120 secciones simultáneas de G.729; al final del día, gané la propuesta con mi solución de Gateway. Sin embargo, este ejercicio me llevó al descubrimiento de que Asterisk podía resolver una variedad de problemas muy costosos para mi base de clientes. Teníamos problemas con cotizaciones costosas para IVR, mensajería unificada, grabación de llamadas y marcadores; con un dimensionamiento adecuado, los problemas de CPU podían evitarse. De hecho, en solo tres años Asterisk se convirtió en el producto estrella de mi empresa (de hecho, decidí abrir otra empresa solo para el negocio de Asterisk). En mi opinión, Asterisk es una revolución en las telecomunicaciones que representa para la telefonía IP lo que Apache representa para los servicios web.

### Reducción extrema de costos

Si compara una PBX tradicional con Asterisk en lo que respecta a interfaces digitales y teléfonos, Asterisk es ligeramente más barato que esas PBX. Sin embargo, Asterisk realmente vale la pena cuando se añaden funciones avanzadas como correo de voz, ACD, IVR y CTI. Con estas funciones avanzadas, Asterisk se vuelve significativamente menos costoso que las PBX tradicionales. De hecho, comparar las PBX Asterisk con las PBX analógicas de gama baja es injusto porque Asterisk ofrece muchas funciones que no están disponibles en los sistemas analógicos de gama baja.

### Control e independencia del sistema de telefonía

Uno de los beneficios de Asterisk más citados por los clientes es la independencia que proporciona. Algunos de los fabricantes actuales ni siquiera le dan al cliente la contraseña del sistema o la documentación de configuración. Con el enfoque de "hágalo usted mismo" de Asterisk, el usuario logra una libertad total; como beneficio adicional, el usuario tiene acceso a una interfaz estándar.

### Entorno de desarrollo fácil y rápido

Asterisk puede extenderse utilizando lenguajes de script como PHP y Perl con interfaces AMI y AGI. Asterisk es de código abierto y su código fuente puede ser modificado por el usuario. El código fuente está escrito principalmente en lenguaje de programación ANSI C.

### Rico en funciones

Asterisk tiene varias funciones que no se encuentran o son opcionales en las PBX tradicionales (por ejemplo, correo de voz, CTI, ACD, IVR, música en espera integrada y grabación). Los costos de estas funciones en algunas plataformas superan el precio de la plataforma misma.

### Contenido dinámico en el teléfono

Asterisk está programado utilizando el lenguaje C y otros lenguajes comunes en el entorno de desarrollo actual. La posibilidad de proporcionar contenido dinámico es prácticamente ilimitada.

### Plan de marcado flexible y potente

Otro avance de Asterisk es su potente plan de marcado. En las PBX tradicionales, incluso las funciones simples como el enrutamiento de menor costo (LCR) no son factibles o son opcionales. Con Asterisk, elegir la mejor ruta es fácil y limpio.

### Código abierto ejecutándose sobre Linux

Una de las mejores características de Asterisk es su comunidad. Hay varios recursos disponibles, incluida la documentación oficial de Asterisk (docs.asterisk.org), la wiki VoIP-Info mantenida por la comunidad (www.voip-info.org <http://www.voip-info.org>), listas de distribución de correo electrónico y foros. A medida que Asterisk se adopta cada vez más, los errores se encuentran y corrigen rápidamente. Con una gran base de usuarios y un equipo de desarrollo activo, Asterisk se encuentra entre las plataformas PBX más probadas del mundo, lo que ayuda a mantener la base de código estable y madura.

### Limitaciones de la arquitectura de Asterisk

Algunas limitaciones en Asterisk provienen del uso del diseño de telefonía Zapata. En este diseño, Asterisk utiliza la CPU de la PC para procesar canales de voz en lugar de procesadores de señal digital (DSP) dedicados, que son comunes en otras plataformas. Aunque esto permite una gran reducción de costos en la interfaz de hardware, el sistema se vuelve dependiente de la CPU de la PC. Mi recomendación es ejecutar Asterisk en una máquina dedicada y ser conservador con el dimensionamiento del hardware. También puede usar Asterisk en una VLAN separada para evitar transmisiones excesivas que consumen la CPU (tormentas de difusión causadas por bucles o virus). Algunas tarjetas de interfaz más nuevas de varios proveedores ahora incluyen DSP para procesar la cancelación de eco, códecs y otras funciones, lo que hará que Asterisk sea aún mejor.

## Principales objeciones a Asterisk PBX

Es común escuchar objeciones a la adopción de Asterisk, las cuales abordaremos aquí.

### La cuota de mercado de Asterisk es demasiado pequeña

La cuota de mercado generalmente se mide por el número de PBX vendidas. Estas estadísticas se obtienen generalmente de los distribuidores más grandes. Asterisk es un software gratuito que puede descargarse e implementarse sin que se registre ninguna venta, por lo que se subestima sistemáticamente en esas cifras. Aun así, Asterisk impulsa una base instalada muy grande en todo el mundo —desde PBX de oficina de un solo servidor hasta grandes implementaciones de operadores y centros de contacto— y sigue siendo el motor dominante detrás del ecosistema de PBX de código abierto (incluidas las distribuciones llave en mano como FreePBX).

### Si es gratis, ¿cómo sobrevive el fabricante?

En realidad, no existe un fabricante de software de código abierto en el sentido tradicional. Digium desarrolló Asterisk desde 1999, manteniéndose a través de las ventas de tarjetas de interfaz de telefonía, productos PBX comerciales como Switchvox y software relacionado. En 2018, Sangoma Technologies adquirió Digium. Sangoma continúa financiando el desarrollo de Asterisk y genera ingresos a través de productos comerciales (módulos comerciales de FreePBX, PBXact, Switchvox), ventas de hardware y servicios profesionales.

### ¡Es difícil encontrar soporte técnico!

Sangoma proporciona soporte técnico comercial para Asterisk a través de su ecosistema de socios y directamente a través de sus ofertas de productos. Una red global de profesionales certificados proporciona soporte de primera línea y servicios profesionales. El soporte comunitario sigue siendo activo a través de los foros de Asterisk y las listas de correo en www.asterisk.org.

### ¿Asterisk soporta más de 200 extensiones?

Sí, absolutamente. Un solo servidor Asterisk bien dimensionado puede manejar un gran número de extensiones, y Asterisk escala aún más distribuyendo usuarios a través de múltiples servidores con equilibrio de carga y conmutación por error, permitiendo grandes implementaciones multisitio.

### Solo los "geeks" son capaces de instalar Asterisk

Con FreePBX (disponible como una distribución independiente de Sangoma), incluso los profesionales con conocimientos limitados sobre Linux son capaces de instalar y configurar una PBX de complejidad media. Con la ayuda de una GUI, es posible configurar una PBX completa en solo unas pocas horas.

### ¿Qué pasa si el servidor falla?

Una de las principales ventajas de Asterisk es su capacidad para ejecutarse en sistemas tolerantes a fallas. Es relativamente simple y económico tener dos servidores ejecutándose en paralelo. ¡Te desafío a intentar esto con una PBX convencional!

### Nuestra empresa no utiliza software de código abierto

Su empresa probablemente utiliza software de código abierto sin siquiera darse cuenta. Varios dispositivos utilizan Linux como sistema operativo. Además, el soporte comercial y las implementaciones gestionadas están disponibles a través de Sangoma y su red de socios certificados.

### No se recomienda utilizar la CPU de la PC para procesar señalización y medios

Asterisk utiliza la CPU del servidor para procesar la señalización y los medios para los canales de voz en lugar de tener DSP dedicados. Aunque esto permite una reducción de costos de hasta cinco veces, hace que el sistema dependa del rendimiento de la CPU principal. Con el dimensionamiento correcto, Asterisk es capaz de manejar grandes volúmenes. Si aún desea liberar la CPU principal de estas tareas, también puede utilizar tarjetas de cancelación de eco de hardware e incluso tarjetas transcodificadoras, como la Sangoma (anteriormente Digium) TC400B basada en DSP.

## Arquitectura de Asterisk

Esta sección explicará cómo funciona la arquitectura de Asterisk. La figura a continuación muestra la arquitectura básica de Asterisk. A continuación, explicaremos los conceptos relacionados con la arquitectura, incluidos canales, códecs y aplicaciones.

![La arquitectura de Asterisk](../images/01-introduction-fig01.png)

### Canales

Un canal es el equivalente a una línea telefónica, pero en formato digital. Por lo general, consiste en un sistema de señalización analógico o digital (TDM) o una combinación de códec y protocolo de señalización (por ejemplo, SIP-GSM, IAX-uLaw). Inicialmente, todas las conexiones telefónicas eran analógicas y susceptibles al eco y al ruido. Más tarde, la mayoría de los sistemas se convirtieron a sistemas digitales, con el sonido analógico convertido a un formato digital utilizando modulación por código de pulso (PCM) en la mayoría de los casos. Este formato permite la transmisión de voz a 64 kilobits/segundo sin compresión.

Canales que se conectan con la Red Telefónica Pública Conmutada (PSTN):

- `chan_dahdi`: tarjetas TDM analógicas (FXO/FXS) y digitales (E1/T1/PRI) de Sangoma (anteriormente Digium), Xorcom y otros. Construidas por separado contra DAHDI — vea el capítulo *Canales heredados*.

Canales que se conectan con Voz sobre IP:

- `chan_pjsip`: SIP — el controlador de canal SIP principal y único en Asterisk 22 LTS. Cadena de marcado: `PJSIP/endpoint_name`. (**Nota:** el antiguo `chan_sip` fue eliminado en Asterisk 21 y no existe en Asterisk 22. Vea *Construyendo su primera PBX con PJSIP* para la configuración.)
- `chan_iax2`: el protocolo IAX2 — todavía se envía en Asterisk 22 pero es heredado; SIP/PJSIP es preferido para nuevas implementaciones. Cadena de marcado: `IAX2/peer`.
- `chan_unistim`: teléfonos Nortel/Avaya UNISTIM. Todavía disponible (soporte extendido) pero raramente utilizado.

Los canales VoIP más antiguos ya no forman parte de una compilación estándar de Asterisk 22: `chan_h323` (H.323) sobrevive solo como el complemento comunitario `ooh323`, y `chan_mgcp` (MGCP) y `chan_skinny` (Cisco SCCP) fueron obsoletos y eliminados del conjunto de canales moderno. Si debe interoperar con esos protocolos, un gateway frente a Asterisk es el enfoque habitual.

Canales misceláneos:

- **Local**: un pseudocanal (integrado en el núcleo) que vuelve al plan de marcado en un contexto diferente — útil para el enrutamiento recursivo y para distribuir una llamada a múltiples destinos. Cadena de marcado: `Local/extension@context`.

### Códec y traducción de códecs

Normalmente intentamos poner tantas conexiones de voz como sea posible en una red de datos. Los códecs permiten nuevas funciones en la voz digital, incluida la compresión, que es una de las características más importantes ya que permite tasas de compresión superiores a 8 a 1. Muchos códecs también definen características como la detección de actividad de voz (supresión de silencio), ocultación de pérdida de paquetes y generación de ruido de confort, aunque Asterisk en sí mismo no genera ruido de confort ni realiza supresión de silencio. Varios códecs están disponibles para Asterisk y pueden traducirse de forma transparente de uno a otro. Internamente, Asterisk utiliza slinear como formato de flujo cuando necesita convertir de un códec a otro. Algunos códecs en Asterisk solo son compatibles en modo de paso directo (pass-through); estos códecs no se pueden traducir. Para verificar qué códecs están instalados en su sistema, puede usar el comando de consola:

```
CLI>core show translation
```

Se admiten los siguientes códecs:

- G.711 ulaw (EE. UU.) - (64 Kbps).
- G.711 alaw (Europa) - (64 Kbps).
- G.722 (Alta definición) – (64 Kbps)
- G.723.1 - Solo modo de paso directo
- G.726 - (16/24/32/40kbps)
- G.729 - Módulo de códec binario distribuido por Sangoma; la descarga es gratuita, pero el uso legal requiere la compra de una licencia por canal (8Kbps)
- GSM - (12-13 Kbps)
- iLBC - (15 Kbps)
- LPC10 - (2.4 Kbps)
- Speex - (2.15-44.2 Kbps)
- Opus - (6-510 Kbps)

### Protocolos

Enviar datos de un teléfono a otro debería ser fácil siempre que los datos encuentren un camino al otro teléfono por sí mismos. Desafortunadamente, no sucede de esta manera, y es necesario un protocolo de señalización para establecer conexiones entre teléfonos, descubrir dispositivos finales e implementar la señalización telefónica. SIP es el protocolo de señalización dominante en las implementaciones modernas y es el único canal SIP disponible en Asterisk 22 LTS (a través de chan_pjsip). IAX2 todavía está disponible pero se considera heredado. Asterisk admite los siguientes protocolos.

- SIP — vía `chan_pjsip`
- IAX2 — heredado, todavía se envía en Asterisk 22
- UNISTIM — teléfonos Nortel/Avaya (soporte extendido)
- H.323, MGCP y SCCP (Cisco Skinny) — protocolos heredados que ya no están en una compilación estándar de Asterisk 22 (H.323 solo a través del complemento comunitario `ooh323`)

### Aplicaciones

Para conectar llamadas de un teléfono a otro, se utiliza la aplicación dial(). La mayoría de las funciones de Asterisk (por ejemplo, correo de voz y conferencias) se implementan como aplicaciones. Puede ver las aplicaciones de Asterisk disponibles utilizando el comando de consola core show applications.

```
CLI>core show applications
```

Puede añadir aplicaciones desde complementos de Asterisk, proveedores externos o incluso aquellas que usted mismo desarrolle.

## Descripción general de un sistema Asterisk

Asterisk es una PBX de código abierto que actúa como una PBX híbrida, integrando tecnologías como TDM y telefonía IP. Asterisk está listo para implementar funcionalidades como respuesta de voz interactiva (IVR) y distribución automática de llamadas (ACD); además, como se mencionó anteriormente, está abierto al desarrollo de nuevas aplicaciones. Esta figura muestra cómo Asterisk se conecta a la PSTN y a las PBX existentes utilizando interfaces analógicas y digitales, así como también admite teléfonos analógicos e IP. Puede actuar como soft-switch, media gateway, correo de voz y conferencia de audio, y también tiene música en espera integrada.

![Descripción general de un sistema Asterisk](../images/01-introduction-fig02.png)

## Comparando el viejo y el nuevo mundo

En el antiguo modelo de soft-switch, todos los componentes se vendían por separado, lo que significaba que tenías que comprar cada componente por separado y luego integrarlo al entorno de PBX o soft-switch. Los costos y riesgos eran altos y la mayoría de los equipos eran propietarios.

![El viejo mundo: componentes comprados e integrados por separado](../images/01-introduction-fig03.png)

### Telefonía usando Asterisk

Todas las funciones están integradas en la plataforma Asterisk en la misma o en diferentes cajas según el dimensionamiento, y todas tienen licencia GPL. A veces es más fácil instalar Asterisk que licenciar algunas de las IP-PBX convencionales.

![Telefonía usando Asterisk: las funciones están integradas](../images/01-introduction-fig04.png)

## Construyendo un sistema de prueba

Al implementar una solución Asterisk, nuestro primer paso es generalmente construir una máquina de prueba. La máquina de prueba más fácil es la PBX 1x1, que incluye al menos un teléfono y una línea. Hay varias formas de hacer esto.

![Un sistema de prueba Asterisk simple](../images/01-introduction-fig05.png)

### Un FXO, un FXS

La primera y más sencilla forma de construir una máquina de prueba es comprar una tarjeta con una interfaz FXO y una FXS. Conecte el puerto FXO a una línea existente y conecte un FXS a un teléfono analógico. Así, tiene una PBX 1x1.

### Proveedor de servicios VoIP: ATA

Esta es la opción VoIP. En este caso, usted se registraría con un proveedor de servicios de voz para tener los troncales SIP y tendrá que comprar un adaptador de telefonía analógica SIP. Probablemente gastará menos de cien dólares si ya tiene la PC.

### Tarjeta FXO o ATA económica

Comencé con una tarjeta FXO económica. Algunos módems de fax V.90 económicos funcionan con Asterisk como una tarjeta FXO. Algunas de las primeras tarjetas Digium se crearon utilizando estas tarjetas (por ejemplo, X100P y X101P), que son módems antiguos basados en chipsets de Motorola e Intel (se sabe que funcionan Motorola 68202-51, Intel 537PU, Intel 537PG e Intel Ambient MD3200). Estos módems a menudo son incompatibles con las nuevas placas base. Recientemente, algunos fabricantes comenzaron a vender estas tarjetas como clones de X100P. Algunas de las incompatibilidades se pueden resolver utilizando un parche; puede encontrar más información en:

- http://www.voip.school/mediawiki/index.php/Asterisk_patch_for_the_X100P_card

## Escenarios de Asterisk

Asterisk se puede utilizar en varios escenarios diferentes. Enumeraremos algunos de ellos y explicaremos las ventajas y posibles limitaciones de cada uno.

### IP PBX

El escenario más común es la instalación de una nueva PBX o el reemplazo de una existente. Si compara Asterisk con algunas otras alternativas, encontrará que es más barato y más rico en funciones que la mayoría de las PBX disponibles actualmente en el mercado. Varias empresas están cambiando ahora sus especificaciones a Asterisk en lugar de otras PBX de marca.

![Asterisk como una IP PBX](../images/01-introduction-fig06.png)

### Habilitación de IP en PBX heredadas

La siguiente imagen ilustra una de las configuraciones más utilizadas. Las grandes empresas generalmente no quieren asumir riesgos significativos al invertir en nuevas tecnologías y, al mismo tiempo, desean preservar sus inversiones en equipos heredados. Habilitar IP en una PBX heredada puede ser muy costoso; por lo tanto, conectar una PBX Asterisk usando líneas T1/E1 puede ser una buena alternativa para los clientes conscientes de los costos. Otro beneficio es la posibilidad de conectarse a un proveedor de servicios VoIP con mejores tarifas telefónicas.

![Habilitación de IP en una PBX heredada](../images/01-introduction-fig07.png)

### Omisión de peajes (Toll Bypass)

Una aplicación muy útil para VoIP es conectar sucursales a través de Internet o una WAN. El uso de una conexión de datos existente le permite evitar los cargos de peaje incurridos en las conexiones de telecomunicaciones entre la sede central y las sucursales.

![Omisión de peajes entre oficinas a través de una WAN](../images/01-introduction-fig08.png)

### Servidor de aplicaciones (IVR, Conferencia, Correo de voz)

Asterisk se puede utilizar como servidor de aplicaciones para la PBX existente o conectarse directamente a la PSTN. Asterisk ofrece servicios como correo de voz, recepción de fax, grabación de llamadas, IVR conectado a una base de datos y un servidor de conferencias de audio. Si integra el correo de voz y el fax en un servidor de correo electrónico existente, tendrá un sistema de mensajería unificada, que suele ser una solución costosa. El uso de Asterisk como servidor de aplicaciones proporciona una reducción extrema de costos en comparación con otras soluciones.

![Asterisk como servidor de aplicaciones](../images/01-introduction-fig09.png)

### Media Gateway

La mayoría de los proveedores de servicios de voz sobre IP utilizan un proxy SIP para alojar todo el registro, la ubicación y la autenticación de los usuarios SIP. Todavía tienen que enviar llamadas a la PSTN directamente o enrutarlas a través de un proveedor de terminación de llamadas al por mayor utilizando una conexión de voz sobre IP SIP o H.323. Asterisk puede actuar como un agente de usuario de espalda a espalda (B2BUA) o media gateway, reemplazando soft switches o media gateways muy costosos. Compare el precio de un gateway de cuatro E1/T1 de los principales fabricantes del mercado con Asterisk. La solución Asterisk puede costar varias veces menos que otras soluciones y es capaz de traducir protocolos de señalización (H.323, SIP, IAX...) y códecs (G.711, G.729...).

![Asterisk como media gateway](../images/01-introduction-fig10.png)

### Plataforma de Centro de Contacto

Un centro de contacto es una solución muy compleja que combina varias tecnologías, como distribución automática de llamadas (ACD), respuesta de voz interactiva (IVR) y supervisión de llamadas. Básicamente, hay tres tipos de centros de contacto disponibles: entrantes, salientes y combinados. Los centros de contacto entrantes son muy sofisticados y generalmente requieren ACD, IVR, CTI, grabación, supervisión e informes. Asterisk tiene un ACD incorporado para poner las llamadas en cola. El IVR se puede hacer utilizando la Interfaz de Gateway de Asterisk (AGI) o mecanismos internos como la aplicación background(). La integración de telefonía informática (CTI) se logra utilizando la Interfaz de Administrador de Asterisk (AMI); la grabación y los informes están integrados en Asterisk. Para un centro de contacto saliente, un marcador predictivo o de potencia es uno de los componentes principales. Aunque hay varios marcadores disponibles para el Asterisk de código abierto, no es difícil construir el suyo propio para la plataforma si así lo desea. Un centro de contacto combinado permite la operación simultánea de entrada y salida, ahorrando dinero al garantizar un mejor uso del tiempo del agente. Es posible utilizar Asterisk y su mecanismo ACD para implementar una solución combinada.

![Una plataforma de centro de contacto Asterisk](../images/01-introduction-fig11.png)

## Encontrar información y ayuda

Esta sección proporcionará algunas de las principales fuentes de información relacionadas con Asterisk.

- Sitio web oficial de Asterisk: <https://www.asterisk.org> Aquí puede encontrar información sobre:
- Documentación y Wiki -> <https://docs.asterisk.org>
- Foro comunitario -> <https://community.asterisk.org>
- Seguimiento de errores -> <https://github.com/asterisk/asterisk/issues>
- Wiki (heredada, en gran parte reemplazada por docs.asterisk.org) -> <https://wiki.asterisk.org>

### Foro comunitario

El foro de la comunidad de Asterisk ha reemplazado en gran medida a las antiguas listas de correo y es el lugar para hacer preguntas. Intente recopilar la mayor cantidad de información posible antes de publicar. Nadie le ayudará si no ha hecho su tarea: intente al menos una vez resolver el problema por su cuenta.

- <https://community.asterisk.org>

## Resumen

Asterisk es un software con licencia GPL que permite que una PC común actúe como una potente plataforma IP PBX. Mark Spencer de Digium creó Asterisk a finales de los años 90, y Digium se mantuvo vendiendo hardware relacionado con Asterisk y productos comerciales. Digium fue adquirida por Sangoma Technologies en 2018; Sangoma ahora patrocina el desarrollo de Asterisk. El diseño de la interfaz de hardware se originó en el proyecto Zapata desarrollado por Jim Dixon, que dio lugar a DAHDI.

La arquitectura de Asterisk tiene los siguientes componentes principales:

- CANALES: Analógicos, digitales o de voz sobre IP. En Asterisk 22 LTS, SIP se maneja exclusivamente mediante chan_pjsip.
- PROTOCOLOS: Protocolos de comunicación, que son responsables de señalar las llamadas, incluidos SIP (a través de PJSIP), H323, MGCP e IAX2.
- CÓDECS: Traducen formatos digitales de voz permitiendo la compresión y la ocultación de pérdida de paquetes. Tenga en cuenta que Asterisk en sí mismo no realiza supresión de silencio (detección de actividad de voz) ni generación de ruido de confort; cuando los endpoints utilizan VAD, el ruido de confort debe desactivarse en el lado del cliente.
- APLICACIONES: Responsables de la funcionalidad de la PBX Asterisk. Conferencias, correo de voz y fax son ejemplos de aplicaciones de Asterisk.

Asterisk se puede utilizar en varios escenarios, desde una pequeña IP PBX hasta un sofisticado centro de contacto. Puede encontrar ayuda fácilmente en www.asterisk.org y docs.asterisk.org.

## Cuestionario

1. ¿Qué empresa adquirió Digium en 2018 y ahora sirve como administrador principal del proyecto de código abierto Asterisk?
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

4. ¿Cuáles de los siguientes canales/protocolos **ya no** forman parte de una compilación estándar de Asterisk 22? (Elija todos los que correspondan.)
   - A. MGCP (`chan_mgcp`)
   - B. SCCP / Cisco Skinny (`chan_skinny`)
   - C. IAX2 (`chan_iax2`)
   - D. H.323 (`chan_h323`, sobreviviendo solo como el complemento comunitario `ooh323`)

5. La arquitectura de hardware del proyecto Zapata, originalmente llamada Zaptel, fue renombrada más tarde a ____.
   - A. DAHDI
   - B. PJSIP
   - C. PRI
   - D. mISDN

6. Cuando Asterisk debe convertir audio de un códec a otro, ¿a través de qué formato de flujo interno se traduce?
   - A. G.711 ulaw
   - B. GSM
   - C. slinear (signed linear)
   - D. Opus

7. Según el capítulo, ¿cuál es la situación de licenciamiento del módulo de códec G.729 distribuido por Sangoma?
   - A. Es GPL y completamente gratuito para cualquier uso.
   - B. La descarga es gratuita, pero el uso legal requiere la compra de una licencia por canal.
   - C. No se puede obtener en absoluto sin comprar Asterisk Business Edition.
   - D. Solo funciona en modo de paso directo y no se puede instalar.

8. ¿Qué aplicación de Asterisk se utiliza para conectar una llamada de un teléfono a otro?
   - A. `Background()`
   - B. `Dial()`
   - C. `Queue()`
   - D. `Goto()`

9. ¿Qué es el canal `Local` en Asterisk?
   - A. Una interfaz FXS de hardware para teléfonos analógicos.
   - B. Un troncal SIP a un proveedor de servicios local.
   - C. Un pseudocanal que devuelve una llamada al plan de marcado en un contexto diferente.
   - D. Un códec utilizado para llamadas en la red.

10. ¿En qué escenario de uso actúa Asterisk como un agente de usuario de espalda a espalda (B2BUA), traduciendo entre protocolos de señalización y códecs para reemplazar costosos soft switches?
    - A. Habilitación de IP en una PBX heredada
    - B. Omisión de peajes
    - C. Media Gateway
    - D. Plataforma de Centro de Contacto

**Respuestas:** 1 — B · 2 — C · 3 — Verdadero · 4 — A, B, D · 5 — A · 6 — C · 7 — B · 8 — B · 9 — C · 10 — C
