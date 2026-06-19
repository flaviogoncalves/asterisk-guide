-- SPONSORED build only: drop a small sponsor credit at the opening of every numbered
-- chapter (right after the chapter title). Lab chapters credit their lab sponsor; all other
-- chapters credit the founding sponsor. Part dividers / front matter ({.unnumbered}) are skipped.
-- Runs AFTER strip-notes, so these credits are never mistaken for editorial notes.
-- The credit text is localized from the document language (meta.lang); the brand names
-- (SipPulse / voip.ms) and their links stay verbatim.

-- {founding-credit, lab-credit} per language; %s is where the linked brand name goes.
local STR = {
  en = { "This free edition is sponsored by %s.",
         "The SIP Trunking & DID labs in this chapter are sponsored by %s." },
  pt = { "Esta edição gratuita é patrocinada por %s.",
         "Os laboratórios de SIP Trunking e DID deste capítulo são patrocinados por %s." },
  es = { "Esta edición gratuita está patrocinada por %s.",
         "Los laboratorios de SIP Trunking y DID de este capítulo están patrocinados por %s." },
  fr = { "Cette édition gratuite est sponsorisée par %s.",
         "Les ateliers SIP Trunking et DID de ce chapitre sont sponsorisés par %s." },
  de = { "Diese kostenlose Ausgabe wird von %s gesponsert.",
         "Die SIP-Trunking- und DID-Labore in diesem Kapitel werden von %s gesponsert." },
  it = { "Questa edizione gratuita è sponsorizzata da %s.",
         "I laboratori di SIP Trunking e DID di questo capitolo sono sponsorizzati da %s." },
  hi = { "यह निःशुल्क संस्करण %s द्वारा प्रायोजित है।",
         "इस अध्याय की SIP Trunking और DID लैब %s द्वारा प्रायोजित हैं।" },
  zh = { "本免费版本由 %s 赞助。",
         "本章中的 SIP Trunking 和 DID 实验由 %s 赞助。" },
  ja = { "この無料版は %s のスポンサーによって提供されています。",
         "本章の SIP トランキングおよび DID ラボは %s のスポンサーによって提供されています。" },
}

-- Build inlines from a "...%s..." template plus a link, splitting around the %s marker.
local function fill(tmpl, link)
  local before, after = tmpl:match("^(.-)%%s(.*)$")
  local out = {}
  if before and before ~= "" then out[#out + 1] = pandoc.Str(before) end
  out[#out + 1] = link
  if after and after ~= "" then out[#out + 1] = pandoc.Str(after) end
  return out
end

local function credit(inlines)
  return pandoc.BlockQuote({ pandoc.Para({ pandoc.Emph(inlines) }) })
end

local SIPPULSE = pandoc.Link({ pandoc.Str("SipPulse") }, "https://www.sippulse.com")
local VOIPMS = pandoc.Link({ pandoc.Str("voip.ms") }, "https://voip.ms")

function Pandoc(doc)
  local lang = (pandoc.utils.stringify(doc.meta.lang or "en")):sub(1, 2):lower()
  local s = STR[lang] or STR.en
  local FOUNDING = fill(s[1], SIPPULSE)
  local SIP_TRUNK = fill(s[2], VOIPMS)

  local out = {}
  for _, b in ipairs(doc.blocks) do
    out[#out + 1] = b
    if b.t == "Header" and b.level == 1 and not b.classes:includes("unnumbered") then
      local title = pandoc.utils.stringify(b):lower()
      if title:find("trunk") then
        out[#out + 1] = credit(SIP_TRUNK)
      else
        out[#out + 1] = credit(FOUNDING)
      end
    end
  end
  return pandoc.Pandoc(out, doc.meta)
end
