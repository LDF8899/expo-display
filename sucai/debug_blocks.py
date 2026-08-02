# -*- coding: utf-8 -*-
"""调试: 检查 extract_content 的块流提取。"""
import sys
sys.path.insert(0, "sucai")
from pathlib import Path
from extract_content import extract_docx_blocks

p = Path(sys.argv[1])
blocks, rels = extract_docx_blocks(p)
print("total blocks:", len(blocks))
for i, (kind, payload) in enumerate(blocks[:10]):
    print(i, kind, repr(payload)[:80])
print("rels sample:", list(rels.items())[:3])
