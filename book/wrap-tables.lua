-- Force every table to use wrapping (p{}) columns in the PDF so wide cells (long
-- inline code, file paths, prose) wrap inside the measure instead of bleeding off the
-- right margin. Pandoc only emits wrapping columns when column widths are set; by default
-- short tables get non-wrapping `l` columns. We give all columns an equal share of the
-- text width. (Harmless for EPUB/HTML, which wrap anyway.)
function Table(t)
  local n = #t.colspecs
  if n > 0 then
    for i = 1, n do
      local align = t.colspecs[i][1]
      t.colspecs[i] = { align, 1.0 / n }   -- {alignment, ColWidth fraction}
    end
  end
  return t
end
