# DOCX reader drops text sharing a run with a footnote reference

A `w:r` containing ordinary `w:t` and `w:footnoteReference` retains the note but loses the text. Placing them in separate runs preserves both. Text following the reference inside the same run is also lost.

## Reproduce

Generate four synthetic, five-part DOCX packages using [make.py](make.py), then compare:

```sh
python3 make.py
pandoc -f docx -t markdown --wrap=none mixed-run.docx
pandoc -f docx -t markdown --wrap=none separate-runs.docx
pandoc -f docx -t markdown --wrap=none mixed-run-after.docx
pandoc -f docx -t markdown --wrap=none separate-runs-after.docx
```

The `word/document.xml` run difference:

```xml
<!-- Text and reference within one run (fails) -->
<w:r><w:t>A synthetic paper</w:t><w:footnoteReference w:id="1"/></w:r>
<!-- Text and reference in separate runs (control passes) -->
<w:r><w:t>A synthetic paper</w:t></w:r><w:r><w:footnoteReference w:id="1"/></w:r>
```

`word/footnotes.xml` defines footnote 1 as `Synthetic note.`. The additional `*-after.docx` pair appends `<w:t> continues</w:t>` after the reference, either in the same run or a third run.

## Expected

Both base documents:

```markdown
A synthetic paper[^1]

[^1]: Synthetic note.
```

Both `*-after.docx` documents should have `A synthetic paper[^1] continues` as the first line.

## Actual

Both mixed-run documents:

```markdown
[^1]

[^1]: Synthetic note.
```

Both separate-run controls produce the expected output. `-t native` also loses the ordinary text, ruling out a Markdown-writer issue.

Reproduced on the minimal package with Pandoc 3.1.11.1 (Linux). The original synthetic mixed-run case was reproduced with Pandoc 3.1.3 and official 3.12.1.

## Possible source

[`elemToRun` in `Readers/Docx/Parse.hs`](https://github.com/jgm/pandoc/blob/3.12.1/src/Text/Pandoc/Readers/Docx/Parse.hs#L1328-L1346) appears to select an entire run's footnote, endnote, or drawing child ahead of the ordinary run-content branch. This is a suspected location, not a verified root cause. Processing should retain original child order, including text after a reference.

Upstream issues [#11971](https://github.com/jgm/pandoc/issues/11971) and [#11991](https://github.com/jgm/pandoc/issues/11991) report different DOCX footnote defects.