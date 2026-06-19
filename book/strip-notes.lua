-- Strip editorial admonitions from the RENDERED book (print/EPUB): block quotes that start
-- with "[2nd-ed note]" or "[author...]" (e.g. "[author]", "[author TODO]"). They stay in the
-- Markdown source as author/illustrator guidance, but must never reach the reader.
function BlockQuote(el)
  local s = pandoc.utils.stringify(el)
  if s:find("^%s*%[2nd%-ed note%]") or s:find("^%s*%[author") then
    return {}              -- drop it
  end
  return nil               -- leave all other block quotes (callouts) untouched
end
