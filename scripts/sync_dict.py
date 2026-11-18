#!/usr/bin/env python3
"""以 dict/figma-zh-CN.json 为唯一来源，重新生成两个 JS 文件内的词典块。"""
import json, re, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
block = json.dumps(json.load(open(root / 'dict/figma-zh-CN.json')), ensure_ascii=False, indent=2)
pat = re.compile(r'(const (?:MAP|FIGMA_ZH_CN_MAP) = \n)\{\n.*?\n\}(\n;)', re.S)

for rel in ['tampermonkey/replacements.js', 'tampermonkey/figma-zh-cn.user.js']:
    p = root / rel
    s = p.read_text()
    new, n = pat.subn(lambda m: m.group(1) + block + m.group(2), s)
    assert n == 1, f'{rel}: 未找到唯一的词典块'
    p.write_text(new)
    print(f'{rel}: synced')
