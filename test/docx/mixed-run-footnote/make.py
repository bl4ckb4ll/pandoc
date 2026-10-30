#!/usr/bin/env python3
"""Generate independent DOCX fixtures for mixed-run footnote text loss."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo
from xml.etree import ElementTree as ET

out = Path(__file__).resolve().parent
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def make_docx(name, run_xml):
    parts = {
        "[Content_Types].xml":
            f'<Types xmlns="{CT}">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            '<Override PartName="/word/footnotes.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml"/>'
            '</Types>',
        "_rels/.rels":
            f'<Relationships xmlns="{REL}">'
            f'<Relationship Id="rId1" Type="{R}/officeDocument" Target="word/document.xml"/>'
            '</Relationships>',
        "word/_rels/document.xml.rels":
            f'<Relationships xmlns="{REL}">'
            f'<Relationship Id="rId1" Type="{R}/footnotes" Target="footnotes.xml"/>'
            '</Relationships>',
        "word/document.xml":
            f'<w:document xmlns:w="{W}"><w:body><w:p>{run_xml}</w:p></w:body></w:document>',
        "word/footnotes.xml":
            f'<w:footnotes xmlns:w="{W}">'
            '<w:footnote w:id="-1" w:type="separator"><w:p><w:r><w:separator/></w:r></w:p></w:footnote>'
            '<w:footnote w:id="1"><w:p><w:r><w:t>Synthetic note.</w:t></w:r></w:p></w:footnote>'
            '</w:footnotes>',
    }
    with ZipFile(out / name, "w", compression=ZIP_DEFLATED) as archive:
        for path, data in parts.items():
            ET.fromstring(data)
            entry = ZipInfo(path, date_time=(2000, 1, 1, 0, 0, 0))
            entry.compress_type = ZIP_DEFLATED
            archive.writestr(entry, data.encode("utf-8"))


text = '<w:t>A synthetic paper</w:t>'
note = '<w:footnoteReference w:id="1"/>'
tail = '<w:t> continues</w:t>'
make_docx("mixed-run.docx", f"<w:r>{text}{note}</w:r>")
make_docx("separate-runs.docx", f"<w:r>{text}</w:r><w:r>{note}</w:r>")
make_docx("mixed-run-after.docx", f"<w:r>{text}{note}{tail}</w:r>")
make_docx("separate-runs-after.docx", f"<w:r>{text}</w:r><w:r>{note}</w:r><w:r>{tail}</w:r>")
