# Asterisk Security

Desde o início, a questão da segurança para o Asterisk é crítica. SIP, Session Initiation Protocol, é o protocolo mais atacado na Internet segundo o CERT.BR. Qualquer pessoa que execute um honeypot pode confirmar. O problema da Internet Revenue Share Fraud é muito sério e pode gerar perdas superiores a centenas de milhares de dólares. Você nunca deve instalar um servidor Asterisk conectado à Internet sem a devida segurança. Neste capítulo, você aprenderá a identificar os principais tipos de ataques que pode receber e como preveni‑los usando uma política de segurança adequada. Por último, mas não menos importante, você aprenderá a implementar a política de segurança sugerida.

Este capítulo tem como alvo **Asterisk 22 LTS**, onde o PJSIP (`res_pjsip` / `chan_pjsip`) é o único canal SIP. (O antigo driver `chan_sip` foi removido no Asterisk 21 — veja o capítulo *Legacy Channels* se você estiver migrando de um sistema mais antigo.) Uma consequência relevante para a segurança: autenticações falhas agora são emitidas através da **security event framework** do Asterisk e do canal de logger dedicado `security`, o que altera a forma como o Fail2Ban é configurado (abordado mais adiante neste capítulo).

## Objectives

By the end of this chapter you should be able to:

- Identify the main types of attacks frequently made to Asterisk servers
- Define an effective security policy
- Implement the security policy
- Install and configure IPTABLES for Asterisk
- Install and configure Fail2Ban for Asterisk
- Install and configure TLS and SRTP for encryption

## Principais ataques à telefonia IP

Os principais ataques à telefonia IP podem ser classificados como DOS/DDOS, Roubo de Serviço/Fraude de Tarifação e Interceptação. Alguns dos nomes podem ser confusos e diferentes fontes às vezes têm nomes diferentes para o mesmo ataque. Roubo de Serviço, Fraude de Tarifação, Fraude de Compartilhamento de Receita na Internet, Fraude Telefônica são nomes diferentes para hackers que usam seu PBX para gerar tráfego para um Número de Tarifa Premium e recebem reembolsos do provedor.

### DDoS/DOS

Denial of Service e Distributed Denial of Service são ataques populares contra qualquer infraestrutura de TI. Não é diferente com SIP e outros protocolos de Voice over IP. Distributed denial of service geralmente é perpetrado por uma botnet, enquanto DOS ocorre apenas por um único computador. Em fevereiro de 2011, a botnet Sality realizou uma varredura furtiva e coordenada de todo o espaço de endereços IPv4 em busca de servidores SIP vulneráveis — pesquisadores que observavam o UCSD Network Telescope atribuíram isso a aproximadamente três milhões de IPs de origem distintos sondando a porta UDP 5060, provavelmente para forçar contas SIP em fraudes de tarifação.[^sality]

[^sality]: A. Dainotti et al., "Analysis of a '/0' Stealth Scan from a Botnet," *IEEE/ACM Transactions on Networking*, 2015 (DOI 10.1109/TNET.2013.2297678).

![Uma botnet ponto-a-ponto direcionando milhares de tentativas de registro SIP a um servidor](../images/19-security-fig01.png)

O DOS é geralmente aplicado por meio de técnicas como fuzzing e flooding. O flooding pode usar SIP, IAX, RTP e outros protocolos. Eles podem interromper o serviço completamente ou degradar a qualidade da voz. São muito difíceis de mitigar se as portas estiverem abertas para a Internet. Abaixo estão algumas das ferramentas usadas pelos atacantes.

**Fuzzing:**

- **PROTOS Test Suite (c07-sip)** — da Universidade de Oulu OUSPG. Envia milhares de pacotes malformados para provocar uma falha, como um estouro de buffer que interrompe o software.
- **Voiper** — gera mais de 200.000 testes que cobrem todos os atributos SIP e verifica se o seu servidor pode processar as mensagens de forma eficaz. <http://voiper.sourceforge.net/>

**Inundação:**

- **INVITE Flooder** — inunda o servidor com solicitações SIP INVITE. <http://www.hackingvoip.com/tools/inviteflood.tar.gz>
- **IAX Flooder** — inunda o servidor com tráfego IAX2. <http://www.hackingvoip.com/tools/iaxflood.tar.gz>
- **RTP Flooder** — inunda sessões de mídia ativas com pacotes RTP para degradar a qualidade de voz. <http://www.hackingvoip.com/tools/rtpflood.tar.gz>

### Técnicas de mitigação para DoS/DDoS

Minhas recomendações são

1. Não exponha seu servidor Asterisk na Internet, a menos que seja necessário, com proteção adequada (SBC)  
2. Na rede interna, use uma VLAN virtual para voz, principalmente se você estiver em uma universidade ou faculdade onde o número de usuários é alto.  
3. Use VPN ou TLS para acesso externo.

### Fraude de Compartilhamento de Receita na Internet

Essa fraude é um pouco complicada de entender. O ponto principal é compreender o conceito de um número internacional de tarifa premium (IPRN).

![Os três passos da fraude de compartilhamento de receita na Internet: comprar um número de tarifa premium, encontrar um dispositivo VoIP vulnerável e ligar para o número, então coletar o pagamento](../images/19-security-fig02.png)

Um IPRN é um número que você pode alocar gratuitamente em algumas operadoras de telefonia internet específicas. Procure por **Internet Premium Rate Number Providers** e você encontrará várias delas. Nesse tipo de operadora você pode alocar, por exemplo, um número em uma rede de satélite como a Iridium, um destino que custa décimos de dólar por minuto ao chamador. O provedor de IPRN lhe devolverá uma porcentagem da receita (10 a 20 % da renda) por cada minuto recebido.

![Lista de preços de provedor IPRN mostrando taxas de pagamento por país e números de teste](../images/19-security-fig03.png)

Após a fase de alocação, o hacker tenta encontrar qualquer servidor Asterisk aberto capaz de discar o IPRN alocado. O PBX da vítima, controlado pelo hacker, fará centenas de chamadas para o número IPRN, gerando um grande retorno para o hacker e uma enorme conta telefônica para a vítima. Muitas vezes, superior a centenas de milhares de dólares em um único fim de semana.

Principais ferramentas usadas por hackers para atacar um PBX:

1. **SIPVicious**: http://code.google.com/p/sipvicious/. Sipvicious é um conjunto de ferramentas de segurança fácil de usar. Seu objetivo principal é reconhecer PBXs vulneráveis e quebrar as senhas SIP usando um ataque de força bruta. A ferramenta mais utilizada é svcrack. A ferramenta é capaz de testar milhares de senhas por segundo.  
2. **Vulnerabilidades de telefone**. Outro ponto frequentemente usado por hackers como vetor de ataque é o próprio telefone. Muitas pessoas que instalam Asterisk não alteram a senha padrão na interface web do telefone. Quando esses telefones ficam acessíveis na Internet, os hackers podem tentar usar a senha padrão da interface para baixar a configuração, onde frequentemente podem encontrar a senha secreta SIP.

#### Roubo de TFTP:

Se você está usando provisionamento automático de telefones via TFTP, provavelmente está vulnerável a esse tipo de ataque. TFTP é uma forma simples e insegura de um protocolo de transferência de arquivos.

![Um atacante baixando arquivos .cfg adivinháveis de um servidor TFTP, coletando credenciais em texto plano dos arquivos de configuração](../images/19-security-fig04.png)

O nome dos arquivos de configuração é facilmente adivinhável usando o endereço MAC seguido de .cfg (ex.: 001A2B3C4D5E.cfg). Um hacker habilidoso pode criar facilmente um utilitário para tentar todos os endereços MAC sequencialmente ou simplesmente baixar uma ferramenta para isso. O arquivo de configuração geralmente não é criptografado e contém a senha secreta SIP dentro.

#### Mitigação contra ataques de força bruta e roubo de tftp

Para mitigar esses ataques, você pode aplicar as soluções abaixo.  

Brute force: A melhor solução para mitigar ataques de força bruta é impedir tentativas sequenciais não autorizadas. Quase todo instalador do Asterisk usa a ferramenta fail2ban para isso. Quando o fail2ban detecta múltiplas tentativas com senha ou nome de usuário incorretos, ele bloqueia o IP do invasor por um determinado período de tempo. A segunda medida contra força bruta é usar senhas fortes, com mais de 12 caracteres, contendo ao menos um caractere especial.  

Tftptheft: Para impedir TFTPTheft, configure o provisionamento para usar https com nome de usuário e senha. O arquivo é transmitido criptografado e um nome de usuário e senha impedem que invasores tentem baixar quaisquer arquivos.

### Escuta

Não vemos muitas desses tipos de ataque porque na maioria dos casos eles simplesmente não são detectados. A interceptação é muito difícil de detectar em um ambiente IP. Utilitários como UCsniff, disponíveis gratuitamente, são capazes de interceptar uma chamada VoIP na maioria das redes. A técnica principal é usar ARP spoofing para forçar o tráfego através do computador que executa o UCsniff e gravar as chamadas.

#### Mitigação contra escuta clandestina

Você pode impedir a escuta clandestina criptografando seu tráfego VoIP. Outra forma é prevenir ataques man‑in‑the‑middle (MITM) em sua rede. A inspeção ARP é muito eficaz para impedir MITM em redes de camada 2. Consulte o suporte técnico da sua rede para entender como implementá‑la. Mais adiante neste livro, aprenderemos a instalar criptografia baseada em TLS e SRTP. Você também pode usar o ARPWatch para descobrir se alguém está abusando do protocolo ARP para atacar sua rede.

## Política de segurança para Asterisk

A melhor forma de implementar segurança é criar uma política de segurança. Para este treinamento, sugerirei uma política de segurança para a maioria das instalações do Asterisk. Use-a como ponto de partida base e altere-a conforme suas necessidades. A política de segurança sugerida segue abaixo:

1. Nenhuma porta UDP/TCP desnecessária aberta
2. Nenhum acesso a qualquer interface administrativa (SSH/HTTPS) aberto na Internet.
3. Para acessar SSH e/ou HTTP/HTTPS deve haver exceções explícitas no firewall IPTABLES
4. Senhas fortes com 12 caracteres e pelo menos um caractere especial
5. Bloquear endereços IP que falharem mais de 10 vezes na autenticação usando Fail2ban
6. Confirmação de senha para chamadas internacionais
7. Limitar o acesso à porta SIP ao seu intervalo conhecido de endereços IP

Se você precisar ter acesso externo ao seu PBX, há duas possibilidades. Use um SBC (Session Border Controller) para proteger seu servidor contra DOS/DDOS ou use uma VPN sempre que quiser acesso externo. Se você deixar a porta 5060 aberta na Internet sem um SBC ou VPN, estará vulnerável a um ataque de DOS/DDOS. O risco é seu.

### Reforço da era PJSIP (Asterisk 22)

Além do firewall e do Fail2Ban, a pilha PJSIP do Asterisk 22 oferece vários controles em nível de configuração que devem fazer parte da sua política de segurança. Eles complementam (não substituem) os controles de rede acima:

- **Autenticação por endpoint.** Cada endpoint deve referenciar uma seção `type=auth` dedicada com um `password` forte e exclusivo (`auth_type=digest`). Nunca reutilize credenciais entre endpoints.  
- **O tratamento anônimo está incorporado.** O PJSIP não revela se um nome de usuário existe quando a autenticação falha. Para aceitar chamadas anônimas, você deve criar explicitamente um endpoint chamado `anonymous` e usar seções `type=identify` (correspondendo ao IP de origem) para mapear pares conhecidos a endpoints. Se não quiser chamadas anônimas, basta não criar um endpoint `anonymous`, e solicitações não correspondidas são desafiadas/rejeitadas.  
- **ACLs.** Restrinja quem pode alcançar um endpoint com ACLs nomeadas `/etc/asterisk/acl.conf`, referenciadas a partir do endpoint com `acl=` (ACL de sinalização/fonte) e `contact_acl=` (restrição do endereço de contato/registro). Você também pode definir permit/deny diretamente no endpoint.  
- **`qualify`.** Defina `qualify_frequency` (e `qualify_timeout`) no AOR para que o Asterisk monitore ativamente a alcançabilidade dos contatos registrados e elimine os inativos.  
- **Endurecimento do transporte PJSIP / proteção contra DoS.** O `type=transport` não expõe um limite de clientes por transporte, portanto a proteção contra inundação de conexões vem do firewall (as regras iptables/Fail2Ban neste capítulo) em vez de uma opção do PJSIP. O que o transporte *faz* oferecer são ajustes de keep-alive TCP (`tcp_keepalive_enable`, `tcp_keepalive_idle_time`, `tcp_keepalive_interval_time`, `tcp_keepalive_probe_count`) para limpar conexões mortas/semipermanentes, e configurações `local_net`/`external_*` para tratamento correto de NAT. Combine esses ajustes com as regras de firewall para atenuar ataques de inundação de conexões.  
- **TLS + SRTP para mídia.** Criptografe o sinalizador com um transporte TLS e a mídia com `media_encryption=sdes` (ou `dtls` para WebRTC) no endpoint — abordado mais adiante neste capítulo.  
- **Controle de acesso AMI/ARI.** Restrinja a Interface de Gerenciamento do Asterisk (`manager.conf`) e o ARI (`ari.conf` / `http.conf`) ao localhost ou a uma rede de gerenciamento confiável, use segredos fortes e exclusivos, vincule o servidor HTTP a uma interface privada e nunca exponha esses serviços à Internet.

All of the option names above are confirmed against Asterisk 22.10: the `type=transport` section exposes `tcp_keepalive_enable`, `tcp_keepalive_idle_time`, `tcp_keepalive_interval_time`, `tcp_keepalive_probe_count`, `tos`, `cos`, `local_net`, and the `external_*` family, but it has **não** `max_clients` option — connection-flood protection comes from the firewall, not from the transport. The `acl` and `contact_acl` endpoint options take section names from `acl.conf`, and source-IP matching for unauthenticated peers is done with `type=identify` sections (`match=`).

### Removendo portas desnecessárias

Em vez de descobrir todas as vulnerabilidades associadas a todos os protocolos do Asterisk, vamos simplificar o problema removendo as portas desnecessárias. Para listar todas as portas abertas pelo servidor Asterisk use:

```
netstat -pantu |grep asterisk
```

The output of the command is shown below.

![netstat output showing the many ports bound by Asterisk, including 4569 (IAX) and 2727 (MGCP)](../images/19-security-fig05.png)

If you look at the output, you will discover that many ports are open. Do we need them? Not necessarily, 2727 is the MGCP protocol (chan_mgcp), 4569 is the IAX (chan_iax2). If you are not using these protocols, you can simply remove the module in the configuration file modules.conf.

You may notice Asterisk binding a high-numbered UDP port. This comes from `res_pjsip`'s resolver making outbound DNS queries (the source port is ephemeral, like any client DNS lookup), not from an inbound listener — your firewall only needs to allow **established/related** return traffic for it (the iptables `conntrack ESTABLISHED,RELATED` rule shown below already covers this). You do **not** need to open a wide inbound high-UDP range just for PJSIP DNS.

To remove the unnecessary ports, disable the modules you don't use. Edit the file modules.conf and add `noload` lines for the channels and protocols you are not using. **Do not** noload `res_pjsip`, `res_pjproject`, or `chan_pjsip` — those are required for SIP in Asterisk 22:

```
; res_pjsip / res_pjproject / chan_pjsip are REQUIRED in Asterisk 22 - keep them loaded
noload => chan_iax2.so
noload => chan_unistim.so
```

(In Asterisk 22 you no longer need to noload `chan_mgcp` or `chan_skinny` — those drivers were *removed* in Asterisk 21 and are not part of a stock 22 build.) With the instructions above, I have removed all unnecessary channels keeping only PJSIP. You can choose whatever protocol modules you want, just remove the unused ones. The result is shown in the screenshot below — only the SIP port (5060) bound by your PJSIP transport is now exposed inbound.

![saída do netstat após desativar os módulos não usados: apenas a porta UDP 5060 permanece vinculada ao Asterisk](../images/19-security-fig06.png)

### Implementando a política de segurança com IPTABLES

IPTABLES ou netfilter é um firewall padrão presente na maioria das distribuições Linux. Neste laboratório configuraremos iptables e fail2ban. O objetivo é implementar a política de segurança recomendada para Asterisk e bloquear todo o tráfego desnecessário. Siga os passos abaixo:

1. Bloquear todo o tráfego externo
2. Permitir tráfego SSH a partir de uma rede interna ou host único
3. Permitir tráfego SIP em UDP e TCP nas portas 5060
4. Permitir tráfego RTP na faixa de portas de mídia UDP. Não existe um padrão interno único — o próprio `rtp.conf` do Asterisk recua para as portas 5000–31000 quando nada está configurado, mas o `rtp.conf.sample` distribuído configura `rtpstart=10000` / `rtpend=20000`, então usamos esse intervalo de exemplo aqui. Ajuste sua regra de firewall ao `rtpstart`/`rtpend` que você realmente definiu em `rtp.conf`.

Certifique‑se de ter acesso ao console do servidor, você não quer se bloquear fora do sistema. Tenha cuidado.

1. Instale o pacote net-persistent.```
   sudo apt-get install iptables-persistent
   ```

2. Permitir todo o tráfego da interface de loopback```
   sudo iptables -I INPUT -i lo -j ACCEPT
   sudo iptables -I OUTPUT -o lo -j ACCEPT
   ```

3. Permitir conexões estabelecidas```
   sudo iptables -I INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
   ```

Permitir tráfego SSH/HTTPS da rede 192.168.0.0```
   sudo iptables -I INPUT -p tcp -s 192.168.0.0/16 --dport 22 -m conntrack --ctstate
   NEW,ESTABLISHED -j ACCEPT
   sudo iptables -I INPUT -p tcp -s 192.168.0.0/16 --dport 443 -m conntrack --ctstate
   NEW,ESTABLISHED -j ACCEPT
   ```

5. Insira as regras do Asterisk```
   sudo iptables -I INPUT -p udp -m udp --dport 5060 -j ACCEPT
   sudo iptables -I INPUT -p tcp -m tcp --dport 5060 -j ACCEPT
   sudo iptables -I INPUT -p tcp -m tcp --dport 5061 -j ACCEPT
   sudo iptables -I INPUT -p udp -m udp --dport 10000:20000 -j ACCEPT
   ```

Note that port 5061 (SIP over TLS) is **TCP**, not UDP. The rules above open 5060 on both UDP and TCP and 5061 on TCP. If you only run TLS, you can drop the plain 5060 rules entirely. Only open the ports your PJSIP transports actually bind to.

`-I` means PREPEND

6. The last rule has to be a drop```
   sudo iptables -A INPUT -j DROP
   ```

`-A` significa APPEND. Nota: Tenha cuidado ao manter novas regras, você tem que adicionar regras antes do DROP. Use PREPEND para novas regras `-I`

7. Salve as regras e reinicie o iptables```
   sudo iptables-save >/etc/iptables/rules.v4
   sudo /etc/init.d/netfilter-persistent restart
   ```

### Usando Fail2Ban para bloquear múltiplas tentativas falhas de autenticação

Fail2Ban é quase um padrão para Asterisk. A maioria dos usuários o implementa para melhorar a segurança. Esta utilidade analisa os logs do Asterisk em busca de tentativas falhas e bane os endereços IP dos atacantes. A seguir, forneço as instruções para instalar o Fail2Ban.

No Asterisk 22, o PJSIP registra autenticações falhas e outros eventos de segurança através da **framework de eventos de segurança** do Asterisk, escrita no canal de logger dedicado **`security`**. Para que o Fail2Ban funcione, você deve:

1. Habilitar o canal de segurança em `/etc/asterisk/logger.conf`. A sintaxe é `<filename> => <levels>`, portanto, para enviar o nível de segurança para um arquivo chamado `security` escreva:

```
[logfiles]
security => security
```

então execute `logger reload` a partir da CLI. Isso produz `/var/log/asterisk/security` com uma linha por evento de segurança, no formato:

```
[2026-01-15 10:23:45] SECURITY[1234] res_security_log.c: SecurityEvent="InvalidPassword",...,RemoteAddress="IPV4/UDP/203.0.113.7/5060",...
```

Os eventos que o Fail2Ban se importa são `InvalidPassword`, `ChallengeResponseFailed`, `InvalidAccountID` e `FailedACL`, cada um contendo um campo `RemoteAddress="IPV4/UDP/<ip>/<port>"` que identifica o infrator. (Observe que o endereço está encapsulado como `IPV4/UDP/.../...`, não como um IP puro — seu filtro deve extrair o host de dentro dessa string.)

2. Aponte a prisão `asterisk` para esse arquivo (`logpath = /var/log/asterisk/security`) e use um filtro que analise este formato de evento de segurança.

O Fail2Ban moderno inclui um filtro `asterisk` cujo `failregex` já corresponde aos eventos acima e extrai `<HOST>` do campo `RemoteAddress`, por exemplo:

```
failregex = ^SecurityEvent="(?:FailedACL|InvalidAccountID|ChallengeResponseFailed|InvalidPassword)".*,RemoteAddress="IPV[46]/[^/"]+/<HOST>/\d+"
```

PBX distributions (FreePBX/Sangoma) ship equivalent filters. Prefer the packaged filter over hand‑writing one, since the exact event strings are version‑dependent. One caveat to be aware of: a now‑patched advisory (GHSA-5743-x3p5-3rg7) showed that crafted PJSIP traffic could inject fake log lines — keep both Asterisk and your Fail2Ban filter current.

Below I provide the instructions to install Fail2Ban

1. Install fail2ban on Linux```
   sudo apt-get install fail2ban
   ```

2. Ativar fail2ban para Asterisk e SSH```
   sudo vi /etc/fail2ban/jails.d/defaults-debian.conf
   ```

Adicione as linhas a seguir para ativar o fail2ban para ssh e asterisk```
   [sshd]
   enabled = true
   [asterisk]
   enabled=true
   ```

3. Reiniciar fail2ban```
   /etc/init.d/fail2ban restart
   ```

4. Verifique. Altere o segredo do seu softphone e tente registrar novamente 10 vezes. Usando `iptables -L`, verifique se o endereço do softphone foi incluído como um endereço bloqueado.  
5. Remova o endereço da proibição (suponha que o endereço seja 192.168.0.5)```
   sudo fail2ban-client set asterisk unbanip 192.168.0.5
   ```

Note: In the command replace 192.168.0.5 by the ip address of your phone

### Implementando TLS e SRTP

Dividirei esta seção em duas partes. Na primeira parte abordaremos TLS para criptografar o sinalização e, na segunda parte, SRTP para criptografar a mídia. O objetivo aqui é configurar o Asterisk para esses recursos.

#### TLS

TLS (Transport Layer Security) é o mecanismo de criptografia definido para proteger a sinalização SIP. A tabela abaixo resume contra quais ataques o TLS protege:

| Type of attack | Protected? | Notes |
|----------------|-----------|-------|
| Signaling attacks | Yes | TLS assures the integrity of the messages |
| Man in the middle | Yes | TLS checks the server certificate |
| Eavesdropping | No | TLS encrypts signaling, not media |

Para criptografia de mídia (voz/vídeo) use SRTP.

#### Certificados digitais autoassinados

Existem dois tipos de certificados que você pode usar: autoassinados e comerciais. Certificados autoassinados são assinados pelo seu próprio servidor, enquanto certificados comerciais são assinados por uma autoridade externa. Para VoIP, você pode ser sua própria autoridade certificadora. Não há necessidade de um certificado externo como GoDaddy ou Verisign, isso seria um gasto desnecessário. Geraremos nossos próprios certificados usando ast_tls_cert.

#### Configurando TLS com certificados autoassinados

Abaixo está um guia passo a passo sobre como implementar TLS. Primeiro geramos os certificados, depois configuramos o transporte TLS do PJSIP (veja "Configuring TLS with chan_pjsip") e, por fim, apontamos o softphone para ele. Usaremos o SipPulse Softphone, que suporta TLS e SRTP nativamente. (Qualquer softphone SIP compatível com TLS/SRTP funciona da mesma forma.)

**Step 1.** Crie uma chave RSA privada usando criptografia 3DES com comprimento de 4096 bits para nossa autoridade certificadora. O comando abaixo presente em /usr/src/asterisk-22.x.y/contrib/scripts criará a Certification Authority e o Asterisk Certificate. Como de costume, adapte as instruções se necessário, versões mudam, diretórios mudam. Por favor, preste atenção ao que está fazendo. Use seu domínio ou endereço IP na opção –C. O comando ast_tls_cert tem três opções.

- -C host or IP address (I have used 192.168.0.74, the IP address of my VM)
- -O Organizational name
- -d Directory where to store the keys

```
mkdir /etc/asterisk/keys
cd /usr/src/asterisk-22.0.0/contrib/scripts
root@asterisk:/usr/src/asterisk-22.0.0/contrib/scripts# ./ast_tls_cert -C 192.168.0.74 -O "AsteriskGuide" -d /etc/asterisk/keys
No config file specified, creating '/etc/asterisk/keys/tmp.cfg'
You can use this config file to create additional certs without
re-entering the information for the fields in the certificate
Creating CA key /etc/asterisk/keys/ca.key
Generating RSA private key, 4096 bit long modulus
........................................................++
........................................................++
e is 65537 (0x010001)
Enter pass phrase for /etc/asterisk/keys/ca.key:
Verifying - Enter pass phrase for /etc/asterisk/keys/ca.key:
Creating CA certificate /etc/asterisk/keys/ca.crt
Enter pass phrase for /etc/asterisk/keys/ca.key:
Creating certificate /etc/asterisk/keys/asterisk.key
Generating RSA private key, 2048 bit long modulus
........................++++++
......................++++++
e is 65537 (0x010001)
Creating signing request /etc/asterisk/keys/asterisk.csr
Creating certificate /etc/asterisk/keys/asterisk.crt
Signature ok
subject=CN = 192.168.0.74, O = AsteriskGuide
Getting CA Private Key
Enter pass phrase for /etc/asterisk/keys/ca.key:
Combining key and crt into /etc/asterisk/keys/asterisk.pem
root@asterisk:/usr/src/asterisk-22.0.0/contrib/scripts#
```

Não vou gerar um certificado de cliente porque não vamos usar o certificado para autenticar o cliente. O cliente não precisa apresentar seu próprio certificado.

**Step 2.** Configure o Asterisk para suportar nosso cliente via TLS. Isso é feito em `pjsip.conf` (um transporte TLS mais as configurações do endpoint) — a configuração completa é mostrada na seção seguinte, “Configuring TLS with chan_pjsip.” Não estamos autenticando usando certificados, apenas criptografando o tráfego.

**Step 3.** Instale um softphone SIP compatível com TLS (o autor usa o SipPulse Softphone).

**Step 4.** Copie a autoridade certificadora para o computador que executa o softphone. Após instalá‑la, copie o arquivo `/etc/asterisk/keys/ca.crt` para o computador que executa o softphone (use scp, ou WinSCP no Windows) se você estiver usando um certificado autoassinado.

**Step 5.** Crie a conta no softphone. Na tela de conta adicione a conta normalmente como qualquer outra conta sip. Use a senha correta, a autenticação ainda se baseia na senha.

**Step 6.** Defina TLS como o transporte nas configurações da conta. Na tela de conta do SipPulse Softphone (abaixo), escolha **TLS** como transporte e use a porta 5061. Ajuste seu firewall para abrir a porta TCP 5061.

![The SipPulse Softphone account screen — enter the Server (your Asterisk IP or domain), Username, Password, and Display Name, then choose the Transport (UDP, TCP, or TLS).](../images/softphone/sipphone-account.png){width=35%}

**Step 7.** Confie na autoridade certificadora. Se o certificado TLS do seu Asterisk for assinado por uma CA pública (por exemplo Let’s Encrypt — veja o capítulo *Deployment*), um softphone moderno como o SipPulse Softphone confia nele automaticamente através do repositório de certificados do sistema, sem necessidade de importação manual. Se você usar um certificado autoassinado, importe sua CA (`/etc/asterisk/keys/ca.crt`) no cliente ou no repositório de confiança do sistema operacional, ou aceite‑a quando solicitado.

**Step 8.** Você **não** precisa de um certificado de cliente. Um equívoco comum é que cada telefone precise de seu próprio certificado para autenticar — isso não ocorre. Neste ponto o Asterisk apenas *criptografa* a sessão; a autenticação ainda é feita por nome de usuário e senha. O Asterisk não verifica certificados de cliente por padrão, portanto não há necessidade de distribuir um certificado por cliente.

**Step 9.** Após mudar o certificado ou o transporte, reinicie completamente o softphone (saia e abra novamente, não apenas feche a janela) para que ele reconecte usando o novo transporte.

### Configuring TLS with chan_pjsip

Agora vamos aprender como configurar o PJSIP para TLS. O PJSIP é o único canal SIP no Asterisk 22, portanto não há nada para trocar — apenas certifique‑se de que `res_pjsip`, `res_pjproject` e `chan_pjsip` estejam carregados. Passo 1: Confirme que o PJSIP está habilitado em /etc/asterisk/modules.conf.

```
; res_pjsip / res_pjproject / chan_pjsip must be loaded (do NOT noload them)
noload => chan_iax2.so
noload => chan_unistim.so
```

Step 2: Configure PJSIP to support TLS. Add a section for TLS transport in the file /etc/asterisk/pjsip.conf

```
[transport-tls]
type=transport
protocol=tls
bind=0.0.0.0:5061
cert_file=/etc/asterisk/keys/asterisk.crt
priv_key_file=/etc/asterisk/keys/asterisk.key
method=tlsv1_2
```

Use `method=tlsv1_2` (ou `tlsv1_3` se sua compilação OpenSSL/PJSIP suportar) — TLS 1.0/1.1 são obsoletos e inseguros e não devem ser usados.

Etapa 3: Configure o endpoint para blink. Edite `pjsip.conf` e edite a seção para blink. Deixe o PJSIP escolher o transporte automaticamente.

```
[blink]
type=endpoint
aors=blink
auth=blink
context=from-internal
disallow=all
allow=ulaw
dtmf_mode=rfc4733
media_encryption=sdes
[blink]
type=aor
max_contacts=2
remove_existing=yes
[blink]
type=auth
auth_type=digest
username=blink
password=supersecret
```

Etapa 4: Verificando. Para verificar se o registro ocorreu via TLS, use o comando a seguir no console do Asterisk.

```text
asterisk*CLI> pjsip show aor blink

      Aor:  <Aor.............................................>  <MaxContact>
    Contact:  <Aor/ContactUri........................> <Hash....> <Status> <RTT(ms)..>
==========================================================================================

      Aor:  blink                                                2
    Contact:  blink/sip:03694827@192.168.0.67:56295;transp 620d91556d NonQual    nan
 ParameterName        : ParameterValue
 ====================================================================
 authenticate_qualify : false
 contact              : sip:03694827@192.168.0.67:56295;transport=tls
 default_expiration   : 3600
 max_contacts         : 2
 maximum_expiration   : 7200
 minimum_expiration   : 60
 qualify_frequency    : 0
 qualify_timeout      : 3.000000
 remove_existing      : true
 support_path         : false
```

### Making secure calls using SRTP

O protocolo responsável pela criptografia de mídia é o Secure Real Time Protocol (SRTP) definido na RFC3711. Uma das limitações do protocolo é a falta de um método padronizado para troca de chaves. Asterisk usa troca de chaves SDES sobre o protocolo SDP protegido pela criptografia de sinalização fornecida pelo TLS. Também existem outros métodos, como MIKEY e ZRTP. O ZRTP, desenvolvido por Philipp Zimmermann, está entre os métodos mais sofisticados para troca de chaves e criptografia de mídia. Alguns softphones e hard phones suportam ZRTP. No entanto, a forma padrão ainda é o SDES e você encontrará esse método em quase qualquer telefone disponível no mercado. Abaixo, um exemplo de uma solicitação com as chaves de criptografia definidas no SDP nas linhas a=crypto:1 e a=crypto:2.

```
INVITE sip:8000@192.168.1.237 SIP/2.0
Via:
SIP/2.0/tls
192.168.1.192:65525;rport;branch=z9hG4bKPj9fa224a14b17488ea15625ead833ea3a
Max-Forwards: 70
From:
"Flavio"
<sip:flavio@192.168.1.237>;tag=35afe6cc11274934867b24e43c805638
To: <sip:8000@192.168.1.237>
Contact: <sip:pyhkxnjz@192.168.1.192:65524;transport=tls>
Call-ID: 530a339c72af47f0a76e7ecb2a58ac43
CSeq: 5669 INVITE
Allow: SUBSCRIBE, NOTIFY, PRACK, INVITE, ACK, BYE, CANCEL, UPDATE, MESSAGE
Supported: 100rel
User-Agent: Blink 0.2.5 (Windows)
Authorization: Digest username="flavio", realm="asterisk", nonce="72ff51ad",
uri="sip:8000@192.168.1.237",
response="ba8c10672751baa7007d82eb34e2340e",
algorithm=MD5
Content-Type: application/sdp
Content-Length: 544
v=0
o=- 3509174186 3509174186 IN IP4 192.168.1.192
s=Blink 0.2.5 (Windows)
c=IN IP4 192.168.1.192
t=0 0
m=audio 50004 RTP/SAVP 9 104 103 102 0 8 101
a=rtcp:50005
a=rtpmap:9 G722/8000
a=rtpmap:104 speex/32000
a=rtpmap:103 speex/16000
a=rtpmap:102 speex/8000
a=rtpmap:0 PCMU/8000
a=rtpmap:8 PCMA/8000
a=rtpmap:101 telephone-event/8000
a=fmtp:101 0-15
a=crypto:1
AES_CM_128_HMAC_SHA1_80
inline:WrtZH82ztz93albRNT8o+oMcK9GvlAHRoaR1STvJ
a=crypto:2
AES_CM_128_HMAC_SHA1_32
inline:4Ma9jJOCEEGMPzzkmgyf6ttp1qhN16yumdXB7eRv
a=sendrecv
```

#### Configurando SRTP no Asterisk

Para configurar SRTP no Asterisk é muito simples. Defina `media_encryption=sdes` no endpoint; você também pode exigí‑lo com `media_encryption_optimistic=no` para que mídia não criptografada seja rejeitada em vez de ser permitida silenciosamente. Observe que SDES requer que a sinalização rode sobre TLS, de modo que as chaves não sejam enviadas em texto claro.

**Step 1.** configuração do Asterisk

Defina o seguinte na seção `type=endpoint` em `pjsip.conf`:

```
[blink]
type=endpoint
aors=blink
auth=blink
context=from-internal
disallow=all
allow=ulaw
transport=transport-tls
media_encryption=sdes
media_encryption_optimistic=no
```

**Step 2.** Configuração do softphone

No softphone, habilite SRTP para a mídia da conta (defina a opção **SRTP (Media Encryption)** como *Mandatory*) para que a voz seja criptografada.

![As configurações da conta SipPulse Softphone (seção inferior) — defina **Transport** para TLS e **SRTP (Media Encryption)** para *Mandatory* para que sinalização e mídia sejam ambas criptografadas.](../images/softphone/sipphone-config.png){width=35%}

## Habilitando autenticação de dois fatores para chamadas internacionais

Às vezes, a melhor solução é não ter rotas internacionais. Contudo, se realmente for necessário discar para o exterior, use uma senha extra. Vamos usar a aplicação do Asterisk **vmauthenticate** para solicitar a senha do correio de voz antes de discar internacionalmente. Isso é configurado no dialplan no **extensions.conf**. Veja o exemplo abaixo. Assim, um invasor, mesmo após descobrir a senha de um peer ou comprometer um telefone, ainda precisará da senha do correio de voz para discar para esse destino.

```
exten=_9011.,1,Playback(pleasedialyourvmpassword)
exten=_9011.,2,VMAuthenticate(${CALLERID(num)}@default,s)
exten=_9011.,3,Dial(PJSIP/${EXTEN:1}@my_trunk,20,tT)
exten=_9011.,4,Hangup()
```

`VMAuthenticate` ainda é uma aplicação padrão no Asterisk 22. O `Dial()` acima encaminha a chamada por um tronco SIP/PJSIP (`PJSIP/<number>@<trunk>`), que é como a maioria das instalações modernas acessa a PSTN — adapte o `my_trunk` ao nome do seu tronco e use o `DAHDI/g1/...` somente se você realmente possuir um span DAHDI. Defesa contra fraude de tarifas no dialplan — um segundo fator como este, combinado com a restrição de quais contexts podem alcançar suas rotas de saída e internacionais — continua sendo uma das proteções individuais mais importantes que você pode implantar.

## Summary

Neste capítulo você aprendeu sobre os riscos de ter um IP PBX conectado à Internet. Em seguida, aprendemos como proteger nosso PBX implementando uma política de segurança. Nessa política de segurança implementamos iptables, fail2ban, TLS, SRTP e autenticação de duas vias para chamadas internacionais. Espero que você tenha apreciado este capítulo.

## Quiz

1. Qual é a medida de mitigação mais importante contra Fraude de Compartilhamento de Receita na Internet?
   - A. Implementar SRTP
   - B. Manter o Asterisk atualizado
   - C. Implementar TLS
   - D. Usar senhas fortes
2. Fuzzing SIP é definido como:
   - A. Um ataque DoS usando solicitações e respostas malformadas
   - B. Roubo de serviço onde senhas são forçadas por força bruta
   - C. Interceptação de chamadas em andamento
   - D. Um DDoS com inundação de solicitações SIP
3. TFTPTheft ocorre quando o servidor fornece arquivos de configuração via TFTP. Você pode evitá‑lo usando:
   - A. FTP
   - B. HTTP
   - C. HTTPS com nome de usuário e senha
   - D. SCP
4. Ataques man‑in‑the‑middle utilizam uma técnica chamada:
   - A. TFTP theft
   - B. ARP spoofing
   - C. MAC poisoning
   - D. dsniff
5. Para SRTP, o Asterisk usa o seguinte sistema para troca de chaves:
   - A. MIKEY
   - B. SDES
   - C. ZRTP
   - D. Pluto
6. O utilitário que gera a autoridade certificadora e os certificados, encontrado em `/usr/src/asterisk-22.x.y/contrib/scripts`, é:
   - A. ast_tls_cert
   - B. gen_tls
   - C. gen_ast_tls
   - D. tls_generator
7. Estratégias válidas para prevenir interceptação (marque todas que se aplicam):
   - A. Implementar detectores analógicos de interceptação
   - B. Usar o utilitário ARPwatch para detectar ARP spoofing
   - C. Habilitar detecção de ARP‑spoofing nos switches
   - D. Usar SRTP
8. O Asterisk oferece autenticação forte verificando certificados de cliente. (O transporte TLS do PJSIP pode exigir e verificar o certificado do cliente.)
   - A. Verdadeiro
   - B. Falso
9. No Asterisk 22, qual configuração de endpoint PJSIP ativa a criptografia de mídia SRTP usando chaves in‑SDP (SDES)?
   - A. `encryption=yes`
   - B. `media_encryption=sdes`
   - C. `srtp=mandatory`
   - D. `transport=tls`
10. No Asterisk 22, o Fail2Ban deve ler eventos de falha de autenticação do PJSIP a partir do canal de logger dedicado ________ (habilitado em `logger.conf`).
   - A. `console`
   - B. `messages`
   - C. `security`
   - D. `verbose`

**Answers:** 1 — D · 2 — A · 3 — C · 4 — B · 5 — B · 6 — A · 7 — B, C, D · 8 — A · 9 — B · 10 — C
