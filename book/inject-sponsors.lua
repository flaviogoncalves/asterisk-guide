-- SPONSORED build only: drop a small sponsor credit at the opening of every numbered
-- chapter (right after the chapter title). Lab chapters credit their lab sponsor; all other
-- chapters credit the founding sponsor. Part dividers / front matter ({.unnumbered}) are skipped.
-- Runs AFTER strip-notes, so these credits are never mistaken for editorial notes.

local function credit(inlines)
  return pandoc.BlockQuote({ pandoc.Para({ pandoc.Emph(inlines) }) })
end

local FOUNDING = {
  pandoc.Str("This free edition is sponsored by "),
  pandoc.Link({ pandoc.Str("SipPulse") }, "https://www.sippulse.com"),
  pandoc.Str("."),
}
local SIP_TRUNK = {
  pandoc.Str("The SIP Trunking & DID labs in this chapter are sponsored by "),
  pandoc.Link({ pandoc.Str("voip.ms") }, "https://voip.ms"),
  pandoc.Str("."),
}

function Pandoc(doc)
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
