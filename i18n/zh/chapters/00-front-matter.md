```{=latex}
\frontmatter
```

## 版权 {.unnumbered}

*Asterisk Guide* — 第二版 (Asterisk 22 LTS)

版权所有 © 2006–2026 Flavio E. Gonçalves。保留所有权利。

未经作者事先书面同意，不得以任何形式或任何手段复制、存储于检索系统或传播本书的任何部分，出版评论中引用的简短摘录除外。

**版本：** 第二版。
**ISBN：** *待分配。*

> **[2nd-ed note]** 为第二版分配一个**新 ISBN** — 不要重复使用第一版的 ISBN (9781796396973)。同时在此处设置出版日期。

制造商和销售商用于区分其产品的许多名称均被声明为商标。在本书中出现这些名称且作者知晓商标声明的情况下，它们均以大写或首字母大写形式印刷。Asterisk、Digium、IAX 和 DUNDi 是 Sangoma Technologies 的商标（Digium 于 2018 年被 Sangoma 收购；Asterisk 现由 Sangoma 赞助）。

尽管在编写本书时已采取一切预防措施，但作者对错误或遗漏，或因使用此处包含的信息而导致的损害不承担任何责任。

## 前言 {.unnumbered}

本书旨在帮助任何想要学习如何安装和配置基于 Asterisk 22 LTS 的 PBX（专用分组交换机）的读者。Asterisk 是一个开源电话平台，连接了 VoIP 和传统的 TDM 通道。

这是本书的第五代版本，本书最初名为 *Asterisk Configuration Guide*。这些材料源于我 2006 年为准备 Digium dCAP 认证所做的工作（我一次性通过了该认证），自那时起，这些内容已被教授给超过一千名学生。

开源 PBX 的概念具有革命性。几十年来，电话行业一直被少数几家销售昂贵专有系统的公司所垄断。Asterisk 将这种权力交还给了用户：曾经在经济上遥不可及的功能——CTI（计算机电话集成）、IVR（交互式语音应答）、ACD（自动呼叫分配）、voicemail 等——现在任何拥有 Linux 机器并愿意学习的人都可以使用。

本书本身不会让你成为大师——没有任何书能做到这一点——但读完本书后，你将能够构建和操作一个具有高级功能的真实 PBX。本书配有配套的实践实验室和在线课程——**VoIP School Blackbelt** (<https://voip.school>)。

## 读者对象 {.unnumbered}

本书面向 Asterisk 的初学者。我假设你熟悉 Linux——包括 shell、文本编辑器和基本的系统管理。如果你在学习过程中觉得方便，可以在 Linux 桌面版上跟随操作，虚拟机也适用于实验室环境（语音质量可能会稍差）。对于生产系统，我不建议在桌面环境或资源受限的虚拟机中运行 Asterisk。对 IP 网络、Voice over IP (VoIP) 和基本电话概念的了解将会有所帮助。

## 第二版的新内容 {.unnumbered}

第二版是针对 **Asterisk 22 LTS**（2024 年发布，支持至 2028 年 10 月）的全面现代化更新。主要变化如下：

- **PJSIP 是唯一的 SIP 通道。** `chan_sip`已在 Asterisk 21 中移除，在 22 中不存在。每个 SIP 示例现在都使用 PJSIP (`pjsip.conf`)；遗留的 `sip.conf` 材料仅作为迁移参考保留。
- **Sangoma 的管理。** Digium 于 2018 年被 Sangoma 收购；该项目现在由 Sangoma 开发和赞助，全书内容均反映了这一点。
- **三个新章节。** *WebRTC with Asterisk*（通过 WSS/DTLS-SRTP 的浏览器电话）、*SIP trunking, DID & the PSTN* 以及 *Deployment, monitoring & scaling*。
- **可复现的实验室。** 书中的每个配置和命令都已通过你可以自行运行的 Asterisk 22 Docker 实验室进行了验证。
- **现代化功能。** ConfBridge 取代了旧的 MeetMe 会议，引入了 ARI（与 AMI/AGI 并列），涵盖了 PJSIP Realtime (Sorcery)，并更新了安装、安全和 CDR 章节。
- **新的结构。** 本书现在分为四个部分——基础、通道与连接、dialplan 与呼叫功能、集成与运维。

## 关于作者 {.unnumbered}

Flavio E. Gonçalves 于 1966 年出生在巴西。自 1983 年获得第一台 PC 以来，他就对计算机产生了浓厚的兴趣，并于 1989 年获得了工程学位，专注于计算机辅助设计和制造。他是巴西 SipPulse 的首席执行官，该公司致力于 softswitch、SBC 和多租户 PBX。

在他的职业生涯中，他获得了众多认证——包括 Novell MCNE/MCNI、Microsoft MCSE/MCT、Cisco CCSP/CCNP/CCDP 和 Asterisk dCAP。他开始撰写关于开源软件的书籍，是因为他相信认证曾经教授材料的结构化方式是一种极好的学习方法，并且他利用超过 25 年的教学经验，从人们实际学习的角度而非纯粹的技术角度进行写作。

Flavio 是两个孩子的父亲，居住在世界上最美丽的地方之一——巴西弗洛里亚诺波利斯，他在那里度过冲浪和航海的闲暇时光。

## 反馈、致谢与培训 {.unnumbered}

我努力寻找并消除错误，但总会有一些遗漏。如果你发现任何错误，请告知我，我将予以处理。

本书也用作培训材料。如果你想在自己的培训中心使用它，或者参加配套的在线课程和实验室，请访问 **VoIP School Blackbelt** (<https://voip.school>) 或发送电子邮件至 <flavio@voip.school>。

**致谢。** 封面设计：Karla Braga。审校：Luis F. Gonçalves、Guilherme Goes (dCAP) 以及专业校对人员。我也要感谢多年来反馈意见塑造了这些材料的众多学生，以及支持我的家人。

```{=latex}
\cleardoublepage
```
