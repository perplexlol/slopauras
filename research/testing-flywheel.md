# Testing and contribution flywheel

This is a staged engineering loop. Local source checks are executable now; the
WoW client's rendering, taint, native secrets and protected actions remain an
independent validation layer. No scheduled automation exists yet.

## Stage 1: record the actual environment

Before relying on API details, capture in a run record:

- `GetBuildInfo()` output, date, locale, UI scale, resolution/window mode.
- SlopAuras version and exact Git commit; installation path and any addon manager
  that might replace development files.
- Exported SlopAuras config and a SavedVariables backup made while the game is closed
  or after a deliberate reload/logout. WoW writes saved variables itself.
- Other enabled addons, especially Masque, font providers, unit-frame/nameplate
  addons, and the resolved LibGetFrame minor/version.
- Character class, level, relevant known spells/ranks, and unit/context used.
- Combat state, `ShouldAurasBeSecret`, relevant restriction state, and whether Edit
  Mode/test provider is active. Never log raw secret values for debugging.

For API disputes use `/api search ShouldAurasBeSecret`, `/api search GetAuraDuration`,
or the relevant named API in the client. Extract matching Blizzard UI source where
available. Preserve source/build hashes before refreshing a public mirror checkout.

## Stage 2: local checks

The current `probes.py` proves a useful narrow baseline: all Lua parses, sharing
validation works for selected cases, known-rank expansion works, and a migration
retains display identity. It also reproduces export/count defects.

Next expand with actual behavior requirements:

| Area | Regression examples |
|---|---|
| Sharing/inheritance | Empty overrides, explicit false, group-value inclusion, config/group/display round-trips, rejected input leaves DB untouched |
| Validation | Unknown keys, duplicates, malformed colors/IDs, bounded and integer count limits, valid example configs |
| Migration | Old profiles, group filter, lineMax/newLine conversions, unsupported modes, break normalization |
| Filtering | Rank expansion, include/exclude conflict policy, dispel None complement, missing-icon icon selection |
| Layout eligibility | First-line conflicts, stack selection, wraps/caps blocked for incompatible shapes, unloaded line leaders |
| Scheduling/lifecycle | Coalesced changes, class/known-spell rebuilds, stale host work, retired/spare accounting, test exit/restoration |

Mocks should implement contract failures, not always succeed. A frame mock should
refuse post-initialization button access when aura secrecy is active; a container
mock should require integer `maxFrameCount`. Lua proxies can catch some attempted
secret arithmetic, but cannot faithfully model native secret primitive semantics.
Mark these as mock tests, never client passes.

API inventories capture headers plus full file hashes. On a new snapshot compare
hashes, inspect diffs, and review changed `Requires*`, `SecretWhen*`, argument/return
and widget contracts. Generated header metadata alone is incomplete. Retain both
old and new manifests with their source commits.

## Stage 3: client regression matrix

| Scenario | What to observe |
|---|---|
| Fresh login and reload | DB migration, no duplicate hosts, real aura source, correct initial combat state |
| `/slop` preview | All configured groups, missing icons, editor reset/inheritance, close restores real provider |
| Edit Mode | Party/raid preview hosts, fonts/scale/layout, transition back to live units |
| Known player buff apply/expire | Eligible exact ID/rank matching, icon/count/timer, missing icon changes correctly |
| Friendly harmful aura | Broad CC/dispel filters; exact-ID restriction result recorded explicitly |
| Enemy helpful aura | Broad purge/dispel filters; identity restriction result recorded explicitly |
| Enemy harmful aura | Eligible exact-ID filter and sort behavior |
| Combat enter/leave and reload in fight | No forbidden operations, correct glows, real filters after preview exit |
| PvP outside combat | Secret-but-not-in-combat editing and reskin behavior, identity restrictions |
| Priority-stack edit under secrecy | Correct position/order after new slot construction, compare to non-secret baseline |
| Target/focus swaps and roster reorder | No stale person/token auras; rows follow exact unit frame |
| Pet replacement and nameplate reuse | Old unit clears; new unit receives correct rows; no stale aura identity |
| Skin/font changes | Deferred during secrecy, correct after it ends, missing font fallback |
| Repeated edits on raid/nameplates | Queue latency, frame accumulation, idle CPU, reload recovery |

Keep tested counts small initially, then increase to dense nameplates and a populated
raid. A stationary town preview cannot establish combat correctness. Placeholder
auras lack the IDs/types/durations needed for real matching tests.

Use `/fstack` to identify the addon frames. Enable Lua error reporting or use an
error collector if already installed. Capture `ADDON_ACTION_BLOCKED` /
`ADDON_ACTION_FORBIDDEN` evidence and a minimal reproduction. A visual failure with
no Lua error is still a failure, because the addon swallows some native-call errors.

## Stage 4: visual evidence

Each case needs deterministic setup, exported config, a screenshot before/action/after,
expected visible outcome, error result and timing. Fix UI scale/resolution when
comparing pictures. Compare cropped addon regions; masks exclude changing world/chat
content. Countdown text naturally varies, so test its presence/format or bounded
expectation rather than expecting identical pixels.

Store human-readable run metadata alongside screenshots and logs. Visual automation
can navigate settings and inspect outcomes when client access becomes available;
real spells/units and restriction transitions still need reproducible scenario setup.
Do not declare an integration pass because a mock or preview passed.

Suggested run layout, created only when we have an actual run:

```
research/runs/YYYY-MM-DD-case/
  run.json       # build, addon commit, context, steps, expectation, outcome
  config.txt     # exact SlopAuras export
  before.png
  after.png
  errors.txt
  notes.md       # interpretation and remaining uncertainty
```

## Stage 5: close the loop

```
player observation or API change
  -> classify permitted data path
  -> smallest reproducible fixture
  -> failing desired-behavior regression
  -> focused code change
  -> local contract checks
  -> real client + visual regression
  -> reviewable contribution with evidence
  -> update notebook / regression corpus / capability matrix
```

A future automation should select one bounded issue, refresh relevant contracts,
prepare a focused change, run available tests, and report what still requires client
verification. It should not convert repeated self-generated proposals into proof
that a feature is needed or API-safe. User gameplay findings and observed failures
are the strongest inputs to the backlog.

For GitHub CI, use a pinned Lua environment for pure tests plus static checks of TOC
paths/load order and fixture/schema compatibility. Client smoke results must be
separate artifacts with a real build/run ID. Publishing a build or upstream PR should
include what actually ran and avoid implying WoW can be faithfully tested in CI.

## Observation template

```text
Date / timezone:
Addon commit / version:
Client version / build / locale:
Other addons / resolved libraries:
Config and character context:
Restriction / combat / provider state:
Steps:
Expected:
Observed:
Errors / screenshots / timing:
Evidence level: source-confirmed | offline-reproduced | client-verified | candidate
Conclusion:
Regression added:
Open questions:
Supersedes earlier observation:
```
