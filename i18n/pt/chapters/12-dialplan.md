# Recursos avançados do Dial Plan

O Capítulo 3 discutiu os fundamentos de um dial plan. Por razões didáticas, não explicamos todos os recursos, apenas alguns dos mais importantes. Este capítulo aprofundará o dial plan, descrevendo técnicas avançadas, novas aplicações e conceitos.

## Objetivos

Ao final deste capítulo, você deverá ser capaz de:

- Simplificar suas entradas de extension
- Tratar a segurança do dial plan e filtrar extensions
- Receber chamadas usando um menu IVR
- Usar sub-rotinas para evitar reescritas desnecessárias
- Implementar alguma segurança no dial plan usando "Include"
- Implementar o siga-me usando AsteriskDB
- Implementar comportamento de fora do horário comercial em seu PBX
- Usar o comando switch para transferir para outro PBX
- Implementar o gerenciador de privacidade
- Implementar voicemail
- Implementar um diretório corporativo

## Simplificando seu Dial Plan

Você pode simplificar seu dial plan usando a palavra-chave "same" para definir uma extension. Isso deve reduzir o número de erros de digitação no dial plan. Confira o exemplo abaixo:

```
exten => 4000,1,NoOp()
same  =>      n,Dial(PJSIP/005C2B313E22)
```

## Segurança do Dial Plan

Uma falha foi descoberta no dial plan do Asterisk que permite que um usuário injete um novo canal e um número de discagem em seu dial plan. Vamos supor que você tenha a seguinte linha em seu servidor `exten=>_X.,1,Dial(PJSIP/${EXTEN})` e algum usuário mal-intencionado discou o número `3000&DAHDI/1/011551123456789` no softphone. O protocolo SIP, por padrão, aceita quaisquer caracteres alfanuméricos, então a extension discada acionará, na verdade, duas chamadas: uma para o canal PJSIP/3000 e a outra para o canal DAHDI/011551123456789, que é um número internacional. Assim, qualquer usuário com acesso a uma extension pode, na verdade, discar para qualquer lugar do mundo. A maneira mais fácil de evitar esse comportamento é filtrar os números antes de chamar a aplicação dial. A função FILTER() é muito útil para isso. Exemplo:

```
exten=>_X.,1,DIAL(PJSIP/${FILTER(0-9,${EXTEN})})
```

A aplicação filter permitirá que você filtre todos os caracteres do número discado, exceto os números de 0 a 9. Mais informações podem ser encontradas no arquivo README-SERIOUSLY.bestpractices.txt disponível no Asterisk.

## Recebendo chamadas usando um menu IVR

Na última seção, você recebeu todas as chamadas usando DID ou encaminhamento para a operadora. Agora você aprenderá como implementar um menu IVR, bem como criar um serviço de atendimento automático. Antes de entrar nos detalhes, vamos examinar algumas novas aplicações. Colocamos a saída do comando show application abaixo simplesmente para facilitar a leitura. Você pode obter essas descrições usando show application nome_da_aplicacao. 1 http://downloads.asterisk.org/pub/security/AST-2010-002.pdf

### A aplicação Background()

Esta aplicação reproduzirá a lista de arquivos fornecida enquanto aguarda que uma extension seja discada pelo canal chamador. Para continuar aguardando dígitos após a conclusão da reprodução dos arquivos por esta aplicação, a aplicação WaitExten deve ser usada. A opção langoverride especifica explicitamente qual idioma tentar usar para os arquivos de som solicitados. Qualquer context especificado será o context do dial plan que esta aplicação usa ao sair para uma extension discada. Se um dos arquivos de som solicitados não existir, o processamento da chamada será encerrado. Opções:

- s - Faz com que a reprodução da mensagem seja ignorada se o canal não estiver no estado 'up' (ou seja, ainda não foi atendido). Se isso acontecer, a aplicação retornará imediatamente.
- n - Não atende o canal antes de reproduzir os arquivos.
- m - Interrompe apenas se um dígito pressionado corresponder a uma extension de um dígito no context de destino.

### A aplicação Record()

Esta aplicação grava do canal em um nome de arquivo fornecido. Se o arquivo existir, ele será sobrescrito.

![10-dialplan-advanced-features figure 1](../images/10-dialplan-advanced-features-img01.png)

- 'format' é o formato do tipo de arquivo a ser gravado (wav, gsm, etc).
- 'silence' é o número de segundos de silêncio permitidos antes de retornar.
- 'maxduration' é a duração máxima da gravação em segundos; se estiver ausente ou for zero, não há máximo.
- 'options' pode conter qualquer uma das seguintes letras:
    - `a` — anexa a uma gravação existente em vez de substituí-la
    - `n` — não atende, mas grava mesmo assim se a linha ainda não tiver sido atendida
    - `q` — silencioso (não reproduz um tom de bipe)
    - `s` — pula a gravação se a linha ainda não tiver sido atendida
    - `t` — usa a tecla terminadora alternativa `*` (DTMF) em vez da padrão `#`
    - `x` — ignora todas as teclas terminadoras (DTMF) e continua gravando até o desligamento

Se o nome do arquivo contiver %d, esses caracteres serão substituídos por um número incrementado em um cada vez que o arquivo for gravado. Use core show file formats para ver os formatos disponíveis em seu sistema. O usuário pode pressionar # para encerrar a gravação e continuar para a próxima prioridade. Se o usuário desligar durante uma gravação, todos os dados serão perdidos e a aplicação será encerrada.

### A aplicação Playback()

Esta aplicação reproduz nomes de arquivos fornecidos (não inclua a extensão). Opções também podem ser incluídas após um símbolo de pipe. A opção 'skip' faz com que a reprodução da mensagem seja ignorada se o canal não estiver no estado 'up' (ou seja, ainda não foi atendido).

![10-dialplan-advanced-features figure 2](../images/10-dialplan-advanced-features-img02.png)

![10-dialplan-advanced-features figure 3](../images/10-dialplan-advanced-features-img03.png)

Se 'skip' for especificado, a aplicação retornará imediatamente caso o canal não esteja fora do gancho. Caso contrário, a menos que 'noanswer' seja especificado, o canal será atendido antes que o som seja reproduzido. Nem todos os canais suportam a reprodução de mensagens enquanto ainda estão no gancho. Se 'j' for especificado, a aplicação saltará para a prioridade n+101 quando o arquivo não existir, se presente. Esta aplicação define a seguinte variável de canal após a conclusão:

- PLAYBACKSTATUS — o status da tentativa de reprodução como uma string de texto, um de:
    - `SUCCESS`
    - `FAILED`

### A aplicação Read()

Esta aplicação lê um número predeterminado de dígitos de string, um certo número de vezes, do usuário para a variável fornecida.

- filename -- arquivo para reproduzir antes de ler os dígitos ou tom com a opção i
- maxdigits -- número máximo aceitável de dígitos. Para de ler após a entrada de maxdigits (sem exigir que o usuário pressione a tecla #). O padrão é 0 - sem limite - para aguardar que o usuário pressione a tecla #. Qualquer valor abaixo de 0 significa o mesmo. O valor máximo aceito é 255.

![10-dialplan-advanced-features figure 4](../images/10-dialplan-advanced-features-img04.png)

![10-dialplan-advanced-features figure 5](../images/10-dialplan-advanced-features-img05.png)

- option -- as opções são `s`, `i`, `n`:
    - `s` — retorna imediatamente se a linha não estiver ativa
    - `i` — reproduz filename como um tom de indicação do seu `indications.conf`
    - `n` — lê dígitos mesmo se a linha não estiver ativa
- attempts -- se maior que 1, o número de tentativas que serão feitas caso nenhum dado seja inserido
- timeout -- Um número inteiro de segundos para aguardar uma resposta de dígito. Se maior que 0, esse valor substituirá o tempo limite padrão.

A aplicação read() deve desconectar se a função falhar ou apresentar erro.

### A aplicação Gotoif()

Esta aplicação fará com que o canal chamador salte para o local especificado no dial plan com base na avaliação da condição fornecida. O canal continuará em labeliftrue se a condição for verdadeira, ou 'labeliffalse' se a condição for falsa. Os rótulos são especificados com a mesma sintaxe usada na aplicação Goto. Se o rótulo escolhido pela condição for omitido, nenhum salto será realizado; em vez disso, a execução continua com a próxima prioridade no dial plan.

### Laboratório: Construindo um menu IVR passo a passo

Vamos criar um menu IVR com a seguinte funcionalidade. Quando discado, o IVR reproduz um arquivo de áudio com a mensagem “Bem-vindo à XYZ Corporation; pressione 1 para vendas, 2 para suporte técnico, 3 para treinamento ou aguarde para falar com um representante.” Os dígitos roteiam o chamador da seguinte forma:

- `1` — transfere para vendas (PJSIP/4001)
- `2` — transfere para suporte técnico (PJSIP/4002)
- `3` — transfere para treinamento (PJSIP/4003)
- Nenhum dígito pressionado — transfere para a operadora (PJSIP/4000)

**Passo 1 – Gravar as mensagens**

Vamos criar uma extension para gravar as mensagens. Para gravar uma mensagem, disque de um softphone para `9003<filename>` (por exemplo, `9003welcome`). Quando ouvir o bipe, comece a gravar; pressione `#` para parar. Você ouvirá um bipe e o sistema reproduzirá a mensagem gravada.

**Passo 2 – Criar a lógica do menu**

Ao discar a extension 9004, o processamento salta para o menu na extension `s`, prioridade 1.

### Correspondência conforme você disca

Este é um menu de configuração da empresa para receber chamadas. A aplicação background lê o context atual e define o comprimento máximo para cada número para qualquer combinação possível.

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

Ao discar para esta empresa, a mensagem de boas-vindas é reproduzida primeiro. Depois disso, o Asterisk aguarda que um dígito seja discado. Número discado Ação do Asterisk Chama imediatamente Dial(DAHDI/1) Aguarda o tempo limite, então vai para Dial(DAHDI/2) Chama imediatamente (DAHDI/3) Chama imediatamente (DAHDI/4) Aguarda o tempo limite, então desconecta Chama imediatamente Dial(DAHDI/5) Chama imediatamente Dial(DAHDI/6) Desconecta imediatamente É importante evitar ambiguidade nos menus. Todos querem ser atendidos rapidamente. Por esse motivo, você não deve usar os números 2, 21 ou 22.

### Laboratório: Usando a aplicação Read()

Por favor, tente o laboratório com a aplicação read(). Read aceita dígitos do usuário e os insere na variável especificada; você pode então usar a aplicação gotoif para redirecionar a chamada.

## Inclusão de context

Um context pode incluir o conteúdo de outro context. No exemplo acima, qualquer canal pode discar qualquer extension no context internal, mas apenas o canal 4003 pode discar para extensions internacionais. Você pode usar a inclusão de context para facilitar a criação do dial plan. Usando a inclusão de context, você pode controlar quem tem acesso a quais extensions.

### Solução de problemas da mensagem “number not found”

É muito comum receber a mensagem “number not found”. A maioria das pessoas confunde o conceito de contexts incluídos porque ele realmente não é intuitivo. Como regra geral, primeiro vá para o arquivo de configuração do canal de entrada, como `pjsip.conf`, `chan_dahdi.conf` e `iax.conf`, e determine o context atual. Em seguida, vá para o dial plan no arquivo extensions.conf e verifique se o número discado pode ser encontrado nesse context. Se não, algo está errado com seu dial plan. As regras de ouro dos contexts são: 1. Um canal só pode discar números dentro do mesmo context que o canal. 2. O context onde a chamada é processada é definido no arquivo de configuração do canal de entrada (`chan_dahdi.conf`, `iax.conf`, `pjsip.conf`).

## Usando a instrução switch

Você pode enviar o processamento do dial plan para outro servidor usando o comando switch. Você precisará do nome e da chave do outro servidor. O context é o context de destino.

![10-dialplan-advanced-features figure 6](../images/10-dialplan-advanced-features-img06.png)

## Ordem de processamento do dial plan

Quando o Asterisk recebe uma chamada de entrada, ele procura no context definido pelo canal. Em alguns casos, se mais de um padrão corresponder ao número discado, o Asterisk não consegue processar a chamada da maneira exata que você pensa que deveria. Você pode ver a ordem de correspondência usando o comando CLI dialplan show. Exemplo: Digamos que você queira discar 912 para rotear para um trunk analógico (DAHDI/1) e todos os outros números começando com 9 para outro trunk analógico (DAHDI/2). Você escreveria algo como:

```
[example]
exten=>_912.,1,Dial(DAHDI/1/${EXTEN})
exten=>_9.,1,Dial(DAHDI/2/${EXTEN})
```

Se dois padrões corresponderem a uma extension, você pode controlar qual extension é processada primeiro usando os contexts incluídos. Um context incluído é processado depois de um padrão no mesmo context.

## A instrução #INCLUDE

Devemos usar um arquivo grande ou vários arquivos? Você pode usar a instrução #include <filename> para incluir outros arquivos em seu extensions.conf. Por exemplo, poderíamos criar um users.conf para usuários locais e services.conf para serviços especiais. Tenha cuidado para não confundir #include <filename> com o

```
include=>context statement.
```

## Sub-rotinas com GOSUB

Em versões mais antigas do Asterisk, você tinha o comando Macro. Este comando foi descontinuado há muito tempo em favor do GOSUB. Demonstraremos aqui como criar sub-rotinas para processamento de voicemail de uma maneira fácil e organizada. Formato do comando:

```
gosub([[context,]exten,]priority[(arg1[,...][,argN])])
```

O comando GOSUB está disponível desde o Asterisk 1.6 e suporta a passagem de argumentos (disponíveis dentro da sub-rotina como `${ARG1}`, `${ARG2}` e assim por diante). Com argumentos, agora é possível substituir completamente os antigos comandos Macro. Macros (`app_macro`) foram removidas no Asterisk 21; você deve usar GOSUB para sub-rotinas.

### Criando a sub-rotina

A definição é muito semelhante. Observe a sub-rotina abaixo definida para voicemail com o nome stdexten (escolha o nome que desejar). Após chamar o comando Dial com o primeiro argumento (nome do canal), verificamos a ${DIALSTATUS} para enviar a lógica da chamada para a próxima etapa.

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

### Chamando uma sub-rotina

Preste atenção ao chamar a sub-rotina para usar parênteses antes dos parâmetros.

```
exten=>6000,1,Gosub(stdexten,s,1(PJSIP/6000,${EXTEN}))
exten=>6001,1,Gosub(stdexten,s,1(PJSIP/6001,${EXTEN}))
exten=>6002,1,Gosub(stdexten,s,1(PJSIP/6002,${EXTEN}))
exten=>6003,1,Gosub(stdexten,s,1(PJSIP/6003,${EXTEN}))
```

## Usando o Asterisk DB

Para implementar encaminhamento de chamadas e listas negras, precisamos de alguma maneira de armazenar e restaurar dados. Felizmente, o Asterisk fornece um mecanismo para armazenar e recuperar dados de um banco de dados embutido chamado AstDB. No Asterisk moderno (incluindo o Asterisk 22), o AstDB é suportado pelo **SQLite3** (o arquivo `/var/lib/asterisk/astdb.sqlite3`); versões mais antigas usavam Berkeley DB v1. Isso é semelhante ao banco de dados de registro do Windows, usando o conceito hierárquico de família e chaves. Os dados persistem entre as reinicializações do Asterisk.

> **[Nota da 2ª ed.]** Desde o Asterisk 10, o AstDB é armazenado em SQLite3 (`astdb.sqlite3`), não no arquivo legado Berkeley DB v1 usado pelo Asterisk 1.8 e anteriores. A API de família/chave permanece inalterada.

### Funções, aplicações e comandos CLI

Existem algumas funções, aplicações e comandos CLI que funcionam com o AstDB:

- variable=${DB(<family/key>)}
- DB(<family/key>)=value
- DB_EXISTS(<family/key>)

Exemplos:

```
exten=_*21*XXXX,1,set(DB(CFBS/${CALLERID(num)}=${EXTEN:4}))
exten=s,1,set(temp=${DB(CFBS/${EXTEN})})
```

Algumas aplicações podem ser usadas para manipular o AstDB:

- DB_DELETE(<family/key>) — função que retorna e exclui uma chave (a antiga aplicação `DBdel()` foi removida)
- DBdeltree(<family>)

> **[Nota da 2ª ed.]** A aplicação `DBdel()` não existe mais no Asterisk 22. Exclua uma única chave com a função de dial plan `DB_DELETE()` — por exemplo, `Set(x=${DB_DELETE(family/key)})` ou, como uma operação de escrita, `Set(DB_DELETE(family/key)=)`. `DBdeltree()` (excluir uma família/subárvore inteira) ainda é uma aplicação.

É possível usar comandos CLI para definir e excluir chaves também:

- database del
- database put
- database show <family[/key]>
- database showkey
- database deltree
- database get

![10-dialplan-advanced-features figure 7](../images/10-dialplan-advanced-features-img07.png)

![10-dialplan-advanced-features figure 8](../images/10-dialplan-advanced-features-img08.png)

### Implementando Encaminhamento de Chamadas, DND e Listas Negras

Neste exemplo, você aprenderá como implementar encaminhamento de chamadas imediato e encaminhamento de chamadas ocupado. Usaremos *21* para programar o encaminhamento de chamadas imediato e *61* para programar o status de encaminhamento de chamadas ocupado. Para cancelar a programação, use #21# e #61#, respectivamente. Use o exemplo acima para popular o banco de dados. Famílias usadas:

- CFIM – Call Forward Immediate (Encaminhamento Imediato)
- CFBS – Call Forward on Busy status (Encaminhamento se Ocupado)
- DND – Do Not Disturb (Não Perturbe)

Tente popular o banco de dados discando:

- *21* (Extension de destino para encaminhamento de chamadas imediato)
- *61* (Extension de destino para status de encaminhamento de chamadas ocupado)
- *41* (Extension para colocar em não perturbe)

Use o comando CLI database show para ver as famílias, chaves e valores adicionados.

![10-dialplan-advanced-features figure 9](../images/10-dialplan-advanced-features-img09.png)

![10-dialplan-advanced-features figure 10](../images/10-dialplan-advanced-features-img10.png)

### Encaminhamento de Chamadas, BlackList, DND

A sub-rotina acima verifica se o banco de dados contém os pares chave:valor correspondentes a CFIM, CFBS ou DND e, em seguida, os trata adequadamente. A sub-rotina follow chama a rotina de discagem:

```
exten=_4XXX,1,gosub(stdexten,s,1(${EXTEN}))
```

## Usando uma lista negra

> **[Nota da 2ª ed.]** A aplicação `LookupBlacklist()` foi **removida** (ela desapareceu com o antigo mecanismo de "salto de prioridade+101" bem antes do Asterisk 22 — confirmado não registrado no laboratório 22.10.0). Implemente uma lista negra em vez disso com as funções `DB()`/`DB_EXISTS()` mais `GotoIf`, por exemplo:
>
> ```
> exten => s,1,GotoIf($[${DB_EXISTS(blacklist/${CALLERID(num)})}]?blocked,s,1)
> exten => s,n,Dial(PJSIP/4000,20,tT)
> exten => s,n,Hangup()
> ```
>
> O exemplo abaixo é mantido para referência histórica; a opção `j` e o salto de prioridade `n+101` não existem mais.

Para criar uma lista negra, usamos a aplicação LookupBlacklist(). A aplicação verifica o nome/número no identificador de chamadas (caller ID). Se o número não for encontrado, a aplicação define a variável $LOOKUPBLSTATUS como NOTFOUND. Se o número for encontrado, a aplicação define a variável como FOUND. Você pode usar a opção “j” na aplicação para usar o comportamento antigo (1.0), saltando 101 posições se o número/nome for encontrado. Exemplo:

```
[incoming]
exten => s,1,LookupBlacklist(j)
exten => s,2,Dial(PJSIP/4000,20,tTj)
exten => s,3,Hangup()
exten => s,102,Goto(blocked,s,1)
[blocked]
exten => s,1,Answer()
exten => s,2,Playback(blockedcall)
exten => s,3,Hangup()
```

Para inserir um número na lista negra, podemos usar o mesmo recurso de antes, usando *31* seguido pelas extensions a serem colocadas na lista negra. Para remover um número da lista negra, você deve usar #31# seguido pelo número a ser removido.

```
[apps]
exten=>_*31*X.,1,Set(DB(blacklist/${EXTEN}=1})
exten=>_*31*X.,2,Hangup()
exten=>_#31#X.,1,Set(x=${DB_DELETE(blacklist/${EXTEN:4})})
exten=>_#31#X.,2,Hangup()
```

Você também pode inserir os números na lista negra usando o console CLI:

```
CLI>database put blacklist <name/number> 1
```

Nota: Qualquer valor pode ser associado à chave. A aplicação de lista negra pesquisará a chave, não o valor. Para apagar o número da lista negra, você pode usar:

```
CLI>database del blacklist <name/number>
```

## Contexts baseados em tempo

Na figura a seguir, temos um dial plan com três contexts. O context [incoming] é onde as chamadas geralmente são recebidas. Incluímos quatro linhas que alteram o comportamento dependendo do horário do sistema, conforme exemplificado abaixo:

```
include => context,<times>,<weekdays>,<mdays>,<months>
```

> **[Nota da 2ª ed.]** O Asterisk moderno (incluindo o 22) separa os campos de time-include com **vírgulas**, não pipes. A forma de pipe legada (`include => context|times|weekdays|mdays|months`) é analisada como um nome de context literal simples e falha silenciosamente ao aplicar qualquer condição de tempo. Verificado no laboratório do Asterisk 22.10.0.

Durante o horário comercial normal, o processamento será redirecionado para o mainmenu, onde provavelmente chamará um IVR para lidar com a chamada de entrada. Se a chamada ocorrer fora do horário comercial, ela chamará a extension de segurança definida na variável ${SECURITY}. Se a extension de segurança não atender a chamada, ela será enviada para o voicemail da operadora.

![10-dialplan-advanced-features figure 11](../images/10-dialplan-advanced-features-img11.png)

![10-dialplan-advanced-features figure 12](../images/10-dialplan-advanced-features-img12.png)

## Mensagens baseadas em tempo usando gotoiftime()

A sintaxe gotoiftime() é mostrada abaixo.

```
GotoIfTime(<timerange>,<daysofweek>,<daysofmonth>,<months>[,<timezone>]?[[context,]extension,]pri)
```

> **[Nota da 2ª ed.]** No Asterisk 22, o separador de campo é uma **vírgula**, não um pipe (a forma de pipe foi descontinuada no Asterisk 1.6). A sintaxe documentada atual é `GotoIfTime(times,weekdays,mdays,months[,timezone]?[labeliftrue][:labeliffalse])`. Um campo opcional `timezone` é suportado.

Esta aplicação pode substituir o context baseado em tempo e parece mais fácil de entender e ler. Você pode especificar o tempo da seguinte forma:

- <timerange>=<hora>':'<minuto>'-'<hora>':'<minuto> |"*"
- <daysofweek>=<nomedodia>|<nomedodia>'-'<nomedodia>|"*"
- <nomedodia>="sun"|"mon"|"tue"|"wed"|"thu"|"fri"|"sat"
- <daysofmonth>=<numdodia>|<numdodia>'-'<numdodia> |"*"
- <numdodia>=número de 1 a 31
- <hora>=número de 0 a 23
- <minuto>=número de 0 a 59
- <meses>=<nomedomes>|<nomedomes>'-'<nomedomes>|"*"
- <nomedomes>="jan"|"feb"|"mar"|"apr"|"may"|"jun"|"jul"|"aug"|"sep"|"oct"|"nov"|"dec"

Os nomes dos dias e meses não diferenciam maiúsculas de minúsculas.

```
exten=>s,1,GotoIfTime(8:00-18:00,mon-fri,*,*?normalhours,s,1)
```

A instrução anterior transfere o processamento para a extension s no context normalhours se a chamada ocorrer entre 08:00 e 18:00 de segunda a sexta-feira.

## Usando DISA para obter um novo tom de discagem

DISA, ou “direct inward system access” (acesso direto ao sistema interno), é um sistema que permite aos usuários receber um segundo tom de discagem. Ele permite que os usuários discem novamente para outro destino. É frequentemente usado por técnicos ao discar chamadas de longa distância para suporte técnico nos fins de semana; em vez de discar de suas casas diretamente para o destino, eles ligam para o número DISA do escritório, recebem um tom de discagem e então ligam para o destino. As cobranças de longa distância são incorridas na empresa em vez do telefone residencial.

```
DISA(passcode[,context])
DISA(password-file[,context])
```

Exemplo:

```
exten => s,1,DISA(no-password,default)
```

Usando a instrução anterior, o usuário disca para o PBX e — sem exigir nenhuma senha — recebe um tom de discagem. Qualquer chamada usando DISA será processada usando o context `default`. Os argumentos para esta aplicação incluem uma senha global ou senha individual dentro de um arquivo. Se nenhum context for especificado, o context `disa` é assumido. Se você usar um arquivo de senha, o caminho completo deve ser especificado. Um identificador de chamadas (caller ID) pode ser especificado para a discagem externa DISA também. Exemplo:

```
numeric-passcode,context,"Flavio" <4830258590>
```

> **[Nota da 2ª ed.]** O Asterisk 22 usa vírgulas como separadores de argumentos (a forma de pipe foi descontinuada na 1.6). A sintaxe completa é `DISA(passcode|filename[,context[,cid[,mailbox[@context][,options]]]])`, e o context padrão quando nenhum é fornecido é `disa` (não "DISA"). Verificado com `core show application DISA` no laboratório do Asterisk 22.10.0.

## Limitar chamadas simultâneas

A função GROUP() permite contar quantos canais ativos você tem em um grupo ao mesmo tempo. Exemplo: Você tem uma filial no Rio de Janeiro, onde os telefones seguem o padrão “_214X”. Este local é atendido por uma linha dedicada, com 64K reservados para largura de banda de voz. Nesse caso, o número máximo de chamadas permitidas é 2 (G.729, 30r.2K por chamada). Para limitar as chamadas para o Rio a duas:

```
exten=>_214X,1,set(GROUP()=Rio)
exten=>_214X,n,Gotoif($[${GROUP_COUNT()} > 1]?outoflimit)
exten=>_214X,n,Dial(PJSIP/${EXTEN})
exten=>_214X,n,hangup
exten=>_214X,n(outoflimit),playback(callsexceedcapacity)
exten=>_214X,n,hangup
```

## Voicemail

Voicemail é um sistema de atendimento telefônico computadorizado que grava mensagens de voz recebidas, salvando-as em disco ou enviando-as por e-mail. Às vezes, ele possui um diretório onde você pode procurar caixas de correio de voz por nome. No passado, os sistemas de voicemail eram muito caros. Agora, com a telefonia IP, o voicemail está se tornando um recurso padrão.

Para configurar o voicemail, você deve seguir as etapas a seguir.

**Passo 1: Edite `voicemail.conf` e defina os parâmetros gerais.**

- `format` — codec usado para gravar a mensagem (por exemplo, wav49, wav, gsm)
- `serveremail` — de quem a notificação por e-mail deve parecer vir
- `maxmsg` — número máximo de mensagens na caixa de correio; após esse limite, as mensagens são descartadas
- `maxsecs` — duração máxima de uma mensagem de voicemail, em segundos
- `minsecs` — duração mínima de uma mensagem, em segundos; abaixo desse limite, nenhuma mensagem é gravada
- `maxsilence` — quantos segundos de silêncio tratar como o fim da mensagem

**Passo 2: Edite `voicemail.conf` e crie as caixas de correio dos usuários.**

### Voicemail.conf

Uma caixa de correio é definida com uma linha por caixa de correio, na forma:

```
mailboxID => pincode,fullname,email,pager-email,options
```

Os campos são:

- **MailboxID** — geralmente o número da extension
- **Pincode** — senha para acessar o sistema de voicemail
- **Full name** — usado pela aplicação de diretório
- **E-mail** — endereço para notificação de voicemail
- **Pager e-mail** — endereço para notificação via gateway SMS ou pager
- **Options** — opções por caixa de correio (as mesmas opções em `[general]`, mas aplicadas a esta caixa de correio)

O voicemail tem várias opções que controlam seu comportamento. Por enquanto, manteremos as opções padrão e nos concentraremos na definição da caixa de correio. Após a seção `[general]` no arquivo, você começa a configurar os IDs das caixas de correio, cada um em seu próprio context. Exemplo:

```
[general]
[default]
1234=>1234,SomeUser,email@address.com,pager@address.com,saycid=yes|dialout=fromvm|callback=fromvm|review=yes|operator=yes
```

Por favor, verifique as opções avançadas no arquivo `voicemail.conf`.

**Passo 3: Configure o arquivo `extensions.conf`.**

Abaixo, você tem as instruções para criar a sub-rotina e a chamada que implementam o voicemail em `extensions.conf`. Usamos o valor da variável de canal `${DIALSTATUS}` para redirecionar o fluxo da chamada para o menu de voicemail apropriado.

### Sub-rotina de Voicemail

## Usando a aplicação Voicemailmain()

A aplicação voicemailmain() é usada para configurar a caixa de correio de voicemail. Os usuários podem discar para a aplicação, gravar sua saudação e ouvir seu voicemail. Para chamar a aplicação no dial plan, use:

```
exten=>9000,1,VoiceMailMain()
```

Abaixo você encontrará uma lista das opções disponíveis para a aplicação.

### Sintaxe da aplicação Voicemail

Esta aplicação permite que a parte chamadora deixe uma mensagem para uma lista especificada de caixas de correio. Quando várias caixas de correio são especificadas, a saudação será retirada da primeira caixa de correio especificada. A execução do dial plan parará se a caixa de correio especificada não existir. A sintaxe é mostrada abaixo:

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

![10-dialplan-advanced-features figure 13](../images/10-dialplan-advanced-features-img13.png)

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

Em todos os casos, o arquivo beep.gsm será reproduzido antes que a gravação comece. As mensagens de voicemail serão armazenadas no diretório inbox.

```
/var/spool/asterisk/voicemail/context/boxnumber/INBOX/
```

Se um chamador pressionar 0 (zero) durante o anúncio, ele será movido para a extension ‘o’ (out) no context atual do voicemail. Isso pode ser usado para sair para a operadora. Se durante a gravação o chamador pressionar # ou o limite de silêncio expirar, a gravação é interrompida e a chamada vai para a próxima prioridade. Certifique-se de tratar a chamada após a reprodução do voicemail, conforme mostrado abaixo.

```
exten=>somewhere,5,Playback(Goodbye)
exten=>somewhere,6,Hangup
```

### Marcando mensagens de voicemail como urgentes

Você pode marcar algumas mensagens como “urgentes”. Dois métodos estão disponíveis para isso:

- Passe a opção ‘U’ na aplicação voicemail()
- Especifique review=yes no arquivo voicemail.conf. Se usar esta opção, o usuário poderá marcar a mensagem como urgente após gravar as instruções de voz.

## Enviando voicemail para e-mail

Em alguns casos (como o meu), simplesmente não usamos a aplicação voicemailmain() para ler e-mail. É mais simples e prático enviar todas as mensagens para o e-mail com o áudio anexado. Usando os parâmetros ‘attach’ e ‘delete’, você pode enviar todos os e-mails para o e-mail e excluí-los da caixa de correio.

```
attach=yes
delete=yes
```

Para enviar voicemail para e-mail, a aplicação de voicemail usa o agente de transferência de mensagens (MTA), um componente do seu sistema operacional. O Debian usa o Exim como MTA. A aplicação que envia o e-mail é definida no parâmetro ‘mailcmd’.

```
mailcmd =/usr/sbin/sendmail -t
```

Na distribuição Debian do Linux, o MTA é o Exim. Para configurar o Exim no Debian, use:

```
dpkg-reconfigure exim4-config
```

Você pode optar por fazer seu MTA enviar um e-mail diretamente via SMTP ou um smarthost (geralmente o servidor de e-mail da sua empresa). Verifique com seu administrador de e-mail a melhor maneira de enviar e-mail do servidor Asterisk para seu servidor de e-mail.

## Personalizando a mensagem de e-mail

Você pode controlar como as mensagens são enviadas configurando as seguintes variáveis: Variáveis para assunto e corpo do e-mail:

- VM_NAME
- VM_DUR
- VM_MSGNUM
- VM_MAILBOX
- VM_CIDNUM
- VM_CIDNAME
- VM_CALLERID
- VM_DATE

O corpo e o assunto do e-mail são construídos a partir de um modelo que você define na seção `[general]` de `voicemail.conf`. Você pode modificar tanto o corpo quanto o assunto, mas o limite de tamanho da mensagem é de 512 bytes. No modelo, `\n` insere uma nova linha e `\t` insere uma tabulação.

O exemplo `emailsubject` abaixo é direto. O exemplo `emailbody` é muito próximo do padrão; o padrão mostra apenas o CIDNAME quando não é nulo, caso contrário o CIDNUM, ou "um chamador desconhecido" quando ambos são nulos.

```
emailsubject=[PBX]: New message ${VM_MSGNUM} in mailbox ${VM_MAILBOX}

emailbody=Dear ${VM_NAME}:\n\n\tjust wanted to let you know you were just left a ${VM_DUR} long message (number ${VM_MSGNUM})\nin mailbox ${VM_MAILBOX} from ${VM_CALLERID}, on ${VM_DATE}, so you might\nwant to check it when you get a chance. Thanks!\n\n\t\t\t\t--Asterisk\n
```

## Interface Web de Voicemail

Existe um script Perl na distribuição de origem chamado `vmail.cgi`, localizado em `contrib/scripts/vmail.cgi` na árvore de origem do Asterisk (ele ainda acompanha o Asterisk 22). O comando `make install` não instala esta interface; você deve executar `make webvmail` a partir do diretório de origem. Este script requer que o interpretador de comandos Perl e um servidor web (como o Apache) estejam instalados no servidor.

```
make webvmail
```

O alvo `make webvmail` instala o script (setuid root) no diretório CGI do seu servidor web (`HTTP_CGIDIR`) e copia as imagens de suporte de `images/*.gif` para `HTTP_DOCSDIR/_asterisk` (por padrão `/var/www/html/_asterisk`). Se esses caminhos não corresponderem ao layout do seu servidor web, edite as variáveis `HTTP_CGIDIR` e `HTTP_DOCSDIR` no `Makefile` de nível superior antes de executar o alvo.

## Notificação de Voicemail

Você pode configurar o voicemail para enviar uma mensagem de notificação para seu telefone quando você tiver um novo voicemail. No Asterisk 22, a Indicação de Mensagem em Espera (MWI) funciona com telefones PJSIP e SIP, bem como telefones DAHDI. Para indicar um voicemail não ouvido, uma luz indicadora pode piscar ou o telefone pode reproduzir um tom de obturador. Você precisa configurar a caixa de correio no arquivo de configuração do canal correspondente. Exemplo: `pjsip.conf` (na seção endpoint):

```
mailboxes=8590
```

> **[Nota da 2ª ed.]** No PJSIP, a dica de caixa de correio (mailbox hint) é definida com a opção `mailboxes` dentro da seção `[endpoint]` de `pjsip.conf`, em vez de `mailbox=` em `sip.conf`. As assinaturas MWI são tratadas por `res_pjsip_mwi`. Verifique a sintaxe de configuração exata para o Asterisk 22.

![A interface web Comedian Mail (`vmail.cgi`): o login do Asterisk Web-Voicemail — insira sua caixa de correio e senha para reproduzir, salvar, encaminhar ou excluir voicemail de um navegador. Ele ainda acompanha o Asterisk 22 e é instalado com `make webvmail`.](../images/10-dialplan-advanced-features-img14.png)

### Laboratório: Notificação de Mensagem no Telefone

Este laboratório foi testado usando um softphone SIP. 1. Edite `pjsip.conf` e adicione `mailboxes=4401` na seção endpoint para o dispositivo chamado 4401. 2. Edite o extensions.conf e crie uma extension para gravar um voicemail para as extensions 4401.

```
exten=9008,n,voicemail(b4401)
```

3. Vá para o console CLI e recarregue. 4. Vá para X-Lite > Botão Direito do Mouse > Configurações da Conta SIP > Propriedades > Voicemail e marque a caixa ‘verificar voicemail’. 5. Disque 9008 e deixe uma mensagem. 6. Observe o ícone de mensagem no telefone.

## Usando a aplicação de diretório

Esta aplicação permite que você encontre rapidamente um usuário para discar. A lista de nomes e extensions correspondentes é recuperada do arquivo de configuração de voicemail voicemail.conf. A sintaxe para a aplicação pode ser mostrada usando core show application directory:

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

### Laboratório: Usando a aplicação de diretório

1. Edite o arquivo voicemail.conf para adicionar duas extensions no dial plan

```
[default]
; Define maximum number of messages per folder for a particular context.
;maxmsg=50
4400=>4400,Clint Eastwood,ceastwood@voip.school
4401=>4401,John Wayne,jwayne@voip.school
```

2. Crie essas extensions em seu dial plan

```
exten=9006,1,VoiceMailMain()
exten=9006,n,Hangup()
exten=9007,1,Directory(default,default)
exten=9007,n,Hangup()
```

3. Vá para o console e recarregue 4. Disque 9006 e grave um nome para cada extension (4400, 4401) 5. Disque 9007 e selecione as três letras do sobrenome para uma extension (Eas=327). Se esta for a opção correta, pressione ‘1’ para transferir para o nome.

## Laboratório: Juntando tudo

Até agora, você aprendeu vários conceitos de dial plan. Vamos colocar todas as aplicações, funções e conceitos em um exemplo de dial plan para que você possa entender como eles são usados juntos. Vamos guiá-lo através de toda a configuração do PBX para o cenário abaixo.

- 4 trunks analógicos
- 16 extensions baseadas em SIP
- 3 classes de serviço:
    - restrict (interno, local e 1-800)
    - ld (longa distância)
    - ldi (internacional)
- Mensagem de fora do horário comercial
- Atendente automático

### Passo 1 – Configurando canais

Trunks analógicos (chan_dahdi.conf) Primeiro, configuraremos os trunks analógicos no arquivo de configuração do canal DAHDI chan_dahdi.conf. Neste caso, usaremos uma placa Digium T400P com 4 interfaces FXO. Vamos supor que o driver já esteja carregado e o arquivo de configuração do driver (/etc/dahdi/system.conf) esteja configurado corretamente.

![10-dialplan-advanced-features figure 16](../images/10-dialplan-advanced-features-img16.png)

```
signalling=fxs_ks
language=en
context=incoming
group=1
channel => 1-4
```

Canais SIP (pjsip.conf) Escolhemos a numeração do dial plan de 2000 a 2099. Dois codecs serão usados: G.729 e G.711 ulaw. O primeiro será usado para telefones usando Asterisk pela Internet ou WAN, enquanto o segundo será usado para telefones usando a rede local. Em `pjsip.conf`, arbitraremos quais dispositivos pertencerão a cada classe de serviço (restrict, ld, ldi). Para reduzir a vulnerabilidade a ataques de força bruta, usaremos os endereços MAC dos telefones como nomes de dispositivos. Aconselho fortemente que você use senhas fortes para evitar ataques de força bruta!

Definimos um transporte e três modelos reutilizáveis — uma base de endpoint com os
codecs compartilhados, uma autenticação userpass e um único AOR de contato — então anexamos cada dispositivo
aos modelos e substituímos apenas o que difere (seu context de classe de serviço e
credenciais). `host=dynamic` torna-se um AOR no qual o telefone se registra, e
`directmedia` torna-se `direct_media`:

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

[auth-userpass](!)
type=auth
auth_type=userpass

[aor-single](!)
type=aor
max_contacts=1

[00001A000002](endpoint-base)
context=restrict
auth=00001A000002
aors=00001A000002
mailboxes=20
[00001A000002](auth-userpass)
username=00001A000002
password=#s2cr2t#
[00001A000002](aor-single)

[00001A000003](endpoint-base)
context=ld
dtmf_mode=rfc4733
auth=00001A000003
aors=00001A000003
mailboxes=20
[00001A000003](auth-userpass)
username=00001A000003
password=#s3cr3t#
[00001A000003](aor-single)

[00001A000004](endpoint-base)
context=ldi
dtmf_mode=rfc4733
auth=00001A000004
aors=00001A000004
mailboxes=20
[00001A000004](auth-userpass)
username=00001A000004
password=#s3cr3t#
[00001A000004](aor-single)
```

### Passo 2 – Configurar o dial plan

Agora vamos começar a configurar o extensions.conf. Defina extensions internas e discagem local

```
[restrict]
exten=>_2000,1,Dial(PJSIP/00001A000002,20,t)
exten=>_2030,1,Dial(PJSIP/00001A000003,20,t)
exten=>_2040,1,Dial(PJSIP/00001A000004,20,t)
exten=>_9XXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20) ; local calls
exten=>_91800.,1,Dial(DAHDI/g1/${EXTEN:1},20); 1-800
```

Defina LD (longa distância)

```
[ld]
Include=>restrict
exten=>_9NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

Defina chamadas internacionais

```
[ldi)
include=> ld
exten=>_901X.,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

### Passo 3 - Recebendo chamadas usando um atendente automático

Para receber chamadas, use dois contexts. O primeiro é para operação em horário normal, onde a chamada será recebida por um atendente automático. O segundo é para fora do horário comercial, onde o chamador receberá uma mensagem como “você ligou para a empresa XYZ, nosso horário normal é das 08:00 às 18:00; se você souber o número da extension de destino, pode tentar discá-lo agora ou desligar.” Menus: Horário normal, Fora do horário comercial Nos menus abaixo, o sistema reproduzirá uma mensagem avisando ao chamador que a empresa foi contatada fora do horário comercial, permitindo que o chamador disque o número da extension de destino (alguém pode estar trabalhando fora do horário comercial).

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

Menus: Principal e Vendas Durante o horário comercial normal, a chamada é atendida por um menu de atendente automático, recebendo uma mensagem como “bem-vindo à Empresa XYZ; disque 1 para vendas, 2 para suporte técnico, 3 para treinamento ou a extension desejada”.

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

Com todas essas instruções, a funcionalidade do seu plano de discagem está pronta. Na próxima seção, demonstraremos como operar o PBX.

## Resumo

Neste capítulo, você aprendeu como receber chamadas usando um IVR ou um atendente automático. Você estudou o conceito de inclusão de context e implementou alguns exemplos. Sub-rotinas foram usadas para evitar digitação repetitiva, e o banco de dados Asterisk baseado no mecanismo Berkley DB foi usado para funções que exigem armazenamento de dados (por exemplo, encaminhamento de chamadas, não perturbe, listas negras). Finalmente, você aprendeu como implementar o comportamento de fora do horário comercial e implementou um dial plan completo usando esses conceitos.

## Quiz

1. Uma inclusão de context dependente de tempo usa a forma `include => context,<times>,<weekdays>,<mdays>,<months>`. O que `include => normalhours,08:00-18:00,mon-fri,*,*` faz?
   - A. Executa as extensions de segunda a sexta-feira, das 08:00 às 18:00
   - B. Executa as opções todos os dias em todos os meses
   - C. Nada; o formato é inválido
2. No Asterisk moderno (incluindo o Asterisk 22), os campos de um `include =>` baseado em tempo e de `GotoIfTime()` são separados por qual caractere?
   - A. O pipe `|`
   - B. A vírgula `,`
   - C. O ponto e vírgula `;`
   - D. A barra `/`
3. Para discar para vários canais ao mesmo tempo (fazendo-os tocar simultaneamente), você os separa dentro de `Dial()` com o caractere ___.
4. Um menu de voz que reproduz uma mensagem enquanto aguarda que o chamador disque uma extension é geralmente criado com a aplicação ___.
5. Você pode incluir o conteúdo de outro arquivo dentro de `extensions.conf` usando a instrução ___ (nota: isso é diferente da instrução de context `include =>`).
6. No Asterisk 22, o banco de dados embutido AstDB é suportado por:
   - A. Berkeley DB v1
   - B. MySQL
   - C. SQLite3
   - D. PostgreSQL
7. Quando você usa `Dial(type1/identifier1&type2/identifier2)`, o Asterisk disca para cada canal em sequência, aguardando 20 segundos entre eles.
   - A. Falso
   - B. Verdadeiro
8. Com a aplicação Background(), você deve aguardar até que a mensagem termine de ser reproduzida antes de poder pressionar um dígito DTMF para escolher uma opção.
   - A. Falso
   - B. Verdadeiro
9. Dada a sintaxe `Goto([[context,]extension,]priority)`, quais das seguintes são invocações válidas da aplicação Goto()? (marque todas as que se aplicam)
   - A. Goto(context,extension)
   - B. Goto(context,extension,priority)
   - C. Goto(extension,priority)
   - D. Goto(priority)
10. Para excluir uma única chave do AstDB no dial plan do Asterisk 22, você usa:
    - A. A aplicação `DBdel()`
    - B. A função `DB_DELETE()`
    - C. A aplicação `DBdeltree()`
    - D. A aplicação `LookupBlacklist()`

**Respostas:** 1 — A · 2 — B · 3 — `&` · 4 — Background() · 5 — #include · 6 — C · 7 — A · 8 — A · 9 — B, C, D · 10 — B
