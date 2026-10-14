"""Offline research probes; mocks do not reproduce WoW secrecy or rendering.

Run with Python and lupa==2.6 (Lua 5.1); see research/README.md.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--dependency-path', type=Path)
args = parser.parse_args()
if args.dependency_path:
    sys.path.insert(0, str(args.dependency_path))
from lupa.lua51 import LuaRuntime, lua_type

lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute('''
local function noop() end
local dummy = {RegisterCallback = noop}
function LibStub(name, optional)
  if name == 'Masque' then return nil end
  return dummy
end
AnchorUtil = {FlowDirection = {Left=1,Right=2,Up=3,Down=4}, FlowLayoutAxis={Horizontal=1,Vertical=2}}
Enum = setmetatable({}, {__index=function(t,k)
  local group=setmetatable({}, {__index=function(g,n) rawset(g,n,1); return 1 end})
  rawset(t,k,group); return group
end})
function CreateFrame() return setmetatable({}, {__index=function() return noop end}) end
function hooksecurefunc() end
function UnitClassBase() return 'PRIEST' end
C_SpellBook = {IsSpellKnown=function(id) return id==527 end}
C_EventUtils = {IsEventValid=function() return true end}
CLASS_SORT_ORDER={'WARRIOR','PRIEST','MAGE','DRUID','HUNTER','PALADIN','ROGUE','SHAMAN','WARLOCK'}
AuraContainerSortMethod={Default=1,ExpirationOnly=2,Name=3}
AuraContainerSortDirection={Normal=1,Reverse=2}
function tContains(t, v) for _, x in ipairs(t) do if x==v then return true end end return false end
function wipe(t) for k in pairs(t) do t[k]=nil end end
function strtrim(s) return s:match('^%s*(.-)%s*$') end
function CopyTable(t)
  local copy={}; for k,v in pairs(t) do copy[k]=type(v)=='table' and CopyTable(v) or v end
  return copy
end
AuraUtil={AuraFilters={IncludeNameplateOnly='INCLUDE_NAME_PLATE_ONLY'}}
function AuraUtil.IsValidFilterString(s) return type(s)=='string' and s~='', 'mock invalid filter' end
''')

def to_python(value):
    if lua_type(value) != 'table':
        return value
    keys = list(value.keys())
    if not keys or set(keys) == set(range(1, len(keys)+1)):
        return [to_python(value[i]) for i in range(1, len(keys)+1)]
    return {str(k): to_python(value[k]) for k in keys}

def to_lua(value):
    if isinstance(value, dict):
        return lua.table_from({k: to_lua(v) for k,v in value.items()})
    if isinstance(value, list):
        return lua.table_from([to_lua(v) for v in value])
    return value

lua.globals().C_EncodingUtil = lua.table_from({
    'SerializeJSON': lambda x: json.dumps(to_python(x), separators=(',', ':')),
    'DeserializeJSON': lambda x: to_lua(json.loads(x)),
})
ns = lua.table()
syntax = []
compile_lua = lua.eval('function(s,n) local f,e=loadstring(s,n); return f~=nil,e end')
for path in sorted((ROOT/'SlopAuras').rglob('*.lua')):
    ok, error = compile_lua(path.read_text(encoding='utf-8-sig'), str(path))
    if not ok:
        raise AssertionError(f'{path}: {error}')
    syntax.append(str(path.relative_to(ROOT)))
for name in ['Ranks.lua', 'Chain.lua', 'SlopAuras.lua', 'Share.lua']:
    lua.execute((ROOT/'SlopAuras'/name).read_text(encoding='utf-8-sig'), 'SlopAuras', ns)

observations = []
def observe(name, status, details):
    observations.append(dict(name=name, status=status, details=details))

group = to_lua({'name':'override probe', 'unitPower':['MANA'], 'class':['PRIEST'],
               'displays':[{'unitPower':[], 'class':[]}]})
ns.Prepare(group)
text = ns.Share.ExportGroup(group)
restored = ns.Share.Import(text, 'group')
if isinstance(restored, tuple):
    raise AssertionError(restored)
ns.Prepare(restored)
assert len(group.displays[1].unitPower) == 0
assert len(restored.displays[1].unitPower) == 0, 'Export lost the display power override'
assert len(restored.displays[1]['class']) == 0, 'Export lost the display class override'
observe('empty override group round-trip', 'passed', 'Explicit empty power/class overrides survive inheritance.')

for with_group in [False, True]:
    exported = ns.Share.ExportDisplay(group.displays[1], with_group)
    imported = ns.Share.Import(exported, 'display')
    assert not isinstance(imported, tuple)
    parent = to_lua({'displays':[], 'unitPower':['RAGE'], 'class':['WARRIOR']})
    parent.displays[1] = imported
    ns.Prepare(parent)
    assert len(imported.unitPower) == 0 and len(imported['class']) == 0
observe('display export with/without group values', 'passed', 'Empty overrides survive transfer to a differently restricted group.')

ns.groups = lua.table_from([group])
config = ns.Share.Import(ns.Share.ExportConfig(), 'config')
assert not isinstance(config, tuple)
ns.Prepare(config[1])
assert len(config[1].displays[1].unitPower) == 0
assert len(config[1].displays[1]['class']) == 0
empty_target = to_lua({'name':'no units', 'target':[], 'displays':[{}]})
ns.Prepare(empty_target)
empty_target_copy = ns.Share.Import(ns.Share.ExportGroup(empty_target), 'group')
assert not isinstance(empty_target_copy, tuple)
ns.Prepare(empty_target_copy)
assert lua_type(empty_target_copy.target) == 'table' and len(empty_target_copy.target) == 0
observe('config and empty-target group round-trip', 'passed', 'Explicitly selecting no units stays empty instead of loading on player.')

group.displays[1]['class'] = ''
legacy_class = ns.Share.Import(ns.Share.ExportGroup(group), 'group')
assert not isinstance(legacy_class, tuple)
ns.Prepare(legacy_class)
assert len(legacy_class.displays[1]['class']) == 0
observe('legacy empty-string class override', 'passed', 'Legacy all-classes override is exported as an empty list.')

for key in ['max', 'wrap', 'lineCap']:
    value = ns.Share.Import('SlopAuras:1:display:'+json.dumps({key:1.5}), 'display')
    assert isinstance(value, tuple) and value[0] is None, f'Fractional {key} was accepted'
    assert 'whole number' in value[1]
    for bound in [1, 40]:
        accepted = ns.Share.Import('SlopAuras:1:display:'+json.dumps({key:bound}), 'display')
        assert not isinstance(accepted, tuple) and accepted[key] == bound
    observe('integer '+key+' import', 'passed', 'Fraction rejected; both integer boundaries accepted.')

for key, upper in [('layer',10), ('lineMax',40)]:
    value = ns.Share.Import('SlopAuras:1:group:'+json.dumps({'name':'count check',key:1.5}), 'group')
    assert isinstance(value, tuple) and value[0] is None and 'whole number' in value[1]
    for bound in [1, upper]:
        accepted = ns.Share.Import('SlopAuras:1:group:'+json.dumps({'name':'count check',key:bound}), 'group')
        assert not isinstance(accepted, tuple)
observe('integer layer and legacy lineMax', 'passed', 'Discrete group values reject fractions and accept bounds.')

fractional_pixels = ns.Share.Import('SlopAuras:1:display:{"size":24.5,"spacing":2.5,"maxDuration":30.5}', 'display')
assert not isinstance(fractional_pixels, tuple) and fractional_pixels.size == 24.5
assert fractional_pixels.spacing == 2.5 and fractional_pixels.maxDuration == 30.5
observe('continuous settings retain fractions', 'passed', 'Pixel geometry and duration still accept fractional values.')

empty_ids = to_lua({'spellIDs':{}, 'rankSpellIDs':{}})
exported_ids = json.loads(ns.Share.ExportDisplay(empty_ids, False).split(':',3)[3])
assert 'spellIDs' not in exported_ids and 'rankSpellIDs' not in exported_ids
assert not isinstance(ns.Share.Import(ns.Share.ExportDisplay(empty_ids,False),'display'), tuple)
observe('empty spell-ID sets stay omitted', 'passed', 'No invalid empty ID lists introduced.')

invalid = ns.Share.Import('SlopAuras:1:display:{"size":999}', 'display')
assert isinstance(invalid, tuple) and invalid[0] is None
observe('out-of-range size rejection', 'passed', invalid[1])
invalid = ns.Share.Import('SlopAuras:1:display:{"unknown":true}', 'display')
assert isinstance(invalid, tuple) and invalid[0] is None
observe('unknown setting rejection', 'passed', invalid[1])

include, exclude = ns.Chain.SpellIDs(to_lua({'rankSpellIDs':{588:True}, 'spellIDs':{1243:False}}))
family = ns.SpellRanks(588)
assert len(family)>1 and all(include[x] for x in family.values()) and exclude[1243]
observe('rank expansion with exclusion', 'passed', 'All known ranks of 588 included; exact 1243 excluded.')

legacy = to_lua({'displays':[{'name':'one'}, {'name':'two','newLine':True}]})
ns.ConvertNewLine(legacy)
assert legacy.displays[2].mode == 'break' and legacy.displays[3].newLine is None
observe('legacy newline migration', 'passed', 'newLine converts into a break entry without dropping the display.')

priority_text = (ROOT/'research'/'fixtures'/'priority-stack.txt').read_text(encoding='utf-8').strip()
priority = ns.Share.Import(priority_text, 'group')
assert not isinstance(priority, tuple), priority
ns.Prepare(priority)
stack = ns.StackDisplays(priority)
assert stack is not None and len(stack) == 2, 'Fixture does not select the priority-stack path'
assert stack[1].name == 'Shield first' and stack[2].name == 'Other buff fallback'
priority.growth = 'CENTER'
assert ns.StackDisplays(priority) is None, 'Centered groups must use the regular container path'
priority.growth = 'RIGHT'
priority.displays[1].max = 2
assert ns.StackDisplays(priority) is None, 'Multiple icons must use the regular container path'
observe('priority-stack fixture qualification', 'passed', 'Two ordered one-icon lines select stack; centered/multi-icon controls do not. No rendering or secrecy simulated.')

lua.execute((ROOT/'research'/'stack-restriction.lua').read_text(encoding='utf-8'), ns)
observe('priority-stack initialization access contract', 'passed', 'Actual stack code positions/levels before modeled restrictions; non-secret grow/shrink retains priority and spare slots. Not native secrecy/rendering.')

report = {'runtime':'lupa 2.6 / Lua 5.1', 'limits':'WoW API stubs; modeled slot access timing only, no real secret values, native frame restrictions, or rendering.',
          'lua_files_compiled':len(syntax), 'observations':observations}
(ROOT/'research'/'regression-results.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
print(json.dumps(report, indent=2))
