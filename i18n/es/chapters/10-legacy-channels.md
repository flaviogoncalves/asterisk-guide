# Canales heredados: analógico, TDM e IAX2

En un mundo puro‑VoIP de 2026, los tipos de canal de este capítulo son cada vez más raros: la mayoría de los despliegues nuevos son trunks SIP y endpoints PJSIP sobre Ethernet, sin hardware de telefonía en absoluto. Asterisk 22, sin embargo, sigue soportando la mayor parte de ellos completamente. La conectividad analógica (FXO/FXS) y digital TDM (E1/T1/ISDN PRI/BRI) se proporciona a través de DAHDI — la pila de controladores originalmente desarrollada por Digium, que fue adquirida por Sangoma en 2018, después de que los controladores Zaptel fueran renombrados tras una disputa de marca registrada. La conectividad servidor‑a‑servidor sobre IAX2 la proporciona `chan_iax2`, que aún se envía y soporta pero ahora es firmemente un protocolo heredado.

Este capítulo también recopila el material **legacy SIP**: el antiguo controlador `chan_sip` y su configuración `sip.conf` — eliminados en Asterisk 21 y desaparecidos en Asterisk 22 — junto con una guía completa para migrar un sistema `sip.conf` existente a PJSIP. Si estás ejecutando una tienda pura‑SIP en PJSIP sin tarjetas de telefonía, sin trunks IAX2 y sin legacy `sip.conf` que convertir, puedes omitir este capítulo con seguridad.

## Objetivos

Al final de este capítulo, deberías ser capaz de:

- Conectar Asterisk a líneas y teléfonos analógicos con interfaces FXO/FXS a través de DAHDI;
- Reconocer la conectividad digital TDM (E1/T1, ISDN PRI/BRI) y cómo se configura;
- Configurar IAX2 (`chan_iax2`) para trunks de servidor a servidor y entender por qué ahora es legado;
- Identificar el controlador retirado `chan_sip` y la sintaxis `sip.conf` que aún puedes encontrar; y
- Migrar un sistema existente `chan_sip`/`sip.conf` a PJSIP.

## Canales analógicos (FXO/FXS)

A partir de Asterisk 22, las tarjetas de telefonía analógica y DAHDI siguen totalmente soportadas, y DAHDI aún se compila contra los núcleos actuales. La mayoría de los nuevos despliegues son sin embargo puramente VoIP (troncales SIP, PJSIP), por lo que el hardware analógico/TDM ahora es una opción de nicho — encontrado principalmente en entornos heredados, conectividad PSTN rural o mercados regulados. Todo lo siguiente sigue aplicándose a esos escenarios.

Existen varias formas de conectar la red telefónica pública conmutada (PSTN). La mejor manera depende de cómo la compañía telefónica ofrece esta conexión en su zona. La forma más simple es usar una línea analógica, similar a la línea que usa en casa. En esta sección, le mostraremos cómo configurar tarjetas analógicas de Sangoma™ (anteriormente Digium™) y Xorcom™.

### Objetivos

Al final de este capítulo usted debería ser capaz de:

- Reconocer los principales términos y acrónimos de telefonía;
- Entender cuándo usar circuitos digitales y analógicos;
- Reconocer la diferencia entre FXS y FXO; y
- Configurar Asterisk para FXS y FXO.

### Conceptos básicos de telefonía

La mayoría de las implementaciones analógicas usan un par de líneas cooper llamadas tip y ring. Cuando se cierra un bucle, el teléfono recibe el tono de marcación del conmutador de telecomunicaciones (o del PBX privado). La señalización más utilizada es loop‑start; existen otras, menos comunes, como ground start, que se usa en varios países. Las tres categorías de señalización son:

- Señalización de supervisión
- Señalización de dirección
- Señalización de información

#### Señalización de supervisión

Las principales señalizaciones de supervisión son on‑hook, off‑hook y ringing.

- **On‑Hook** – Cuando un usuario coloca el teléfono en el gancho, el PBX interrumpe y no permite que la corriente eléctrica pase. En este estado, el circuito se denomina on‑hook. En esta posición, solo el timbre está activo.
- **Off‑Hook** – Antes de iniciar una llamada, el teléfono debe pasar al estado off‑hook. Retirar el auricular del gancho cierra el bucle e indica al PBX que el usuario pretende realizar una llamada. Al recibir esta indicación, el PBX genera un tono de marcación, indicando al usuario que está listo para aceptar la dirección de destino (es decir, el número de teléfono).
- **Ringing** – Cuando un usuario llama a otro teléfono, se genera un voltaje al timbre que avisa al otro usuario de que se está recibiendo una llamada. La señalización varía según el país, con tonos diferentes para cada uno.

Puede personalizar los tonos de Asterisk para su país modificando el archivo indications.conf. Por ejemplo:

```
[br]
description=Brazil
ringcadance=1000,4000
dial=425
busy=425/250,0/250
ring=425/1000,0/4000
congestion=425/250,0/250,425/750,0/250
callwaiting=425/50,0/1000
```

#### Señalización de Dirección

Puedes usar dos tipos de señalización para marcar. El primero y más común es tono dual de múltiple frecuencia (dtmf) mientras que el otro es marcación por pulsos (usada en teléfonos de disco antiguos). Los teléfonos tienen un teclado para marcar, y cada botón está asociado a dos frecuencias: una alta y una baja. En el caso de la señalización dtmf, la combinación de estos tonos indica qué dígito se está presionando. MFC/R2 usa un tono de múltiple frecuencia diferente al dtmf.

#### Señalización de información

La señalización de información muestra el progreso de la llamada y diferentes eventos.

- tono de marcación
- tono ocupado
- tono de retorno
- congestión
- número inválido
- tono de confirmación

### Interfaces PSTN

Como en el caso de los PBX antiguos, a menudo se requiere conectar el Asterisk PBX a la PSTN. Aquí le mostraremos cómo hacerlo. Normalmente tiene tres opciones para líneas telefónicas.

- Analógica: La forma más común para hogares y pequeñas empresas, generalmente entregada con un par metálico de líneas de cobre.  
- Digital: Se usa cuando se requieren muchas líneas. Una línea digital suele entregarse mediante un CSU/DSU o un multiplexor de fibra. El conector del usuario final suele ser un RJ45. En algunos países, las líneas E1 se entregan usando dos conectores coaxiales BNC; en este caso necesitará un adaptador para conectar el conector RJ45 a la tarjeta de telefonía.  
- SIP: Esta opción se ha desarrollado recientemente. La línea telefónica se entrega usando una conexión de datos con señalización SIP (VoIP). Es una buena opción para usar con Asterisk ya que no necesitará comprar una tarjeta de telefonía. Las llamadas telefónicas se entregarán directamente al puerto Ethernet. Otra ventaja es que podrá liberar recursos de su CPU evitando la transcodificación de códecs.

### Interfaces analógicas FXS, FXO y E&M interfaces

Varios tipos de interfaces analógicas están disponibles. Es fundamental comprender las diferencias entre estas interfaces para aprender cómo conectarse a la red telefónica así como a otros PBX. Aquí, le mostraremos la interfaz E&M. Aunque actualmente no está disponible para Asterisk y ha sido descontinuada por varios proveedores, puede encontrar routers y PBX con este tipo de interfaz, por lo que es mejor saber con qué está tratando.

#### Interfaces de Intercambio Extranjero (FX) Interfaces

Las interfaces FX son analógicas. El término “Foreign eXchange” se aplica a los trunks de acceso a una central telefónica PSTN (CO). Foreign eXchange Office (FXO)

![Asterisk entre un teléfono analógico (FXS) y la línea telefónica (FXO): el lado FXS proporciona tono de marcado y timbre al teléfono, mientras que el lado FXO extrae tono de marcado de la central.](../images/10-legacy-fig01.png)

La interfaz FXO se usa para conectar a una central (CO) o a la extensión de otro PBX. Comunica directamente con una línea telefónica proveniente de la PSTN. Otra opción es conectar la interfaz FXO a un PBX existente, permitiendo la comunicación entre Asterisk y el PBX heredado. Conectar Asterisk a un puerto de PBX y proporcionar una extensión remota usando VoIP se suele denominar extensión fuera de promesas (OPX). Una interfaz FXO recibe un tono de marcado. Estación de Intercambio Extranjero (FXS) La interfaz FXS alimenta un teléfono analógico, módem o fax. El FXS proporciona el tono de marcado y la energía para un teléfono.

#### Señalización de tronco

- Inicio en bucle
- Inicio de tierra
- Inicio genial

El uso de la señalización kewlstart en Asterisk es casi predeterminado. Kewlstart no es señalización en sí, pero agrega inteligencia al circuito al monitorear lo que ocurre en el otro extremo. Kewlstart se basa en loop-start. La mayoría de los conmutadores no soportan esta característica, que se usa para obtener la notificación de colgado.

- Loopstart: Usado en la mayoría de líneas analógicas, permite que el teléfono indique “on-hook” y “off-hook” y que el conmutador indique “ring” y “no-ring”. Probablemente sea lo que la mayoría de la gente tiene en casa. El nombre proviene del hecho de que la línea está siempre abierta. Cuando cierras el bucle, el conmutador te proporciona un tono de marcación. Una llamada entrante se señala con una tensión de timbre de 100 V sobre el par abierto.

![Asterisk funcionando como una pasarela VoIP: un puerto FXO se conecta a una extensión PBX heredada mientras un Asterisk remoto entrega esa línea a un teléfono analógico a través de IP mediante un puerto FXS (una extensión fuera de las instalaciones, o OPX).](../images/10-legacy-fig02.png)

- Groundstart: Similar a Loopstart. Cuando deseas realizar una llamada, un lado de la línea está cortocircuitado. Cuando el conmutador identifica este estado, invierte la tensión a través del par abierto, y luego se cierra el bucle. En consecuencia, la línea primero queda ocupada antes de ser ofrecida al llamante.
- Kewlstart: Añade inteligencia a los circuitos, permitiendo la monitorización del otro lado. Kewlstart incorpora muchas ventajas del loop-start.

### Configuración de canales de telefonía Asterisk

Para configurar una tarjeta de interfaz telefónica, son necesarios varios pasos. En este capítulo, mostraremos tres de los escenarios más comunes:

- Conexión analógica usando FXS
- Conexión analógica usando FXO
- Conexión de un Astribank™ con interfaces FXS y FXO

### Procedimiento de Configuración (válido en ambos casos)

Antes de elegir el hardware para Asterisk, debe considerar la cantidad de llamadas simultáneas, servicios y códecs que se instalarán y habilitarán. Asterisk es una aplicación intensiva en CPU, por lo que recomendamos una máquina dedicada para Asterisk. La cantidad de tarjetas de interfaz instaladas en la computadora está limitada por el número de ranuras e interrupciones disponibles. Es preferible instalar una sola tarjeta con ocho interfaces de voz que dos tarjetas con cuatro. Otra opción es usar un banco de canales USB, como el Xorcom Astribank. Recientemente, algunos fabricantes (p. ej., CIANET) han comenzado a producir bancos de canales TDMoE, lo que facilita aún más conectar decenas de interfaces analógicas.

![A Xorcom Astribank: un banco de canales USB de montaje en rack de 19 pulgadas que expone docenas de puertos FXS/FXO (aquí una unidad de 32 puertos) sin consumir ranuras PCI en el host.](../images/10-legacy-fig03.png)

#### Ejemplo 1: Instalación de un FXO y un FXS

En este ejemplo, utilizaremos una tarjeta de interfaz telefónica Sangoma TDM400 (anteriormente vendida como Digium TDM400) con un módulo FXS y un módulo FXO. Los pasos requeridos se enumeran a continuación:

1. Instale la tarjeta analógica FXS, FXO, o ambas.  
2. Configure el archivo `/etc/dahdi/system.conf` (anteriormente `/etc/zaptel.conf`).  
3. Genere los archivos de configuración usando `dahdi_genconf`.  
4. Cargue el controlador para la interfaz DAHDI.  
5. Ejecute `dahdi_test` para verificar pérdidas de interrupción.  
6. Ejecute `dahdi_cfg` para configurar el controlador.  
7. Configure el canal DAHDI en el archivo `chan_dahdi.conf`, luego cargue Asterisk.

##### Paso 1: Instalar la placa TDM400

La tarjeta TDM404P contiene módulos FXS y FXO. Conecte los módulos FXS (S110M, verde) y FXO (X100M, rojo). Si está usando módulos FXS, conecte la tarjeta directamente a la fuente de alimentación usando un conector molex. Por favor, use protección electrostática antes de manipular tarjetas de interfaz para evitar daños al hardware. Las tarjetas analógicas de Sangoma (anteriormente Digium) también soportan un módulo de cancelación de eco hardware VPMADT032.

##### Paso 2: Generar la configuración con dahdi_genconf

La buena noticia sobre la configuración es la nueva utilidad `dahdi_genconf`, que detecta automáticamente y genera la configuración para interfaces DAHDI. La utilidad genera dos archivos:

- `/etc/dahdi/system.conf`
- `/etc/asterisk/dahdi-channels.conf`
- `/etc/asterisk/users.conf` (con la opción `users`)
- Todos estos archivos usan la opción `chan_dahdi full`

Before you can execute `dahdi_genconf`, it is important to configure the file `genconf_parameters` (often referred to as `gen_parameters.conf`):
--- END MARKDOWN ---

![Una tarjeta analógica Sangoma/Digium TDM404P: hasta cuatro módulos FXS o FXO se conectan a los puertos numerados, con una tarjeta hija opcional de cancelación de eco de hardware y un conector de alimentación dedicado de 12 V para módulos FXS.](../images/10-legacy-fig04.png)

```
#
# /etc/dahdi/genconf_parameters
#
# This file contains parameters that affect the
# dahdi_genconf configurator generator.
#
#base_exten          4000
#fxs_immediate       no
#fxs_default_start   ks
#lc_country          il
#context_lines       from-pstn
#context_phones      from-internal
#context_input       astbank-input
#context_output      astbank-output
#group_phones        0
#group_lines         5
#brint_overlap
#bri_sig_style       bri_ptmp
#
# The echo canceller to use. If you have a hardware echo canceller, just
# leave it be, as this one won't be used anyway.
#
# The default is mg2, but it may change in the future. E.g: a packager
# that bundles a better echo canceller may set it as the default, or
# dahdi_genconf will scan for the "best" echo canceller.
#
#echo_can            hpec
#echo_can            oslec
#echo_can            none   # to avoid echo cancellers altogether
# bri_hardhdlc: If this parameter is set to 'yes', in the entries for
# BRI cards 'hardhdlc' will be used instead of 'dchan' (an alias for
# 'fcshdlc').
#
#bri_hardhdlc        yes
# For MFC/R2 Support
#pri_connection_type R2
#r2_idle_bits        1101
# pri_types contains a list of settings:
# Currently the only setting is for TE or NT (the default is TE)
#
#pri_termtype
# SPAN/2              NT
# SPAN/4              NT
```

El archivo `genconf_parameters` le permite personalizar su configuración. Los parámetros más importantes para líneas analógicas son:

```
base_exten          4000
fxs_immediate       no
fxs_default_start   ks
lc_country          br
context_lines       from-pstn
context_phones      from-internal
context_input       astbank-input
context_output      astbank-output
group_phones        0
group_lines         5
#echo_can           hpec
#echo_can           oslec
echo_can            MG2
```

Warning: Es necesario que configure al menos el algoritmo de cancelación de eco para los canales. El parámetro base_exten define el plan de marcación básico para extensiones FXS. En este caso, el primer canal FXS recibirá el número de extensión 4000, el segundo 4001, y así sucesivamente. El contexto en el que se crean las líneas (context_phones) y los trunks (context_lines) es muy importante. Después de generar los archivos, debe incluir el archivo `/etc/asterisk/dahdi-channels.conf` en el archivo `/etc/asterisk/chan_dahdi.conf`:

```
#include dahdi-channels.conf
```

Note: La señalización analógica es un poco confusa; siempre es la inversa de la tarjeta. Las tarjetas FXS se señalan con FXO mientras que las tarjetas FXO se señalan con FXS. Asterisk habla con estos dispositivos como si estuviera en el lado opuesto.

##### Step 3: Load kernel drivers

Now you have to load the chan_dahdi module and the related card kernel driver. Use dahdi_hardware to detect your card and the driver name. For example:

| Card | Driver | Description |
| --- | --- | --- |
| TE410P | wct4xxp | 4xE1/T1 - PCI de 3.3V |
| TE405P | wct4xxp | 4xE1/T1 - PCI de 5V |
| TDM400P | wctdm | 4 FXS/FXO |
| T100P | wct1xxp | 1 T1 |
| E100P | wct1xxp | 1 E1 |
| X100P | wcfxo | 1 FXO |

Commands to load the drivers:

```
modprobe dahdi
modprobe wctdm
```

##### Paso 4: Use la utilidad dahdi_test

Una utilidad importante es dahdi_test, que se usa para verificar pérdidas de interrupciones en la tarjeta DAHDI. Los problemas de calidad de audio a menudo están relacionados con conflictos de interrupciones. Para verificar que su tarjeta DAHDI no está compartiendo una interrupción con otras tarjetas, use el siguiente comando:

```
#cat /proc/interrupts
```

Puedes verificar el número de interrupciones perdidas usando la utilidad dahdi_test compilada con las tarjetas DAHDI. Un número por debajo del 99.987 % indica posibles problemas.

##### Paso 5: Usa la utilidad dahdi_cfg para configurar el controlador

DAHDI tiene un sistema inusual para cargar los controladores. Primero configura el archivo /etc/dahdi/system.conf y luego aplica esas configuraciones al controlador DAHDI usando dahdi_cfg. En este caso, dahdi_cfg se utiliza para configurar la señalización de las interfaces FX. Para ver los resultados, puedes añadir “-vvvvv” al comando para obtener salida detallada.

```
#
/sbin/dahdi_cfg -vv
Dahdi Configuration
======================
Channel map:
Channel 01: FXS Kewlstart (Default) (Slaves: 01)
Channel 02: FXO Kewlstart (Default) (Slaves: 02)
2 channels configured.
```

If the channels were loaded successfully, you will see an output similar to the one shown above. Users often incorrectly configure chan_dahdi.conf with inverted signaling between channels. If this happens, you will see a message like the one shown below:

```
DAHDI_CHANCONFIG failed on channel 1: Invalid argument (22)
Did you forget that FXS interfaces are configured with FXO signalling
and that FXO interfaces use FXS signalling?
```

After successfully configuring the hardware, you can proceed to Asterisk configuration.

##### Step 6: Configure the /etc/asterisk/chan_dahdi.conf file

It sounds strange, but after configuring the /etc/dahdi/system.conf, you configured the card itself. DAHDI can be used for other purposes, like routing and SS7. To use it with Asterisk, you must configure the Asterisk DAHDI channels. Every channel in Asterisk has to be defined; SIP/PJSIP channels are defined in pjsip.conf (note: chan_sip and sip.conf were removed in Asterisk 21) while TDM channels are defined in chan_dahdi.conf. This creates the logical TDM channels to be used in your dial plan.

```
signalling=fxs_ks;                  ; FXS signaling for the FXO interface
group=1;                            ; channel group
context=incoming;                   ; context
channel => 1;                       ; channel number
signalling=fxo_ks;                  ; FXO signaling for the FXS interface
group=2;                            ; channel group
context=extensions;                 ; context
channel => 2                        ; channel number
```

### Opciones de configuración

Hay varias opciones disponibles en el archivo chan_dahdi.conf. Una descripción de todas las opciones sería aburrida e improductiva; en su lugar, nos centraremos en los principales grupos de opciones disponibles para una fácil comprensión.

#### Opciones generales (independientes del canal)

Estas opciones funcionan para cualquier canal: context: Define el contexto de entrada.

```
context=default
```

channel: Define canal o rango de canales. Cada definición de canal heredará las opciones definidas antes de la declaración. Los canales pueden identificarse individualmente o en la misma línea mediante separación por comas. Los rangos pueden definirse usando “-”.

```
Channel=>1-15
Channel=>16
Channel=>17,18
```

group: Permite que los canales se manejen como un grupo. Si marca un número de grupo en lugar de un número de canal, se utiliza el primer canal disponible. Si los canales son teléfonos, cuando llama a un grupo, todos los teléfonos sonarán simultáneamente. Con comas, puede especificar más de un grupo para el mismo canal.

```
group=1
group=3,5
```

language: Activa la internacionalización y configura un idioma. Esta función configurará los mensajes del sistema para un idioma específico. English es el único idioma con indicaciones completas disponibles mediante la instalación estándar. musiconhold: Selecciona la clase de música en espera.

#### Opciones de Caller ID

Existen muchas opciones de callerid. Algunas pueden desactivarse, aunque la mayoría están habilitadas por defecto. usecallerid: Habilita o deshabilita la transmisión del callerid para los canales subsecuentes (Yes/No). Nota: Si su sistema recibe dos timbres antes de contestar, intente desactivar esta función. Debería contestar inmediatamente. hidecallerid: Define si se debe ocultar o no el callerid saliente (Yes/No). callerid: Configura una cadena de callerid para un canal específico. El caller puede configurarse con asreceived. Esto se usa principalmente en interfaces de trunk para indicar el callerid entrante.

```
callerid = "Flavio Eduardo Gonçalves" <48 30258500>
```

callwaitingcallerid: Soporta la identificación de llamada durante la espera de llamada. useincomingcalleridondahditransfer: Usa la identificación de llamada entrante en una transferencia.

#### Espera de Llamada

Asterisk soporta la espera de llamada en canales FXS. El usuario recibirá un tono de espera si alguien intenta la extensión. Para habilitar la espera de llamada:

```
callwaiting=yes
```

Para soportar la identificación de llamadas en la espera de llamada:

```
callwaitingcallerid=yes
```

#### Opciones de calidad de audio

Ajustar la cancelación de eco es medio técnico, medio arte. Estas opciones modifican ciertos parámetros de Asterisk que afectan la calidad de audio en los canales DAHDI. Pueden ayudar a mejorar la calidad de audio en interfaces analógicas.

#### La utilidad fxotune

La fxotune es una utilidad usada para afinar ciertos parámetros de los módulos FXO. Este afinamiento es necesario para ajustar el desajuste de impedancia causado por el híbrido. La utilidad tiene tres modos de operación:

- Detection (-i): detects and fixes the existing FXO channels and saves the configuration to

```
fxotune.conf
```

- Modo de volcado (-d): genera los archivos de forma de onda en fxotune_dump.vals
- Modo de inicio (-s): lee el archivo fxotune.conf y lo aplica a los módulos FXO

Es importante entender que deberá insertar la instrucción fxotune –s en la carga del sistema antes de iniciar Asterisk:

```
#modprobe dahdi
#modprobe wctdm
#fxotune -s
```

### Cancelación de eco

La mayoría de los algoritmos de cancelación de eco operan generando múltiples copias de la señal recibida, en las que cada una está retrasada una cantidad específica de tiempo. La cantidad de taps del filtro determina el tamaño del retardo del eco que debe cancelarse. Estas copias retrasadas se ajustan y se restan de la señal recibida. El truco consiste en ajustar solo la señal retrasada para eliminar el eco sin usar demasiados ciclos de CPU. Desde la perspectiva del usuario, es importante elegir un algoritmo de cancelación de eco apropiado. El predeterminado es MG2; sin embargo, hay dos opciones adicionales disponibles: la Cancelación de Eco de Alto Rendimiento (HPEC) de Sangoma (anteriormente Digium) y la cancelación de eco de código abierto (OSLEC) desarrollada por David Rowe.

OSLEC (https://www.rowetel.com/?page_id=454) se ha fusionado con el kernel de Linux — reside en el área `drivers/staging/echo` del kernel — y DAHDI se compila contra él en lugar de distribuir una descarga separada. Para cambiar el algoritmo de cancelación de eco, establezca el parámetro `echo_can` en `/etc/dahdi/system.conf`. Por ejemplo:

```
echo_can=oslec
```

La cancelación de eco en Asterisk se controla mediante tres parámetros en el archivo /etc/asterisk/chan-

```
dahdi.conf.
```

- **echocancel**: Desactiva o activa la cancelación de eco. Debe mantener esta función activada. Acepta "yes" o el número de taps. (Explanation: How does echo canceling work? Most echo canceling algorithms operate by generating multiple copies of a received signal, with each being delayed by a small interval. This little flow is called a "tap". The number of taps determines the echo delay that can be cancelled. These copies are delayed, adjusted, and subtracted from the original signal. The trick is to adjust the delayed signal exactly to what is necessary to remove the echo.)
- **echocancelwhenbridged**: Activa o desactiva el cancelador de eco durante una llamada TDM pura. Esto usualmente no es necesario.
- **rxgain**: Ajusta la ganancia de recepción de audio para aumentar o disminuir el volumen de recepción (-100% a 100%).
- **txgain**: Ajusta la ganancia de transmisión de audio para aumentar o disminuir el volumen de transmisión (-100% a 100%).

For example:

```
echocancel=yes
echocancelwhenbridged=yes
txgain=-10%
rxgain=10%
```

#### Opciones de facturación

Estas opciones cambian cómo se registra la información de llamadas en la base de datos de registros de detalle de llamadas (CDR). amaflags: Configura los indicadores AMA que afectan la categorización del CDR. Acepta los siguientes valores:

- billing
- documentation
- omit
- default

accountcode: Configura un código de cuenta para un canal específico. Puede contener cualquier valor alfanumérico—usualmente el nombre del departamento o del usuario.

```
accountcode=finance
amaflags=billing
```

### Opciones de progreso de la llamada

Estos elementos se utilizan para obtener información sobre el progreso de la llamada. En interfaces públicas, puede ser útil detectar el progreso de la llamada y determinar si fue contestada o está ocupada. La detección de ocupado es altamente experimental y está regulada por parámetros específicos.

```
busydetect=yes
busycount=4
busypattern=500,500
callprogress=yes
progzone=br
```

Estos parámetros (arriba) especifican si la interfaz intentará detectar el tono de ocupado, cuántos tonos se usarán para una detección exitosa y cuál es el patrón de ocupado. La detección de ocupado es en gran medida experimental, y algunos parámetros adicionales pueden modificarse en el Makefile. Para detectar la respuesta de una llamada, lo cual es esencial para una facturación precisa, es posible usar la inversión de polaridad para señalar el momento exacto de la respuesta. Esto es importante si planeas cobrar la llamada o simplemente deseas una facturación precisa para comparaciones. Normalmente debes contactar a la compañía telefónica para solicitar este servicio.

```
answeronpolarityswitch=yes
```

En algunos países, también es posible detectar la finalización de la llamada mediante la inversión de polaridad.

```
hanguponpolarityswitch=yes
```

#### Opciones para teléfonos

Estas opciones se usan para teléfonos conectados a las interfaces FXS. Todas las funcionalidades entregadas a teléfonos analógicos conectados directamente a las interfaces DAHDI son controladas por Asterisk.

- **adsi** (Analog Display Services Interface): Este es un conjunto de normas de telecomunicaciones usadas por algunas telcos para ofrecer servicios como la compra de boletos.
- **cancallforward**: Habilita o deshabilita el desvío de llamadas (*72 para habilitar y *73 para deshabilitar).
- **calleridcallwaiting**: Habilita la identificación de llamada recibida durante una indicación de llamada en espera (Sí/No).
- **immediate**: En modo inmediato, en lugar de proporcionar un tono de marcado, el canal salta inmediatamente a la extensión "s" en el contexto definido. Esto se usa para crear líneas directas.
- **threewaycalling**: Habilita o deshabilita la conferencia de tres vías.
- **mailbox**: Advierte al usuario sobre mensajes de buzón de voz disponibles. Puede ser una señal audible o un indicador visual (si el teléfono soporta esta función). El argumento es el número del buzón.
- **callgroup**: Agrupa teléfonos para marcar o para recoger.
- **pickupgroup**: Grupo de teléfonos para recogida de llamadas.

### Comandos útiles de la CLI de DAHDI

Una vez que Asterisk está en ejecución con los canales DAHDI cargados, puedes inspeccionar el estado de los canales desde la CLI de Asterisk. Estos comandos siguen vigentes en Asterisk 22:

```
*CLI> dahdi show channels
*CLI> dahdi show channel 1
*CLI> module reload chan_dahdi.so
```

### Formato de canal DAHDI

Los canales DAHDI usan el siguiente formato en el dialplan:

```
DAHDI/[g]<identifier>[c][r<cadence>]
<identifier> - Physical channel numeric identifier
[g] - Group identifier
[c] - Answer confirmation. A number is not considered until the callee presses "#"
[r] - customized ringing
[cadence] - Integer from 1 to 4
```

Por ejemplo:

```
DAHDI/2     - channel 2
DAHDI/g1    - First available channel in group 1
```

## Canales digitales (E1/T1/PRI / TDM)

A partir de Asterisk 22, DAHDI y libpri siguen totalmente soportados, pero los trunks digitales TDM (E1/T1/ISDN PRI) están siendo reemplazados cada vez más por trunks SIP en nuevas implementaciones. Esta sección sigue siendo totalmente aplicable donde se requiera conectividad TDM; en entornos greenfield, el trunking SIP (Chapter 3) usualmente brinda la misma densidad de canales sin hardware de telefonía.

Los canales digitales son extremadamente comunes, por lo que necesitarás aprender a implementar estos canales si deseas enfocarte en clientes grandes. Cuando el número de canales es alto—usualmente más de 8—es bastante frecuente usar interfaces digitales como T1/E1/J1. T1 es muy común en EE. UU., mientras que E1 es común en Europa y J1 en Japón. Estos tipos de canales permiten una buena densidad de circuitos—24 por canal T1 y 30 por canales E1.

En América Latina, China y África, es común usar un tipo de señalización asociada al canal (CAS) conocida como MFC/R2. Este capítulo examinará cómo implementar MFC/R2 usando la biblioteca OpenR2. En EE. UU. y Europa, la Integrated Services Digital Networks (ISDN) PRI es la señalización más común. El capítulo también discutirá la ISDN Basic Rate Interface (BRI), que es muy común en Europa en aplicaciones de rango medio.

Todos los ejemplos del libro se concentran en los canales DAHDI. Algunas tarjetas están implementadas usando canales propietarios, así que por favor consulte con su fabricante para obtener más detalles sobre cómo configurar su tarjeta específica.

### Objetivos

Al final de este capítulo podrás:

- Reconocer los términos principales usados en telefonía digital
- Diferenciar la señalización CAS y CCS
- Diferenciar la señalización R2 e ISDN
- Configurar interfaces con señalización ISDN
- Configurar interfaces con señalización R2

### Líneas digitales E1/T1

Líneas digitales E1/T1 son una opción siempre que necesite implementar un gran número de canales. Un solo circuito E1 es capaz de 30 llamadas simultáneas, y puede contar con funciones como marcación directa entrante (DID), identificación de llamante (Caller ID) y señalización avanzada. La línea E1/T1 puede llegar a su empresa de varias maneras usando par trenzado, fibra y microondas, según su país. Las líneas digitales se entregan a su empresa mediante UTP, fibra o microondas. Se utilizan módems y multiplexores (MUX) para proporcionar la línea física. La conexión a una línea T1 siempre se basa en un conector RJ45. Sin embargo, las líneas E1 también pueden provisionarse usando BNC. Es muy importante conocer de antemano el tipo de conector que recibirá, principalmente en líneas E1. Usualmente todo el equipo hasta el RJ45 lo proporciona el TELCO.

![Cómo se provisionan los circuitos E1/T1: la telco puede entregar el trunk a través de cobre UTP (módem HDSL para E1, o una conexión directa de tarjeta para T1), a través de fibra óptica mediante un multiplexor óptico, o mediante un enlace de radio microondas.](../images/10-legacy-fig05.png)

![¿UTP o BNC? La mayoría de las tarjetas digitales usan conectores RJ45 (UTP), pero algunas líneas E1 se entregan en coaxial dual BNC, en cuyo caso se necesita un balun para adaptar el par coaxial al conector RJ45 de la tarjeta.](../images/10-legacy-fig06.png)

#### ¿Cómo se convierte la voz en bits?

La señal analógica se muestrea 8,000 veces por segundo para crear una versión digital de la voz analógica. Esta codificación se conoce como modulación por código de pulsos (PCM). En EE. UU. y Japón, la señal se codifica usando law (en Asterisk, referida como ulaw). En el resto del mundo, la codificación es alaw.

![Modulación por impulsos codificados (PCM): la señal de voz analógica de 4 kHz se muestrea 8 000 veces por segundo (Nyquist) y se codifica en una corriente digital de 64 Kbps de bits.](../images/10-legacy-fig07.png)

#### Multiplexación por División de Tiempo

Las líneas analógicas tienen sentido cuando necesitas solo unos pocos canales. Al usar multiplexación por división de tiempo (TDM), es posible empaquetar varios canales en una única conexión de datos. Cuando deseas un gran número de circuitos, la compañía telefónica normalmente te proporcionará un trunk digital, que es un circuito de datos en el que la voz se transporta en formato digital usando PCM. Cada ranura de tiempo usa 64 Kbps de ancho de banda para transportar un solo canal de voz.

![Multiplexación por división de tiempo en E1 y T1: un marco E1 transporta 32 ranuras a 2048 Kbps (DS0 #0 para sincronización de marco, DS0 #16 para señalización), mientras que un marco T1 transporta 24 ranuras a 1544 Kbps usando un bit para sincronización y un esquema de bit robado para señalización.](../images/10-legacy-fig08.png)

En EE. UU., el tronco digital más común es T1, que tiene 24 líneas disponibles; en Europa y América Latina, los troncales E1 tienen 30 líneas. Algunas compañías ofrecen un T1/E1 fraccional con menos canales. Señalización de bit robado A veces un tronco T1 usa un esquema de bit robado donde se toma un bit para la señalización. En los troncales T1, el canal de datos/voz se transmite a 56 Kbps en cada ranura de tiempo. Como puede observar, cuando se usa el bit robado, el circuito T1 no pierde dos ranuras para sincronización y señalización.

#### Código de línea T1/E1

Los T1 y E1 son en realidad circuitos de datos y tienen una codificación de datos que determina la forma en que se interpretan los bits. Para los E1, el código de línea más común es HDB3 para la capa 1 y CCS para la capa 2. La forma más fácil de saber cómo está configurado su tronco digital es preguntar a la TELCO por esta información. Necesitará esta información para configurar el archivo /etc/dahdi/system.conf.

#### Señalización T1/E1

Es importante entender que las líneas T1/E1 pueden entregarse usando diferentes tipos de señalización, como:

- T1 con señalización de bit robado
- T1 con señalización ISDN
- E1 con MFC/R2 (CAS - Señalización Asociada al Canal)
- E1 con señalización ISDN

ISDN se usa a menudo en Europa y EE. UU. Es una red de voz digital, estandarizada por la Unión Internacional de Telecomunicaciones (ITU) en 1984. ISDN proporciona dos tipos de canales:

- Canales portadores
  - Voz
  - Datos
- Canales de datos
  - Señalización fuera de banda
  - Señalización LAPD
  - Q.931

Normalmente, una línea ISDN se proporciona usando dos medios físicos:

- Interfaz de tasa básica (BRI)
  - Conocida como 2B+D
  - Dos canales portadores (64K) y un canal de datos (16K)
  - Utiliza un par de cables de cobre con 148Kbps.
- Interfaz de tasa primaria (PRI)
  - Proporcionada mediante un trunk T1/E1
  - 23B+D para T1s
  - 30B+D para E1s

A veces, los circuitos E1 utilizan un esquema de señalización CAS llamado MFC/R2, que fue definido por la ITU como una norma conocida como Q.421/Q441. Esto se encuentra frecuentemente en América Latina y Asia. Varias compañías de telefonía en estos países usan variantes personalizadas de MFC/R2. Por lo tanto, necesitará conocer la variación del país correcta para que funcione.

### ISDN BRI

Los canales que usan señalización ISDN BRI son muy populares en Europa. La mayoría de las tarjetas ISDN BRI para Asterisk soportan una interfaz S/T con capacidades NT y TE. La conexión TE (terminal) es la que se usa para conectar al TELCO o a otros PBX configurados como terminación de red (NT). El NT se usa para conectar teléfonos y PBX configurados como TE. ISDN BRI proporciona dos canales de datos/voz y un canal de señalización. Las tarjetas ISDN BRI están disponibles de varios proveedores de tarjetas de interfaz para Asterisk.

### Elegir una tarjeta de telefonía para su servidor Asterisk

Hay varios fabricantes de tarjetas digitales compatibles con Asterisk. La elección de una tarjeta depende de algunos de los siguientes factores:

#### Bus de datos

Hay varios tipos de bus en su PC. Es muy importante que tenga la tarjeta adecuada para su servidor. La siguiente visión general describe las tarjetas más usadas frecuentemente:

- 32 bits PCI 5 V encontrado en la mayoría de los ordenadores, incluidos los de escritorio
  - Sangoma (formerly Digium) TE405, TE407, TE205, TE207, TE120, TE122, B410, TDM2400, TDM800, TDM410, and TC400
  - Sangoma A101, A102, and A104
- 32/64 bits PCI 3.3 V, básicamente encontrado en servidores
  - Sangoma (formerly Digium) TE410, TE412, TE210, TE212, TE120, TE122, B410, TDM2400, TDM800, TDM410, and TC400
- PCI Express encontrado en ordenadores de escritorio y servidores
  - Sangoma (formerly Digium) TE420, TE220, TE121, AEX2400, and AEX800
  - Sangoma A101, A102, and A104

These card families originated at Digium, which Sangoma acquired in 2018; they are now sold and supported under the Sangoma brand. Many of the older SKUs listed here have been discontinued, so confirm current model availability at www.sangoma.com before purchasing.

- MiniPCI encontrado en sistemas empotrados
  - OpenVOX A100M(FXO), B100M(ISDN BRI), B200M(ISDN BRI), and B400M(ISDN BRI)
- USB 2.0 encontrado en la mayoría de PCs modernos. Las soluciones basadas en USB permiten una gran densidad de canales analógicos y digitales. Este bus soporta 480 Mbps, y cada canal de voz ocupa 64 Kbps. Al usar hubs USB, es posible alcanzar densidades de hasta mil puertos analógicos en un solo puerto.
  - Xorcom Astribank (FXS, FXO, E1-ISDN, E1-R2)
- Ethernet. La mayor ventaja de Ethernet es permitir que la tarjeta sea conectada por más de un servidor. Las soluciones de alta disponibilidad son normalmente la aplicación principal para estos dispositivos. La fortaleza de esta solución es el uso de servidores sin ranuras PCI libres o servidores blade.
  - Redfone FoneBridge (up to four E1 circuits)

### Uso de cancelación de eco por hardware

La cancelación de eco por hardware reduce la carga en la CPU del host. Para tarjetas con más de una única interfaz E1, la cancelación de eco por hardware puede ayudar a aliviar su procesador. Los nuevos canceladores de eco por software mejorados, como el OSLEC, están reduciendo la necesidad de un cancelador de eco por hardware. Para elegir entre canceladores de eco por hardware y por software, debe considerar la cantidad de potencia de procesamiento disponible en su servidor y el número de circuitos E1. Un proceso de cancelación de eco puede usar hasta nueve MIPS (millones de instrucciones por segundo) por canal de voz con 128 taps de amplitud usando OSLEC (Reference: Xorcom Ltd.). Si considera 1 ciclo de CPU por cada instrucción (lo cual no siempre es correcto según el procesador y la implementación del software), estamos hablando de 1.080 GHz para cuatro E1.

#### Tipo de señalización

Seleccionar el tipo de señalización (p. ej., T1 CAS, T1 PRI, E1 CAS R2 o E1 CAS ISDN) no es una tarea fácil. Realmente depende de lo que tenga disponible en su zona y a qué precio. La Señalización de Canal Común (CCS) suele ser mejor que la señalización asociada al canal (CAS). Sin embargo, a menudo no está disponible. En EE. UU., normalmente puede elegir, ya que la mayoría de los TELCOS ofrecen T1 CAS para usuarios regulares y T1 PRI para usuarios avanzados (p. ej., centros de llamadas). En América Latina, E1 CAS R2 es predominante, pero ISDN PRI está disponible en algunas ciudades.

![La arquitectura de software DAHDI: Asterisk se comunica con el controlador de canal `chan_dahdi`, que a su vez carga las bibliotecas de protocolo libpri (ISDN), libopenr2 (MFC/R2) y libss7 (SS7); estas se sitúan sobre la interfaz `/dev/dahdi`, el controlador del kernel DAHDI y el controlador del kernel de la interfaz específica de la tarjeta.](../images/10-legacy-fig09.png)

Implementar R2 es necesario para instalar una biblioteca conocida como OpenR2 (www.libopenr2.org), desarrollada por Moises Silva, y para parchear Asterisk antes de la instalación—un procedimiento sencillo que se muestra más adelante en este capítulo. La biblioteca ha pasado varias pruebas y está en producción en varios de nuestros clientes. En mi opinión, ISDN es siempre la mejor opción, si está disponible. Algunos proveedores pueden tener acceso al sistema de señalización 7 (SS7), que es una señalización CCS disponible entre compañías telefónicas. Existen soluciones propietarias y de código abierto para SS7. La biblioteca libss7 se usa para soportar SS7 en Asterisk.

### Configuración de canales de telefonía Asterisk

Configurar una tarjeta de interfaz de telefonía implica varios pasos necesarios. En este capítulo, mostraremos tres de los escenarios más comunes:

- Conexión digital usando ISDN PRI
- Conexión digital usando ISDN BRI
- Conexión digital usando MFC/R2

Hay dos formas de configurar los canales DAHDI. La primera es configurarlos manualmente con control total de todos los parámetros. La segunda forma es usar la utilidad dahdi_genconf para detectar y configurar las tarjetas.

#### Detección automática y configuración

Gracias al equipo de desarrollo de DAHDI, ahora tenemos detección y configuración automáticas de las tarjetas. Paso 1: Para generar la configuración automáticamente, use la utilidad dahdi_genconf, que detectará la tarjeta y generará los archivos /etc/dahdi/system.conf y dahdi-channels.conf.

```
dahdi_genconf
```

Step 2: En la última línea del archivo chan_dahdi.conf, incluya el archivo dahdi-channels.conf

```
#include dahdi_channels.conf
```

Paso 3: Comente todos los módulos no utilizados en el archivo modules o simplemente use:

```
dahdi_genconf modules
```

#### Configuración manual

Otra opción es configurar las interfaces manualmente. A continuación se presentan algunos ejemplos de la configuración para canales DAHDI.

##### Ejemplo #1 – Dos canales T1/ E1 usando ISDN

Pasos requeridos:

1. Instalación de TE205P o TE210P
2. `/etc/dahdi/system.conf` file configuration
3. DAHDI driver loading
4. `dahdi_test` utility
5. `dahdi_cfg` utility
6. `chan_dahdi.conf` file configuration
7. Asterisk load and testing

Paso 1: Instalación de TE205P. Antes de instalar TE205P, es importante comprender las diferencias entre las tarjetas TE205P y TE210P. La tarjeta TE210P utiliza un bus de 64 bits alimentado por 3.3 voltios que se encuentra casi exclusivamente en las placas base de servidores. Tenga cuidado al especificar esta tarjeta de interfaz; asegúrese de que su hardware soporte un bus de 64 bits y 3.3 V. La tarjeta TE205P usa un PCI de 5 V, que suele encontrarse en computadoras de escritorio. Hemos elegido la tarjeta de interfaz TE205P con dos tramos para este ejemplo porque es más fácil reducirla a una tarjeta de un solo tramo o ampliarla a una tarjeta de cuatro tramos. Estas tarjetas se venden ahora bajo la marca Sangoma (anteriormente Digium).

![A Sangoma/Digium TE205P dual-span E1/T1 card: the two RJ45 ports accept the digital trunks, and an on-board jumper (the E1/T1/J1 selector) sets the line standard.](../images/10-legacy-fig10.png)

```
Step 2: /etc/dahdi/system.conf configuration file
```

La configuración de tarjetas digitales TDM es un poco diferente de la configuración de sus contrapartes analógicas. Primero, necesitaremos configurar los spans de la tarjeta y luego los canales. Los spans se numeran secuencialmente según el orden de reconocimiento de las tarjetas. En otras palabras, si tiene más de una tarjeta de interfaz, es difícil saber a cuál span pertenece cada una. Use `dahdi_hardware` para verificar qué hardware está instalado en cada span. Ejemplo #1 (2xT1 PRI)

```
span=1,1,0,esf,b8zs
span=2,0,0,esf,b8zs
bchan=1-23
dchan=24
bchan=25-47
dchan=48
defaultzone=us
loadzone=us
```

Ejemplo #2 (2xE1 PRI)

```
span=1,1,0,ccs,hdb3,crc4 # not always necessary, consult Telco.
span=2,0,0,ccs,hdb3,crc4
bchan=1-15, 17-31
dchan=16
bchan=33-47, 49-63
dchan=48
defaultzone=br
loadzone=br
```

Ejemplo #3 (4xBRI)

```
loadzone=de
defaultzone=de
span=1,1,0,ccs,ami
bchan=1,2
hardhdlc=3
span=2,0,0,ccs,ami
bchan=4,5
hardhdlc=6
span=3,0,0.ccs.ami
bchan=7,8
hardhdlc=9
span=4,0,0,ccs,ami
bchan=10,11
hardhdlc=12
```

Paso 3: Cargando controladores del kernel Verifique qué controlador necesita instalar usando dahdi_hardware.

```
dahdi_hardware
pci:0000:04:02.0     wcte2xxp    e159:0001 Sangoma Wildcard TE205P T1/E1 Board
```

Para cargar, use:

```
modprobe dahdi
modprobe wct2xxp
```

Step 4: Using dahdi_test, check the missing interrupts  
You may verify the number of interrupt misses using the dahdi_test utility compiled with the DAHDI cards. A number below 99.987% indicates possible problems. You will find dahdi_test in

```
/usr/sbin.
#./dahdi_test
Opened pseudo zap interface, measuring accuracy...
99.987793% 100.000000% 100.000000% 100.000000% 100.000000% 100.000000%
100.000000%
100.000000% 100.000000% 100.000000% 100.000000% 100.000000% 100.000000%
100.000000% 100.000000%
100.000000% 100.000000% 100.000000% 100.000000% 99.987793% 100.000000%
100.000000% 100.000000%
100.000000% 100.000000% 100.000000%
--- Results after 26 passes ---
Best: 100.000000 -- Worst: 99.987793 -- Average: 99.999061
```

Paso 5: Uso de la utilidad dahdi_cfg Esta es la salida correcta de dahdi_cfg para un tramo E1 fraccional (15 puertos) y dos puertos FXO.

```
#./dahdi_cfg -vvvv
Dahdi configuration
======================
SPAN 1: CCS/HDB3 Build-out: 0 db (CSU)/0-133 feet (DSX-1)
Channel map:
Channel 01: Clear channel (Default) (Slaves: 01)
Channel 02: Clear channel (Default) (Slaves: 02)
Channel 03: Clear channel (Default) (Slaves: 03)
Channel 04: Clear channel (Default) (Slaves: 04)
Channel 05: Clear channel (Default) (Slaves: 05)
Channel 06: Clear channel (Default) (Slaves: 06)
Channel 07: Clear channel (Default) (Slaves: 07)
Channel 08: Clear channel (Default) (Slaves: 08)
Channel 09: Clear channel (Default) (Slaves: 09)
Channel 10: Clear channel (Default) (Slaves: 10)
Channel 11: Clear channel (Default) (Slaves: 11)
Channel 12: Clear channel (Default) (Slaves: 12)
Channel 13: Clear channel (Default) (Slaves: 13)
Channel 14: Clear channel (Default) (Slaves: 14)
Channel 15: Clear channel (Default) (Slaves: 15)
Channel 16: D-channel (Default) (Slaves: 16)
16 channels configured.
```

Step 6: Configuración de DAHDI en el archivo /etc/asterisk/chan_dahdi.conf Example #1 (2xT1)

```
callerid="John Doe"<(555)555-1111>
switchtype=national
signalling =pri_cpe
context=from-pstn
group = 1
channel => 1-23
group =2
channel => 25-47
```

Ejemplo #2 (2xE1)

```
callerid="Flavio Eduardo" <4830258580>
switchtype=euroisdn
signalling = pri_cpe
group = 1
channel => 1-15;17-31
group =2
channel => 32-46;48-62
```

Ejemplo #3 (4xBRI)

```
signaling=bri_cpe
switchtype=euroisdn
group=1
context=from-pstn
channel=>1,2,4,5,7,8,10,11
```

Use signaling=bri_cpe_ptmp para BRI punto a multipunto. Actualmente, BRI punto a multipunto no es compatible en modo NT.

#### Loading the kernel drivers

Después de configurar los controladores, puede simplemente reiniciar el servidor. Si ha instalado DAHDI con `make config`, no necesitará hacer nada extra. El controlador del kernel se cargará y configurará automáticamente. Sin embargo, a veces es útil cargar y descargar los controladores manualmente. Example:

```
modprobe wct11xp
dahdi_cfg -vvvvv
```

The first command loads the driver and the second, dahdi_cfg, applies the configuration to the kernel driver.

### Solución de problemas

A veces las cosas no funcionan a la primera. Revisemos algunos recursos para solucionar problemas de DAHDI. Paso 1: Verifique si la tarjeta está siendo reconocida por el sistema operativo. Las tarjetas Sangoma/Digium suelen ser reconocidas como el módem ISDN.

```
lspci -v
00:00.0 Host bridge: Intel Corporation E7230/3000/3010 Memory Controller Hub
00:01.0 PCI bridge: Intel Corporation E7230/3000/3010 PCI Express Root Port
00:1c.0 PCI bridge: Intel Corporation 82801G (ICH7 Family) PCI Express Port 1 (rev 01)
00:1c.4 PCI bridge: Intel Corporation 82801GR/GH/GHM (ICH7 Family) PCI Express Port 5 (rev
01)
00:1c.5 PCI bridge: Intel Corporation 82801GR/GH/GHM (ICH7 Family) PCI Express Port 6 (rev
01)
00:1d.0 USB Controller: Intel Corporation 82801G (ICH7 Family) USB UHCI Controller #1 (rev
01)
00:1d.1 USB Controller: Intel Corporation 82801G (ICH7 Family) USB UHCI Controller #2 (rev
01)
00:1d.2 USB Controller: Intel Corporation 82801G (ICH7 Family) USB UHCI Controller #3 (rev
01)
00:1d.7 USB Controller: Intel Corporation 82801G (ICH7 Family) USB2 EHCI Controller (rev 01)
00:1e.0 PCI bridge: Intel Corporation 82801 PCI Bridge (rev e1)
00:1f.0 ISA bridge: Intel Corporation 82801GB/GR (ICH7 Family) LPC Interface Bridge (rev 01)
00:1f.1 IDE interface: Intel Corporation 82801G (ICH7 Family) IDE Controller (rev 01)
00:1f.2 IDE interface: Intel Corporation 82801GB/GR/GH (ICH7 Family) SATA IDE Controller (rev
01)
00:1f.3 SMBus: Intel Corporation 82801G (ICH7 Family) SMBus Controller (rev 01)
01:00.0 PCI bridge: Intel Corporation 6702PXH PCI Express-to-PCI Bridge A (rev 09)
01:00.1 PIC: Intel Corporation 6700/6702PXH I/OxAPIC Interrupt Controller A (rev 09)
02:08.0 SCSI storage controller: LSI Logic / Symbios Logic SAS1068 PCI-X Fusion-MPT SAS (rev
01)
03:00.0 PCI bridge: Intel Corporation 6702PXH PCI Express-to-PCI Bridge A (rev 09)
04:02.0 Network controller: Tiger Jet Network Inc. Tiger3XX Modem/ISDN interface
05:00.0 Ethernet controller: Broadcom Corporation NetXtreme BCM5721 Gig. Eth.PCI Express (rev
11)
07:00.0 Ethernet controller: Realtek Semiconductor Co., Ltd. RTL-8139/8139C/8139C+ (rev 10)
07:05.0 VGA compatible controller: ATI Technologies Inc ES1000 (rev 02)
```

Paso 2: Verifique si el controlador del kernel se está cargando correctamente usando:

```
modprobe wct11xp
dmesg
TE110P: Setting up global serial parameters for E1 FALC V1.2
TE110P: Successfully initialized serial bus for card
TE110P: Span configured for CAS/HDB3
Calling startup (flags is 4099)
Found a Wildcard: Sangoma Wildcard TE110P T1/E1
TE110P: Span configured for CCS/HDB3/CRC4
Calling startup (flags is 4099)
dahdi: Registered tone zone 0 (United States / North America)
wcte1xxp: Setting yellow alarm
```

Paso 3: Verifique el estado de las alarmas relacionadas con la capa física de la conexión. Para verificar la capa física de la conexión E1, puede usar el siguiente comando CLI de Asterisk.

```
dahdi show status
```

Las alarmas indican problemas con el puerto: Alarma roja: No se puede mantener la sincronización con el conmutador remoto. Esto suele ser un problema físico, como un código de línea o una incompatibilidad de encuadre. Alarma amarilla: Señala que el conmutador remoto está en alarma roja. Esto indica que el conmutador remoto no está recibiendo sus transmisiones. Alarma azul: Recibe todos los 1 sin encuadrar en todas las ranuras de tiempo; dahdi_tool actualmente no detecta una alarma azul. Loopback: El puerto está en bucle local o remoto

```
vtsvoffice*CLI> dahdi show status
Description                              Alarms     IRQ        bpviol     CRC4
Sangoma Wildcard E100P E1/PRA Card 0      OK         0          0          0
Wildcard X100P Board 1                   OK         0          0          0
Wildcard X100P Board 2                   RED        0          0          0
```

Paso 4: Para detectar problemas con DAHDI en el servidor Asterisk, primero verifique si los canales están siendo reconocidos usando:

```
dahdi show channels
pabxip01*CLI> dahdi show channels
   Chan Extension  Context         Language   MOH Interpret
 pseudo            default                    default
      1            from-pstn                  default
      2            from-pstn                  default
      3            from-pstn                  default
      4            from-pstn                  default
      5            from-pstn                  default
      6            from-pstn                  default
      7            from-pstn                  default
      8            from-pstn                  default
      9            from-pstn                  default
     10            from-pstn                  default
     11            from-pstn                  default
     12            from-pstn                  default
     13            from-pstn                  default
     14            from-pstn                  default
     15            from-pstn                  default
     17            from-pstn                  default
     18            from-pstn                  default
     19            from-pstn                  default
     20            from-pstn                  default
     21            from-pstn                  default
     22            from-pstn                  default
     23            from-pstn                  default
     24            from-pstn                  default
     25            from-pstn                  default
     26            from-pstn                  default
     27            from-pstn                  default
     28            from-pstn                  default
     29            from-pstn                  default
     30 2171       from-pstn                  default
     31 2171       from-pstn                  default
```

Paso 5: Verifique el estado de la capa 3 de ISDN, también conocida como q.931. Puede comprobar si la capa 3 de ISDN está activa usando: `pri show spans` (para listar todos los spans) o `pri show span <n>` para un span específico:

```
vtsvoffice*CLI> pri show span 1
Primary D-channel: 16
Status: Provisioned, Up, Active
Switchtype: EuroISDN
Type: CPE
Window Length: 0/7
Sentrej: 0
SolicitFbit: 0
Retrans: 0
Busy: 0
Overlap Dial: 0
T200 Timer: 1000
T203 Timer: 10000
T305 Timer: 30000
T308 Timer: 4000
T313 Timer: 4000
N200 Counter: 3
```

Use `pri show spans` (plural) para listar el estado de todos los tramos PRI configurados de una vez.

Verifique un canal específico. dahdi show channel x:

```
vtsvoffice*CLI> dahdi show channel 1
Channel: 1
File Descriptor: 21
Span: 1
Extension:
Dialing: no
Context: entrada
Caller ID: 4832341689
Calling TON: 33
Caller ID name:
Destroy: 0
InAlarm: 0
Signalling Type: PRI Signalling
Radio: 0
Owner: <None>
Real: <None>
Callwait: <None>
Threeway: <None>
Confno: -1
Propagated Conference: -1
Real in conference: 0
DSP: no
Relax DTMF: no
Dialing/CallwaitCAS: 0/0
Default law: alaw
```

debug pri span x: Si después de todo aún tienes problemas, comienza a depurar el pri span. Este comando habilita una depuración detallada de llamadas ISDN. Es un comando importante cuando piensas que algo no está correcto. Puedes detectar dígitos marcados incorrectamente y otros problemas. A continuación presentamos el ejemplo de una salida de depuración para una llamada exitosa. Consulta este ejemplo si necesitas comparar una llamada fallida con una sin problemas. Un consejo es usar core set verbose=0 para recibir solo los mensajes ISDN q.931.

```
-- Making new call for cr 32833
> Protocol Discriminator: Q.931 (8)  len=57
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: SETUP (5)
> [04 03 80 90 a3]
> Bearer Capability (len= 5) [ Ext: 1  Q.931 Std: 0  Info transfer capability: Speech (0)
>                              Ext: 1  Trans mode/rate: 64kbps, circuit-mode (16)
>                              Ext: 1  User information layer 1: A-Law (35)
> [18 03 a9 83 81]
> Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
>                        ChanSel: Reserved
>                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
>                       Ext: 1  Channel: 1 ]
> [28 0e 46 6c 61 76 69 6f 20 45 64 75 61 72 64 6f]
> Display (len=14) @h@>[ Flavio Eduardo ]
> [6c 0c 21 80 34 38 33 30 32 35 38 35 39 30]
> Calling Number (len=14) [ Ext: 0  TON: National Number (2)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1)
>                           Presentation: Presentation permitted, user number not screened
(0) '4830258590' ]
> [70 09 a1 33 32 32 34 38 35 38 30]
> Called Number (len=11) [ Ext: 1  TON: National Number (2)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1) '32248580' ]
> [a1]
> Sending Complete (len= 1)
< Protocol Discriminator: Q.931 (8)  len=10
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: CALL PROCEEDING (2)
< [18 03 a9 83 81]
< Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
<                        ChanSel: Reserved
<                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
<                       Ext: 1  Channel: 1 ]
-- Processing IE 24 (cs0, Channel Identification)
< Protocol Discriminator: Q.931 (8)  len=9
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: ALERTING (1)
< [1e 02 84 88]
< Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Public network serving the remote user (4)
<                               Ext: 1  Progress Description: Inband information or
appropriate pattern now available. (8) ]
-- Processing IE 30 (cs0, Progress Indicator)
< Protocol Discriminator: Q.931 (8)  len=64
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: SETUP (5)
< [04 03 80 90 a3]
< Bearer Capability (len= 5) [ Ext: 1  Q.931 Std: 0  Info transfer capability: Speech (0)
<                              Ext: 1  Trans mode/rate: 64kbps, circuit-mode (16)
<                              Ext: 1  User information layer 1: A-Law (35)
< [18 03 a1 83 82]
< Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Preferred Dchan: 0
<                        ChanSel: Reserved
<                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
<                       Ext: 1  Channel: 2 ]
< [1c 15 91 a1 12 02 01 bc 02 01 0f 30 0a 02 01 01 0a 01 00 a1 02 82 00]
< Facility (len=23, codeset=0) [ 0x91, 0xa1, 0x12, 0x02, 0x01, 0xbc, 0x02, 0x01, 0x0f, '0',
0x0a, 0x02, 0x01, 0x01, 0x0a, 0x01, 0x00, 0xa1, 0x02, 0x82, 0x00 ]
< [1e 02 82 83]
< Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Public network serving the local user (2)
<                               Ext: 1  Progress Description: Calling equipment is non-ISDN.
(3) ]
< [6c 0c 21 83 34 38 33 32 32 34 38 35 38 30]
< Calling Number (len=14) [ Ext: 0  TON: National Number (2)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1)
<                           Presentation: Presentation allowed of network provided number (3)
'4832248580' ]
< [70 05 c1 38 35 38 30]
< Called Number (len= 7) [ Ext: 1  TON: Subscriber Number (4)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1) '8580' ]
< [a1]
< Sending Complete (len= 1)
-- Making new call for cr 5720
-- Processing Q.931 Call Setup
-- Processing IE 4 (cs0, Bearer Capability)
-- Processing IE 24 (cs0, Channel Identification)
-- Processing IE 28 (cs0, Facility)
Handle Q.932 ROSE Invoke component
-- Processing IE 30 (cs0, Progress Indicator)
-- Processing IE 108 (cs0, Calling Party Number)
-- Processing IE 112 (cs0, Called Party Number)
-- Processing IE 161 (cs0, Sending Complete)
> Protocol Discriminator: Q.931 (8)  len=10
> Call Ref: len= 2 (reference 5720/0x1658) (Terminator)
> Message type: CALL PROCEEDING (2)
> [18 03 a9 83 82]
> Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
>                        ChanSel: Reserved
>                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
>                       Ext: 1  Channel: 2 ]
> Protocol Discriminator: Q.931 (8)  len=14
> Call Ref: len= 2 (reference 5720/0x1658) (Terminator)
> Message type: CONNECT (7)
> [18 03 a9 83 82]
> Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
>                        ChanSel: Reserved
>                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
>                       Ext: 1  Channel: 2 ]
> [1e 02 81 82]
> Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Private network serving the local user (1)
>                               Ext: 1  Progress Description: Called equipment is non-ISDN.
(2) ]
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: CONNECT ACKNOWLEDGE (15)
< Protocol Discriminator: Q.931 (8)  len=9
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: PROGRESS (3)
< [1e 02 84 82]
< Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Public network serving the remote user (4)
<                               Ext: 1  Progress Description: Called equipment is non-ISDN.
(2) ]
-- Processing IE 30 (cs0, Progress Indicator)
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: CONNECT (7)
> Protocol Discriminator: Q.931 (8)  len=5
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: CONNECT ACKNOWLEDGE (15)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Active, peerstate Connect Request
> Protocol Discriminator: Q.931 (8)  len=9
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: DISCONNECT (69)
> [08 02 81 90]
> Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Private network
serving the local user (1)
>                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: RELEASE (77)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Null, peerstate Release Request
> Protocol Discriminator: Q.931 (8)  len=9
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: RELEASE COMPLETE (90)
> [08 02 81 90]
> Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Private network
serving the local user (1)
>                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Null, peerstate Null
NEW_HANGUP DEBUG: Destroying the call, ourstate Null, peerstate Null
< Protocol Discriminator: Q.931 (8)  len=9
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: DISCONNECT (69)
< [08 02 82 90]
< Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Public network
serving the local user (2)
<                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
-- Processing IE 8 (cs0, Cause)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Disconnect Indication, peerstate Disconnect
Request
> Protocol Discriminator: Q.931 (8)  len=9
> Call Ref: len= 2 (reference 5720/0x1658) (Terminator)
> Message type: RELEASE (77)
> [08 02 81 90]
> Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Private network
serving the local user (1)
>                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: RELEASE COMPLETE (90)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Null, peerstate Null
NEW_HANGUP DEBUG: Destroying the call, ourstate Null, peerstate Null
```

### Opciones de configuración en chan_dahdi.conf

Varias opciones están disponibles en el archivo chan_dahdi.conf. Una descripción de todas las opciones sería aburrida y contraproducente. Aquí, detallaremos los principales grupos de opciones disponibles para proporcionar una mejor comprensión.

#### Opciones generales (independientes del canal)

context: Define el contexto de entrada.

```
context=default
```

channel: Define canal o rango de canales. Cada definición de canal heredará las opciones definidas antes de la declaración. Los canales pueden identificarse individualmente o en la misma línea con separación por comas. Los rangos pueden definirse usando “-”.

```
Channel=>1-15
Channel=>16
Channel=>17,18
```

group: Permite que los canales se traten como un grupo. Si marca un número de grupo en lugar de un número de canal, se usa el primer canal disponible. Si los canales son teléfonos, cuando llama a un grupo, todos los teléfonos sonarán simultáneamente. Usando comas, puede especificar más de un grupo para el mismo canal.

```
group=1
group=3,5
```

language: Activa la internacionalización y configura un idioma. Esta función configurará los mensajes del sistema para un idioma específico. English es el único idioma con indicaciones completas disponibles desde la instalación estándar. musiconhold: Selecciona la clase de música en espera.

#### ISDN options

switchtype: Depende del PBX o conmutador usado. En Europa y América Latina, EuroISDN es común.

- 5ess: Lucent 5ESS
- euroisdn: EuroISDN
- national: National ISDN
- dms100: Nortel DMS100
- 4ess: AT&T 4ESS
- Qsig: Q.SIG

```
switchtype = EuroISDN
```

pridialplan: Requerido para algunos conmutadores que necesitan una especificación de plan de marcación. Esta opción es ignorada por muchos conmutadores. Las opciones válidas son private, national, international, y unknown.

```
pridialplan = unknown
```

prilocaldialplan: Necesario para algunos conmutadores, usualmente desconocido.

```
prilocaldialplan = unknown
```

overlapdial: El marcado superpuesto se usa cuando se envían dígitos después de que se establece la conexión. Puede usar numeración en modo bloque (overlapdial=no) o modo dígito (overlapdial=yes). El modo bloque es a menudo usado por los operadores. signaling: Configura el tipo de señalización para los canales subsecuentes. Estos parámetros deben corresponder a los del archivo chan_dahdi.conf. Las elecciones correctas dependen del canal disponible. Para ISDN puede elegir cinco opciones:

- pri_cpe: Se usa cuando el dispositivo es un CPE, a veces llamado cliente, usuario o esclavo. Esta es la forma más simple y más usada de señalización. A veces, cuando intenta conectar a una PBX privada, la PBX también se ha configurado comúnmente como un CPE. En este caso, use señalización pri_net en Asterisk.
- pri_net: Se usa cuando Asterisk está conectado a una PBX privada configurada como un CPE. La señalización a menudo se denomina host, master o network.
- bri_cpe: Se usa cuando Asterisk está conectado como un CPE a un trunk ISDN BRI
- bri_net: Se usa cuando Asterisk está conectado a un teléfono ISDN o a una PBX configurada como un terminal (TE).
- bri_cpe_ptmp: Igual que bri_cpe, pero en una arquitectura punto‑a‑multipunto.

#### CallerID options

Muchas opciones de Caller ID están disponibles. Algunas pueden desactivarse, aunque la mayoría están habilitadas por defecto. usecallerid: Habilita o deshabilita la transmisión del Caller ID para los canales subsecuentes (Yes/No). Nota: Si su sistema requiere dos timbres antes de contestar, intente desactivar esta función para que conteste inmediatamente. hidecallerid: Oculta el Caller ID (Yes/No). calleridcallwaiting: Habilita la recepción del Caller ID durante una indicación de llamada en espera (Yes/No). callerid: Configura una cadena de Caller ID para un canal específico. El llamante puede configurarse con “asreceived” en interfaces de trunk para pasar el Caller ID hacia adelante.

```
callerid = "Flavio Eduardo Gonçalves" <48 30258500>
```

Note: La mayoría de los TELCO exigen que configure su ID de llamante correcto. Si no envía el ID de llamante adecuado, no debería poder marcar salientes a través del TELCO. Por otro lado, podrá recibir llamadas incluso sin configurar el ID de llamante.

#### Opciones de calidad de audio

Estas opciones ajustan ciertos parámetros de Asterisk que afectan la calidad de audio en los canales DAHDI.

- **echocancel**: Desactivar o activar la cancelación de eco. Debe mantener esta función activada. Acepta "yes" o el número de taps. (Explicación: ¿Cómo funciona la cancelación de eco? La mayoría de los algoritmos de cancelación de eco operan generando múltiples copias de una señal recibida, cada una retrasada por un pequeño intervalo. Este pequeño flujo se llama "tap". El número de taps determina el retraso de eco que puede cancelarse. Estas copias se retrasan, ajustan y se restan de la señal original. El truco consiste en ajustar la señal retrasada exactamente a lo necesario para eliminar el eco.)
- **echocancelwhenbridged**: Activa o desactiva el cancelador de eco durante una llamada TDM pura. Normalmente no es necesario.
- **rxgain**: Ajusta la ganancia de recepción de audio para aumentar o disminuir el volumen de recepción (-100% a 100%).
- **txgain**: Ajusta la ganancia de transmisión de audio para aumentar o disminuir el volumen de transmisión (-100% a 100%).

Example:

```
echocancel=yes
echocancelwhenbridged=yes
txgain=-10%
rxgain=10%
```

#### Opciones de facturación

These options change the way in which call information is recorded in the call detail records (CDR) database. amaflags: Affects the categorization of CDR. It accepts these values:

- billing
- documentation
- omit
- default

accountcode: It configures an account code for a specific channel. It can contain any alphanumeric value, usually the department or user name.

```
accountcode=finance
amaflags=billing
```

### Configuración de MFC/R2

MFC/R2 se usa en varios países de América Latina, China y África, así como en algunos países europeos. ISDN es superior y se prefiere si está disponible en su zona.

#### Entendiendo el problema

La tarjeta usada para señalizar MFC/R2 es la misma que se usa para señalizar ISDN. Es posible usar MFC/R2 en canales DAHDI usando la biblioteca llamada libopenR2 (www.libopenr2.com). Esta biblioteca no formaba parte de las versiones de Asterisk anteriores a la 1.6.2.

##### Comprendiendo el protocolo MFC/R2

El protocolo MFC/R2 combina señalización in-band y out-of-band. La señalización de dirección se reenvía in-band usando un conjunto de tonos mientras que la información del canal se transmite en el timeslot 16 como señalización out-of-band.

**Line Signaling (ITU-T Q.421).** En el intervalo de tiempo 16, cada canal de voz usa cuatro bits ABCD para señalizar sus estados y el control de llamadas. Los bits C y D se usan raramente. En algunos países, pueden usarse para la medición (medición por pulsos para facturación). En una conversación normal, tenemos ambos lados trabajando: el llamante y el llamado. La señalización desde el lado del llamante se denomina señalización hacia adelante mientras que el lado llamado usa señalización hacia atrás. Designaremos Af y Bf para señalización hacia adelante y Ab y Bb para señalización hacia atrás.

| State | ABCD forward | ABCD backward |
| --- | --- | --- |
| Idle/Released | 1001 | 1001 |
| Seized | 0001 | 1001 |
| Seize Ack | 0001 | 1101 |
| Answered | 0001 | 0101 |
| ClearBack | 0001 | 1101 |
| ClearFwd (before clear-back) | 1001 | 0101 |
| ClearFwd (disconnection confirmation) | 1001 | 1001 |
| Blocked | 1001 | 1101 |

MFC/R2 fue definido por la ITU. Desafortunadamente, varios países personalizaron el estándar según sus propias necesidades. Como resultado, surgieron variaciones en los estándares entre países.

**Señales interregistro (ITU-T Q.441).** La señalización MFC/R2 usa una combinación de dos tonos. Las tablas a continuación muestran el estándar ITU.

Grupo de señal I (adelante):

| Description | Forward signal |
| --- | --- |
| Dígito 1 | I-1 |
| Dígito 2 | I-2 |
| Dígito 3 | I-3 |
| Dígito 4 | I-4 |
| Dígito 5 | I-5 |
| Dígito 6 | I-6 |
| Dígito 7 | I-7 |
| Dígito 8 | I-8 |
| Dígito 9 | I-9 |
| Dígito 0 | I-10 |
| Indicador de código de país, supresor de medio eco saliente requerido | I-11 |
| Indicador de código de país, no se requiere supresor de eco | I-12 |
| Indicador de llamada de prueba | I-13 |
| Indicador de código de país, supresor de medio eco saliente insertado | I-14 |
| No usado | I-15 |

Grupo de señal II (adelante):

| Descripción | Señal de avance |
| --- | --- |
| Suscriptor sin prioridad | II-1 |
| Suscriptor con prioridad | II-2 |
| Equipo de mantenimiento | II-3 |
| Repuesto | II-4 |
| Operador | II-5 |
| Transmisión de datos | II-6 |
| Suscriptor u operador sin facilidad de transferencia directa | II-7 |
| Transmisión de datos | II-8 |
| Suscriptor con prioridad | II-9 |
| Operador con facilidad de transferencia directa | II-10 |
| Repuesto | II-11 |
| Repuesto | II-12 |
| Repuesto | II-13 |
| Repuesto | II-14 |
| Repuesto | II-15 |

Grupo de señales A (hacia atrás):

| Description | Backward signal |
| --- | --- |
| Enviar el siguiente dígito (n+1) | A-1 |
| Enviar el penúltimo dígito (n-1) | A-2 |
| Dirección completa, cambio a la recepción de señales del Grupo B | A-3 |
| Congestión en la red nacional | A-4 |
| Enviar la categoría de la parte llamante | A-5 |
| Dirección completa, cobro, establecer condiciones de voz | A-6 |
| Enviar el antepenúltimo dígito (n-2) | A-7 |
| Enviar el tercer dígito desde el final (n-3) | A-8 |
| Reserva | A-9 |
| Reserva | A-10 |
| Enviar indicador de código de país | A-11 |
| Enviar dígito de idioma o discriminación | A-12 |
| Enviar naturaleza del circuito | A-13 |
| Solicitar información sobre el uso del supresor de eco | A-14 |
| Congestión en un intercambio internacional o en su salida | A-15 |

Grupo de señal B (hacia atrás):

| Description | Backward signal |
| --- | --- |
| Libre | B-1 |
| Enviar tono de información especial | B-2 |
| Línea del suscriptor ocupada | B-3 |
| Congestión (después del cambio del grupo A a B) | B-4 |
| Número no asignado | B-5 |
| Línea del suscriptor libre, con cargo | B-6 |
| Línea del suscriptor libre, sin cargo | B-7 |
| Línea del suscriptor fuera de servicio | B-8 |
| Libre | B-9 |
| Libre | B-10 |
| Libre | B-11 |
| Libre | B-12 |
| Libre | B-13 |
| Libre | B-14 |
| Libre | B-15 |

#### secuencia MFC/R2

The following sequence illustrates a call originating from an Asterisk’s extension to a terminal in the PSTN. The PSTN drops the call and ends the communication.

![Un flujo de llamada MFC/R2 completo entre Asterisk y la telco: la señalización de línea (Idle, Seized, Seize Ack, Answer, Clearback, Clear Forward) se intercambia en la ranura de tiempo 16, los dígitos marcados y las señales de retroceso "send next digit" (grupos I/A/B) viajan en banda, y los tonos audibles llegan al suscriptor.](../images/10-legacy-fig11.png)

### Cómo usar el controlador libopenr2

El proyecto iniciado por Moises Silva se inspiró en el controlador de canal Unicall escrito por Steve Underwood. La biblioteca OpenR2 es actualmente la solución de software más estable para Asterisk. Con esta solución, podemos usar cualquier tarjeta digital compatible con DAHDI. Anteriormente, solo estaban disponibles soluciones propietarias para MFC/R2; una de las mejores que he usado es la que ofrece Khomp, www.khomp.com.br. En Asterisk 22, el soporte MFC/R2 a través de libopenR2 está incorporado cuando la biblioteca está presente en tiempo de compilación — no se requiere ningún parche externo. Los pasos a continuación muestran la instalación manual histórica como referencia; en sistemas modernos, instale `libopenr2-dev` desde el gestor de paquetes de su distribución antes de ejecutar `./configure`, luego habilite `chan_dahdi` en `make menuselect`.

Los pasos a continuación construyen openr2 y Asterisk a partir de sus repositorios Git actuales. Se conservan como referencia para los sitios que compilan desde el código fuente; en una distribución moderna normalmente puedes omitirlos por completo instalando el paquete `libopenr2-dev` y una versión empaquetada de Asterisk 22, ya que `chan_dahdi` compila el soporte R2 directamente contra libopenr2 sin parche externo.

Paso 1: Instale las herramientas de compilación que necesita.

```
apt-get install git
```

Paso 2: Clone la biblioteca openr2 y el código fuente de Asterisk. No se necesita un árbol parcheado especial en Asterisk 22 — una extracción estándar compila el soporte R2 siempre que libopenr2 esté presente.

```
cd /usr/src
git clone https://github.com/moises-silva/openr2.git
git clone https://github.com/asterisk/asterisk.git
```

Step 3: Compile and install Por favor, HAGA UNA COPIA DE SEGURIDAD de su servidor antes de continuar.

```
cd /usr/src/openr2
./configure && make && make install && ldconfig
cd /usr/src/asterisk
./configure && make menuselect && make && make install
```

Note: No ejecute “make samples” para evitar sobrescribir sus archivos de configuración.

```
Step 4: Changing the file /etc/dahdi/system.conf:
vim /etc/dahdi/system.conf
```

Supongamos que tienes una tarjeta con una interfaz E1.

```
span=1,1,0,cas,hdb3
cas=1-15:1101
cas=17-31:1101
dchan=16
loadzone=br
defaultzone=br
```

Step 5: Run the command dahdi_cfg to apply the changes to the driver:
--- END MARKDOWN ---

```
dahdi_cfg -vvvvvvvv
Dahdi Version:SVN-branch-1.4-r4348
Echo Canceller: MG2
Configuration
======================
SPAN 1: CAS/HDB3 Build-out: 0 db (CSU)/0-133 feet (DSX-1)
Channel map:
Channel 01: CAS / User (Default) (Slaves: 01)
Channel 02: CAS / User (Default) (Slaves: 02)
Channel 03: CAS / User (Default) (Slaves: 03)
Channel 04: CAS / User (Default) (Slaves: 04)
Channel 05: CAS / User (Default) (Slaves: 05)
Channel 06: CAS / User (Default) (Slaves: 06)
Channel 07: CAS / User (Default) (Slaves: 07)
Channel 08: CAS / User (Default) (Slaves: 08)
Channel 09: CAS / User (Default) (Slaves: 09)
Channel 10: CAS / User (Default) (Slaves: 10)
Channel 11: CAS / User (Default) (Slaves: 11)
Channel 12: CAS / User (Default) (Slaves: 12)
Channel 13: CAS / User (Default) (Slaves: 13)
Channel 14: CAS / User (Default) (Slaves: 14)
Channel 15: CAS / User (Default) (Slaves: 15)
Channel 16: D-channel (Default) (Slaves: 16)
Channel 17: CAS / User (Default) (Slaves: 17)
Channel 18: CAS / User (Default) (Slaves: 18)
Channel 19: CAS / User (Default) (Slaves: 19)
Channel 20: CAS / User (Default) (Slaves: 20)
Channel 21: CAS / User (Default) (Slaves: 21)
Channel 22: CAS / User (Default) (Slaves: 22)
Channel 23: CAS / User (Default) (Slaves: 23)
Channel 24: CAS / User (Default) (Slaves: 24)
Channel 25: CAS / User (Default) (Slaves: 25)
Channel 26: CAS / User (Default) (Slaves: 26)
Channel 27: CAS / User (Default) (Slaves: 27)
Channel 28: CAS / User (Default) (Slaves: 28)
Channel 29: CAS / User (Default) (Slaves: 29)
Channel 30: CAS / User (Default) (Slaves: 30)
Channel 31: CAS / User (Default) (Slaves: 31)
31 channels to configure.
-----------------------------------------------------------------------
```

Step 5: Cambiar el archivo chan_dahdi.conf

```
vim /etc/asterisk/chan_dahdi.conf
[channels]
usecallerid=yes
callwaiting=yes
usecallingpres=yes
callwaitingcallerid=yes
threewaycalling=yes
transfer=yes
canpark=yes
cancallforward=yes
callreturn=yes
echocancel=yes
echotrainning=yes
echocancelwhenbridged=yes
signalling=mfcr2
mfcr2_variant=br
mfcr2_get_ani_first=no
mfcr2_max_ani=20
mfcr2_max_dnis=4
mfcr2_category=national_subscriber
mfcr2_logdir=span1
mfcr2_logging=all
group=1
callgroup=1
pickupgroup=1
callerid=asreceived
context=from-mfcr2
channel => 1-15,17-31
```

Step 6: Cambiar el dial plan en el archivo extensions.conf

```
vim /etc/asterisk/extensions.conf
[default]
exten => _XXXXXXXX,1,Set(CALLERID(num)=1145678990)
exten => _XXXXXXXX,n,Dial(DAHDI/g1/${EXTEN},60,tT)
```

Nota: Algunos TELCOS no aceptan llamadas sin la identificación del llamante. Por favor, configure la identificación del llamante con uno de los números DID asignados por el operador. En algunos países, este paso no es necesario. Paso 7: Pruebe la solución: Ahora, con una extensión en el contexto from-internal, llame a cualquier número y observe la consola. Verifique si se están produciendo errores. -- Executing Set("SIP/8564-081ca5d8", "CALLERID(num)=1145678990") in new stack -- Executing Dial("SIP/8564-081ca5d8", "DAHDI/g1/35678899|60|tT") in new stack

#### Depuración de OpenR2

Para detectar errores en las llamadas, puede activar la depuración. Para hacerlo, siga los pasos a continuación.

1. Edite el archivo `chan_dahdi.conf` y agregue las siguientes tres líneas a la configuración:

```
mfcr2_logdir=span1
mfcr2_logging=all
mfcr2_call_files=yes
```

2. Reinicie el servidor Asterisk
3. Pruebe la llamada y verifique los archivos de llamada en `/var/log/asterisk/mfcr2/span1`

A continuación se muestra una traza de una llamada normal. Compárela con lo que recibe en su llamada.

```
[15:05:47:710] [Thread: 3078019984] [Chan 1] - Call started at Mon Jul  6 15:05:47 2009 on
chan 1
[15:05:47:710] [Thread: 3078019984] [Chan 1] - CAS Tx >> [SEIZE] 0x00
[15:05:47:710] [Thread: 3078019984] [Chan 1] - CAS Raw Tx >> 0x01
[15:05:47:951] [Thread: 3078019984] [Chan 1] - Bits changed from 0x08 to 0x0C
[15:05:47:951] [Thread: 3078019984] [Chan 1] - CAS Rx << [SEIZE ACK] 0x0C
[15:05:47:951] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 2
[15:05:47:951] [Thread: 3078019984] [Chan 1] - timer id 2 found, cancelling it now
[15:05:47:951] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 3
[15:05:47:951] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [ON]
[15:05:48:070] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:070] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:070] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:070] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [OFF]
[15:05:48:150] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:150] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 0
[15:05:48:150] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [ON]
[15:05:48:150] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:250] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:250] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:250] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:250] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [OFF]
[15:05:48:350] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:350] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 2
[15:05:48:350] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [ON]
[15:05:48:350] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:450] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:450] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:450] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:450] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [OFF]
[15:05:48:550] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:550] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 5
[15:05:48:550] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [ON]
[15:05:48:550] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:650] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:650] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:650] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:650] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [OFF]
[15:05:48:750] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:750] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 8
[15:05:48:750] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [ON]
[15:05:48:750] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:850] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:850] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:850] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:850] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [OFF]
[15:05:48:950] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:950] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 5
[15:05:48:950] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [ON]
[15:05:48:950] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:49:050] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:49:050] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:050] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:050] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [OFF]
[15:05:49:150] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:49:150] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 8
[15:05:49:150] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [ON]
[15:05:49:150] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:49:250] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:49:250] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:250] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:250] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [OFF]
[15:05:49:330] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:49:330] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 4
[15:05:49:330] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [ON]
[15:05:49:330] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:49:590] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:49:590] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:590] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:590] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [OFF]
[15:05:49:670] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:49:670] [Thread: 3078019984] [Chan 1] - Sending category National Subscriber
[15:05:49:670] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:49:770] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:49:770] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:770] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:770] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:49:850] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:49:850] [Thread: 3078019984] [Chan 1] - Sending ANI digit 4
[15:05:49:850] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [ON]
[15:05:49:930] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:49:930] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:930] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:930] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [OFF]
[15:05:50:030] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:030] [Thread: 3078019984] [Chan 1] - Sending ANI digit 8
[15:05:50:030] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [ON]
[15:05:50:130] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:130] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:130] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:130] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [OFF]
[15:05:50:230] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:230] [Thread: 3078019984] [Chan 1] - Sending ANI digit 3
[15:05:50:230] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [ON]
[15:05:50:330] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:330] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:330] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:330] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [OFF]
[15:05:50:430] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:430] [Thread: 3078019984] [Chan 1] - Sending ANI digit 0
[15:05:50:430] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [ON]
[15:05:50:530] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:530] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:530] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:530] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [OFF]
[15:05:50:610] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:610] [Thread: 3078019984] [Chan 1] - Sending ANI digit 2
[15:05:50:610] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [ON]
[15:05:50:710] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:710] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:710] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:710] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [OFF]
[15:05:50:810] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:810] [Thread: 3078019984] [Chan 1] - Sending ANI digit 7
[15:05:50:810] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [ON]
[15:05:50:910] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:910] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:910] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:910] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [OFF]
[15:05:51:010] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:010] [Thread: 3078019984] [Chan 1] - Sending ANI digit 2
[15:05:51:010] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [ON]
[15:05:51:110] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:110] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:110] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:110] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [OFF]
[15:05:51:210] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:210] [Thread: 3078019984] [Chan 1] - Sending ANI digit 1
[15:05:51:210] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:51:310] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:310] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:310] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:310] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:51:410] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:410] [Thread: 3078019984] [Chan 1] - Sending ANI digit 7
[15:05:51:410] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [ON]
[15:05:51:510] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:510] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:510] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:510] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [OFF]
[15:05:51:610] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:610] [Thread: 3078019984] [Chan 1] - Sending ANI digit 1
[15:05:51:610] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:51:710] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:710] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:710] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:710] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:51:810] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:810] [Thread: 3078019984] [Chan 1] - Sending more ANI unavailable
[15:05:51:810] [Thread: 3078019984] [Chan 1] - MF Tx >> F [ON]
[15:05:51:990] [Thread: 3078019984] [Chan 1] - MF Rx << 3 [ON]
[15:05:51:990] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:990] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:990] [Thread: 3078019984] [Chan 1] - MF Tx >> F [OFF]
[15:05:52:090] [Thread: 3078019984] [Chan 1] - MF Rx << 3 [OFF]
[15:05:52:090] [Thread: 3078019984] [Chan 1] - Sending category National Subscriber
[15:05:52:090] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:53:350] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:53:350] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:53:350] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:53:350] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:53:430] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:06:03:322] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:06:03:322] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:06:03:322] [Thread: 3078019984] [Chan 1] - CAS Tx >> [CLEAR FORWARD] 0x08
[15:06:03:322] [Thread: 3078019984] [Chan 1] - CAS Raw Tx >> 0x09
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Bits changed from 0x0C to 0x08
[15:06:03:569] [Thread: 3085228944] [Chan 1] - CAS Rx << [IDLE] 0x08
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Call ended
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Attempting to cancel timer timer 0
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Cannot cancel timer 0
```

#### Configuración MFC/R2

Las opciones están documentadas en el archivo chan_dahdi.conf. Algunas de las opciones más importantes se detallan aquí. Parámetros obligatorios: mfcr2_variant, mfcr2_max_ani y mfcr2_max_dnis. mfcr2_variant: variante de país.

```
r2test -l
Variant Code        Country
AR                  Argentina
BR                  Brazil
CN                  China
CZ                  Czech Republic
CO                  Colombia
EC                  Ecuador
ITU                 International Telecommunication Union
MX                  Mexico
PH                  Philippines
VE                  Venezuela
```

mfcr2_max_ani: Max amount of ANI digits to ask for mfcr2_max_dnis: Max amount of DNIS digits to ask for mfcr2_get_ani_first: Whether or not to get ANI before DNIS (required by some TELCOS) mfcr2_category: Caller category. You can set the variable MFCR2_CATEGORY before starting the call mfcr2_logdir: Directory to log the call files. (/var/log/asterisk/mfcr2/directory) mfcr2_call_files: Whether or not to log the calls

- mfcr2_logging: logging values
- cas – ABCD bits for tx and rx
- mf – Multifrequency tones
- stack – verbose output of the channel and context stack
- all – all activities
- nothing – do not log anything

mfcr2_mfback_timeout: This value deserves to be mentioned. Sometimes if you are calling a cell phone or any call that takes a long time to complete, this parameter can time out, so it is often changed for fine tuning. If some of your calls are not being completed, this is the parameter you should change first. mfcr2_metering_pulse_timeout: Pulses are used by some R2 variants to indicate costs mfcr2_allow_collect_calls: In Brazil, the tone II-8 is used to indicate a collect call; this parameter allows you to block collect calls. mfcr2_double_answer: Also used to avoid collect calls when a double answer is required. With double_answer=yes you actually block the collect calls. mfcr2_immediate_accept: Allows you to skip the use of group B/II signals and go directly to the accepted state. mfcr2_forced_release: Allows you to speed up the release of the call; works for the Brazilian variant.

#### ANI y DNIS

La Identificación Automática de Número (ANI) es el número del llamante. El Servicio de Identificación de Número Marcado (DNIS) es el número llamado o, en otras palabras, el número marcado. Cuando se recibe una llamada, normalmente los últimos cuatro dígitos se pasan al PBX en un proceso llamado marcación directa interna (DID). El número ANI es en realidad el Caller ID. ANI tendrá la extensión del llamante al marcar, mientras que DNIS contendrá el destino de la llamada. Es importante que estos parámetros estén configurados correctamente. Algunos conmutadores envían solo los últimos cuatro dígitos, mientras que otros envían el número completo.

### Formato del canal DAHDI

Los canales DAHDI usan el siguiente formato en el dialplan:

```
DAHDI/[g]<identifier>[c][r<cadence>]
<identifier> - Physical channel numeric identifier
[g] - Group identifier
[c] - Answer confirmation. A number is not considered until the callee presses "#"
[r] - customized ringing
[cadence] - Integer from 1 to 4
```

Ejemplos:

```
DAHDI/2     - channel 2
DAHDI/g1    - First available channel in group 1
```

## The IAX2 protocol

In this chapter, we will learn about the Inter-Asterisk eXchange (IAX) protocol, including its strengths and weaknesses. Details such as trunk mode and the interconnection of two Asterisk servers will also be covered. All references in this document correspond to IAX version 2.

The IAX protocol provides media transport and signaling for voice and video. IAX is very innovative; it saves bandwidth in trunk mode and is much simpler than SIP when you need to traverse NAT. The primary use for IAX nowadays is to interconnect Asterisk servers. IAX was created primarily for voice, but it can also accommodate video and other multimedia streams.

IAX was inspired from other VoIP protocols, such as SIP and MGCP. Instead of using two separate protocols for signaling and media, IAX unified them to make a unique protocol. IAX does not use RTP for media transport; instead, it embeds the media in the same UDP connection.

**Status in Asterisk 22.** `chan_iax2` is still included and fully supported in Asterisk 22 LTS, so everything in this section remains valid. IAX2 is, however, a legacy protocol that sees relatively little new deployment: the industry has largely converged on SIP (via `chan_pjsip` in Asterisk 22) for both provider trunking and server interconnection. IAX2's main remaining advantage is its single-port design — all signaling and media flow over a single UDP port (4569 by default), which simplifies firewall and NAT configuration compared to SIP plus its separate RTP streams. For a new Asterisk-to-Asterisk trunk where NAT is not a concern, a PJSIP trunk is the recommended modern approach; IAX2 is covered here because it remains a valid choice, especially where only one UDP port can be opened through a firewall.

### Objectives

By the end of this chapter, you should be able to:

- Identify strengths and weakness of IAX protocol
- Describe usage scenarios for the IAX protocol
- Describe the advantages of IAX trunk mode
- Configure iax.conf for phones
- Configure iax.conf for connection to a VoIP provider
- Configure iax.conf for Asterisk interconnection
- Understand IAX authentication

### IAX design

The main objectives for IAX design are:

- To reduce the bandwidth required for media transport and signaling
- To provide NAT transparency
- To be able to transmit the dial plan information
- To support the efficient use of paging and intercom

IAX is a peer-to-peer signaling and media protocol that is similar to SIP without using RTP. The basic approach is to multiplex the multimedia streams over a single UDP connection between two hosts. The greatest benefit of this approach is its simplicity when traversing connections over NAT, regularly found in xDSL modems. IAX uses a single port, UDP 4569 by default, and then uses a call number with 15 bits to multiplex all streams. The IAX protocol uses registration and authentication processes similar to the SIP protocol. A description of the protocol can be found at http://www.ietf.org/internet-drafts/draft-guy-iax-05.txt

![El protocolo IAX multiplexa muchas llamadas entre dos endpoints a través de un solo puerto UDP (4569 por defecto), usando un número de llamada de 15 bits para mantener los flujos separados — lo que hace que el paso por NAT sea simple.](../images/10-legacy-fig12.png)

### Bandwidth usage

The bandwidth used in VoIP networks is affected by several factors; codecs and protocol headers are the most important. The IAX protocol has a surprising feature called trunk mode, whereby it multiplexes several calls using a single header. By playing with the Asterisk bandwidth calculator, you will see how IAX trunks can save you up to 80% of the traffic with multiple calls.

![Comparación del overhead de IAX y SIP: dos llamadas SIP/RTP necesitan dos paquetes (40 bytes de carga útil bajo 156 bytes de overhead), mientras que el modo trunk IAX2 lleva ambas llamadas en un solo paquete (40 bytes de carga útil bajo solo 66 bytes de overhead) compartiendo una cabecera IP/UDP entre muchos mini‑frames.](../images/10-legacy-fig13.png)

### Channel naming

It is important to understand channel-naming conventions as you will use these names when specifying a channel in the dial plan. The format of an IAX channel name used for outbound channels is:

```
IAX/[<user>[:<secret>]@]<peer>[:<portno>][/<exten>[@<context>][/<options>]
```

- `<user>` — ID de usuario en el par remoto, o nombre del cliente configurado en iax.conf
- `<secret>` — La contraseña. Alternativamente puede ser el nombre de archivo de una clave RSA sin la extensión final (.key o .pub) y entre corchetes
- `<peer>` — Nombre del servidor al que conectarse
- `<portno>` — Número de puerto para la conexión
- `<exten>` — Extensión en el servidor Asterisk remoto
- `<context>` — Contexto en el servidor Asterisk remoto
- `<options>` — La única opción disponible es 'a', que significa 'solicitar auto‑respuesta'

#### Ejemplo de canales salientes:

Los canales salientes se ven en la consola de Asterisk.

- `IAX2/8590:secret@myserver/8590@default` — Llamar a la extensión 8590 en myserver. Usa 8590:secret como el par nombre/contraseña
- `IAX2/iaxphone` — Llamar a "iaxphone"
- `IAX2/judy:[judyrsa]@somewhere.com` — Llamar a somewhere.com usando judy como nombre de usuario y una clave RSA para autenticación

#### El formato de un canal IAX entrante es:

Los canales entrantes se ven en la consola de Asterisk.

```
IAX2/[<username>@]<host>]-<callno>
```

- `<username>` — Nombre de usuario si se conoce
- `<host>` — Host que se conecta
- `<callno>` — Número de llamada local

Ejemplo de canal entrante:

- `IAX2[flavio@8.8.30.34]/10` — Número de llamada 10 desde la dirección IP 8.8.30.34 usando flavio como usuario.
- `IAX2[8.8.30.50]/11` — Número de llamada 11 desde la dirección IP 8.8.30.50.

### Uso de IAX

Puede usar IAX de varias maneras. En esta sección, le mostraremos cómo configurar IAX para varios escenarios, incluyendo:

- Conectar un softphone usando IAX
- Conectar IAX a un proveedor VoIP usando IAX
- Conectar dos servidores usando IAX
- Conectar dos servidores usando IAX en modo trunk
- Depurar una conexión IAX
- Usar pares de claves RSA para autenticación

#### Conectar un softphone usando IAX

Asterisk soporta teléfonos IP basados en IAX como el ATCOM y el antiguo ATA de Digium (llamado IAXy) así como softphones que aún implementan el protocolo IAX2. El proceso para softphones, ATAs y teléfonos duros es similar. Para configurar un dispositivo IAX, necesita editar el archivo iax.conf en /etc/asterisk

```
directory.
```

Usaremos un softphone compatible con IAX2 como ejemplo.

1. Haga una copia de seguridad del archivo original `iax.conf` usando:

```
#cd /etc/asterisk
#mv iax.conf iax.conf.backup
```

2. Comience a editar un nuevo archivo `iax.conf`:

```
[general]
bindport=4569
bindaddr=8.8.1.4
bandwidth=high
```

- ; Muy importante parámetro, cambia los códecs disponibles

```
disallow=all
allow=ulaw
jitterbuffer=no
forcejitterbuffer=no
tos=lowdelay
autokill=yes
[guest]
type=user
context=guest
callerid="Guest IAX User"
; Trust Caller*ID Coming from iaxtel.com
;
[iaxtel]
type=user
context=default
auth=rsa
inkeys=iaxtel
;
; Trust Caller*ID Coming from iax.fwdnet.net
;
[iaxfwd]
type=user
context=default
auth=rsa
inkeys=freeworlddialup
;
; Trust callerid delivered over DUNDi/e164
;
;
;[dundi]
;type=user
;dbsecret=dundi/secret
;context=dundi-e164-local
[2003]
type=friend
context=default
secret=senha
host=dynamic
```

He intentado conservar las líneas predeterminadas (no comentadas) del archivo de ejemplo. Los siguientes parámetros fueron modificados:

```
bandwidth=high
```

Esta línea afecta la selección del codec. Usar la configuración alta permite la selección de un codec de gran ancho de banda y alta calidad como g.711 definido por la palabra clave ulaw. Si mantienes el parámetro predeterminado, no podrás elegir ulaw. En este caso, Asterisk te mostrará el mensaje “no codec available” para la configuración a continuación.

```
disallow=all
allow=ulaw
```

En los comandos descritos arriba, desactivamos todos los códecs y habilitamos solo ulaw. En LANs, la mayoría de la gente prefiere usar ulaw porque no consume muchos recursos del procesador y ahorra ciclos de CPU. Aunque usa más ancho de banda, este códec es preferible porque en LANs usualmente se cuenta con Ethernet de 100 megabits o incluso de Gigabit. Una llamada de voz que utiliza ulaw consume casi 100 kilobits por segundo de ancho de banda de su red, lo que representa un uso muy ligero para las LANs de alta velocidad actuales. En redes WAN o Internet, normalmente se desactiva ulaw, intercambiando algunos ciclos de CPU disponibles por compresión de voz para un mejor uso del ancho de banda. Los códecs gsm, g729 e ilbc también proporcionan un buen factor de compresión.

```
[2003]
type=friend
context=default
secret=senha
host=dynamic
```

En los comandos anteriores, hemos definido a un amigo llamado [2003]. El contexto es el predeterminado (en los primeros laboratorios siempre usamos el contexto predeterminado para evitar confusiones; este contexto se explicará completamente cuando cubramos el dialplan). La línea “host=dynamic” proporciona un registro dinámico de la dirección IP del teléfono.

3. Descargue e instale un softphone compatible con IAX2. Puede elegir cualquier softphone que aún admita el protocolo IAX2 para el laboratorio.  
4. Configure una cuenta IAX en el cliente (normalmente *Add account* → IAX). Tenga en cuenta que el SipPulse Softphone es solo SIP y no puede registrarse mediante IAX2, por lo que para pruebas de IAX necesita un cliente que aún soporte el protocolo.

5. Configure el archivo `extensions.conf` para probar su dispositivo IAX.

```
[default]
exten=>2000,1,Dial(SIP/2000)
exten=>2001,1,Dial(SIP/2001)
exten=>2003,1,Dial(IAX2/2003)
```

Now you can dial between the SIP phones created in Chapter 3 and the IAX phone created in the lab.

#### Connecting to a VoIP provider using IAX

A few VoIP providers support IAX. You can easily find an IAX provider by searching for “IAX providers”. Using an IAX provider makes a lot of sense as IAX can save a lot of bandwidth, easily traverses NAT, and can authenticate using RSA key pairs.

![A customer's Asterisk connected to a VoIP provider over an IAX trunk across the Internet: a single trunk carries all calls to and from the provider.](../images/10-legacy-fig14.png)

The number of IAX-capable commercial VoIP providers has declined sharply over the past several Asterisk releases; most providers now offer SIP/PJSIP trunks exclusively. Before committing to an IAX provider, confirm they actively maintain their IAX infrastructure. For a new provider integration, a PJSIP trunk (Chapter 3) is the recommended alternative.

#### Connecting to a provider using IAX

Step 1: Open an account in your favorite provider. Your provider will provide you three things.

- Name
- Secret
- IP address or Host name
- RSA public key

Step 2: Configure the iax.conf file to register your Asterisk with your provider. Add the following lines to the [general] section of the file.

```
[general]
register=>name:secret@hostname/2003
```

En las instrucciones descritas arriba, te registraste con tu proveedor usando tu cuenta y contraseña. En el momento en que recibas una llamada, será reenviada a la extensión 2003.

```
[name]
```

- ; Su nombre de cuenta o número

```
type=peer
secret=secret
; Your password
host=hostname
```

En las instrucciones descritas arriba, hemos creado un peer que corresponde al proveedor para propósitos de marcación.

```
[nameiax]
type=user
context=default
auth=rsa
inkeys=hostname
```

Esto es necesario para la autenticación RSA. Usar la clave pública de su proveedor le permite estar seguro de que la llamada recibida proviene realmente del proveedor auténtico. Si alguien más intenta usar la misma ruta, no podrá autenticarse porque no posee la clave privada correspondiente. Paso 4: Pruebe la conexión. Para probar la conexión, marque cualquier número. Algunos proveedores ofrecen una prueba de eco. Para lograr esto, por favor edite el archivo extensions.conf.

```
[default]
exten=>*98,1,Dial(IAX2/name:secret@hostname/*98,20,r)
```

Vaya a la CLI de Asterisk y ejecute un reload. Para verificar si Asterisk está registrado con el proveedor, use el siguiente comando.

```
*CLI>reload
*CLI>iax2 show register
```

Now simply dial *98 on the softphone connected to the Asterisk server.

#### Conectando dos servidores Asterisk a través de un trunk IAX

It is very easy to connect one server to another. You won’t need to register them because the IP addresses are already known. You will have to create the peers and users in the iax.conf file. All extensions in the HQ site start with 20 followed by two digits (e.g., 2000). In the Branch, all extensions start with 22 followed by two digits (e.g., 2200). We will use the trunk. You will need a DAHDI timing source to enable this feature. Step 1: Edit the iax.conf file in the Branch server.

![Connecting two Asterisk servers with an IAX trunk: the HQ server (192.168.1.1, extensions 20xx) and the Branch server (192.168.1.2, extensions 22xx) reach each other over a single IAX trunk — no registration is needed because both IP addresses are fixed and known.](../images/10-legacy-fig15.png)

```
[general]
bindport=4569                   ; bindport and bindaddr may be specified
bindaddr=0.0.0.0                ; more than once to bind to multiple
disallow=all
allow=ulaw
;allow=gsm
[Branch]
type=user
context=default
secret=password
host=192.168.2.10
trunk=yes
notransfer=yes
[HQ]
type=peer
context=default
username=HQ
secret=password
host=192.168.2.10
callerID='HQ'
trunk=yes
notransfer=yes
[2200]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2000'
[2201]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2001'
```

Paso 2: Configurar el archivo extensions.conf en el servidor Branch

```
[general]
static=yes
writeprotect=no
autofallthrough=yes
clearglobalvars=no
priorityjumping=no
[default]
exten=>_20XX,1,dial(IAX2/HQ/${EXTEN},20)
exten=>_20XX,2,hangup
exten=>_22XX,1,dial(IAX2/${EXTEN},20)
exten=>_22XX,2,hangup
```

# Paso 3: Configurar el archivo iax.conf en el servidor central

```
[general]
bindaddr=0.0.0.0
bindport=4569
disallow=all
allow=ulaw
allow=gsm
[Branch]
type=peer
context=default
username=Branch
secret=password
host=192.168.2.9
callerid="Branch"
trunk=yes
notransfer=yes
[HQ]
type=user
secret=password
context=default
host=192.168.2.9
callerid="HQ"
trunk=yes
notransfer=yes
[2000]
type=friend
auth=md5
context=default
secret=password
callerid="2200"
host=dynamic
[2001]
type=friend
auth=md5
context=default
secret=password
callerid="2201"
host=dynamic
```

Step 4: Configurar el archivo extensions.conf en el servidor HQ.

```
[general]
static=yes
writeprotect=no
autofallthrough=yes
clearglobalvars=no
priorityjumping=no
[default]
exten=>_22XX,1,Dial(IAX2/Branch/${EXTEN})
exten=>_22XX,2,hangup
exten=>_20XX,1,Dial(IAX2/${EXTEN})
exten=>_20XX,2,hangup
```

Step 5: Test a call from the phone 2000 in the HQ server to the phone 2200 in the Branch server.

### IAX authentication

Now let’s analyze the IAX authentication process from the practical standpoint to help you choose the best method for each specific requirement.

#### Incoming connections

![El flujo de decisión de autenticación IAX para una llamada entrante: Asterisk se ramifica según si se proporciona un nombre de usuario, si coincide con una sección, si la IP de origen está permitida y si el secreto (texto plano, MD5 o RSA) coincide — aceptando la llamada con el contexto y las opciones de peer de esa sección, o denegándola.](../images/10-legacy-fig16.png)

When Asterisk receives an incoming connection, the initial information can include a user name (from the field "username=") or not. The incoming connection has an IP address too, which Asterisk uses for authentication as well.

If a user is provided, Asterisk:

1. Searches iax.conf for an entry with type=user (or type=friend with a section name matching the username). If it did not find it, Asterisk refuses the connection.
2. If the entry found has deny/allow configurations, it compares the IP address from the caller to determine whether to accept the call or not depending on the deny/allow clauses.
3. It checks the password (secret) using plaintext, md5, or RSA.
4. It accepts the connection and sends the call to the context specified in the line "context=" from the iax.conf file.

If a username is not provided, Asterisk:

1. Searches for an entry containing type=user (or type=friend) in the iax.conf file without a specified secret. It checks deny/allow clauses as well. If an entry is found, the connection is accepted and the section name is used as the user's name.
2. Searches for an entry containing type=user (or type=friend) in the iax.conf file with a secret or RSA key specified. It checks deny/allow clauses. If an entry is found, it tries to authenticate the caller using the specified secret; if it matches, it accepts the connection. Section name is the user's name.

Let's suppose your iax.conf file has the following entries:

```
[guest]
type=user
context=guest
[iaxtel]
type=user
context=incoming
auth=rsa
inkeys=iaxtel
[iax-gateway]
type=friend
allow=192.168.0.1
context=incoming
host=192.168.0.1
[iax-friend]
type=user
secret=this_is_secret
auth=md5
context=incoming
```

Si una llamada tiene un nombre de usuario especificado, como:

- guest
- iaxtel
- iax-gateway
- iax-friend

Asterisk intentará autenticar la llamada usando solo la entrada correspondiente en el archivo iax.conf. Si se especifican otros nombres, la llamada será rechazada. Si no se especifica un usuario, Asterisk intentará autenticar la conexión como guest. Sin embargo, si guest no existe, intentará cualquier otra conexión con un secreto coincidente. En otras palabras, si no tienes una sección guest en tu archivo iax.conf, un usuario malintencionado podría intentar adivinar cualquier secreto coincidente sin especificar el nombre de usuario. Las restricciones de denegar/permitir por direcciones IP también se aplican. Una buena forma de evitar la adivinación de secretos es usar autenticación RSA. Otro método es restringir las direcciones IP permitidas para llamar.

#### Restricciones de direcciones IP

Access is controlled with `permit` and `deny` lines:

```
permit = <ipaddr>/<netmask>
deny = <ipaddr>/<netmask>
```

Las reglas se interpretan en secuencia, y todas se evalúan (este concepto es diferente de las ACLs que se encuentran normalmente en routers y firewalls). La última instrucción coincidente reemplaza a las anteriores.

Example #1:

```
permit=0.0.0.0/0.0.0.0
deny=192.168.0.0/255.255.255.0
```

Esto denegará cualquier paquete de la red 192.168.0.0/24.

Ejemplo #2:

```
deny=192.168.0.0/255.255.255.0
permit=0.0.0.0/0.0.0.0
```

Esto permitirá cualquier paquete, porque la última instrucción reemplaza a la primera.

#### Conexiones salientes

Las conexiones salientes adquieren información de autenticación usando los siguientes métodos:

- La descripción del canal IAX2 pasada por la aplicación dial().
- Una entrada con type=peer o type=friend en el archivo iax.conf.
- Una combinación de ambos métodos.

#### Conectar dos servidores Asterisk usando claves RSA

Es posible usar IAX con autenticación fuerte mediante claves RSA asimétricas. Según el código fuente (res_krypto.c), Asterisk usa claves RSA con un algoritmo SHA-1 para los resúmenes de mensaje en lugar del más débil MD5. A continuación se muestra una guía paso a paso para configurar dos servidores usando claves RSA.

##### Configuración del servidor para la rama

Paso 1: Generar las claves RSA en el servidor de la rama

```
astgenkey -n
```

Cuando se solicite, use el nombre de clave branch. Hemos usado el parámetro –n para evitar pasar una frase de paso cada vez que Asterisk se reinicializa. Si desea mejorar la seguridad, no use el –n y inicie Asterisk con asterisk -i Paso 2: Copie las claves al directorio /var/lib/asterisk/keys

```
cp branch.* /var/lib/asterisk/keys
```

# Paso 3: Copiar la clave pública al servidor HQ

```
scp branch.pub root@hq_ip_address:/var/lib/asterisk/keys
```

Paso 4: Editar el archivo iax.conf en el servidor Branch.

```
[general]
bindport=4569                   ; bindport and bindaddr may be specified
bindaddr=0.0.0.0                ; more than once to bind to multiple
disallow=all
allow=ulaw
;Create an entry for the HQ server
[hq]
type=user
context=default
host=192.168.2.10
trunk=yes
notransfer=yes
auth=rsa
inkeys=hq
[2200]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2200'
[2201]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2201'
```

Paso 8: Configurar el archivo extensions.conf en el servidor Branch

```
 [default]
exten=>_20XX,1,dial(IAX2/branch:[branch]@192.168.2.10/${EXTEN},20)
exten=>_20XX,2,hangup
exten=>_22XX,1,dial(IAX2/${EXTEN},20)
exten=>_22XX,2,hangup
```

##### Configurando el servidor para la sede central

Paso 1: Generar las claves RSA en el servidor de la sede central

```
astgenkey -n
```

Cuando se solicite, use el nombre de clave hq. Paso 2: Copie las claves al directorio /var/lib/asterisk/keys

```
cp hq.* /var/lib/asterisk/keys
```

# Paso 3: Copiar la clave pública al servidor BRANCH

```
scp hq.pub root@branch_ip_address:/var/lib/asterisk/keys
```

Step 4: Configurar el archivo iax.conf en el servidor HQ

```
[general]
bindaddr=0.0.0.0
bindport=4569
disallow=all
allow=ulaw
allow=gsm
;Configure an entry for the branch server
[branch]
type=user
context=default
host=192.168.2.9
trunk=yes
notransfer=yes
auth=rsa
inkeys=branch
[2000]
type=friend
auth=md5
context=default
secret=password
callerid="2000"
host=dynamic
[2001]
type=friend
auth=md5
context=default
secret=password
callerid="2001"
host=dynamic
```

Step 10: Configurar el archivo extensions.conf en el servidor HQ.

```
[default]
exten=>_22XX,1,Dial(IAX2/hq:[hq]@192.168.2.9/${EXTEN})
exten=>_22XX,2,hangup
exten=>_20XX,1,Dial(IAX2/${EXTEN})
exten=>_20XX,2,hangup
```

Step 11: Test a call from the 2000 phone in the HQ server to the 2200 phone in the Branch server.

### The iax.conf file configuration

The file iax.conf has several parameters; discussing each parameter one by one would be boring and counterproductive. All parameters, along with a description, can be found in the sample file. In the wiki www.voip-info.org you will find detailed information about each one. Here we will show some of the most important parameters for the configuration of the general section, peers, and users.

#### [General] Section

Server addresses:

- `bindport = <portnum>` — Configures the IAX UDP port. Default is 4569.
- `bindaddr = <ipaddr>` — Use 0.0.0.0 to bind Asterisk to all interfaces, or specify the IP address of a specific interface.

Codec selection:

- `bandwidth = [low|medium|high]` — High = all codecs; Medium = all codecs except ulaw and alaw; Low = low bandwidth codecs.
- `allow/disallow = [alaw|ulaw|gsm|g.729| etc.]` — Codec selection fine tuning.

### Jitter buffer

Jitter is the delay variation between packets. It is the most important factor affecting voice quality. A Jitter buffer is used to compensate for the delay variation. It sacrifices latency in favor of lower jitter. You can make an analogy between the jitter buffer and a water tank. Both can receive packets or water at irregular intervals, but will ultimately deliver a regular flow.

![The jitter buffer as a water tank: packets arrive irregularly from the network and fill the buffer, which then releases them at a steady rate to produce a smooth voice flow. The buffer size (in ms) trades a little latency for lower jitter; the excess-buffer band lets Asterisk grow or shrink the buffer as network conditions change.](../images/10-legacy-fig17.png)

A small jitter (i.e., below 20 ms) is usually imperceptible. However, jitter above this level is annoying. The latency or delay should be kept to below 150ms. Creating a jitter buffer will sacrifice some delay for a lower jitter—a concept known as “delay-budget”. You can affect the jitter buffer using these parameters:

- Jitterbuffer=<yes/no> – Enables or disables
- Dropcount=<number> - Maximum amount of frames that should be delayed in the last two seconds. The recommended setting is 3 (1.5% of dropped frames)
- Maxjitterbuffer=<ms> - Usually below 100 ms
- Maxexcessbuffer=<ms> - If the network delay improves, the jitter buffer could be oversized. Consequently, Asterisk will try to reduce it.
- Minexcessbuffer=<ms> - Once the excess buffer drops to this value, Asterisk starts to increase the buffer size.

### Frame tagging

The parameter below marks the IP packet in the type of service field. Routers can read this tag, thereby prioritizing traffic. Asterisk uses DSCP codes for this field (RFC 2474). Allowed values are CS0, CS1, CS2, CS3, CS4, CS5, CS6, CS7, AF11, AF12, AF13, AF21, AF22, AF23, AF31, AF32, AF33, AF41, AF42, AF43, and ef (i.e., expedited forwarding).

```
tos=ef
```

### Cifrado IAX2

IAX soporta el cifrado de llamadas usando una clave simétrica, cifrado de bloque de 128 bits llamado AES (Advanced Encryption Standard). Es muy simple activar el cifrado entre trunks IAX. En el archivo iax.conf use:

```
encryption=yes
```

Para forzar el cifrado:

```
forceencryption=yes
```

Para garantizar la compatibilidad con versiones anteriores, es posible que necesite desactivar la rotación de claves usando:

```
keyrotate=no
```

### Comandos de depuración IAX2

A continuación se presentan algunos de los comandos de consola de solución de problemas más importantes para Asterisk.

```
iax2 show netstats
vtsvoffice*CLI> iax2 show netstats
                        -------- LOCAL ---------------------  -------- REMOTE ---------------
-----
Channel           RTT  Jit  Del  Lost   %  Drop  OOO  Kpkts  Jit  Del  Lost   %  Drop  OOO
Kpkts
IAX2/8590-1        16   -1    0    -1  -1     0   -1      1   60  110     3   0     0    0
0
iax2 show channels
vtsvoffice*CLI> iax2 show channels
Channel       Peer             Username    ID (Lo/Rem)  Seq (Tx/Rx)  Lag      Jitter  JitBuf
Format
IAX2/8590-2   8.8.30.43        8590        00002/26968  00004/00003  00000ms  -0001ms  0000ms
unknow
iax2 show peers
vtsvoffice*CLI> iax2 show peers
Name/Username    Host                 Mask             Port          Status
8584             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8564             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8576             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8572             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8571             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8585             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8589             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8590             8.8.30.43       (D)  255.255.255.255  4569          OK (16 ms)
3232             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
9 iax2 peers [1 online, 8 offline, 0 unmonitored]
iax2 debug
```

Al observar esta salida, identifique el inicio y el final de la llamada. Observe la información de retardo y jitter obtenida usando paquetes poke y pong. Estos paquetes ayudan a generar la salida del comando “iax2 show netstats”.

```
vtsvoffice*CLI> iax2 debug
IAX2 Debugging Enabled
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: REGREQ
   Timestamp: 00003ms  SCall: 26975  DCall: 00000 [8.8.30.43:4569]
   USERNAME        : 8590
   REFRESH         : 60
Tx-Frame Retry[000] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: REGAUTH
   Timestamp: 00009ms  SCall: 00003  DCall: 26975 [8.8.30.43:4569]
   AUTHMETHODS     : 2
   CHALLENGE       : 137472844
   USERNAME        : 8590
Rx-Frame Retry[ No] -- OSeqno: 001 ISeqno: 001 Type: IAX     Subclass: REGREQ
   Timestamp: 00016ms  SCall: 26975  DCall: 00003 [8.8.30.43:4569]
   USERNAME        : 8590
   REFRESH         : 60
   MD5 RESULT      : f772b6512e77fa4a44c2f74ef709e873
Tx-Frame Retry[000] -- OSeqno: 001 ISeqno: 002 Type: IAX     Subclass: REGACK
   Timestamp: 00025ms  SCall: 00003  DCall: 26975 [8.8.30.43:4569]
   USERNAME        : 8590
   DATE TIME       : 2006-04-17  16:03:00
   REFRESH         : 60
   APPARENT ADDRES : IPV4 8.8.30.43:4569
   CALLING NUMBER  : 4830258590
   CALLING NAME    : Flavio
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 002 Type: IAX     Subclass: ACK
   Timestamp: 00025ms  SCall: 26975  DCall: 00003 [8.8.30.43:4569]
Tx-Frame Retry[000] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: POKE
   Timestamp: 00003ms  SCall: 00006  DCall: 00000 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: ACK
   Timestamp: 00003ms  SCall: 26976  DCall: 00006 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: PONG
   Timestamp: 00003ms  SCall: 26976  DCall: 00006 [8.8.30.43:4569]
   RR_JITTER       : 0
   RR_LOSS         : 0
   RR_PKTS         : 1
   RR_DELAY        : 40
   RR_DROPPED      : 0
   RR_OUTOFORDER   : 0
Tx-Frame Retry[-01] -- OSeqno: 001 ISeqno: 001 Type: IAX     Subclass: ACK
   Timestamp: 00003ms  SCall: 00006  DCall: 26976 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: NEW
   Timestamp: 00003ms  SCall: 26977  DCall: 00000 [8.8.30.43:4569]
   VERSION         : 2
   CALLING NUMBER  : 8590
   CALLING NAME    : 4830258590
   FORMAT          : 2
   CAPABILITY      : 1550
   USERNAME        : 8590
   CALLED NUMBER   : 8580
   DNID            : 8580
Tx-Frame Retry[000] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: AUTHREQ
   Timestamp: 00007ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
   AUTHMETHODS     : 2
   CHALLENGE       : 190271661
   USERNAME        : 8590
Rx-Frame Retry[Yes] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: NEW
   Timestamp: 00003ms  SCall: 26977  DCall: 00000 [8.8.30.43:4569]
   VERSION         : 2
   CALLING NUMBER  : 8590
   CALLING NAME    : 4830258590
   FORMAT          : 2
   CAPABILITY      : 1550
   USERNAME        : 8590
   CALLED NUMBER   : 8580
   DNID            : 8580
Tx-Frame Retry[-01] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: ACK
   Timestamp: 00003ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 001 ISeqno: 001 Type: IAX     Subclass: AUTHREP
   Timestamp: 00063ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
   MD5 RESULT      : 57cc5c48affba14106c29439944413a1
Tx-Frame Retry[000] -- OSeqno: 001 ISeqno: 002 Type: IAX     Subclass: ACCEPT
   Timestamp: 00054ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
   FORMAT          : 1024
Tx-Frame Retry[000] -- OSeqno: 002 ISeqno: 002 Type: CONTROL Subclass: ANSWER
   Timestamp: 00057ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Tx-Frame Retry[000] -- OSeqno: 003 ISeqno: 002 Type: VOICE   Subclass: 138
   Timestamp: 00090ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 002 Type: IAX     Subclass: ACK
   Timestamp: 00054ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 003 Type: IAX     Subclass: ACK
   Timestamp: 00057ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 004 Type: IAX     Subclass: ACK
   Timestamp: 00090ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 004 Type: VOICE   Subclass: 138
   Timestamp: 00210ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Tx-Frame Retry[-01] -- OSeqno: 004 ISeqno: 003 Type: IAX     Subclass: ACK
   Timestamp: 00210ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 003 ISeqno: 004 Type: IAX     Subclass: PING
   Timestamp: 02083ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Tx-Frame Retry[000] -- OSeqno: 004 ISeqno: 004 Type: IAX     Subclass: PONG
   Timestamp: 02083ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
   RR_JITTER       : 0
   RR_LOSS         : 0
   RR_PKTS         : 1
   RR_DELAY        : 40
   RR_DROPPED      : 0
   RR_OUTOFORDER   : 0
Rx-Frame Retry[ No] -- OSeqno: 004 ISeqno: 005 Type: IAX     Subclass: ACK
   Timestamp: 02083ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 004 ISeqno: 005 Type: IAX     Subclass: HANGUP
   Timestamp: 08693ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
   CAUSE           : Dumped Call
```

Para desactivar la depuración, use:

```
vtsvoffice*CLI>iax2 no debug
```

### Resumen

Este capítulo ha revisado las fortalezas y debilidades del protocolo IAX. Ha demostrado cómo funciona IAX en varios escenarios, como softphones y un trunk entre dos servidores Asterisk. El modo trunk le permite ahorrar ancho de banda al transportar más de una llamada en un solo paquete. Finalmente, aprendió los comandos de consola que puede usar para verificar el estado y depurar el protocolo.

## Legacy SIP: chan_sip and sip.conf (removed in Asterisk 21+)

> **Legacy / historical:** Everything in this section uses the old `chan_sip`
> driver and its `sip.conf` configuration file. `chan_sip` was deprecated for
> several releases and **removed in Asterisk 21**, so it **does not exist in
> Asterisk 22**. None of the `sip.conf` examples below will run on a current
> system — they are kept here only to document how legacy deployments worked and
> to help you migrate them. For the modern, supported way to do any of this, see
> the *PJSIP: the SIP channel* section of the *SIP & PJSIP in depth* chapter. The
> SIP *protocol* theory (methods, registration, proxy/redirect, SDP, NAT types)
> is protocol-level and lives in that chapter; what follows is purely the removed
> `chan_sip` **configuration**.

On legacy systems through Asterisk 20, SIP was configured in `/etc/asterisk/sip.conf`, which used to be the second most changed file (just after `extensions.conf`). The sections below show how `chan_sip` connected Asterisk to a SIP provider, how to connect two Asterisks together using SIP, domain support, presence, codec/DTMF/QoS options, authentication, and NAT — followed by a guide to migrating all of it to PJSIP.

### Connecting Asterisk to a SIP provider (sip.conf)

Asterisk is often used to connect to a SIP VoIP provider. VoIP providers usually have better rates for phone calls than traditional providers. Another interesting and attractive point of VoIP providers is the possibility to buy DID numbers in other cities—even in foreign countries. These are good reasons to use VoIP for telecommunications. In this section, you will learn how legacy `chan_sip` connected Asterisk to a VoIP provider. Three steps are required to connect Asterisk to a SIP provider. Tests can be conducted by establishing an account with your favorite provider. Step 1: Registering with a SIP provider in sip.conf To connect to a SIP provider, you will need the following information from the provider:

![Asterisk connected to a VoIP service provider over the Internet or a private WAN, with local SIP phones registered to the Asterisk server](../images/07-sip-and-pjsip-fig07.png)

- username
- secret and remotesecret (Use secret to authenticate inbound requests and remotesecret for outbound requests)
- hostname
- domain
- codecs allowed

This configuration will allow your provider to locate Asterisk’s IP address. In the following statement, we are telling Asterisk to register to a SIP provider defined by the hostname and inform the provider of Asterisk’s IP address. The statement says that you want to receive calls at extension 4100. In the [general] section of the sip.conf file, enter the following line:

```
register=>name:secret@hostname/4100
```

Paso 2: Configure el [peer] en sip.conf Cree una entrada de tipo peer al proveedor deseado para simplificar la marcación de Asterisk.

```
[provider]
context=incoming
type=friend
dtmfmode=rfc2833
directmedia=no
username=username
remotesecret=secret
host=hostname
fromuser=username
fromdomain=domain
insecure=invite
disallow=all
allow=ulaw ; or any other codec available from your provider
```

Paso 3: Crear una ruta al proveedor en el dial plan  
Elegiremos los dígitos 010 como la ruta de destino al proveedor.  
Para marcar #610000 dentro del proveedor, simplemente marque 010610000.

```
exten=>_010.,1,Set(CALLERID(num)=username)
exten=>_010.,n,Set(CALLERID(Name)="Flavio Gonçalves")
exten=>_010.,n,Dial(SIP/${EXTEN:3}@provider)
exten=>_010.,n,Hangup
```

#### Opciones SIP específicas para el escenario del proveedor

La siguiente discusión examina los detalles de las opciones establecidas en el archivo sip.conf para la conexión a un proveedor de VoIP.

```
register=>username:password@hostname/4100
```

La instrucción `registered` en el archivo `sip.conf` se usa para registrarse con un proveedor. La transacción `register` se autentica con el nombre y el secreto. Puede usar una barra diagonal (“/”) para proporcionar una extensión para llamadas entrantes. Técnicamente, la extensión se colocará en el campo de encabezado “Contact” de la solicitud SIP. El comportamiento de registro puede controlarse mediante ciertos parámetros:

```
registertimeout=20
registerattempts=10
```

Para verificar si el registro fue exitoso, el comando de consola heredado era `sip show registry`. En Asterisk 22 el comando equivalente es `pjsip show registrations` (registraciones salientes) y `pjsip show endpoints` para el estado del endpoint.

El parámetro “username” se usa en el digest de autenticación. El digest se calcula usando username, secret y realm:

```
username=username
```

Host define la dirección o el nombre del proveedor de VoIP:

```
host=hostname
```

Los parámetros Fromuser y Fromdomain a veces son requeridos para la autenticación. Estos parámetros se utilizan en el campo de encabezado SIP From:

```
fromuser=username
fromdomain=hostname
```

Cuando te conectas a un proveedor de VoIP, se requieren credenciales. Después de la invitación inicial, el proveedor te envía un mensaje llamado “407 Proxy Authentication Required”; proporcionas las credenciales en el mensaje INVITE subsiguiente. Para llamadas entrantes, tu servidor Asterisk solicitará credenciales al proveedor. Evidentemente, el proveedor no posee una credencial válida para tu servidor Asterisk. Cuando utilizas insecure=invite, le indicas a Asterisk que no envíe el “407 Proxy Authentication Required” al proveedor y que acepte llamadas entrantes. También puedes usar insecure=port, invite para que coincida con el peer basándose en la dirección IP sin coincidir el número de puerto.

```
insecure=invite, port
```

### Conectando dos servidores Asterisk entre sí usando SIP (sip.conf)

Puede usar SIP para interconectar dos cajas Asterisk. Es importante prestar atención al dial plan antes de continuar con esta configuración. Los usuarios generalmente quieren conectar otras PBX con el mínimo esfuerzo. La idea aquí es usar solo un número de extensión para conectar con la otra PBX. Paso 1: Edite el archivo sip.conf en el servidor A:

```
[B]
type=user
secret=B
host=A
disallow=all
allow=ulaw
directmedia=no
[B-out]
type=peer
fromuser=A
username=A
remotesecret=A
host=B
disallow=all
allow=ulaw
directmedia=no
```

Paso 2: Edite el archivo sip.conf en el servidor B:

```
[A]
type=user
host=B
secret=A
disallow=all
allow=ulaw
directmedia=no
[A-out]
```

![Conectando dos servidores Asterisk usando SIP: el servidor A (extensiones 4400/4401) y el servidor B (extensiones 4500/4501) intercambian señalización SIP para que los usuarios en cada PBX puedan marcar al otro](../images/07-sip-and-pjsip-fig08.png)

```
type=peer
host=A
fromuser=B
username=B
remotesecret=B
disallow=all
allow=ulaw
directmedia=no
```

Paso 3: Editar el archivo extensions.conf en el servidor A:

```
[default]
exten=_44XX,1,dial(SIP/${EXTEN},20)
exten=_44XX,2,hangup()
exten=_45XX,1,dial(SIP/B-out/${EXTEN})
exten=_45XX,2,hangup()
```

Paso 4: Edite el archivo extensions.conf en el servidor B:

```
[default]
exten=_44XX,1,dial(SIP/A-out/${EXTEN})
exten=_44XX,2,hangup()
exten=_45XX,1,dial(SIP/${EXTEN})
exten=_45XX,2,hangup()
```

### Soporte de dominio de Asterisk (sip.conf)

El protocolo SIP sigue la arquitectura de Internet. Lo primero que hay que hacer antes de configurar SIP es establecer correctamente los servidores DNS. En un entorno SIP, puedes llamar a un usuario ubicado en cualquier proxy SIP, y otros usuarios también pueden llamarte usando tu Identificador Uniforme de Recursos SIP (URI). Para establecer un servidor DNS para SIP, debes añadir registros SRV a tu servidor DNS.

```
; SIP server/proxy and its backup server/proxy
sip1.yourdomain.com
21600 IN A
200.180.4.169
sip2.yourdomain.com
21600 IN A
200.175.61.150
;
; DNS SRV records for SIP
_sip._udp.yourdomain.com  21600 IN SRV 10 0 5060 sip1.voip.school.
_sip._udp.yourdomain.com  21600 IN SRV 20 0 5060 sip2.voip.school.
```

Después de configurar el DNS, puedes usar el URI, que apunta a un usuario SIP, un teléfono SIP o una extensión telefónica. Un URI SIP se parece a una dirección de correo electrónico (p. ej., sip:chuck@yourpartnerdomain.com). Al usar URIs SIP, no se necesita un número de teléfono para realizar una llamada de un teléfono SIP a otro. Para marcar a un usuario externo, simplemente usa una sentencia como la que se muestra a continuación.

```
exten=4000,1,dial(SIP/chuck@yourpartnerdomain.com)
```

Ciertos parámetros pueden controlar el comportamiento del dominio.

```
srvlookup=yes
```

Este parámetro habilita búsquedas DNS SRV en llamadas salientes. Usando este parámetro, es posible marcar llamadas usando nombres SIP basados en el dominio.

```
allowguest=yes
```

Este parámetro permite que una invitación externa sea procesada sin autenticación. Procesa la llamada dentro del contexto definido en la sección general o en la declaración de dominio. Advertencia: Si define un contexto en la sección general con acceso a PSTN, un usuario externo puede marcar la PSTN a través de su PBX. En este caso, incurrirá en cargos. Permita solo sus propias extensiones en el contexto definido en la sección general.

![Conexión a otros servidores SIP por dominio: youdomain.com y yourpartnerdomain.com intercambian señalización SIP, de modo que usuarios como lee y bruce pueden llamar a chuck y norris usando URIs SIP](../images/07-sip-and-pjsip-fig09.png)

```
domain=acme.com,default
```

El comando **domain** permite manejar más de un dominio dentro de Asterisk. Si una llamada proviene de un dominio específico, se dirige a un contexto específico.

```
;autodomain=yes
```

Este parámetro incluye la IP local y el nombre de host en los dominios permitidos.

```
;allowexternaldomains=no
```

The default is yes. Uncomment the line to disallow calls to outside domains.

### SIP advanced configurations (sip.conf)

This section explains some advanced parameters of the legacy SIP channel, such as presence, codec selection, DTMF options, and QoS packet marking. The **concepts** (BLF/presence, codec negotiation, DTMF modes, DSCP marking) carry over to PJSIP, but the `sip.conf` parameter names shown here do **not** exist in Asterisk 22. On PJSIP, DTMF mode is `dtmf_mode=` on an endpoint, and codecs are set with `allow=`/`disallow=`.

#### SIP Presence

SIP presence is partially implemented in Asterisk. Asterisk supports requests such as SUBSCRIBE and NOTIFY users depending on the state of a channel. Asterisk does not support the SIP method PUBLISH. In other words, you can subscribe to the states (busy, idle, and ringing) of a channel, but cannot publish information such as “away” or “do not disturb”. The most common scenario for presence is busy lamp field (BLF), in which you simulate the behavior of a KS system with lamps for each extension and trunk. SIP parameters for presence:

- allowsubscribe=yes: Allow SIP subscription methods
- subscribecontext=sip_subscribers: Context where to look for hints
- notifyring=yes: Send SIP NOTIFY on ring
- notifyhold=yes: Send SIP NOTIFY on hole
- counteronpeer (renamed from limitonpeer for Asterisk 1.4.x): Apply the counter only on the peer side
- callcounter=yes: Enable call counters in the device.
- busylevel=1: Threshold for the number of calls for considering the device as busy.

For example: Step 1: Testing SIP presence with Asterisk is not that hard. First, let’s configure the files sip.conf and extensions.conf.

In the file sip.conf

```
[general]
bindaddr=0.0.0.0
bindport=5060
disallow=all
allow=ulaw
allowsubscribe=yes
notifyringing=yes
notifyhold=yes
limitonpeer=yes
counteronpeer=yes
subscribecontext=default
[2000]
type=friend
host=dynamic
context=default
dtmfmode=rfc2833
secret=senha
callcounter=yes
busylevel=1
[2001]
type=friend
host=dynamic
context=default
dtmfmode=rfc2833
secret=senha
callcounter=yes
busylevel=1
In the file extensions.conf
[default]
exten=2000,hint,SIP/2000
exten=2001,hint,SIP/2001
exten=_20XX,1,dial(SIP/${EXTEN})
exten=_20XX,n,Hangup()
```

Step 2: Ahora configure el softphone para usar presencia. Le mostraremos cómo configurar el SipPulse Softphone.

- Secuencia: clic‑derecho→SIP Account Settings→Properties→Presence
- Cambie el modelo de presencia de peer-to-peer a presence agent, lo que hará que el softphone se suscriba a Asterisk para eventos SIP.

Step 3: Añada el contacto a otros softphones. En este ejemplo, el SipPulse Softphone es la cuenta 2000, así que añadiremos un contacto para la cuenta 2001. Secuencia: Abra el panel derecho (panel de presencia en el softphone)→Haga clic en Contacts→Add a contact. Complete el nombre 2001. Display as 2001 y no olvide marcar la casilla Show this contact’s availability.

Step 4: Ahora llame a la extensión 2001 y verifique el estado del teléfono en el panel derecho del softphone. Use el comando de consola `core show hints` para ver cómo cambia el estado de presencia en el servidor (en chan_sip heredado, `sip show inuse` mostraba cuántas llamadas tenía en cada línea). En Asterisk 22, use `pjsip show endpoints` para inspeccionar el estado del endpoint y del canal. El estado de presencia/BLF aparece en los contactos del softphone o en el panel BLF — exactamente cómo se muestra depende del cliente.

#### Codec configuration

Codec configuration is simple and straightforward. You can set the words allow and disallow in the [general] section or peer/user section. The best practice is to standardize the codec to avoid transcoding, which is processor intensive. Please use the same codec for messages and prompts.

```
[general]
disallow=all
allow=g729
```

#### Opciones DTMF

En ciertas ocasiones, pasarás dígitos a una aplicación como voicemail o respuesta de voz interactiva (IVR). Es importante pasar DTMF correctamente. El método más simple para pasar DTMF se llama inband. Se configura en la sección [general] o peer/user del archivo sip.conf. Cuando estableces dtmfmode=inband, los tonos DTMF se generan como sonidos en el canal de audio. El principal problema de este método es que, al comprimir el canal de audio usando un codec como g729, los sonidos se distorsionan y los tonos DTMF no se reconocen adecuadamente. Si planeas usar dtmfmode=inband, utiliza el codec g.711 (ulaw y alaw).

```
dtmfmode=inband
```

Otro enfoque es usar RFC2833, que permite pasar tonos DTMF como eventos nombrados en los paquetes RTP.

```
dtmfmode=rfc2833
```

Finalmente, puedes pasar dígitos DTMF dentro de paquetes SIP, en lugar de paquetes RTP. Este método está definido en los RFC3265 (eventos de señalización) y RFC2976.

```
dtmfmode=info
```

Following the release of version 1.2, it is now possible to use:

```
dtmfmode=auto
```

Esto intenta usar RFC2833; si no es posible, use tonos de banda.

#### Configuración del marcado de Calidad de Servicio (QoS)

QoS es un conjunto de técnicas responsables de la calidad de voz. QoS se implementa de manera que reduzca el ancho de banda, la latencia y el jitter. Las funciones principales de QoS son la programación de paquetes, la fragmentación y la compresión de encabezados. QoS se implementa en conmutadores y enrutadores, no en Asterisk mismo. Sin embargo, Asterisk puede ayudar a los enrutadores y conmutadores marcando los paquetes para entrega rápida. El marcado se realiza usando puntos de código de servicios diferenciados (DSCP) definidos en los RFC 2474 y RFC2475.

```
tos_sip=cs3
tos_audio=ef
tos_video=af41
```

A partir de la versión 1.4, puedes especificar códigos diferentes para señalización (SIP), audio (RTP) y video (RTP).

### Autenticación SIP (sip.conf)

Cuando el legado `chan_sip` recibía una llamada SIP, seguía las reglas descritas en el diagrama siguiente. Tres parámetros jugaban un papel importante en la autenticación SIP. En Asterisk 22, la autenticación se configura en su lugar con objetos PJSIP `auth` (`type=auth`, `auth_type=userpass`, `username=`, `password=`) referenciados por un endpoint, y el control de acceso IP se realiza con `permit=`/`deny=` en el endpoint o mediante un `acl`.

![Flujo de decisión de autenticación del chan_sip heredado: Asterisk verifica el encabezado From contra sip.conf, intenta la sección type=user/peer coincidente y credenciales MD5, y recurre a insecure=invite o allowguest antes de permitir o denegar la llamada](../images/07-sip-and-pjsip-fig10.png)

```
allowguest=yes/no
```

Este parámetro controla si un usuario sin un peer correspondiente puede autenticarse sin un nombre y secreto. Discutimos este parámetro en la sección de soporte de dominios.

```
insecure=invite,port
```

Cuando usamos `insecure=invite`, Asterisk no genera el mensaje “407 Proxy Authentication Required”. Sin este mensaje, el usuario puede realizar una llamada sin autenticación. Esto se usa a menudo para conectar con proveedores de servicios VoIP. Las llamadas que provienen del proveedor de servicios VoIP generalmente no están autenticadas.

```
autocreatepeer=yes/no
```

Este comando se usa cuando Asterisk está conectado a un proxy SIP. Crea dinámicamente un peer para cada llamada. Cuando esta opción está habilitada, cualquier UAC puede conectarse al servidor Asterisk. Es importante limitar la conexión IP al proxy SIP. El proxy SIP, a su vez, se encarga del control de acceso. La configuración del peer se basa en las opciones generales así como en el campo de encabezado “Contact” del paquete SIP. Advertencia: Use esto con extrema precaución ya que abre completamente Asterisk.

```
secret=secret, remotesecret=secret
```

Este parámetro configura el secreto para la autenticación; use secret para solicitudes entrantes y remotesecret para solicitudes salientes. Si no desea presentar los secretos en archivos de texto, puede usar md5secret para incluir un hash en lugar del secreto. Para generar el secreto MD5, puede usar:

```
echo -n "username:realm:secret" |md5sum
```

Luego use la siguiente declaración:

```
md5secret=0b0e5d467890....
```

Advertencia: No olvide usar el parámetro –n; el retorno de carro se usará en el cálculo md5.

```
deny=0.0.0.0/0.0.0.0
permit=192.168.1.0/255.255.255.0
```

Las declaraciones anteriores denegarán todas las direcciones IP y permitirán UAC solo desde la red local (192.168.1.0/24).

#### Opciones RTP

Es posible controlar algunos parámetros RTP.

```
rtptimeout=60
```

This terminates calls without RTP activity for more the 60 seconds when not in hold.

```
rtpholdtimeout=120
```

Esto termina llamadas sin actividad RTP incluso en espera (debe ser mayor que rtptimeout).

### SIP NAT traversal (sip.conf)

La *teoría* NAT (los cuatro tipos de NAT, el problema del encabezado Contact, los keep-alives y forzar los medios a través del servidor) es a nivel de protocolo y se cubre en el capítulo *SIP & PJSIP in depth*. Los parámetros `sip.conf` mostrados aquí (`nat=`, `qualify=`, `directmedia=`, `externaddr=`, `localnet=`) son **legacy chan_sip** y fueron eliminados en Asterisk 21+. En PJSIP estos se asignan a configuraciones de transporte/endpoint como `rewrite_contact=yes`, `force_rport=yes`, `rtp_symmetric=yes`, `direct_media=no`, `external_media_address`, `external_signaling_address` y `local_net=` en el transporte, más `qualify_frequency=` en el AOR.

En legacy chan_sip, el parámetro `nat` tenía cinco opciones:

- nat = no — No realizar manejo especial de NAT más allá de RFC3581
- nat = force_rport — Pretender que había un parámetro rport aun si no lo había
- nat = comedia — Enviar medios al puerto desde el que Asterisk los recibió sin importar a dónde indique el SDP.
- nat = auto_force_rport — Establecer la opción force_rport si Asterisk detecta NAT (predeterminado)
- nat = auto_comedia — Establecer la opción comedia si Asterisk detecta NAT

Cuando colocas la declaración “nat=force_rport” en el archivo sip.conf, le estás indicando a Asterisk que ignore la dirección contenida en el campo de encabezado “Contact” del encabezado SIP y que use la dirección IP de origen y el puerto en el encabezado IP del paquete, y también que envíe los medios de vuelta a la dirección desde donde fueron recibidos ignorando el contenido del encabezado SDP.

```
nat=force_rport,comedia
```

Es necesario mantener el mapeo NAT abierto. Si el NAT expira, Asterisk no puede enviar una invitación al UAC. El UAC puede enviar llamadas, pero no recibir ninguna. La siguiente declaración puede usarse para mantener el NAT abierto.

```
qualify=yes
```

Qualify enviará un paquete SIP usando el método OPTIONS de forma regular, lo que ayudará a mantener abierto el NAT. Qualify envía un OPTIONS cada 60 segundos y cada décimo segundo cuando el host no es accesible. Puedes usar “sip show peers” para ver la latencia de los peers. Si el NAT del usuario es del tipo simétrico, no es posible enviar paquetes de un UAC a otro directamente; en ese caso debes forzar el RTP a través de Asterisk usando:

```
directmedia=no
```

#### Asterisk behind NAT (sip.conf)

Todos los escenarios anteriores asumen que el servidor Asterisk tiene una dirección externa (válida) de Internet. A veces el servidor Asterisk se implementa detrás de un firewall con NAT. En este caso, es necesario realizar algunas configuraciones adicionales.

![Asterisk behind NAT: a firewall maps the public address 200.180.4.168 to the internal Asterisk server (192.168.1.100), forwarding SIP on UDP 5060 and the RTP range UDP 10000–20000 defined in rtp.conf](../images/07-sip-and-pjsip-fig13.png)

1. Configure el firewall para redirigir el puerto UDP 5060 de forma estática al servidor Asterisk.  
2. Configure el firewall para redirigir los puertos UDP del 10000 al 20000 de forma estática.

Si desea restringir la cantidad de puertos abiertos, puede editar el archivo `rtp.conf` para cambiar el rango de puertos RTP. Otra forma es usar un firewall inteligente que admita el protocolo SIP para abrir los puertos RTP dinámicamente.

```
; RTP Configuration
;
[general]
;
; RTP start and RTP end configure start and end addresses
;
rtpstart=10000
rtpend=20000
```

Paso 3: Configure Asterisk para incluir la dirección externa en los campos de encabezado de los paquetes SIP, incluido el Session Description Protocol (SDP). Puede lograrlo añadiendo las siguientes dos declaraciones al archivo sip.conf:

```
externaddr=200.180.4.168
;External IP address
localnet=192.168.1.0/255.255.255.0
;Internal Network Address
nat=force_rport,comedia
```

El primer parámetro **externaddr** indica a Asterisk que incluya la dirección IP externa dentro de los encabezados SIP para destinos externos. El segundo parámetro **localnet** permite a Asterisk diferenciar entre direcciones externas e internas. Opcionalmente, puede usar **externhost** si utiliza un DNS dinámico con una dirección DHCP en el servidor.

### Cadenas de marcación SIP (chan_sip)

La tecnología de cadena de marcación `SIP/...` mostrada a continuación es el controlador **chan_sip** eliminado. En Asterisk 22 use la tecnología `PJSIP/...` en su lugar — por ejemplo `Dial(PJSIP/2000)` o `Dial(PJSIP/${EXTEN}@provider)`. Las formas y el significado son, por lo demás, análogos.

Puede llamar a un destino SIP heredado usando diferentes cadenas de marcación:

```
SIP/peer
```

- ; Necesita tener un peer definido en sip.conf

```
SIP/flavio@voffice.com.br ; By the URI
SIP/[exten@]peer[:portno]
SIP/[user:password@domain/extension
```

Los ejemplos incluyen:

```
exten=>s,1,Dial(SIP/ipphone)
exten=>s,1,Dial(SIP/info@voffice.com.br)
exten=>s,1,Dial(SIP/192.168.1.8:5060,20)
exten=>s,1,Dial(SIP/8500@sip.com:9876)
```

## Migrando un sistema legacy chan_sip a PJSIP

Porque `chan_sip` fue eliminado en Asterisk 21 y ya no está en Asterisk 22, cualquier
despliegue existente de `sip.conf` debe migrarse a PJSIP. El mayor cambio conceptual
es que un solo `sip.conf` `[peer]` o `[friend]` se divide en varios
objetos PJSIP, cada uno con un `type=`: un **endpoint** (configuraciones de llamada/códec/media),
uno o más objetos **aor** (donde se puede alcanzar el dispositivo / registro),
un objeto **auth** (credenciales), y un **transport** compartido (el socket de escucha,
direcciones NAT). La tabla siguiente asigna los conceptos más comunes.

| Concepto legacy sip.conf | Equivalente PJSIP (pjsip.conf) |
| --- | --- |
| `[peer]` / `[friend]` block | `type=endpoint` + `type=aor` + `type=auth` (referenciado vía `auth=` y `aors=`) |
| `type=friend` / `type=peer` / `type=user` | un solo `type=endpoint` (PJSIP no tiene distinción de friend/peer/user) |
| `host=dynamic` (el dispositivo se registra) | `type=aor` con `max_contacts=1`; el dispositivo REGISTERs para actualizar su contacto |
| `host=<ip/hostname>` (estático) | `type=aor` con un `contact=sip:host:port` estático |
| `register=>user:secret@host/ext` (saliente) | `type=registration` (`server_uri=`, `client_uri=`, `outbound_auth=`) |
| `secret=` / `username=` | `type=auth`, `auth_type=userpass`, `username=`, `password=` |
| `context=` | `context=` en el endpoint |
| `disallow=all` / `allow=ulaw` | `disallow=all` / `allow=ulaw` en el endpoint (misma sintaxis) |
| `dtmfmode=rfc2833` | `dtmf_mode=rfc4733` (PJSIP) — también `inband`, `info`, `auto` |
| `directmedia=yes/no` | `direct_media=yes/no` en el endpoint |
| `nat=force_rport,comedia` | `force_rport=yes`, `rewrite_contact=yes`, `rtp_symmetric=yes` (endpoint) |
| `qualify=yes` | `qualify_frequency=` (segundos) en el **aor** |
| `externaddr=` | `external_media_address=` y `external_signaling_address=` en el **transport** |
| `localnet=` | `local_net=` en el **transport** |
| `insecure=invite` (proveedor, sin auth) | omitir `auth=`/`outbound_auth=` y usar `identify` (`type=identify`, `match=`) |
| `allowguest=yes` | `anonymous` endpoint + `allow_unauthenticated_options` (usar con cuidado) |
| `tos_sip` / `tos_audio` | `tos_audio` / `tos_video` (y `cos_audio` / `cos_video`) en el endpoint |

Una extensión registradora que se veía así en el legacy `sip.conf`:

```
[2000]
type=friend
host=dynamic
context=default
dtmfmode=rfc2833
disallow=all
allow=ulaw
secret=senha
```

se convierte en lo siguiente en `pjsip.conf` en Asterisk 22:

```
[2000]
type=endpoint
context=default
disallow=all
allow=ulaw
dtmf_mode=rfc4733
direct_media=no
auth=2000
aors=2000

[2000]
type=auth
auth_type=userpass
username=2000
password=senha

[2000]
type=aor
max_contacts=1
qualify_frequency=60
```

### The sip_to_pjsip.py conversion script

Asterisk ships a helper script, **`sip_to_pjsip.py`**, that reads an existing
`sip.conf` and produces a `pjsip.conf`. You can run it directly in the
/etc/asterisk directory. The utility is in the Asterisk source tree under
`contrib/scripts/sip_to_pjsip/`, where `${PATH_TO_ASTERISK_SOURCE}` is the path
where the Asterisk source files are found (usually /usr/src/asterisk-22.x.y/):

```
${PATH_TO_ASTERISK_SOURCE}/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py
```

If you run it with the `--help` option you will see its options:

```
-h, --help                help
-p, --prefix PREFIX       prefix to use for the included config files
-q, --quiet               suppress warnings and informational messages
```

También acepta argumentos posicionales opcionales — `[input-file [output-file]]`,
con valores predeterminados `sip.conf` y `pjsip.conf` en el directorio actual.

Trate su salida como un **punto de partida**: revise cada objeto generado,
especialmente los transportes, la configuración NAT y las listas de códecs, y pruebe a fondo antes de pasar a producción.

Migramos el sip.conf en nuestros laboratorios acompañantes en VoIP School Blackbelt (voip.school)

#### sip.conf

```
[general]
bindport=5060
bindaddr=0.0.0.0
context=dummy
disallow=all
allow=ulaw
alwaysauthreject=yes
allowguest=no
register=>1020:supersecret@sip.flagonc.com:5600/9999
[alice]
type=friend
secret=#supersecret#
host=dynamic
qualify=yes
directmedia=no
context=from-internal
[bob]
type=friend
secret=#supersecret#
host=dynamic
qualify=yes
directmedia=no
context=from-internal
[siptrunk]
type=peer
defaultuser=1020
secret=supersecret
port=5600 ; nor 5060, 5600
insecure=invite
host=sip.flagonc.com
fromuser=1020
fromdomain=sip.flagonc.com
context=from-siptrunk
```

#### pjsip.conf

```
;--
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements start
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
[general]
bindport = 5060
[alice]
qualify = yes
[bob]
qualify = yes
[siptrunk]
defaultuser = 1020
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements end
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
--;
[transport-udp]
type = transport
protocol = udp
bind = 0.0.0.0:5060
[reg_sip.flagonc.com]
type = registration
retry_interval = 20
max_retries = 10
contact_user = 9999
expiration = 120
transport = transport-udp
outbound_auth = auth_reg_sip.flagonc.com
client_uri = sip:1020@sip.flagonc.com:5600
server_uri = sip:sip.flagonc.com:5600
[auth_reg_sip.flagonc.com]
type = auth
password = supersecret
username = 1020
[alice]
type = aor
max_contacts = 1
[alice]
type = auth
username = alice
password = #supersecret#
[alice]
type = endpoint
context = from-internal
disallow = all
allow = ulaw
direct_media = no
auth = alice
outbound_auth = alice
aors = alice
[bob]
type = aor
max_contacts = 1
[bob]
type = auth
username = bob
password = #supersecret#
[bob]
type = endpoint
context = from-internal
disallow = all
allow = ulaw
direct_media = no
auth = bob
outbound_auth = bob
aors = bob
[siptrunk]
type = aor
contact = sip:1020@sip.flagonc.com:5600
[siptrunk]
type = identify
endpoint = siptrunk
match = sip.flagonc.com
[siptrunk]
type = auth
username = siptrunk
password = supersecret
[siptrunk]
type = endpoint
context = from-siptrunk
disallow = all
allow = ulaw
from_user = 1020
from_domain = sip.flagonc.com
auth = siptrunk
outbound_auth = siptrunk
aors = siptrunk
```

Mientras la conversión parece correcta, podemos ver que algunos elementos como qualify=yes no pueden mapearse directamente. Para solucionarlo, debe agregar a la sección aor el comando qualify_frequency=time en segundos. Ejemplo a continuación.

```
[bob]
type = aor
max_contacts = 1
qualify_frequency=15
```

La configuración completa de PJSIP se cubre en el capítulo *SIP & PJSIP in depth*, y la documentación oficial en docs.asterisk.org cubre completamente el canal. En nuestros laboratorios complementarios en voip.school, el laboratorio 5 le permite practicar lo que acaba de aprender.

## Resumen

Este capítulo reúne las tecnologías de canales que preceden a los despliegues de VoIP puro de hoy, pero que Asterisk 22 aún soporta. Viste cómo las líneas **analógicas** y los teléfonos se conectan mediante interfaces **FXO/FXS** en DAHDI, cómo se provisionan los enlaces **digitales TDM** (E1/T1 e ISDN PRI/BRI), y cómo **IAX2** (`chan_iax2`) sigue sirviendo como un tronco servidor‑a‑servidor eficiente y amigable con NAT, aunque ahora es claramente legado. También revisaste el controlador **`chan_sip`** retirado y su sintaxis `sip.conf` — que encontrarás en sistemas más antiguos pero que ya no existe en Asterisk 22 — y trabajaste en la migración de dicho sistema a PJSIP con la tabla de mapeo de conceptos y el script `sip_to_pjsip.py`. La regla práctica: recurre a cualquier cosa de este capítulo solo cuando el hardware real o un sistema legado existente te obliguen; todo lo nuevo debe ser PJSIP sobre IP.

## Quiz

1. Regarding the two analog Foreign eXchange interfaces, mark the correct statements (choose all that apply):
   - A. An FXO interface connects to the public switched telephone network (PSTN) central office and draws dial tone from it.
   - B. An FXS interface provides dial tone and ringing power to a standard analog phone, fax, or modem.
   - C. An FXS interface is the correct way to connect Asterisk to a telco line.
   - D. An FXO interface can also be connected to an extension port of a legacy PBX.
2. Supervision signaling on an analog line includes which of the following (choose all that apply)?
   - A. On-hook
   - B. Off-hook
   - C. Ringing
   - D. DTMF
3. Echo, pops, and noise on a DAHDI analog card are most often caused by:
   - A. The way Asterisk was compiled
   - B. PCI interrupt conflicts
   - C. An incorrect SIP codec
   - D. A missing dial plan
4. For precise billing on analog channels you must detect exactly when the far end answers. Which feature do you activate on Asterisk (and request from the telco) to do this?
   - A. Answer reversal
   - B. Billing reversal
   - C. Polarity reversal
   - D. Dial-tone generation
5. The DAHDI hardware is independent of Asterisk: the physical card is configured in `/etc/dahdi/system.conf`, while `chan_dahdi.conf` defines the Asterisk channels, not the hardware itself.
   - A. True
   - B. False
6. Regarding digital trunk capacity and signaling, mark the correct statements (choose all that apply):
   - A. An E1 trunk carries 30 voice channels and a T1 trunk carries 24.
   - B. An ISDN PRI uses 30B+D on an E1 and 23B+D on a T1.
   - C. ISDN is an example of CCS signaling, while MFC/R2 is an example of CAS signaling.
   - D. T1 is the digital trunk most commonly used in Europe and Latin America.
7. Which utility automatically detects DAHDI cards and generates `/etc/dahdi/system.conf` and `dahdi-channels.conf`?
   - A. dahdi_generator
   - B. dahdi_genconf
   - C. dahdi_cfg
   - D. generate_dahdi
8. When migrating a legacy `sip.conf` `[friend]` to PJSIP, a single block must be split into several objects. Which set of PJSIP `type=` objects normally replaces one registering `[friend]`?
   - A. `type=endpoint`, `type=aor`, and `type=auth`
   - B. `type=peer` and `type=user`
   - C. `type=sip` only
   - D. `type=channel` and `type=device`
9. What is the main practical advantage of using IAX2 trunk mode between two Asterisk servers?
   - A. It encrypts every call with TLS by default
   - B. It carries several calls under a single header, saving bandwidth
   - C. It removes the need for any codec
   - D. It allocates a separate UDP port per call for better quality
10. RSA keys can be used for IAX2 authentication. Which key must you keep secret, and which do you give to the other server?
    - A. Keep the public key secret; share the private key
    - B. Keep the private key secret; share the public key
    - C. Keep the shared key secret; share the private key
    - D. Both keys must be shared

**Answers:** 1 — A, B, D · 2 — A, B, C · 3 — B · 4 — C · 5 — A · 6 — A, B, C · 7 — B · 8 — A · 9 — B · 10 — B
