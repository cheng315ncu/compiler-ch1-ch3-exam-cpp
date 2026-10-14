#!/usr/bin/env python3
"""試編手冊中的每個修改範例，驗證題目範例，輸出供 HTML 使用的證據。
Run: /Volumes/D/graduate/presentation/.venv/bin/python Complier/Code/check_cpp_handbook.py"""
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import build_cpp_short_pack as pack
from cpp_handbook_examples import PROMPTS, variants_for, apply_variant

results=[];checks=0
with tempfile.TemporaryDirectory(prefix='compiler-handbook-') as scratch:
    def build(source,name):
        path=Path(scratch)/(name+'.cpp');path.write_text(source);binary=path.with_suffix('')
        subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-std=c++17','-Wall','-Wextra','-Wpedantic','-Werror','-O2',str(path),'-o',str(binary)],check=True,timeout=90)
        return binary
    def run(binary,data,expected,args=()):
        global checks
        r=subprocess.run([str(binary),*args],input=data.encode(),capture_output=True,timeout=20)
        assert r.returncode==(1 if expected is None else 0),(binary,r)
        assert r.stdout.decode()==('' if expected is None else expected),(binary,data,r.stdout,expected)
        assert bool(r.stderr)==(expected is None),(binary,r.stderr)
        checks+=1
        return dict(input=data,output=r.stdout.decode(),stderr=r.stderr.decode(),exit=r.returncode)
    for spec in pack.SPECS:
        source=spec['source_path'].read_text();stem=spec['stem'];binary=build(source,stem)
        samples=[run(binary,*case) for case in PROMPTS[stem]['samples']]
        fixture=run(binary,spec['source_path'].with_suffix('.in').read_text(),spec['source_path'].with_suffix('.expected').read_text())
        variants=[]
        for i,recipe in enumerate(variants_for(spec,pack.HANDBOOK[stem]['edits'])):
            changed,edits=apply_variant(source,recipe);binary=build(changed,stem+'_'+str(i))
            observed=run(binary,recipe['input'],recipe['expected'],recipe['args'])
            variants.append(dict(title=recipe['title'],edits=edits,example=observed,args=recipe['args'],changed_sha256=hashlib.sha256(changed.encode()).hexdigest()))
        results.append(dict(stem=stem,source_sha256=hashlib.sha256(source.encode()).hexdigest(),samples=samples,fixture=fixture,variants=variants))
    report=dict(checks=checks,programs=8,variant_builds=sum(len(r['variants']) for r in results),results=results)
    (pack.ROOT/'Complier/Review/cpp-handbook-examples.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('PASS:',checks,'samples;',report['variant_builds'],'compiled modification examples;',8,'base programs')
