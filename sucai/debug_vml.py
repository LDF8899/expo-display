# -*- coding: utf-8 -*-
"""调试: 检查 docx 中图片引用方式 (a:blip vs v:imagedata)。"""
import sys
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
V_NS = "urn:schemas-microsoft-com:vml"

p = Path(sys.argv[1])
with ZipFile(str(p)) as z:
    names = z.namelist()
    media = [n for n in names if n.startswith("word/media/")]
    print(f"media files: {len(media)}")
    root = ET.fromstring(z.read("word/document.xml"))
    blips = list(root.iter(f"{{{A_NS}}}blip"))
    print(f"a:blip count: {len(blips)}")
    # VML imagedata
    imgs = list(root.iter(f"{{{V_NS}}}imagedata"))
    print(f"v:imagedata count: {len(imgs)}")
    for im in imgs[:3]:
        print("  v:imagedata attrs:", dict(im.attrib))
    # 检查 r:embed 属性
    embeds = [b.get(f"{{{R_NS}}}embed") for b in blips[:3]]
    print("first blip embeds:", embeds)
