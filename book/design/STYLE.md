# Visual style guide (Art Director)

The book should read as one calm, professional object. Restraint over decoration.

- **Type:** serif body (TeX Gyre Pagella, 10pt), sans headings (TeX Gyre Heros),
  monospace code (TeX Gyre Cursor). One brand accent blue (#1C5D99); everything else
  is near-black on white. Must degrade cleanly to grayscale for print.
- **Hierarchy:** Part page → Chapter opener (big ghosted number, accent rule) → sans
  section/subsection in brand ink. Front matter and Part pages stay unnumbered and quiet.
- **Code:** every block sits in a light shaded, thin-framed box in the mono face — the
  single biggest readability win for a technical book.
- **Callouts:** `[2nd-ed note]` blockquotes get a thin accent left-rule so they read as
  editorial asides, not body text.
- **Figures:** centered, capped to the text width, with a small accent "Figure N." label.
- **Consistency:** all visual decisions live in `interior.tex` + `tokens.yaml`, never in
  the chapter Markdown. Fix look-and-feel at the template level.
