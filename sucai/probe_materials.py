# -*- coding: utf-8 -*-
"""探测素材 docx/.doc 内部结构，用于规划提取方案。"""
import sys
from pathlib import Path
from zipfile import ZipFile


def probe_docx(path: Path):
    print(f"== {path.name} ==")
    with ZipFile(path) as z:
        names = z.namelist()
        media = [n for n in names if n.startswith("word/media/")]
        print(f"  files={len(names)} media={len(media)}")
        for n in ["word/document.xml", "word/_rels/document.xml.rels"]:
            if n in names:
                print(f"  {n}: {z.getinfo(n).file_size} bytes")
        total_media = sum(z.getinfo(n).file_size for n in media)
        print(f"  media total: {total_media / 1024 / 1024:.1f} MB")
        # 打印前 5 个 media 文件名
        for n in media[:8]:
            print(f"    - {n} ({z.getinfo(n).file_size // 1024} KB)")


def probe_doc(path: Path):
    import olefile
    print(f"== {path.name} (OLE .doc) ==")
    if not olefile.isOleFile(str(path)):
        print("  not an OLE file")
        return
    ole = olefile.OleFileIO(str(path))
    print(f"  streams: {ole.listdir()[:20]}")
    if ole.exists("WordDocument"):
        data = ole.openstream("WordDocument").read()
        print(f"  WordDocument stream: {len(data)} bytes")
    # 数据流
    for entry in ["1Table", "0Table"]:
        if ole.exists(entry):
            print(f"  {entry}: {ole.get_size(entry)} bytes")
    ole.close()


if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"D:\杂\修改资料7.27\修改资料7.27")
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() in {".docx", ".doc"}:
            try:
                if p.suffix.lower() == ".docx":
                    probe_docx(p)
                else:
                    probe_doc(p)
            except Exception as exc:
                print(f"== {p.name} == ERROR: {exc}")
