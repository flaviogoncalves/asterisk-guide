# Recursos avançados do Dial Plan

O Capítulo 3 abordou o básico de um dial plan. Por razões didáticas, não explicamos todas as funcionalidades, mas apenas algumas das mais importantes. Este capítulo aprofundará o dial plan, descrevendo técnicas avançadas, novas aplicações e conceitos.

## Objetivos

- Simplifique as entradas de ramais
- Aborde a segurança do plano de discagem e o filtragem de ramais
- Receba chamadas usando um menu IVR
- Use sub-rotinas para evitar reescritas desnecessárias
- Implemente alguma segurança no plano de discagem usando “Include”
- Implemente follow-me usando AsteriskDB
- Implemente comportamento fora do horário no seu PBX
- Use o comando switch para transferir para outro PBX
- Implemente o gerenciador de privacidade
- Implemente correio de voz
- Implemente um diretório corporativo

## Simplificando seu Dial Plan

Você pode simplificar seu dial plan usando a palavra‑chave “same” para definir uma extensão. Isso deve reduzir o número de erros de digitação no dial plan. Veja o exemplo abaixo:

```
exten => 4000,1,NoOp()
same  =>      n,Dial(PJSIP/005C2B313E22)
```

## Segurança do Plano de Discagem

Uma falha foi descoberta no plano de discagem do Asterisk que permite a um usuário injetar um novo canal e número discado no seu plano de discagem. Suponha que você tenha a seguinte linha no seu servidor `exten=>_X.,1,Dial(PJSIP/${EXTEN})` e que um usuário malicioso disque o número `3000&DAHDI/1/011551123456789` no softphone. O protocolo SIP, por padrão, aceita quaisquer caracteres alfanuméricos, portanto a extensão discada realmente acionará duas chamadas: uma para o canal PJSIP/3000 e outra para o canal DAHDI/011551123456789, que é um número internacional. Assim, qualquer usuário com acesso a uma extensão pode discar para qualquer lugar do mundo. A maneira mais simples de evitar esse comportamento é filtrar os números antes de chamar a aplicação dial. A função FILTER() é muito útil para isso. Exemplo:

```
exten=>_X.,1,DIAL(PJSIP/${FILTER(0-9,${EXTEN})})
```

A aplicação filter permitirá que você filtre todos os caracteres do número discado, exceto os números de 0 a 9. Mais informações podem ser encontradas no arquivo README‑SERIOUSLY.bestpractices.txt disponível no Asterisk.

## Recebendo chamadas usando um menu IVR.

Na última seção, você recebeu todas as chamadas usando DID ou encaminhamento para o operador. Agora você aprenderá como implementar um menu IVR, bem como criar um serviço de autoatendimento. Antes de entrar nos detalhes, vamos examinar algumas novas aplicações. Colocamos a saída do comando `core show application` abaixo simplesmente para facilitar a leitura. Você pode obter essas descrições por conta própria usando `core show application <application_name>`.

### A aplicação Background()

Esta aplicação reproduzirá a lista de arquivos fornecida enquanto aguarda que um ramal seja discado pelo canal chamador. Para continuar aguardando dígitos após esta aplicação terminar de reproduzir os arquivos, a aplicação **WaitExten** deve ser usada. A opção **langoverride** especifica explicitamente qual idioma deve ser tentado para os arquivos de som solicitados. Qualquer **context** especificado será o **dial plan context** que esta aplicação usa ao sair para um ramal discado. Se um dos arquivos de som solicitados não existir, o processamento da chamada será encerrado. **Options:**

- s - Faz com que a reprodução da mensagem seja pulada se o canal não estiver no estado 'up' (ou seja, ainda não foi atendido). Se isso acontecer, a aplicação retornará imediatamente.
- n - Não atenda o canal antes de reproduzir os arquivos.
- m - Interrompa somente se o dígito pressionado corresponder a uma extensão de um dígito no contexto de destino.

### O aplicativo Record()

Este aplicativo grava do canal em um nome de arquivo especificado. Se o arquivo existir, ele será sobrescrito.

![10-dialplan-advanced-features figura 1](../images/10-dialplan-advanced-features-img01.png)

- 'format' é o formato do tipo de arquivo a ser gravado (wav, gsm, etc).
- 'silence' é o número de segundos de silêncio permitido antes de retornar.
- 'maxduration' é a duração máxima da gravação em segundos; se estiver ausente ou zero, não há limite máximo.
- 'options' pode conter qualquer uma das seguintes letras:
    - `a` — acrescenta a uma gravação existente em vez de substituí‑la
    - `n` — não atende, mas grava mesmo assim se a linha ainda não foi atendida
    - `q` — silencioso (não reproduz o tom de bip)
    - `s` — pula a gravação se a linha ainda não foi atendida
    - `t` — usa a tecla terminadora alternativa `*` (DTMF) em vez da padrão `#`
    - `x` — ignora todas as teclas terminadoras (DTMF) e continua gravando até o desligamento

Se o nome do arquivo contiver %d, esses caracteres serão substituídos por um número incrementado em um a cada vez que o arquivo for gravado. Use core show file formats para ver os formatos disponíveis no seu sistema. O usuário pode pressionar # para encerrar a gravação e continuar para a próxima prioridade. Se o usuário desligar durante uma gravação, todos os dados serão perdidos e a aplicação será encerrada.

### O aplicativo Playback() application

Este aplicativo reproduz os nomes de arquivos fornecidos (não inclua a extensão). Opções também podem ser incluídas após um símbolo de pipe. A opção 'skip' faz com que a reprodução da mensagem seja ignorada se o canal não estiver no estado 'up' (ou seja, ainda não foi atendido).

![10-dialplan-advanced-features figura 2](../images/10-dialplan-advanced-features-img02.png)

![10-dialplan-advanced-features figura 3](../images/10-dialplan-advanced-features-img03.png)

Se ‘skip’ for especificado, a aplicação retornará imediatamente caso o canal não esteja off the hook. Caso contrário, a menos que ‘noanswer’ seja especificado, o canal será atendido antes que o som seja reproduzido. Nem todos os canais suportam reproduzir mensagens enquanto ainda estão on the hook. Se ‘j’ for especificado, a aplicação pulará para a prioridade n+101 quando o arquivo não existir, se presente. Esta aplicação define a seguinte variável de canal ao concluir:

- PLAYBACKSTATUS — o status da tentativa de reprodução como uma string de texto, um dos:
    - `SUCCESS`
    - `FAILED`

### A aplicação Read()

Esta aplicação lê um número predeterminado de dígitos de string, um certo número de vezes, do usuário para a variável fornecida.

- filename -- arquivo a ser reproduzido antes de ler dígitos ou tom com a opção i  
- maxdigits -- número máximo aceitável de dígitos. Interrompe a leitura após a inserção de maxdigits (sem exigir que o usuário pressione a tecla #). O padrão é 0 – sem limite – para aguardar que o usuário pressione a tecla #. Qualquer valor abaixo de 0 tem o mesmo efeito. O valor máximo aceito é 255.

![10-dialplan-recursos avançados figura 4](../images/10-dialplan-advanced-features-img04.png)

![10-dialplan-advanced-features figura 5](../images/10-dialplan-advanced-features-img05.png)

- option -- options are `s`, `i`, `n`:
    - `s` — retornar imediatamente se a linha não estiver ativa
    - `i` — reproduzir o arquivo como tom de indicação a partir do seu `indications.conf`
    - `n` — ler dígitos mesmo se a linha não estiver ativa
- attempts -- se maior que 1, o número de tentativas que serão feitas caso nenhum dado seja inserido
- timeout -- Um número inteiro de segundos para aguardar uma resposta de dígito. Se maior que 0, esse valor substituirá o timeout padrão.

A aplicação read() deve desconectar se a função falhar ou gerar erro.

### O aplicativo Gotoif()

Esta aplicação fará com que o canal de chamada pule para a localização especificada no dialplan com base na avaliação da condição fornecida. O canal continuará em **labeliftrue** se a condição for verdadeira, ou em **labeliffalse** se a condição for falsa. Os rótulos são especificados com a mesma sintaxe usada dentro da aplicação Goto. Se o rótulo escolhido pela condição for omitido, nenhum salto será realizado; ao invés disso, a execução continuará com a próxima prioridade no dialplan.

### Lab: Construindo um menu IVR passo a passo

Vamos criar um menu IVR com a seguinte funcionalidade. Quando discado, o IVR reproduz um arquivo de áudio com a mensagem “Welcome to the XYZ Corporation; press 1 for sales, 2 for tech support, 3 for training, or wait to speak to a representative.” Os dígitos encaminham a chamada da seguinte forma:

- `1` — transferir para vendas (PJSIP/4001)
- `2` — transferir para suporte técnico (PJSIP/4002)
- `3` — transferir para treinamento (PJSIP/4003)
- Nenhum dígito pressionado — transferir para o operador (PJSIP/4000)

**Etapa 1 – Grave os prompts**

Let’s create an extension to record the prompts. To record a prompt, dial from a soft phone to `9003<filename>` (for example, `9003welcome`). When you hear the beep, start recording; press `#` to stop. You will hear a beep, and the system will play back the recorded prompt.

**Passo 2 – Crie a lógica do menu**

When dialing the 9004 extension, processing jumps to the menu in the `s` extension, priority 1.

### Correspondência ao discar

Este é um menu de configuração da empresa para receber chamadas. O aplicativo `Background()` reproduz a mensagem de boas‑vindas e então aguarda dígitos, comparando o que o chamador disca com as extensões definidas no contexto atual.

```
[incoming]
exten=>s,1,Background(welcome)
exten=>1,1,Dial(DAHDI/1)
exten=>2,1,Dial(DAHDI/2)
exten=>21,1,Dial(DAHDI/3)
exten=>22,1,Dial(DAHDI/4)
exten=>31,1,Dial(DAHDI/5)
exten=>32,1,Dial(DAHDI/6)
```

Quando você disca esta empresa, a mensagem de boas‑vindas é reproduzida primeiro. Em seguida, o Asterisk aguarda que um dígito seja discado:

| Dialed number | Asterisk action |
|---------------|-----------------|
| 1 | Chama imediatamente `Dial(DAHDI/1)` |
| 2 | Aguarda o tempo limite e então chama `Dial(DAHDI/2)` |
| 21 | Chama imediatamente `Dial(DAHDI/3)` |
| 22 | Chama imediatamente `Dial(DAHDI/4)` |
| 3 | Aguarda o tempo limite e então desconecta |
| 31 | Chama imediatamente `Dial(DAHDI/5)` |
| 32 | Chama imediatamente `Dial(DAHDI/6)` |

É importante evitar ambiguidade nos menus. Todos querem ser atendidos rapidamente. Por esse motivo, não se deve usar os números 2, 21 ou 22.

### Lab: Using the Read() application

Por favor, experimente o laboratório com a aplicação read(). Read aceita dígitos do usuário e os insere na variável especificada; você pode então usar a aplicação gotoif para redirecionar a chamada.

## Inclusão de contexto

Um contexto pode incluir o conteúdo de outro contexto. No exemplo acima, qualquer canal pode discar qualquer ramal no contexto interno, mas somente o canal 4003 pode discar ramais internacionais. Você pode usar a inclusão de contexto para facilitar a criação do plano de discagem. Usando a inclusão de contexto, você pode controlar quem tem acesso a quais ramais.

### Solucionando a mensagem “number not found”

É muito comum receber a mensagem “number not found”. A maioria das pessoas confunde o conceito de contextos incluídos porque ele realmente não é intuitivo. Como regra geral, primeiro vá ao arquivo de configuração do canal de entrada, como `pjsip.conf`, `chan_dahdi.conf` e `iax.conf`, e determine o contexto atual. Em seguida, vá ao plano de discagem no arquivo extensions.conf e verifique se o número discado pode ser encontrado nesse contexto. Caso não, algo está errado com seu plano de discagem. As regras de ouro dos contextos são: 1. Um canal só pode discar números dentro do mesmo contexto do canal. 2. O contexto onde a chamada é processada é definido no arquivo de configuração do canal de entrada (`chan_dahdi.conf`, `iax.conf`, `pjsip.conf`).

## Usando a instrução switch

Você pode enviar o processamento do dialplan para outro servidor usando o comando switch. Você precisará do nome e da chave do outro servidor. O context é o context de destino.

![10-dialplan-advanced-features figura 6](../images/10-dialplan-advanced-features-img06.png)

## Ordem de processamento do dialplan

Quando o Asterisk recebe uma chamada entrante, ele procura no contexto definido pelo canal. Em alguns casos, se mais de um padrão corresponder ao número discado, o Asterisk não conseguirá processar a chamada exatamente da forma que você espera. Você pode ver a ordem de correspondência usando o comando CLI `dialplan show`. Exemplo: suponha que você queira discar 912 para encaminhar para um tronco analógico (DAHDI/1) e todos os demais números que começam com 9 para outro tronco analógico (DAHDI/2). Você escreveria algo como:

```
[example]
exten=>_912.,1,Dial(DAHDI/1/${EXTEN})
exten=>_9.,1,Dial(DAHDI/2/${EXTEN})
```

Se dois padrões corresponderem a uma extensão, você pode controlar qual extensão será processada primeiro usando os contextos incluídos. Um contexto incluído é processado depois de um padrão no mesmo contexto.

## A instrução #INCLUDE

Devemos usar um arquivo grande ou vários arquivos? Você pode usar a instrução #include <filename> para incluir outros arquivos no seu extensions.conf. Por exemplo, poderíamos criar um users.conf para usuários locais e um services.conf para serviços especiais. Tenha cuidado para não confundir #include <filename> com o

```
include=>context statement.
```

## Subrotinas com GOSUB

Em versões mais antigas do Asterisk você tinha o comando Macro. Esse comando foi descontinuado há muito tempo em favor do GOSUB. Demonstramos aqui como criar subrotinas para o processamento de voicemail de forma simples e organizada. Formato do comando:

```
gosub([[context,]exten,]priority[(arg1[,...][,argN])])
```

O comando GOSUB está disponível desde o Asterisk 1.6 e suporta passagem de argumentos (disponíveis dentro da subrotina como `${ARG1}`, `${ARG2}`, e assim por diante). Com argumentos, agora é possível substituir completamente os antigos comandos Macro. Macros (`app_macro`) foram removidas no Asterisk 21; você deve usar GOSUB para subrotinas.

### Criando a subrotina

A definição é muito semelhante. Observe a subrotina abaixo definida para voicemail com o nome stdexten (escolha o nome que preferir). Após chamar o comando Dial com o primeiro argumento (nome do canal) verificamos o ${DIALSTATUS} para encaminhar a lógica da chamada ao próximo passo.

```
[stdexten]
exten=>s,1,Dial(${ARG1},20,tT)
exten=>s,n,Goto(${DIALSTATUS})
exten=>s,n,hangup()
exten=>s,n(BUSY),voicemail(${ARG2},b)
exten=>s,n,hangup()
exten=>s,n(NOANSWER),voicemail(${ARG2},u)
exten=>s,n,hangup()
exten=>s,n(CANCEL),hangup
exten=>s,n(CHANUNAVAIL),hangup
exten=>s,n(CONGESTION),hangup
```

### Chamando uma subrotina

Preste atenção ao chamar a subrotina para usar parênteses antes dos parâmetros.

```
exten=>6000,1,Gosub(stdexten,s,1(PJSIP/6000,${EXTEN}))
exten=>6001,1,Gosub(stdexten,s,1(PJSIP/6001,${EXTEN}))
exten=>6002,1,Gosub(stdexten,s,1(PJSIP/6002,${EXTEN}))
exten=>6003,1,Gosub(stdexten,s,1(PJSIP/6003,${EXTEN}))
```

## Usando o Asterisk DB

Para implementar encaminhamento de chamadas e listas negras, precisamos de alguma forma de armazenar e restaurar dados. Felizmente, o Asterisk fornece um mecanismo para armazenar e recuperar dados de um banco de dados interno chamado AstDB. No Asterisk moderno (incluindo o Asterisk 22) o AstDB é suportado por **SQLite3** (o arquivo `/var/lib/asterisk/astdb.sqlite3`); o Asterisk 1.8 e versões anteriores usavam Berkeley DB v1. Isso é semelhante ao banco de dados do registro do Windows, usando o conceito hierárquico de família e chaves. Os dados persistem entre reinicializações do Asterisk. A API família/chave permanece inalterada em relação ao backend antigo; apenas o formato de armazenamento em disco mudou.

### Funções, aplicações e comandos CLI

Existem algumas funções, aplicações e comandos CLI que trabalham com o AstDB:

- variable=${DB(<family/key>)}
- DB(<family/key>)=value
- DB_EXISTS(<family/key>)

Exemplos:

```
exten=_*21*XXXX,1,Set(DB(CFIM/${CALLERID(num)})=${EXTEN:4})
exten=s,1,Set(temp=${DB(CFIM/${EXTEN})})
```

Algumas aplicações podem ser usadas para manipular o AstDB:

- DB_DELETE(<family/key>) — função que retorna e exclui uma única chave
- DBdeltree(<family>) — aplicação que exclui uma família/subárvore inteira

A antiga aplicação `DBdel()` não existe mais no Asterisk 22. Exclua uma única chave com a função de dialplan `DB_DELETE()` — por exemplo `Set(x=${DB_DELETE(family/key)})` ou, como operação de escrita, `Set(DB_DELETE(family/key)=)`. `DBdeltree()` (excluir uma família/subárvore inteira) ainda é uma aplicação.

Também é possível usar comandos CLI para definir e excluir chaves:

- database del
- database put
- database show <family[/key]>
- database showkey
- database deltree
- database get

![10-dialplan-advanced-features figure 7](../images/10-dialplan-advanced-features-img07.png)

![10-dialplan-advanced-features figure 8](../images/10-dialplan-advanced-features-img08.png)

### Implementando Encaminhamento de Chamadas, DND e Listas Negras

Neste exemplo, você aprenderá como implementar encaminhamento de chamada imediato e encaminhamento de chamada quando ocupado. Usaremos *21* para programar o encaminhamento imediato e *61* para programar o encaminhamento quando ocupado. Para cancelar a programação, use #21# e #61#, respectivamente. Use o exemplo acima para popular o banco de dados. Famílias usadas:

- CFIM – Call Forward Immediate
- CFBS – Call Forward on Busy status
- DND – Do Not Disturb

Tente popular o banco de dados discando:

- *21* (Ramal de destino para encaminhamento imediato)
- *61* (Ramal de destino para encaminhamento quando ocupado)
- *41* (Ramal para ativar o modo não perturbe)

Use o comando CLI `database show` para ver as famílias, chaves e valores adicionados.

![10-dialplan-advanced-features figure 9](../images/10-dialplan-advanced-features-img09.png)

![10-dialplan-advanced-features figure 10](../images/10-dialplan-advanced-features-img10.png)

### Encaminhamento de Chamadas, Lista Negra, DND

A subrotina verifica se o banco de dados contém os pares chave:valor correspondentes a CFIM, CFBS ou DND, e então os trata adequadamente. A subrotina a seguir chama a rotina de discagem:

```
exten=_4XXX,1,gosub(stdexten,s,1(${EXTEN}))
```

## Usando uma blacklist

A antiga aplicação `LookupBlacklist()` foi **removida** do Asterisk (desapareceu junto com o mecanismo legado de “priority+101 jump”). No Asterisk 22 você cria uma blacklist diretamente com a função `DB_EXISTS()` (que tanto testa por uma chave quanto, quando encontrada, expõe seu valor em `${DB_RESULT}`) mais `GotoIf`. Armazene cada número bloqueado como uma chave em uma família `blacklist`, então verifique o caller ID no início do seu contexto de entrada:

```
[incoming]
exten => s,1,GotoIf($[${DB_EXISTS(blacklist/${CALLERID(num)})}]?blocked,s,1)
exten => s,n,Dial(PJSIP/4000,20,tT)
exten => s,n,Hangup()
[blocked]
exten => s,1,Answer()
exten => s,2,Playback(blockedcall)
exten => s,3,Hangup()
```

`DB_EXISTS(blacklist/${CALLERID(num)})` retorna `1` quando o número do chamador está presente no banco de dados (encaminhando a chamada para o contexto `blocked`) e `0` caso contrário, de modo que a chamada prossegue para o `Dial()` normal.

Para inserir um número na blacklist, podemos usar o mesmo recurso de antes, usando *31* seguido das extensões a serem bloqueadas. Para remover um número da blacklist, use #31# seguido do número a ser removido.

```
[apps]
exten=>_*31*X.,1,Set(DB(blacklist/${EXTEN:4})=1)
exten=>_*31*X.,2,Hangup()
exten=>_#31#X.,1,Set(x=${DB_DELETE(blacklist/${EXTEN:4})})
exten=>_#31#X.,2,Hangup()
```

Você também pode inserir os números na blacklist usando o console CLI:

```
*CLI>database put blacklist <name/number> 1
```

Nota: Qualquer valor pode ser associado à chave. O teste `DB_EXISTS()` procura a chave, não o valor. Para apagar o número da blacklist, você pode usar:

```
*CLI>database del blacklist <name/number>
```

## Contextos baseados em horário

Na figura a seguir, temos um dialplan com três contexts. O context [incoming] é onde as chamadas geralmente são recebidas. Incluímos quatro linhas que alteram o comportamento dependendo da hora do sistema, como exemplificado abaixo:

```
include => context,<times>,<weekdays>,<mdays>,<months>
```

O Asterisk moderno (incluindo a versão 22) separa os campos time-include com **vírgulas**, não com pipes. A forma legada com pipe (`include => context|times|weekdays|mdays|months`) é interpretada como um nome de context literal e falha silenciosamente ao aplicar qualquer condição de horário.

Durante o horário comercial regular, o processamento será redirecionado para o mainmenu, onde provavelmente chamará um IVR para atender a chamada recebida. Se a chamada ocorrer fora do horário, ela chamará a extensão de segurança definida na variável ${SECURITY}. Caso a extensão de segurança não atenda a chamada, ela será enviada para o correio de voz do operador.

![10-dialplan-advanced-features figura 11](../images/10-dialplan-advanced-features-img11.png)

![10-dialplan-advanced-features figura 12](../images/10-dialplan-advanced-features-img12.png)

## Mensagens baseadas em tempo usando gotoiftime()

A sintaxe do GotoIfTime() é mostrada abaixo.

```
GotoIfTime(times,weekdays,mdays,months[,timezone]?[labeliftrue][:labeliffalse])
```

No Asterisk 22 o separador de campos é uma **vírgula**, não um pipe (a forma com pipe foi descontinuada no Asterisk 1.6). Um campo opcional `timezone` é suportado, e cada rótulo de ramificação usa a forma usual `[[context,]extension,]priority`.

Esta aplicação pode substituir o contexto baseado em tempo e parece mais fácil de entender e ler. Você pode especificar o horário da seguinte forma:

- <timerange>=<hour>':'<minute>'-'<hour>':'<minute> |"*"
- <daysofweek>=<dayname>|<dayname>'-'<dayname>|"*"
- <dayname>="sun"|"mon"|"tue"|"wed"|"thu"|"fri"|"sat"
- <daysofmonth>=<daynum>|<daynum>'-'<daynum> |"*"
- <daynum>=número de 1 a 31
- <hour>=número de 0 a 23
- <minute>=número de 0 a 59
- <months>=<monthname>|<monthname>'-'<monthname>|"*"
- <monthname>="jan"|"feb"|"mar"|"apr"|"may"|"jun"|"jul"|"aug"|"sep"|"oct"|"nov"|"dec"

Nomes de dias e meses não diferenciam maiúsculas de minúsculas.

```
exten=>s,1,GotoIfTime(8:00-18:00,mon-fri,*,*?normalhours,s,1)
```

A instrução anterior transfere o processamento para a extensão s no contexto normalhours se a chamada ocorrer entre 08:00 AM e 06:00 PM de segunda a sexta.

## Usando DISA para obter um novo tom de discagem

DISA, ou “acesso direto ao sistema interno”, é um sistema que permite aos usuários receber um segundo tom de discagem. Ele permite que os usuários discem novamente para outro destino. É frequentemente usado por técnicos ao discar chamadas de longa distância para suporte técnico nos fins de semana; em vez de discar de suas casas diretamente para o destino, eles ligam para o número DISA do escritório, recebem um tom de discagem e então ligam para o destino. As cobranças de longa distância são incorridas pela empresa em vez do telefone residencial.

```
DISA(passcode|filename[,context[,cid[,mailbox[@context][,options]]]])
```

Exemplo:

```
exten => s,1,DISA(no-password,default)
```

Usando a instrução anterior, o usuário disca a PBX e—sem exigir nenhuma senha—recebe um tom de discagem. Qualquer chamada usando DISA será processada usando o contexto `default`. Os argumentos para esta aplicação incluem uma senha global ou senha individual dentro de um arquivo. Se nenhum contexto for especificado, assume‑se o contexto `disa`. Se você usar um arquivo de senhas, o caminho completo deve ser especificado. Um ID de chamador pode ser especificado também para a discagem externa do DISA. Exemplo:

```
exten => s,1,DISA(numeric-passcode,default,"Flavio" <4830258590>)
```

O Asterisk 22 usa vírgulas como separadores de argumentos (a forma com pipe foi descontinuada na versão 1.6). O primeiro argumento é ou um único código de acesso ou o caminho para um arquivo de códigos de acesso, e o contexto padrão quando nenhum é fornecido é `disa`.

## Limitar chamadas simultâneas

A função GROUP() permite contar quantos canais ativos você tem em um grupo ao mesmo tempo. Exemplo: Você tem uma filial no Rio de Janeiro, onde os telefones seguem o padrão “_214X”. Essa localização é atendida por uma linha dedicada, com 64K reservados para largura de banda de voz. Nesse caso, o número máximo de chamadas permitidas é 2 (G.729, cerca de 31,2K por chamada). Para limitar as chamadas para o Rio a duas:

```
exten=>_214X,1,set(GROUP()=Rio)
exten=>_214X,n,Gotoif($[${GROUP_COUNT()} > 1]?outoflimit)
exten=>_214X,n,Dial(PJSIP/${EXTEN})
exten=>_214X,n,hangup
exten=>_214X,n(outoflimit),playback(callsexceedcapacity)
exten=>_214X,n,hangup
```

## Voicemail

Voicemail é um sistema de atendimento telefônico computadorizado que grava mensagens de voz recebidas, salvando-as em disco ou enviando-as por e‑mail. Às vezes, possui um diretório onde você pode consultar caixas de correio por nome. No passado, os sistemas de voicemail eram muito caros. Agora, com a telefonia IP, o voicemail está se tornando um recurso padrão.

Para configurar o voicemail, você deve seguir as etapas a seguir.

**Step 1: Edit `voicemail.conf` and set the general parameters.**

- `format` — codec used to record the message (e.g., wav49, wav, gsm)
- `serveremail` — who the e-mail notification should appear to come from
- `maxmsg` — maximum number of messages in the mailbox; after this threshold, messages are discarded
- `maxsecs` — maximum length of a voicemail message, in seconds
- `minsecs` — minimum length of a message, in seconds; below this threshold, no message is recorded
- `maxsilence` — how many seconds of silence to treat as the end of the message

**Step 2: Edit `voicemail.conf` and create the users’ mailboxes.**

### Voicemail.conf

A mailbox is defined with one line per mailbox, in the form:

```
mailboxID => pincode,fullname,email,pager-email,options
```

The fields are:

- **MailboxID** — usually the extension number
- **Pincode** — password to access the voicemail system
- **Full name** — used by the directory application
- **E-mail** — address for voicemail notification
- **Pager e-mail** — address for notification via an SMS gateway or pager
- **Options** — per-mailbox options (the same options as in `[general]`, but applied to this mailbox)

Voicemail has several options that control its behavior. For now, we will stick to the default options and concentrate on the mailbox definition. After the `[general]` section in the file, you start configuring the mailbox IDs, each in its own context. Example:

```
[general]
[default]
1234=>1234,SomeUser,email@address.com,pager@address.com,saycid=yes|dialout=fromvm|callback=fromvm|review=yes|operator=yes
```

Please check for advanced options in the file `voicemail.conf`.

**Step 3: Configure the file `extensions.conf`.**

The `stdexten` subroutine shown earlier (under *Subroutines with GOSUB*) is exactly the call/voicemail handler you need here: it dials the extension and uses the value of the channel variable `${DIALSTATUS}` to redirect the call flow to the proper voicemail greeting (`b` for busy, `u` for unavailable). Call it with `Gosub(stdexten,s,1(PJSIP/<device>,<mailbox>))` from each extension in `extensions.conf`.

## Using the VoiceMailMain() application

The application voicemailmain() is used to configure the voicemail mailbox. Users can dial the application, record their greeting, and listen to their voicemail. To call the application in the dial plan, use:

```
exten=>9000,1,VoiceMailMain()
```

Below you will find a list of the options available for the application.

### Voicemail application syntax

This application allows the calling party to leave a message for a specified list of mailboxes. When multiple mailboxes are specified, the greeting will be taken from the first specified mailbox. The dial plan execution will stop if the specified mailbox does not exist. The syntax is shown below:

```
 [Synopsis]
Leave a Voicemail message.
[Description]
This application allows the calling party to leave a message for the specified
list of mailboxes. When multiple mailboxes are specified, the greeting will
be taken from the first mailbox specified. Dialplan execution will stop if
the specified mailbox does not exist.
The Voicemail application will exit if any of the following DTMF digits are
received:
    0 - Jump to the 'o' extension in the current dialplan context.
    * - Jump to the 'a' extension in the current dialplan context.
This application will set the following channel variable upon completion:
${VMSTATUS}: This indicates the status of the execution of the VoiceMail
application.
    SUCCESS
    USEREXIT
    FAILED
[Syntax]
VoiceMail(mailbox[@context][&mailbox[@context][&...]][,options])
[Arguments]
options
```

![10-dialplan-advanced-features figura 13](../images/10-dialplan-advanced-features-img13.png)

```
    b: Play the 'busy' greeting to the calling party.
    d([c]): Accept digits for a new extension in context <c>, if played
    during the greeting. Context defaults to the current context.
    g(#): Use the specified amount of gain when recording the voicemail
    message. The units are whole-number decibels (dB). Only works on supported
    technologies, which is DAHDI only.
    s: Skip the playback of instructions for leaving a message to the
    calling party.
    u: Play the 'unavailable' greeting.
    U: Mark message as 'URGENT'.
    P: Mark message as 'PRIORITY'.
```

In all cases, the beep.gsm file will be played before the recording begins. Voicemail messages will be stored in the inbox directory.

```
/var/spool/asterisk/voicemail/context/boxnumber/INBOX/
```

If a caller presses 0 (zero) during the announcement, it will be moved to the ‘o’ (out) extension in the voicemail current context. This can be used to exit to the operator. If during the recording the caller presses # or the silence limit times out, recording is stopped and the call goes to the next priority. Make sure that you handle the call after the voicemail is played, as shown below.

```
exten=>somewhere,5,Playback(Goodbye)
exten=>somewhere,6,Hangup
```

### Tagging voicemail messages as urgent

You may tag some messages as “urgent.” Two methods are available for this:

- Pass the option ‘U’ in the application voicemail()
- Specify review=yes in the file voicemail.conf. If using this option, the user will be able to tag the message as urgent after recording the voice instructions.

## Enviando correio de voz para e‑mail

Em alguns casos (como o meu), simplesmente não usamos o aplicativo voicemailmain() para ler e‑mail. É mais simples e prático enviar todas as mensagens para e‑mail com o áudio anexado. Usando os parâmetros ‘attach’ e ‘delete’, você pode enviar todos os correios para e‑mail e excluí‑los da caixa de correio.

```
attach=yes
delete=yes
```

Para enviar correio de voz para e‑mail, o aplicativo de correio de voz usa o agente de transferência de mensagens (MTA), um componente do seu sistema operacional. O Debian usa o Exim como MTA. O aplicativo que envia o e‑mail é definido no parâmetro ‘mailcmd’.

```
mailcmd =/usr/sbin/sendmail -t
```

Na distribuição Debian do Linux, o MTA é o Exim. Para configurar o Exim no Debian, use:

```
dpkg-reconfigure exim4-config
```

Você pode optar por fazer o seu MTA enviar um e‑mail diretamente via SMTP ou através de um smarthost (geralmente o servidor de e‑mail da sua empresa). Verifique com o administrador do seu e‑mail a melhor forma de enviar e‑mail do servidor Asterisk para o seu servidor de e‑mail.

## Customizando a mensagem de e‑mail

Você pode controlar como as mensagens são enviadas configurando as seguintes variáveis: Variáveis para o assunto do e‑mail e o corpo do e‑mail:

- VM_NAME
- VM_DUR
- VM_MSGNUM
- VM_MAILBOX
- VM_CIDNUM
- VM_CIDNAME
- VM_CALLERID
- VM_DATE

O corpo e o assunto do e‑mail são construídos a partir de um modelo que você define na seção `[general]` de `voicemail.conf`. Você pode modificar tanto o corpo quanto o assunto, mas o limite de tamanho da mensagem é de 512 bytes. No modelo, `\n` insere uma nova linha e `\t` insere uma tabulação.

O exemplo `emailsubject` abaixo é simples. O exemplo `emailbody` está muito próximo do padrão; o padrão mostra apenas o CIDNAME quando ele não é nulo, caso contrário o CIDNUM, ou “an unknown caller” quando ambos são nulos.

```
emailsubject=[PBX]: New message ${VM_MSGNUM} in mailbox ${VM_MAILBOX}

emailbody=Dear ${VM_NAME}:\n\n\tjust wanted to let you know you were just left a ${VM_DUR} long message (number ${VM_MSGNUM})\nin mailbox ${VM_MAILBOX} from ${VM_CALLERID}, on ${VM_DATE}, so you might\nwant to check it when you get a chance. Thanks!\n\n\t\t\t\t--Asterisk\n
```

## Interface Web de Correio de Voz

Existe um script Perl na distribuição fonte chamado `vmail.cgi`, localizado em `contrib/scripts/vmail.cgi` na árvore de código do Asterisk (ele ainda é incluído no Asterisk 22). O comando `make install` não instala essa interface; você deve executar `make webvmail` a partir do diretório fonte. Esse script requer o interpretador de comandos Perl e um servidor web (como Apache) instalados no servidor.

```
make webvmail
```

O alvo `make webvmail` instala o script (setuid root) no diretório CGI do seu servidor web (`HTTP_CGIDIR`) e copia as imagens de apoio de `images/*.gif` para `HTTP_DOCSDIR/_asterisk` (por padrão `/var/www/html/_asterisk`). Se esses caminhos não corresponderem ao layout do seu servidor web, edite as variáveis `HTTP_CGIDIR` e `HTTP_DOCSDIR` no arquivo de nível superior `Makefile` antes de executar o alvo.

## Notificação de correio de voz

Você pode configurar o correio de voz para enviar uma mensagem de notificação ao seu telefone quando houver um novo correio de voz. No Asterisk 22, a Indicação de Mensagem de Espera (MWI) funciona com telefones PJSIP e SIP, bem como com telefones DAHDI. Para indicar um correio de voz não ouvido, uma luz indicadora pode piscar ou o telefone pode reproduzir um tom de alerta. Você precisa configurar a caixa de correio no arquivo de configuração do canal correspondente. Exemplo: `pjsip.conf` (na seção endpoint):

```
mailboxes=8590
```

No PJSIP, a dica da caixa de correio é definida com a opção `mailboxes` dentro da seção endpoint de `pjsip.conf`, em vez da antiga `mailbox=` de `sip.conf`. As assinaturas MWI são tratadas pelo módulo `res_pjsip_mwi`.

![A interface web do Comedian Mail (`vmail.cgi`): o login do Asterisk Web-Voicemail — insira sua caixa de correio e senha para reproduzir, salvar, encaminhar ou excluir correio de voz a partir de um navegador. Ainda vem incluído no Asterisk 22 e é instalado com `make webvmail`.](../images/10-dialplan-advanced-features-img14.png)

### Laboratório: Notificação de Mensagem no Telefone

Este laboratório foi testado usando um softphone SIP.

1. Edite `pjsip.conf` e adicione `mailboxes=4401` na seção endpoint para o dispositivo chamado 4401.
2. Edite o `extensions.conf` e crie uma extensão para gravar um correio de voz nas extensões 4401.

```
exten=9008,1,voicemail(4401,b)
```

3. Vá ao console e recarregue.
4. No SipPulse Softphone, abra as configurações da conta SIP e habilite a verificação de correio de voz (message-waiting) para a conta.
5. Disque 9008 e deixe uma mensagem.
6. Observe o ícone de mensagem no telefone.

## Usando o aplicativo directory

Este aplicativo permite que você encontre rapidamente um usuário para discar. A lista de nomes e as extensões correspondentes são obtidas do arquivo de configuração de voicemail voicemail.conf. A sintaxe do aplicativo pode ser exibida usando core show application directory:

```
-= Info about application 'Directory' =-
[Synopsis]
Provide directory of voicemail extensions.
[Description]
This application will present the calling channel with a directory of
extensions from which they can search by name. The list of names and
corresponding extensions is retrieved from the voicemail configuration file,
"voicemail.conf".
This application will immediately exit if one of the following DTMF digits
are received and the extension to jump to exists:
'0' - Jump to the 'o' extension, if it exists.
'*' - Jump to the 'a' extension, if it exists.
[Syntax]
Directory([vm-context][,dial-context[,options]])
[Arguments]
vm-context
    This is the context within voicemail.conf to use for the Directory.
    If not specified and 'searchcontexts=no' in "voicemail.conf", then
    'default' will be assumed.
dial-context
    This is the dialplan context to use when looking for an extension
    that the user has selected, or when jumping to the 'o' or 'a' extension.
options
    e: In addition to the name, also read the extension number to the
    caller before presenting dialing options.
    f(n): Allow the caller to enter the first name of a user in the
    directory instead of using the last name.  If specified, the optional
    number argument will be used for the number of characters the user should
    enter.
    l(n): Allow the caller to enter the last name of a user in the
    directory.  This is the default.  If specified, the optional number
    argument will be used for the number of characters the user should enter.
    b(n):  Allow the caller to enter either the first or the last name
    of a user in the directory.  If specified, the optional number argument
    will be used for the number of characters the user should enter.
    m: Instead of reading each name sequentially and asking for
    confirmation, create a menu of up to 8 names.
    p(n): Pause for n milliseconds after the digits are typed.  This
    is helpful for people with cellphones, who are not holding the receiver
    to their ear while entering DTMF.
    NOTE: Only one of the <f>, <l>, or <b> options may be specified.
    *If more than one is specified*, then Directory will act as  if <b> was
    specified.  The number of characters for the user to type defaults to
    '3'.
```

### Laboratório: Usando o aplicativo directory

1. Edite o arquivo voicemail.conf para adicionar duas extensões no plano de discagem

```
[default]
; Define maximum number of messages per folder for a particular context.
;maxmsg=50
4400=>4400,Clint Eastwood,ceastwood@voip.school
4401=>4401,John Wayne,jwayne@voip.school
```

2. Crie essas extensões no seu plano de discagem

```
exten=9006,1,VoiceMailMain()
exten=9006,n,Hangup()
exten=9007,1,Directory(default,default)
exten=9007,n,Hangup()
```

3. Vá ao console e recarregue  
4. Disque 9006 e grave um nome para cada extensão (4400, 4401)  
5. Disque 9007 e selecione as três letras do sobrenome para uma extensão (Eas=327). Se esta for a opção correta, pressione ‘1’ para transferir para o nome.

## Lab: Putting it all together

Thus far, you have learned several dial plan concepts. Let’s put all the applications, functions, and concepts in a dial plan example so you can understand how they are used together. Let’s guide you through the whole PBX configuration for the scenario below.

- 4 analog trunks
- 16 SIP-based extensions
- 3 service classes:
    - restrict (internal, local, and 1-800)
    - ld (long distance)
    - ldi (international)
- After-hours message
- Auto attendant

### Step 1 – Configuring channels

**Analog trunks (`chan_dahdi.conf`).** First, we will configure the analog trunks in the DAHDI channel configuration file `chan_dahdi.conf`. In this case, we will use a T400P Digium card with 4 FXO interfaces. Let’s assume that the driver is already loaded and the driver configuration file (/etc/dahdi/system.conf) is correctly configured.

![10-dialplan-advanced-features figure 16](../images/10-dialplan-advanced-features-img16.png)

```
signalling=fxs_ks
language=en
context=incoming
group=1
channel => 1-4
```

**SIP channels (`pjsip.conf`).** We have chosen the dial plan numbering from 2000 to 2099. Two codecs will be used: G.729 and G.711 ulaw. The first one will be used for phones using Asterisk over the Internet or WAN while the second one will be used for phones using the local network. In `pjsip.conf`, we will arbitrate which devices will belong to each class of service (restrict, ld, ldi). To reduce the vulnerability to brute force attacks, we will use the phone’s MAC addresses as device names. I strongly advise that you use strong passwords to avoid brute force attacks!

We define a transport and three reusable templates — an endpoint base with the
shared codecs, a digest auth, and a single-contact AOR — then attach each device
to the templates and override only what differs (its class-of-service context and
credentials). `host=dynamic` becomes an AOR that the phone registers against, and
`directmedia` becomes `direct_media`:

```ini
; pjsip.conf
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060

[endpoint-base](!)
type=endpoint
disallow=all
allow=ulaw,gsm
direct_media=yes

[auth-digest](!)
type=auth
auth_type=digest

[aor-single](!)
type=aor
max_contacts=1

[00001A000002](endpoint-base)
context=restrict
auth=00001A000002
aors=00001A000002
mailboxes=20
[00001A000002](auth-digest)
username=00001A000002
password=#s2cr2t#
[00001A000002](aor-single)

[00001A000003](endpoint-base)
context=ld
dtmf_mode=rfc4733
auth=00001A000003
aors=00001A000003
mailboxes=20
[00001A000003](auth-digest)
username=00001A000003
password=#s3cr3t#
[00001A000003](aor-single)

[00001A000004](endpoint-base)
context=ldi
dtmf_mode=rfc4733
auth=00001A000004
aors=00001A000004
mailboxes=20
[00001A000004](auth-digest)
username=00001A000004
password=#s3cr3t#
[00001A000004](aor-single)
```

### Step 2 – Configure the dial plan

Now let’s start to configure the extensions.conf. Define internal extensions and local dialing

```
[restrict]
exten=>_2000,1,Dial(PJSIP/00001A000002,20,t)
exten=>_2030,1,Dial(PJSIP/00001A000003,20,t)
exten=>_2040,1,Dial(PJSIP/00001A000004,20,t)
exten=>_9XXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20) ; local calls
exten=>_91800.,1,Dial(DAHDI/g1/${EXTEN:1},20); 1-800
```

Define LD (long distance)

```
[ld]
Include=>restrict
exten=>_9NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

Define international calls

```
[ldi]
include=>ld
exten=>_901X.,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

### Step 3 - Receiving calls using an auto-attendant

To receive calls, use two contexts. The first one is for normal-hours operation, where the call will be received by an auto-attendant. The second one is for after hours, where the caller will receive a message such as “you have called company XYZ, our normal hours are from 08:00 AM to 06:00 PM; if you know the destination extension number you can try dialing it now or hang up.” Menus: Normal-hours, After-hours In the menus below, the system will play a message warning the caller that the company was reached after regular working hours, allowing the caller to dial the destination extension number (someone may be working after regular working hours).

```
[incoming]
include=>normalhours,08:00-18:00,mon-fri,*,*
include=>afterhours,18:00-23:59,*,*,*
include=>afterhours,00:00-07:59,*,*,*
include=>afterhours,*,sat-sun,*,*
[normalhours]
exten=>s,1,Goto(mainmenu,s,1)
[afterhours]
exten=>s,1,Background(afterhours)
exten=>s,2,hangup()
exten=>i,1,hangup()
exten=>t,1,hangup()
include=>restrict
```

Menus: Main and Sales During normal working hours, the call is answered by an auto-attendant menu, receiving a message such as “welcome to XYZ Company; dial 1 for sales, 2 for tech support, 3 for training, or the desired extension number”.

```
[globals]
OPERATOR=PJSIP/2060
SALES=PJSIP/2035
TECHSUPPORT=PJSIP/2004
TRAINING=PJSIP/2036
[mainmenu]
exten=> s,1,Background(welcome)
exten=>1,1,Goto(sales,s,1)
exten=>2,1,Goto(techsupport,s,1)
exten=>3,1,Goto(training,s,1)
exten=>i,1,Playback(Invalid)
exten=>i,2,hangup()
exten=>t,1,Dial(${OPERATOR},20,Tt)
include=>restrict
[sales]
exten=>s,1,Dial(${SALES},20,Tt)
[techsupport]
exten=>s,1,Dial(${TECHSUPPORT},20,Tt)
[training]
exten=>s,1,Dial(${TRAINING},20,Tt)
```

With all these statements, the functionality of your dialing plan is now ready. In the next section, we will demonstrate how to operate the PBX.

## Resumo

Neste capítulo, você aprendeu como receber chamadas usando um IVR ou um atendente automático. Estudou o conceito de inclusão de contextos e implementou alguns exemplos. Sub-rotinas foram usadas para evitar digitação repetitiva, e o banco de dados do Asterisk (AstDB, suportado por SQLite3 no Asterisk 22) foi utilizado para funções que requerem armazenamento de dados (por exemplo, encaminhamento de chamadas, modo não perturbe, listas negras). Por fim, você aprendeu como implementar o comportamento fora do horário de expediente e implementou um plano de discagem completo usando esses conceitos.

## Quiz

1. Um contexto dependente de horário inclui o uso da forma `include => context,<times>,<weekdays>,<mdays>,<months>`. O que `include => normalhours,08:00-18:00,mon-fri,*,*` faz?
   - A. Executa as extensões de segunda a sexta, das 08:00 às 18:00
   - B. Executa as opções todos os dias em todos os meses
   - C. Nada; o formato é inválido
2. No Asterisk moderno (incluindo Asterisk 22), os campos de um `include =>` baseado em horário e de `GotoIfTime()` são separados por qual caractere?
   - A. O pipe `|`
   - B. A vírgula `,`
   - C. O ponto‑e‑vírgula `;`
   - D. A barra `/`
3. Para discar vários canais ao mesmo tempo (tocando‑os simultaneamente), você os separa dentro de `Dial()` com o caractere ___.
4. Um menu de voz que reproduz um prompt enquanto aguarda o chamador discar uma extensão geralmente é criado com a aplicação ___.
5. Você pode incluir o conteúdo de outro arquivo dentro de `extensions.conf` usando a instrução ___ (nota: isso é diferente da instrução de contexto `include =>`).
6. No Asterisk 22, o banco de dados interno AstDB é suportado por:
   - A. Berkeley DB v1
   - B. MySQL
   - C. SQLite3
   - D. PostgreSQL
7. Quando você usa `Dial(type1/identifier1&type2/identifier2)`, o Asterisk disca cada canal em sequência, aguardando 20 segundos entre eles.
   - A. Falso
   - B. Verdadeiro
8. Com a aplicação Background(), você deve esperar até que a mensagem termine de tocar antes de pressionar um dígito DTMF para escolher uma opção.
   - A. Falso
   - B. Verdadeiro
9. Dada a sintaxe `Goto([[context,]extension,]priority)`, quais das seguintes são invocações válidas da aplicação Goto()? (marque todas que se aplicam)
   - A. Goto(context,extension)
   - B. Goto(context,extension,priority)
   - C. Goto(extension,priority)
   - D. Goto(priority)
10. Para excluir uma única chave do AstDB no plano de discagem do Asterisk 22, você usa:
    - A. A aplicação `DBdel()`
    - B. A função `DB_DELETE()`
    - C. A aplicação `DBdeltree()`
    - D. A aplicação `LookupBlacklist()`

**Answers:** 1 — A · 2 — B · 3 — `&` · 4 — Background() · 5 — #include · 6 — C · 7 — A · 8 — A · 9 — B, C, D · 10 — B
