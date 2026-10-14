"""Capture API headers and complete-file hashes from a pinned UI checkout.

This intentionally small scanner is not a complete Lua/documentation parser.
Arguments, returns, predicates and native enforcement must still be reviewed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('checkout', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
root = args.checkout.resolve()
doc_names = ['SecretPredicateAPI', 'SecretPredicates', 'RestrictedActions', 'Unit',
             'UnitAura', 'Spell', 'SpellBook', 'LossOfControl', 'CooldownViewer',
             'AuraContainerUtil', 'DurationTextBindingShared', 'FrameScript']
files = [root/'Interface'/'AddOns'/'Blizzard_APIDocumentationGenerated'/f'{n}Documentation.lua'
         for n in doc_names]
files += sorted((root/'Interface'/'AddOns'/'Blizzard_AuraContainer').glob('*.lua'))
result = {'commit':subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'], text=True).strip(),
          'version':(root/'version.txt').read_text().strip(),
          'scanner':'Top-level function/event/table headers only; full file hashes detect other changes.',
          'files':{}}
for file in files:
    data = file.read_bytes()
    source = data.decode('utf-8-sig')
    entry = {'sha256':hashlib.sha256(data).hexdigest()}
    if 'Documentation' in file.name:
        starts = list(re.finditer(r'^\t{3}Name = "([^"]+)"', source, re.M))
        entry['headers'] = []
        for i, match in enumerate(starts):
            block = source[match.end():starts[i+1].start() if i+1<len(starts) else len(source)]
            # Metadata precedes nested arguments/returns/tables.
            header = re.split(r'^\t{3}(?:Arguments|Returns|Fields|Payload|Values) =', block, maxsplit=1, flags=re.M)[0]
            attributes = dict(re.findall(r'^\t{3}(\w+) = ("[^"\n]*"|true|false),?$', header, re.M))
            entry['headers'].append({'name':match.group(1), **attributes})
    result['files'][str(file.relative_to(root)).replace('\\','/')] = entry
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
print(f"Saved {len(files)} source fingerprints for {result['version']} at {result['commit']}")
