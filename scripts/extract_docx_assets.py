# -*- coding: utf-8 -*-
"""
从 uploads/ 原始素材 docx 中提取内嵌图片到 static/pages/generated/<slug>/，
并生成"段落+图片"映射 JSON（供内容维护参考）。

用法（在项目根目录 expo-display/ 下执行）：
    python scripts/extract_docx_assets.py

说明：
- uploads/ 为原始素材目录（网盘分发，不进 git）；本脚本产物 static/pages/generated/ 会进入 git。
- 提取后的图片 URL 形如 /static/pages/generated/<slug>/img001.jpeg，
  由 department-<slug>.data.js（DEPARTMENT_DATA）引用。
- 段落映射 JSON 输出到 scripts/.docx_parsed/<slug>.json，不入 git。
"""
import os
import json
import shutil
import zipfile
from xml.etree import ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # expo-display/
OUT_DIR = os.path.join(ROOT, 'static', 'pages', 'generated')
JSON_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.docx_parsed')
os.makedirs(JSON_DIR, exist_ok=True)

# (docx 相对路径, 专题 slug)；按需增删
JOBS = [
    ('uploads/创新育人-现代农业(1).docx', 'modern-agriculture'),
    ('uploads/创新育人-智慧康养(合并版).docx', 'smart-healthcare'),
    ('uploads/创新育人-财经商贸2026.8.4更新.docx', 'finance-commerce'),
    ('uploads/修改资料7.27/修改资料7.27/创新育人区/创新育人-智能制造(1).docx', 'intelligent-manufacturing'),
    ('uploads/修改资料7.27/修改资料7.27/创新育人区/创新育人-智慧能源(1).docx', 'smart-energy'),
    ('uploads/修改资料7.27/修改资料7.27/创新育人区/创新育人-数字文旅/创新育人-数字文旅2026.7.25.docx', 'digital-tourism'),
    ('uploads/修改资料7.27/修改资料7.27/系部简介/电子信息工程系系部介绍(2).docx', 'digital-tech'),
]


def extract(docx_path, slug):
    z = zipfile.ZipFile(docx_path)
    rels_root = ET.fromstring(z.read('word/_rels/document.xml.rels').decode('utf-8'))
    rels = {}
    for rel in rels_root:
        rid = rel.get('Id')
        target = rel.get('Target', '')
        if rid and target.startswith('media/'):
            rels[rid] = target

    root = ET.fromstring(z.read('word/document.xml').decode('utf-8'))
    order = []
    for node in root.iter(A + 'blip'):
        rid = node.get(R + 'embed')
        if rid and rid in rels and rels[rid] not in order:
            order.append(rels[rid])

    slug_dir = os.path.join(OUT_DIR, slug)
    os.makedirs(slug_dir, exist_ok=True)
    url_map = {}
    for i, media_name in enumerate(order, 1):
        ext = os.path.splitext(media_name)[1].lower() or '.png'
        out_name = f'img{i:03d}{ext}'
        with z.open('word/' + media_name) as src, open(os.path.join(slug_dir, out_name), 'wb') as dst:
            shutil.copyfileobj(src, dst)
        url_map[media_name] = f'/static/pages/generated/{slug}/{out_name}'

    paras = []
    for p in root.iter(W + 'p'):
        texts, images = [], []
        for node in p.iter():
            if node.tag == W + 't':
                texts.append(node.text or '')
            elif node.tag == A + 'blip':
                rid = node.get(R + 'embed')
                if rid and rid in rels:
                    images.append(url_map.get(rels[rid], rels[rid]))
        line = ''.join(texts).strip()
        if line or images:
            paras.append({'text': line, 'images': images})

    with open(os.path.join(JSON_DIR, f'{slug}.json'), 'w', encoding='utf-8') as f:
        json.dump({'source': docx_path, 'paras': paras}, f, ensure_ascii=False, indent=1)
    print(f'{slug}: 提取 {len(order)} 张图 -> static/pages/generated/{slug}/，段落映射 -> scripts/.docx_parsed/{slug}.json')


def main():
    for rel_path, slug in JOBS:
        full = os.path.join(ROOT, rel_path)
        if not os.path.exists(full):
            print(f'跳过（素材不存在，请先从网盘恢复 uploads/）: {rel_path}')
            continue
        try:
            extract(full, slug)
        except Exception as e:
            print(f'失败 {slug}: {e}')


if __name__ == '__main__':
    main()
