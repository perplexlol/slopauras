# Source architecture and behavior

Baseline: SlopAuras `41369a9`, version 0.5.0. Paths and line numbers below refer to
this checkout and should be refreshed after edits.

## Load and ownership

`SlopAuras.toc` loads LibStub, CallbackHandler, LibGetFrame, LibSharedMedia, AceGUI and
AceConfig, then `Ranks.lua`, `Chain.lua`, `SlopAuras.lua`, `Share.lua`, `Options.lua`.
The addon namespace is passed through Lua's `...`; it is not an OO framework or a
WeakAuras trigger engine. Masque is optional and its presence changes the default skin.
There is no bundled build system, CI workflow, automated test suite, or rank generator.

| Module | Responsibility | Best starting points |
|---|---|---|
| Ranks.lua | Static rank families and reverse ID lookup | `ns.SpellRanks`; header gives date and attribution |
| Chain.lua | Container construction, filtering, styling, geometry, lifecycle | `SpellIDs:94`, `NewList:1167`, `NewStack:1255`, `NewMissing:1340`, `Configure:1429` |
| SlopAuras.lua | Persistence, inheritance, build decisions, hosts, conditions, scheduling | `ComputeRows:440`, `AssignLines:917`, `SyncHost:1187`, `ReadState:1291`, `Shows:1373`, `Apply:2002` |
| Share.lua | Strict config/group/display JSON import and export | spec tables at 178 and 286; `SharedValue:457`, `Import:560` |
| Options.lua | AceConfig editor, grouping, controls, import choices, preview | `SharedTabs:637`, `OpenTest:2541`, `InitOptions:2568` |

## Persistence and inheritance

`SlopAurasDB` is account-wide: `{nextID, groups}`. There are no current profiles;
old AceDB `profiles.Default` is migrated to the top level. `ns.Prepare` establishes
display -> group -> `DEFAULTS` through metatables. Only raw settings are saved/exported.
Deleting an override re-enables inheritance, so `nil` is different from explicit
`false`, `"any"`, `"always"`, `"never"`, or an empty list.

A group defines units and placement plus defaults for its displays. Display entries
are `list`, `missing`, or a line-break marker `{mode="break"}`. `ns.Displays` skips
markers while retaining editor numbering and list position. Migration handles old
group filters, `lineMax`, and display `newLine`. Unsupported old display modes are
dropped on load; retired loss-of-control settings are removed.

Defaults include player/screen, rightward growth, helpful aura filter, eight icons,
24px icons, 2px spacing, hidden dead/offline units, and disabled tooltips.
Default `layer=0` differs from the import/editor's explicit 1-10 layer range: omission
uses the default, but serializing an explicit zero would need review.

Class filtering has two stages: `ComputeRows` gates the group itself and `Builds`
gates displays. A display cannot broaden a group that the group-level class check
already excludes. Known-spell lists mean any positive ID known and no negative ID
known. They are checked with `C_SpellBook.IsSpellKnown`; rank expansion is separate.

## How settings become the UI

```
saved settings -> Prepare -> ComputeRows -> host-specific SyncHost
  -> BuildRow / AssignLines -> Chain constructors -> Blizzard aura engine
  -> trusted filtering/sorting/layout -> frame geometry -> visible addon presentation
```

A **host** is a unit's screen location; a **row** is one group on one host;
a **line** is a layout segment inside the row. The editor calls lines rows/columns.
This distinction matters when reading layout code.

- List displays on one line share a container, with an aura group per display.
  Each aura group preallocates ten buttons even when `max=1`; larger lists can allocate
  further batches. Blizzard determines which auras get those buttons.
- Missing icons use invisible presence and slide containers plus a fixed clipping
  window. Geometry moves the icon out of sight when an eligible aura exists.
  Lua does not inspect aura presence. Missing displays follow list displays on a line,
  even if the saved entries interleave them.
- Centering uses half-length shadow containers, not arithmetic on a secret width.
- `firstLine` clips to one line; empty list lines collapse. Mixed icon sizes can expose
  the next line, so `FirstLineConflict` disables clipping and explains the limitation.
- Qualifying one-icon-per-line priority groups use aura slots rather than ten-button
  groups. The buttons overlap with earlier displays at higher levels.
- Wrap and line-cap settings belong to the entry that starts a line, even if that
  entry is not built on this character. Caps use a clip window and measure slots using
  the largest icon and first display's spacing, so heterogeneous sizes/spacings are not
  an exact global icon count. Centered, multi-host-strand, missing, and priority-stack
  layouts have cap restrictions; wrapping takes precedence.
- Adjacent eligible list displays differing only in dispel types/name/known spells
  can merge to reduce allocations. Their max count and sorting then apply jointly.
- Independent displays do not deduplicate auras.

## Hosts and frame discovery

Player, target, and focus hosts are created at login. Group-token lists include player,
party1-4, pet/partypet1-4, raid1-40 and raidpet1-40. Group hosts are created lazily
when an acceptable unit frame appears. Nameplate hosts are prebuilt for 40 tokens,
then assigned to actual plate frames as plates appear. Later plate appearances
normally need no new aura rows.

LibGetFrame minor 79 discovers visible unit buttons with a coroutine (~2ms/frame
scan budget), frame-name patterns, rankings, and cached inventories. This bundled
copy skips AuraContainer subtrees and preserves the previous inventory on a failed
scan. A higher-minor copy supplied by another addon can replace it through LibStub,
so the resolved runtime library must be part of a bug report.

SlopAuras insists that a selected frame shows the exact public token, rather than
merely a person equivalent under another token. Rebind requests are coalesced; hooks
on Blizzard compact frames and Grid2 unit assignments accelerate updates.
Edit Mode and Grid2 previews get extra player-backed preview hosts.

Party/raid rows inherit their frame's visibility. Nameplate rows are parented to
UIParent and anchored to the plate; per-frame following copies accessible alpha and
scale in 0.05 increments. This avoids the inherited per-frame costs described by
the maintainer. The README's broad compatibility statement is not evidence that
every supported frame addon has been tested in this checkout.

## Apply, secrecy, and resources

Editor changes mutate saved tables, then coalesce for 0.1 seconds. Row signatures
encode structure, shape identifies reusable rows, and fingerprints include settings,
skin epoch, and known spells.

- Outside aura secrecy: reuse rows and fitting containers, keep spare containers,
  push only changed candidate/sort/layout settings, and restyle changed buttons.
- During aura secrecy: keep matching fingerprints; rebuild changed rows, configure
  fresh buttons in their initialization callback, and skip restyling existing buttons.
  Skin/font reskins wait for secrecy to end to avoid rebuilding everything.
- Host builds and secret-state sync use separate ~4ms/frame queues. This budget is
  checked between whole hosts, so one expensive host can exceed it.
- Conditions poll every 0.25 seconds; range uses unit events. Known spells are polled
  to notice level/talent/respec changes. Roster bursts coalesce for 0.2 seconds.
- WoW frames cannot be destroyed. Retired containers are disabled/hidden until reload;
  after 500 the editor suggests reload. Spare and retained host frames also occupy
  memory and are not equivalent to the retired-container count.

Combat-limited list glows use glowing/plain copies with different load conditions.
Range-limited list glows are held fully visible while auras are secret; this is a
documented compromise, not a working combat range alert.
Many styling calls use `pcall`; a refused operation may leave a visual discrepancy
without a visible Lua error. Error-free operation alone is insufficient QA.

## Editor and share contracts

`/slop` opens a standalone 1080x640 AceConfig window. A second window owns test mode.
Right-click resets display overrides; widget hooks check the active app because
AceGUI reuses widgets across addons. Options tables rebuild from current groups on
redraw; Appearance controls must be included in their `Section` layout.

Share strings are `SlopAuras:1:<config|group|display>:<json>`. The format version is
independent of addon 0.5.0. Blizzard JSON parsing plus strict key/value validation
rejects an entire invalid input before the editor mutates saved settings; there is no
execution of pasted Lua. IDs are assigned on insertion; imports can replace all,
replace matching names, or append groups. Group exports omit identity IDs.

Test mode swaps the global aura provider, including Blizzard's frames. Candidate
filters are relaxed for placeholders; missing icons use a rejecting filter to show
absence. Untested groups are hidden. Combat or aura secrecy ends preview; affected
displays hide during restoration until their real filters have been applied.
Placeholders do not prove real spell matching, dispel colors, durations, or secrecy.

## Feature-change checklist

A new setting usually needs its runtime default/behavior, editor control and reset,
Share validator, saved-key documentation, and style-cache key. Structural behavior
also needs row/build flags. A new display type crosses migrations, splitting,
constructors, configuration, test mode, sharing, and editor behavior; adding one
isolated control is insufficient.

Preserve upstream and third-party attribution: project WTFPL, Ace3's license,
LibSharedMedia LGPL v2.1, LibGetFrame GPL v2, and rank data CC BY 4.0. Rank data is
dated 2026-10-01; the generator is absent from this repo. Regeneration must recover
the original source and separate spell variants, not assume every similar name
belongs to one rank family.
