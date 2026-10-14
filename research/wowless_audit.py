"""Static compatibility inventory, not a Wowless runtime test or full YAML parser.

Use Python only: Wowless requires its own elune runtime for execution.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('wowless', type=Path)
parser.add_argument('--output', type=Path, default=Path(__file__).with_name('wowless-audit.json'))
args = parser.parse_args()
root = args.wowless.resolve()
addon = Path(__file__).resolve().parents[1]/'SlopAuras'

def blocks(text, indent=0):
    pattern = re.compile(r'^'+' '*indent+r'([A-Za-z_][A-Za-z0-9_.]*):\s*$', re.M)
    matches = list(pattern.finditer(text))
    return {m.group(1):text[m.end():matches[i+1].start() if i+1<len(matches) else len(text)]
            for i,m in enumerate(matches)}

apis = blocks((root/'data/products/wow/apis.yaml').read_text())
objects = blocks((root/'data/products/wow/uiobjects.yaml').read_text())
api_names = set()
for path in addon.glob('*.lua'):
    api_names.update(re.findall(r'\b(C_\w+\.\w+)\s*\(', path.read_text()))
api_names.update(['issecretvalue', 'secretwrap', 'InCombatLockdown', 'CreateFrame',
                  'CreateSecureDelegate', 'GetForbiddenObjectTable',
                  'C_EncodingUtil.DeserializeJSON', 'C_EncodingUtil.SerializeJSON'])
coverage = {}
for name in sorted(api_names):
    body = apis.get(name)
    impl = re.search(r'^  impl: ([^\n]+)', body or '', re.M)
    coverage[name] = {'status':'missing' if body is None else 'impl-linked' if impl else 'generated-stub',
                      'implementation':impl.group(1) if impl else None}
methods = {}
for typename, names in {'UIObject':['AddAccessRestrictions','AddForbiddenAspects','AddSecretAspect'],
                         'Region':['SetAlphaFromBoolean'],
                         'Cooldown':['SetCooldownFromDurationObject','SetCountdownFormatter']}.items():
    entries = blocks(objects.get(typename,''),4)
    for name in names:
        body = entries.get(name)
        methods[f'{typename}.{name}'] = ('missing' if body is None else
                                        'impl-linked' if re.search(r'^      impl:',body,re.M) else 'generated-stub')
products = re.findall(r'^- (\S+)$', (root/'data/products.yaml').read_text(), re.M)
types = {t:t in objects for t in ['Frame','Button','Cooldown','AuraContainer','AuraButton']}
report = {'date':'2026-10-13',
          'wowless_commit':subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip(),
          'product_build_yaml':(root/'data/products/wow/build.yaml').read_text(),
          'method':'Conservative text scanner; impl-linked does not mean complete or faithful. No Wowless execution.',
          'products':products,'uiobject_types':types,'core_api_calls':coverage,'critical_methods':methods}
args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
counts = {s:sum(v['status']==s for v in coverage.values()) for s in ['impl-linked','generated-stub','missing']}
print(json.dumps({'commit':report['wowless_commit'],'products':products,'uiobject_types':types,
                  'api_counts':counts,'critical_methods':methods},indent=2))
