# PBX सुविधाओं का उपयोग

SIP सिस्टमों में, अधिकांश फ़ोन सुविधाएँ एंडपॉइंट में लागू की जाती हैं। विभिन्न SIP फ़ोन और निर्माताओं की मौजूदगी है, और इंटरऑपरेबिलिटी की गारंटी नहीं है। Asterisk विकास टीम ने PBX में अधिकांश सुविधाओं को लागू करने का अद्भुत काम किया है, जिससे Asterisk लगभग एंडपॉइंट से स्वतंत्र हो गया है। हालांकि, कभी‑कभी आप वही फ़ंक्शन फ़ोन और Asterisk दोनों द्वारा किया जाता हुआ पाएँगे। फ़ोन और PBX का एकीकरण उपयोगिता का अगला चरण है और वर्तमान में प्रोपायटरी सिस्टम इसी पर ध्यान केंद्रित कर रहे हैं। इस अध्याय में, आप इन अधिकांश सुविधाओं का उपयोग कैसे करें, सीखेंगे।

## उद्देश्य

By the end of this chapter, you will be able to understand and use:

- Call Parking
- Call Pickup
- Call Transfer
- Call Conference (ConfBridge)
- Call Recording
- Music on hold

## जहाँ सुविधाएँ लागू की जाती हैं

सबसे पहले, यह समझना महत्वपूर्ण है कि PBX सुविधाएँ कब निष्पादित हो रही हैं और फोन कब सभी कार्य कर रहा है। उदाहरण के लिए, आप कॉल को फोन पर TRANSFER बटन का उपयोग करके या # डायल करके ट्रांसफ़र कर सकते हैं (अशर्त ट्रांसफ़र जो PBX स्वयं द्वारा निष्पादित होता है)।

## Asterisk द्वारा लागू की गई सुविधाएँ

- म्यूजिक ऑन होल्ड
- कॉल पार्किंग
- कॉल पिकअप
- कॉल रिकॉर्डिंग
- ConfBridge कॉन्फ्रेंस रूम
- कॉल ट्रांसफर (ब्लाइंड और कंसल्टेटिव)

## डायल प्लान द्वारा सामान्यतः लागू की जाने वाली सुविधाएँ

These features need to be programmed in the Asterisk dial plan (extensions.conf):

- व्यस्त होने पर कॉल फ़ॉरवर्ड
- तुरंत कॉल फ़ॉरवर्ड
- अनुत्तरित कॉल फ़ॉरवर्ड
- कॉल फ़िल्टरिंग (ब्लैकलिस्ट)
- डू नॉट डिस्ट्रब (Do not disturb)
- रीडायल

## फ़ोन द्वारा आमतौर पर लागू की जाने वाली सुविधाएँ

ये सुविधाएँ फ़ोन के फ़र्मवेयर द्वारा लागू की जाती हैं:

![PBX सुविधाएँ आमतौर पर कहाँ लागू की जाती हैं: Asterisk में स्वयं, डायल प्लान में, या फ़ोन में](../images/13-pbx-features-fig01.png)

- कॉल ऑन होल्ड
- ब्लाइंड ट्रांसफ़र
- कंसल्टेटिव ट्रांसफ़र
- थ्री‑वे कॉन्फ़्रेंस
- मैसेज वेटिंग इंडिकेटर

## The features configuration file

इस अध्याय में प्रस्तुत कुछ सुविधाओं को features.conf कॉन्फ़िगरेशन फ़ाइल में कॉन्फ़िगर किया जाता है। इस फ़ाइल को संशोधित करके कुछ सुविधाओं के व्यवहार को बदलना संभव है। हमने नीचे संबंधित अंश शामिल किया है। इस अध्याय के अगले भागों में हम प्रत्येक सुविधा का विवरण देंगे। नमूना फ़ाइल से अंश (Asterisk 22)

![The `[featuremap]` section of features.conf, with the default DTMF feature codes](../images/13-pbx-features-fig02.png)

Asterisk 12 से, कॉल पार्किंग को `features.conf` से बाहर निकालकर अपना स्वयं का मॉड्यूल `res_parking` में ले जाया गया, जिसका कॉन्फ़िगरेशन `res_parking.conf` में है। नीचे दिया गया parking-lot ब्लॉक (`parkext`, `parkpos`, `context`, `parkingtime`, आदि) `res_parking.conf` में स्थित है। `[featuremap]` सेक्शन (DTMF फीचर कोड, जिसमें `parkcall` शामिल है) अभी भी `features.conf` में रहता है।

parking-lot विकल्प `res_parking.conf` में स्थित हैं। एक parking lot जिसका नाम `default` है, हमेशा मौजूद रहता है, चाहे वह कॉन्फ़िगरेशन फ़ाइल में न हो। नीचे दिया गया अंश Asterisk 22 `res_parking.conf.sample` से लिया गया है:

```
; res_parking.conf
[default]                       ; Default Parking Lot
parkext => 700                  ; What extension to dial to park. (optional; if
                                ; specified, extensions will be created for parkext and
                                ; the whole range of parkpos)
parkpos => 701-720              ; What range of parking spaces to use - must be numeric.
                                ; Creates these spaces as extensions if parkext is set.
context => parkedcalls          ; Which context parked calls and the default park
                                ; extension are created in
;parkingtime => 45             ; Number of seconds a call can be parked before returning
;comebacktoorigin = yes        ; When a parked call times out, attempt to send it back to
                               ; the peer that parked it (default is yes)
;courtesytone = beep           ; Sound file to play when someone picks up a parked call
;parkedplay = caller           ; Who to play courtesytone to: parked, caller, both (default caller)
;parkedcalltransfers = caller  ; Enable DTMF transfers when picking up a parked call (default no)
;parkedcallreparking = caller  ; Enable DTMF parking when picking up a parked call (default no)
;parkedcallhangup = caller     ; Enable DTMF hangups when picking up a parked call (default no)
;findslot => next              ; 'next' uses the next space after the most recently used one;
                               ; 'first' (default) uses the lowest-numbered space available
;parkedmusicclass = default    ; MOH class to use for the parked channel
```

DTMF फीचर कोड (जिसमें एक‑स्टेप `parkcall` भी शामिल है) `[featuremap]` सेक्शन में `features.conf` में रहते हैं:

```
; features.conf
[featuremap]
;blindxfer => #1                ; Blind transfer  (default is #) -- Make sure to set the T and/or t option in the Dial() or Queue() app call!
;disconnect => *0               ; Disconnect  (default is *) -- Make sure to set the H and/or h option in the Dial() or Queue() app call!
;atxfer => *2                   ; Attended transfer  -- Make sure to set the T and/or t option in the Dial() or Queue()  app call!
;parkcall => #72                ; Park call (one step parking)  -- Make sure to set the K and/or k option in the Dial() app call!
;automixmon => *3               ; One Touch Record a.k.a. Touch MixMonitor -- Make sure to set the X and/or x option in the Dial() or Queue() app call!
```

## कॉल ट्रांसफ़र

कॉल ट्रांसफ़र को फ़ोन, ATA, या स्वयं Asterisk द्वारा लागू किया जा सकता है। कॉल ट्रांसफ़र कैसे किया जाता है, यह समझने के लिए अपने फ़ोन मैनुअल को देखें। यदि आपका फ़ोन कॉल ट्रांसफ़र का समर्थन नहीं करता है, तो आप यह कार्य Asterisk के माध्यम से कर सकते हैं। कॉल ट्रांसफ़र दो अलग-अलग तरीकों से लागू किया जाता है।

पहला तरीका ब्लाइंड ट्रांसफ़र फीचर का उपयोग करना है: ट्रांसफ़र करने वाले नंबर से पहले # डायल करें। कभी‑कभी आप अपने IP फ़ोन या IP सॉफ़्टफ़ोन की ट्रांसफ़र सुविधा का उपयोग करेंगे। आप features.conf फ़ाइल में blindxfer पैरामीटर को संपादित करके ट्रांसफ़र कैरेक्टर बदल सकते हैं।

आप features.conf फ़ाइल में atxfer पैरामीटर से पहले के ; को हटाकर Asterisk में असिस्टेड ट्रांसफ़र सक्षम कर सकते हैं। बातचीत के दौरान, आप *2 दबाएँगे। Asterisk "transfer" कहेगा और आपको डायल टोन देगा। कॉलर को म्यूज़िक ऑन होल्ड पर भेज दिया जाता है। गंतव्य व्यक्ति से बात करने और फ़ोन बंद करने के बाद, सिस्टम कॉलर को गंतव्य से जोड़ देता है।

![कॉल ट्रांसफ़र: ब्लाइंड ट्रांसफ़र (कॉल के दौरान # दबाएँ) और अटेंडेड ट्रांसफ़र (press *2) के चरण](../images/13-pbx-features-fig03.png)

### कॉन्फ़िगरेशन कार्य सूची

1. एक PJSIP एंडपॉइंट के लिए, सुनिश्चित करें कि विकल्प `direct_media` को `no` पर सेट किया गया है (ताकि मीडिया Asterisk के माध्यम से प्रवाहित हो और फीचर कोड पहचाने जाएँ), या `Dial()` एप्लिकेशन में `t`/`T` विकल्प का उपयोग करें

## Call parking

यह सुविधा कॉल को पार्क करने के लिए उपयोग की जाती है। यह मदद करता है, उदाहरण के लिए, जब आप अपने कमरे के बाहर फोन कॉल का उत्तर दे रहे हों और आप कॉल को वापस अपनी डेस्क पर ट्रांसफ़र करना चाहते हों। आप इसे एक एक्सटेंशन में कॉल को पार्क करके पूरा कर सकते हैं। एक बार जब आप अपनी डेस्क पर पहुँचें, तो बस पार्किंग एक्सटेंशन का नंबर डायल करके कॉल को पुनः प्राप्त करें।

![Call parking: dial 700 to park a call into the first free slot (701–720); Asterisk announces the slot, which you dial from any phone to retrieve the call](../images/13-pbx-features-fig04.png)

डिफ़ॉल्ट रूप से, कॉल को पार्क करने के लिए 700 एक्सटेंशन का उपयोग किया जाता है। बातचीत के बीच में, कॉल को 700 एक्सटेंशन पर ट्रांसफ़र करने के लिए # दबाएँ। अब Asterisk आपका पार्किंग एक्सटेंशन, जैसे 701 या 702, की घोषणा करेगा। फोन को हैंग अप करें, और कॉलर होल्ड पर रखा जाएगा। अपनी डेस्क फ़ोन पर जाएँ और घोषित पार्किंग एक्सटेंशन डायल करके कॉल को पुनः प्राप्त करें। यदि कॉलर को लंबे समय तक पार्क किया जाता है, तो टाइमआउट सुविधा सक्रिय होगी और मूल डायल किया गया एक्सटेंशन फिर से बजना शुरू हो जाएगा।

### Configuration task list

पार्किंग सुविधा को सक्षम करने के लिए नीचे दिए गए चरणों का पालन करें। चरण 1: अपने डायलप्लान से पार्किंग लॉट को पहुँच योग्य बनाएँ (आवश्यक)। डिफ़ॉल्ट पार्किंग लॉट का `context` `parkedcalls` (`res_parking.conf` में सेट) है। उस कॉन्टेक्स्ट को उस कॉन्टेक्स्ट में शामिल करें जिससे आपके फ़ोन डायल करते हैं, `extensions.conf` में:

```
include => parkedcalls
```

चरण 2: #700 डायल करके कॉल पार्किंग सुविधा का परीक्षण करें। नोट्स:

- पार्किंग एक्सटेंशन डायलप्लान शो CLI कमांड में नहीं दिखेगा।
- पार्किंग कॉन्फ़िगरेशन फ़ाइल बदलने के बाद पार्किंग मॉड्यूल को रीलोड करना आवश्यक है: `module reload res_parking.so`। features.conf में बदलावों के लिए, `module reload features.so`।
- कॉल को पार्क करने के लिए, आपको #700 पर ट्रांसफ़र करना होगा। `Dial()` एप्लिकेशन में `t` और `T` विकल्पों की जाँच करें।

## Call pickup

Call pickup allows you to capture a call from a colleague in the same call group. This would help avoid, for example, having to wake up to take a call that is ringing to another person in your room, but who is not present. By dialing *8, you can capture a call within your call group. This number can be modified in the `features.conf` file.

![कॉल पिकअप: सदस्य केवल अपने समूह के भीतर कॉल को पकड़ सकते हैं; ऑपरेटर (pickupgroup=1,2,3) हर समूह से कॉल को पिकअप कर सकता है](../images/13-pbx-features-fig05.png)

### Configuration task list

Follow the steps below to configure the call pickup feature. Step 1: Configure a call group for your extensions. This is done in the channel configuration file (pjsip.conf, iax.conf, chan_dahdi.conf). For PJSIP endpoints, set `call_group` and `pickup_group` in the endpoint section of `pjsip.conf` (pjsip.conf uses snake_case option names). This task is required.

For PJSIP (pjsip.conf):
```
[4x00]
type=endpoint
call_group=1
pickup_group=1,2
```


Step 2: Change the call-pickup feature number (optional). This is set in the `[general]` section of `features.conf`, not in `pjsip.conf`:

```
; features.conf
[general]
pickupexten = *8   ; Configures the call pickup extension (default is *8)
```

## Conference (call conference)

Asterisk पर कॉन्फ़्रेंस लागू करने के विभिन्न तरीके हैं। पहला विकल्प बस फोन की थ्री‑वे कॉन्फ़्रेंस क्षमता का उपयोग करना है। फोन में इस सुविधा का उपयोग करके आपको सर्वर में किसी भी समर्थन की आवश्यकता नहीं होती। हालांकि, जब आप 3 से अधिक लोगों के साथ कॉन्फ़्रेंस चाहते हैं, तो आपको एक कॉन्फ़्रेंस रूम चलानी चाहिए। Asterisk का आधुनिक कॉन्फ़्रेंस एप्लिकेशन ConfBridge (`app_confbridge`) है।

ConfBridge HD आवाज़ कॉन्फ़्रेंस और वीडियो कॉन्फ़्रेंस दोनों को सपोर्ट करता है। वीडियो कॉन्फ़्रेंस के लिए कुछ सीमाएँ हैं जैसे कोई ट्रांसकोडिंग नहीं — सभी प्रतिभागियों को एक ही कोडेक और प्रोफ़ाइल का उपयोग करना होगा। वीडियो कॉन्फ़्रेंस फॉलो‑द‑टॉकर मोड का उपयोग करता है, जिसमें अंतिम बोलने वाले व्यक्ति की छवि प्रदर्शित होती है। आप आसानी से ConfBridge में नए DTMF मेनू कॉन्फ़िगर कर सकते हैं।

ConfBridge पुराने MeetMe एप्लिकेशन की जगह लेता है, जिसे Asterisk 19 में डिप्रिकेट किया गया था। MeetMe अभी भी Asterisk 22 स्रोत ट्री में मौजूद है, लेकिन यह DAHDI पर निर्भर करता है और डिफ़ॉल्ट रूप से बिल्ट नहीं होता, इसलिए सामान्य PJSIP इंस्टॉल पर यह उपलब्ध नहीं है — ConfBridge समर्थित कॉन्फ़्रेंस एप्लिकेशन है। MeetMe के विपरीत, ConfBridge **DAHDI** या किसी हार्डवेयर टाइमिंग स्रोत की आवश्यकता नहीं रखता: यह Asterisk के बिल्ट‑इन टाइमिंग इंटरफ़ेस (`res_timing_timerfd` on Linux, या `res_timing_pthread`) पर निर्भर करता है, इसलिए कोई `dahdi_dummy` मॉड्यूल आवश्यक नहीं है। यदि आप पुराने सिस्टम से माइग्रेट कर रहे हैं जो `MeetMe()` और `meetme.conf` का उपयोग करता था, तो नीचे वर्णित अनुसार उन्हें `ConfBridge()` और `confbridge.conf` से बदलें।

### ConfBridge

कॉन्फ़्रेंस रूम शुरू करने के लिए, सिंटैक्स नीचे सूचीबद्ध है।

```
ConfBridge(conference,bridge_profile,user_profile,menu)
```

To get a complete description of the command you can use core show application confbridge.

![Output of `core show application confbridge`, showing the synopsis, syntax, and the bridge_profile, user_profile, and menu arguments](../images/13-pbx-features-fig06.png)

![Several PJSIP endpoints join one named ConfBridge conference (101); one participant is the admin. The mixing and timing are handled by `app_confbridge` together with `bridge_softmix` and the built-in `res_timing_*` timer — no DAHDI required.](../images/13-pbx-features-fig09.png)

जैसा कि आप ऊपर देख सकते हैं, यहाँ तीन महत्वपूर्ण तर्क हैं, प्रत्येक `confbridge.conf` में एक सेक्शन प्रकार से मैप होते हैं। **bridge_profile** (एक `type=bridge` सेक्शन): यहाँ आप अधिकतम प्रतिभागियों की संख्या (`max_members`), रिकॉर्डिंग (`record_conference`), `video_mode`, और कई अन्य ब्रिज-व्यापी पैरामीटर चुनते हैं।

पूरे उदाहरण फ़ाइल को यहाँ दोहराना व्यावहारिक नहीं है, इसलिए मैं आपको एक सरल उदाहरण देता हूँ कि कैसे confbridge.conf फ़ाइल में bridge_profile को कॉन्फ़िगर किया जाता है।

```
[default_bridge]
type=bridge
max_members=10
record_conference=yes
```

**user_profile** (एक `type=user` सेक्शन): यहाँ आप उन विकल्पों को परिभाषित करते हैं जो प्रत्येक उपयोगकर्ता के लिए विशिष्ट होते हैं, जैसे कि उपयोगकर्ता व्यवस्थापक है या नहीं (`admin=yes`), क्या वह म्यूटेड शुरू होता है (`startmuted=yes`), म्यूजिक ऑन होल्ड, और कई अन्य उपयोगकर्ता‑विशिष्ट विकल्प। उदाहरण:

```
[admin_user]
type=user
admin=yes
```

**menu** (एक `type=menu` सेक्शन): यहाँ आप कॉन्फ्रेंस के लिए कीपैड (DTMF) मैपिंग परिभाषित करते हैं — उदाहरण के लिए कौन सी कुंजी म्यूट टॉगल करती है, वॉल्यूम समायोजित करती है, या कॉन्फ्रेंस छोड़ती है। सभी उपलब्ध क्रियाओं को देखने के लिए `confbridge.conf.sample` फ़ाइल देखें। उदाहरण:

```
[my_menu]
type=menu
*=playback_and_continue
1=toggle_mute
2=decrease_listening_volume
3=increase_listening_volume
4=decrease_talking_volume
5=increase_talking_volume
6=leave_conference
```

#### Confbridge functions

कॉन्फ्रेंस ब्रिज विकल्पों को डायाल प्लान में CONFBRIDGE() फ़ंक्शन का उपयोग करके डायनामिक रूप से पास किया जा सकता है। नीचे दिए गए उदाहरण देखें:

```
exten => 1,1,Answer()
exten => 1,n,Set(CONFBRIDGE(user,template)=default_user)
exten => 1,n,Set(CONFBRIDGE(user,admin)=yes)
exten => 1,n,Set(CONFBRIDGE(user,marked)=yes)
exten => 1,n,ConfBridge(sales)
```

### ConfBridge admin commands and migrating from MeetMe

यदि आप MeetMe से आ रहे हैं, तो वह प्रशासनिक कार्य जो आप `MeetMeAdmin()` और `a` (admin) विकल्प के माध्यम से उपयोग करते थे, अब **admin user profile** (`admin=yes`) तथा **menu** क्रियाओं के द्वारा व्यक्त किए जाते हैं। एक प्रशासक जो admin प्रोफ़ाइल और admin क्रियाओं वाला मेन्यू लेकर जुड़ता है, वह कीपैड से रूम को लॉक कर सकता है, उपयोगकर्ताओं को किक कर सकता है, और प्रतिभागियों को लाइव म्यूट कर सकता है। `confbridge.conf` में संबंधित मेन्यू क्रियाएँ हैं:

- `admin_kick_last` -- वह अंतिम उपयोगकर्ता किक करें जिसने जुड़ा था
- `admin_toggle_mute_participants` -- सभी गैर‑admin प्रतिभागियों को म्यूट/अनम्यूट करें
- `toggle_mute` -- स्वयं को म्यूट/अनम्यूट करें
- `participant_count` -- प्रतिभागियों की संख्या की घोषणा करें
- `leave_conference` -- ब्रिज से बाहर निकलें और डायलप्लान में जारी रखें

ये MeetMe `MeetMe()` विकल्प फ़्लैग्स (`a`, `A`, `m`, `M`, `l`, `x`, …) और `MeetMeAdmin()` कमांड्स (`k`, `K`, `L`, `M`, `N`, …) की जगह लेते हैं। एक आधुनिक PJSIP इंस्टॉल में आप `app_meetme` को बिल्कुल भी लोड नहीं करेंगे; सभी कॉन्फ़्रेंस कॉन्फ़िगरेशन `confbridge.conf` में रहती है, और परिवर्तन `module reload app_confbridge.so` के साथ लागू होते हैं (ConfBridge लॉजिक `app_confbridge` में रहता है; यहाँ कोई `res_confbridge` मॉड्यूल नहीं है)।

### ConfBridge example

एक कॉन्फ़्रेंस रूम बनाने के लिए जो एक्सटेंशन 500 पर पहुँचा जा सके, `extensions.conf` में:

```
exten => 500,1,Answer()
 same => n,ConfBridge(101,default_bridge,default_user,sample_user_menu)
```

पहला कॉलर जो 500 डायल करता है, सम्मेलन `101` बनाता है; बाद के कॉलर इसमें जुड़ते हैं। यहाँ संदर्भित प्रोफ़ाइल और मेनू (`default_bridge`, `default_user`, `sample_user_menu`) `confbridge.conf` में परिभाषित हैं। PIN की आवश्यकता के लिए, उपयोगकर्ता प्रोफ़ाइल में `pin=` सेट करें; किसी प्रतिभागी को सम्मेलन प्रशासक बनाने के लिए, उन्हें `admin=yes` वाली उपयोगकर्ता प्रोफ़ाइल दें।

## Call Recording

Asterisk में कॉल रिकॉर्ड करने के कई तरीके हैं। आप आसानी से कॉल रिकॉर्ड करने के लिए `MixMonitor()` एप्लिकेशन का उपयोग कर सकते हैं। (पुराना `Monitor` एप्लिकेशन, जो दो अलग फ़ाइलें रिकॉर्ड करता था, हटा दिया गया है; इसके बजाय `MixMonitor` का उपयोग करें।)

### Using the MixMonitor application

`MixMonitor` एप्लिकेशन वर्तमान चैनल की ऑडियो को निर्दिष्ट फ़ाइल में रिकॉर्ड करता है। यदि फ़ाइलनाम एक पूर्ण पथ है, तो वह उसी पथ का उपयोग करता है। अन्यथा, यह asterisk.conf में कॉन्फ़िगर की गई मॉनिटरिंग डायरेक्टरी में फ़ाइल बनाता है।

![The MixMonitor() application: records and mixes the audio of a channel to a file, with options for append, bridged-only, and volume adjustment](../images/13-pbx-features-fig09.png)

### MixMonitor()

कॉल रिकॉर्ड करें और रिकॉर्डिंग के दौरान ऑडियो को मिक्स करें। सिंटैक्स: `MixMonitor(filename.extension[,options[,command]])`। वर्तमान चैनल की ऑडियो को निर्दिष्ट फ़ाइल में रिकॉर्ड करता है। वैध विकल्प:

- a - फ़ाइल को ओवरराइट करने के बजाय उसमें जोड़ता है।
- b - केवल तब ऑडियो को फ़ाइल में सहेजता है जब चैनल ब्रिज्ड हो।
- Note: कॉन्फ्रेंस को शामिल नहीं करता।
- v(<x>) - सुनाई देने वाले वॉल्यूम को <x> गुणक से समायोजित करता है (रेंज -4 से 4)
- V(<x>) - बोले गए वॉल्यूम को <x> गुणक से समायोजित करता है (रेंज -4 से 4)
- W(<x>) - सुनाई देने वाले और बोले गए दोनों वॉल्यूम को <x> गुणक से समायोजित करता है (रेंज -4 से 4)
- <command> रिकॉर्डिंग समाप्त होने पर निष्पादित किया जाएगा। कोई भी स्ट्रिंग जो ^{X} से मेल खाती है, उसे ${X} में अनएस्केप किया जाएगा और सभी वेरिएबल्स उस समय मूल्यांकित किए जाएंगे। वेरिएबल MIXMONITOR_FILENAME में उपयोग की गई फ़ाइलनाम होगी।

एक रोचक संसाधन एक-टच रिकॉर्डिंग फीचर `automixmon` है, जो कॉल के दौरान एक पार्टी को DTMF कोड डायल करने देता है (`features.conf` नमूना `*3` सुझाता है; कोई बिल्ट‑इन डिफ़ॉल्ट नहीं है, इसलिए आपको इसे सेट करना होगा) ताकि तुरंत रिकॉर्डिंग शुरू (और बंद) की जा सके। यह MixMonitor पर आधारित है, इसलिए यह एक ही मिश्रित फ़ाइल लिखता है। Example:

```
exten => _4XXX,1,Set(DYNAMIC_FEATURES=automixmon)
 same => n,Dial(PJSIP/${EXTEN},20,jtTXx) ; X and x enable one-touch MixMonitor recording
```

The `X` और `x` विकल्प क्रमशः कॉलर और कैल्ली के लिए वन‑टच MixMonitor सुविधा को सक्षम करते हैं। क्योंकि MixMonitor एक ही मिश्रित फ़ाइल रिकॉर्ड करता है, बाद में अलग‑अलग IN/OUT फ़ाइलों को मिलाने की आवश्यकता नहीं रहती (पुराना `automon`/`Monitor` तरीका, जो `soxmix` के लिए दो फ़ाइलें बनाता था, `Monitor` एप्लिकेशन के साथ हटा दिया गया था)।

यदि आप Dial() एप्लिकेशन से पहले Set() का उपयोग नहीं करना चाहते, तो आप इसे globals सेक्शन में सेट कर सकते हैं:

```
[globals]
DYNAMIC_FEATURES=automixmon
```

### Music on hold

Music on hold (MOH) ने संस्करण 1.0, 1.2, और 1.4 के बीच कई बार परिवर्तन किया है। नवीनतम संस्करण में, MOH का डिफ़ॉल्ट "FILE-BASED" है। दूसरे शब्दों में, Asterisk MOH फ़ाइलें g729, alaw, ulaw, और gsm जैसे फ़ॉर्मेट में प्रदान करेगा। इसलिए, चैनल को संगीत भेजने से पहले उसे ट्रांसकोड करने की आवश्यकता नहीं है। यह प्रोसेसर समय बचाता है, जो उत्पादन सिस्टम पर काम करने वालों के लिए एक स्वागत योग्य परिवर्तन है।

पुराने संस्करणों में, MOH आमतौर पर MP3 द्वारा प्रदान किया जाता था (इसे अभी भी इस तरह कॉन्फ़िगर किया जा सकता है)। MP3 का उपयोग करके MOH प्रदान करने से Asterisk को ट्रांसकोड करना पड़ता है, जिससे प्रक्रिया में मूल्यवान CPU शक्ति खर्च होती है।

नया कॉन्फ़िगरेशन फ़ाइल नीचे दिखाया गया है। ध्यान दें कि डिफ़ॉल्ट क्लास अब नेेटिव फ़ाइल फ़ॉर्मेट mode=files का उपयोग करती है। अन्य सभी मोड्स टिप्पणी किए गए हैं। प्रत्येक सेक्शन एक क्लास है। इस बिंदु पर केवल अनकमेंटेड क्लास डिफ़ॉल्ट है। यदि आप विभिन्न फ़ाइलों के लिए अलग-अलग क्लासेज़ चाहते हैं, तो आपको नई सेक्शन (क्लासेज़) बनानी होंगी।

![The musiconhold.conf sample configuration, listing the valid MOH modes (quietmp3, mp3, custom, files, …)](../images/13-pbx-features-fig10.png)

```
; Music on Hold -- Sample Configuration
;[samplemp3]
;mode=quietmp3
;directory=/var/lib/asterisk/mohmp3
;
; valid mode options:
; quietmp3      -- default
; mp3           -- loud
; mp3nb         -- unbuffered
; quietmp3nb    -- quiet unbuffered
; custom        -- run a custom application (See examples below)
; files         -- read files from a directory in any Asterisk supported
;                  media format. (See examples below)
;[manual]
;mode=custom
; Note that with mode=custom, a directory is not required, such as when reading
; from a stream.
;directory=/var/lib/asterisk/mohmp3
;application=/usr/bin/mpg123 -q -r 8000 -f 8192 -b 2048 --mono -s
;[ulawstream]
;mode=custom
;application=/usr/bin/streamplayer 192.168.100.52 888
;format=ulaw
; mpg123 on Solaris does not always exit properly; madplay may be a better
; choice
;[solaris]
;mode=custom
;directory=/var/lib/asterisk/mohmp3
;application=/site/sw/bin/madplay -Q -o raw:- --mono -R 8000 -a -12
;
;
; File-based (native) music on hold
;
; This plays files directly from the specified directory, no external
; processes are required. Files are played in normal sorting order
; (same as a sorted directory listing), and no volume or other
; sound adjustments are available. If the file is available in
; the same format as the channel's codec, then it will be played
; without transcoding (same as Playback would do in the dialplan).
; Files can be present in as many formats as you wish, and the
; 'best' format will be chosen at playback time.
;
; NOTE:
; If you are not using "autoload" in modules.conf, then you
; must ensure that the format modules for any formats you wish
; to use are loaded _before_ res_musiconhold. If you do not do
; this, res_musiconhold will skip the files it is not able to
; understand when it loads.
;
[default]
mode=files
directory=/var/lib/asterisk/moh
;
;[native-random]
;mode=files
;directory=/var/lib/asterisk/moh
;random=yes     ; Play the files in a random order
```

### MOH configuration tasks

अब, music on hold का उपयोग करने के लिए, चैनल कॉन्फ़िगरेशन फ़ाइलों (chan_dahdi.conf, pjsip.conf, iax.conf, आदि) में MOH क्लास सेट करें। PJSIP endpoints के लिए, `moh_suggest` को `pjsip.conf` के endpoint सेक्शन में सेट करें (लेगेसी `musicclass` विकल्प नाम chan_dahdi और अन्य चैनल ड्राइवरों पर लागू होता है, PJSIP पर नहीं)। स्थापित freeplay ट्यून अब wav फ़ॉर्मेट में हैं। इंस्टॉलेशन के समय, आप उपलब्ध MOH फ़ाइल फ़ॉर्मेट (make menuselect का उपयोग करके) चुन सकते हैं। यदि आप नए MOH फ़ाइलें जोड़ना चाहते हैं, तो आपको उन्हें आवश्यक फ़ॉर्मेट में प्रदान करना होगा। उदाहरण के लिए:

`/etc/asterisk/chan_dahdi.conf` में, `musiconhold` लाइन जोड़ें।

```
[channels]
musiconhold=default
```

फिर `/etc/asterisk/musiconhold.conf` को संपादित करके उस क्लास को परिभाषित करें:

```
[default]
mode=files
directory=/var/lib/asterisk/moh
```

डायल प्लान में, आप एक चैनल पर `StartMusicOnHold` के साथ होल्ड संगीत शुरू कर सकते हैं (और इसे `StopMusicOnHold` से रोक सकते हैं):

```
exten => 100,1,StartMusicOnHold(default)
 same => n,Dial(PJSIP/2)
```

एक निश्चित समय के लिए होल्ड संगीत चलाने के लिए, एक त्वरित परीक्षण के रूप में, `MusicOnHold` एप्लिकेशन का उपयोग करें जिसमें अवधि (सेकंड में) हो:

```
[local]
exten => 6601,1,MusicOnHold(default,30)
```

## एप्लिकेशन मैप्स

एप्लिकेशन मैप्स आपको features.conf फ़ाइल के `[applicationmap]` सेक्शन का उपयोग करके नई सुविधाएँ जोड़ने की अनुमति देते हैं। मान लीजिए आपको यह पहचानना है कि आप कॉल सेंटर में किस प्रकार के ग्राहक का उत्तर दे रहे हैं। आप प्रत्येक ग्राहक प्रकार के लिए एक एप्लिकेशन मैप बना सकते हैं, जो प्रकार के अनुसार उत्तर दिए गए ग्राहकों की संख्या गिन सकेगा।

## Summary

इस अध्याय में आपने सीखा कि Asterisk के PBX फीचर कहाँ स्थित होते हैं — कुछ कोर में, कुछ डायल प्लान में, और कुछ फोन पर — और कैसे DTMF फीचर कोड `[featuremap]` सेक्शन में `features.conf` में मैप किए जाते हैं। आपने **call transfer** (blind और attended) और **call parking** (`res_parking.conf`, `k`/`K` Dial विकल्पों और `parkedcalls` सेट के साथ), **call pickup** by group, और **conferencing** को **ConfBridge** (`confbridge.conf` bridge/user/menu प्रोफ़ाइल) के साथ सेट किया, जो पुराने MeetMe की जगह लेता है। आपने **one-touch recording** को MixMonitor (`automixmon`, `X`/`x` Dial विकल्प, और `DYNAMIC_FEATURES`) के साथ सेट किया, **music on hold** को कॉन्फ़िगर किया, और देखा कि **application maps** आपको अपने डायलप्लान लॉजिक को DTMF सीक्वेंस से बाइंड करने की अनुमति देते हैं। इन बिल्डिंग ब्लॉक्स के साथ आप एक बिज़नेस PBX से उपयोगकर्ताओं की रोज़मर्रा की अपेक्षित सुविधाएँ प्रदान कर सकते हैं।

## Quiz

1. Which statements are true about call parking?
   - A. By default, extension 800 is used for call parking.
   - B. When you are away from your desk and receive a call, you can park it; the system announces the parking slot, and you dial that slot from any phone to retrieve the call.
   - C. By default, extension 700 parks a call, and calls are parked in slots 701–720.
   - D. You dial 700 to retrieve a parked call.
2. To use the call-pickup feature, all extensions must be in the same ___। For DAHDI channels this is configured in the ___ file.
3. When transferring a call you can choose between a ___ transfer, where the destination is not consulted first, and an ___ transfer, where you talk to the destination before completing it.
4. To make an attended (consultative) transfer you use the ___ sequence; for a blind transfer you use ___.
   - A. #1, *2
   - B. *2, #1
   - C. #2, #1
   - D. #1, #2
5. To host conference calls in Asterisk 22, you use the ___ application.
6. In ConfBridge, a participant is granted administrator privileges (kick, mute others, lock the room) by setting ___ in their user profile (`confbridge.conf`):
   - A. admin=yes
   - B. marked=yes
   - C. moderator=yes
   - D. type=admin
7. The best format for music on hold is MP3, because it uses very little processing power on the Asterisk server.
   - A. True
   - B. False
8. To pick up a call from a specific call group, you must be in the matching ___ group.
9. You can record a call with the MixMonitor() application or the one-touch recording (`automixmon`) feature. In the `features.conf` sample, `automixmon` is mapped to the ___ DTMF sequence.
   - A. *1
   - B. *2
   - C. *3
   - D. #1
10. In ConfBridge, which `confbridge.conf` user-profile option makes a participant join muted (they can hear the conference but cannot be heard until unmuted)?
    - A. startmuted=yes
    - B. listen=only
    - C. muteall=yes
    - D. quiet=yes

**Answers:** 1 — B, C · 2 — pickup group; `chan_dahdi.conf` · 3 — blind; attended · 4 — B · 5 — ConfBridge() · 6 — A · 7 — B · 8 — pickup · 9 — C · 10 — A
