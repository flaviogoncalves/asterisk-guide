-- Strip editorial "[2nd-ed note]" admonitions from the RENDERED book (print/EPUB).
-- They stay in the Markdown source as author guidance, but must not reach the reader.
-- A note is a block quote whose text starts with "[2nd-ed note]".
function BlockQuote(el)
  local s = pandoc.utils.stringify(el)
  if s:find("^%s*%[2nd%-ed note%]") then
    return {}              -- drop it
  end
  return nil               -- leave all other block quotes (callouts) untouched
end
