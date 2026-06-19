# Part II — Channels & Connectivity {.unnumbered}

第二部分主要介绍呼叫如何进入和离开 Asterisk。我们首先围绕它设计 VoIP 网络——包括 codec、带宽和 NAT——然后深入研究 SIP 及其现代的 PJSIP 实现，因为 PJSIP 是 Asterisk 22 中唯一的 SIP 通道。

在此基础上，我们将添加实际部署所需的连接：通过 WebRTC 实现浏览器呼叫，通过 trunk 和 DID 连接 PSTN 及您的服务提供商，以及您在现场可能仍会遇到的传统模拟、数字 (TDM) 和 IAX2 通道。读完本部分，您将能够将 Asterisk 连接到电话、浏览器、运营商以及各种旧式设备。
