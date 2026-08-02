# -*- coding: utf-8 -*-
"""把素材文档全文 dump 到 UTF-8 文本文件（含图片占位标记），供阅读与拆分设计。"""
import sys
from pathlib import Path
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph


def iter_block_items(parent):
    from docx.document import Document as _Doc
    body = parent.element.body
    for child in body.iterchildren():
        if child.tag.endswith("}p"):
            yield Paragraph(child, parent)
        elif child.tag.endswith("}tbl"):
            yield Table(child, parent)


def dump_docx(path: Path, out: Path):
    doc = Document(str(path))
    lines = []
    for block in iter_block_items(doc):
        if isinstance(block, Paragraph):
            text = block.text.strip()
            if text:
                lines.append(text)
            else:
                lines.append("")  # 空行分隔
        else:
            try:
                for row in block.rows:
                    cells = [c.text.strip().replace("\n", " / ") for c in row.cells]
                    lines.append(" | ".join(cells))
            except Exception:
                lines.append("[表格读取失败]")
            lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"dumped {len(lines)} lines -> {out.name}")


def dump_docx_safe(path: Path, out: Path):
    try:
        dump_docx(path, out)
    except Exception as exc:
        print(f"ERROR {path.name}: {exc}")
        # 回退：仅用 zipfile 提取 document.xml 的纯文本
        from zipfile import ZipFile
        import re
        from xml.sax.saxutils import unescape
        with ZipFile(str(path)) as z:
            xml = z.read("word/document.xml").decode("utf-8", "replace")
        text = re.sub(r"<w:p[ >]", "\n<w:p ", xml)
        text = re.sub(r"<[^>]+>", "", text)
        text = unescape(text)
        out.write_text(text, encoding="utf-8")
        print(f"fallback dumped -> {out.name}")


if __name__ == "__main__":
    out_dir = Path("sucai/dumped")
    out_dir.mkdir(parents=True, exist_ok=True)
    for src in sys.argv[1:]:
        p = Path(src)
        dump_docx_safe(p, out_dir / (p.stem + ".txt"))
