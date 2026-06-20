-- SPONSORED build only: drop a small sponsor credit at the opening of every numbered
-- chapter (right after the chapter title). Part dividers / front matter ({.unnumbered})
-- are skipped. Runs AFTER strip-notes, so these credits are never mistaken for editorial
-- notes. The credit text is localized from the document language (meta.lang); the brand
-- name (SipPulse) and its link stay verbatim.

-- founding-credit per language; %s is where the linked brand name goes.
local STR = {
  en = "This free edition is sponsored by %s.",
  pt = "Esta edição gratuita é patrocinada por %s.",
  es = "Esta edición gratuita está patrocinada por %s.",
  fr = "Cette édition gratuite est sponsorisée par %s.",
  de = "Diese kostenlose Ausgabe wird von %s gesponsert.",
  it = "Questa edizione gratuita è sponsorizzata da %s.",
  hi = "यह निःशुल्क संस्करण %s द्वारा प्रायोजित है।",
  zh = "本免费版本由 %s 赞助。",
  ja = "この無料版は %s のスポンサーによって提供されています。",
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

function Pandoc(doc)
  local lang = (pandoc.utils.stringify(doc.meta.lang or "en")):sub(1, 2):lower()
  local tmpl = STR[lang] or STR.en
  local FOUNDING = fill(tmpl, SIPPULSE)

  local out = {}
  for _, b in ipairs(doc.blocks) do
    out[#out + 1] = b
    if b.t == "Header" and b.level == 1 and not b.classes:includes("unnumbered") then
      out[#out + 1] = credit(FOUNDING)
    end
  end
  return pandoc.Pandoc(out, doc.meta)
end
