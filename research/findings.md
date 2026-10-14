# Contribution findings and priorities

The original findings are bounded to SlopAuras `41369a9` and the recorded source
snapshots. Later local repairs and client observations are explicitly noted below.

Follow-up 2026-10-13: findings 1 and 2 have local fixes on
`fix/share-roundtrip-validation`. The original descriptions below remain the historical
baseline. Desired-behavior regressions pass; deployment and live validation are
recorded in [the first iteration](runs/2026-10-13-sharing/run.md).

## 1. Empty-list overrides are lost during export — offline reproduced

Location: `Share.lua:457`, `SharedValue`, especially its generic table branch.
It treats every empty table as equivalent to no setting. That is incorrect for a
display's explicit `unitPower={}` overriding a group `unitPower={"MANA"}`.
After group/config export and import, the display inherits the group's mana-only
filter instead of remaining unrestricted.

The same serialization loss occurs with `class={}`; group-level class gating can
still exclude the whole group, so do not assume every class example changes visible
behavior. `unitPower` provides a clear user-facing reproduction.

Evidence: `research/probes.py` runs the real `Prepare`, export, import and inheritance
functions. `probe-results.json` records the before/after behavior. JSON bridging is
mocked; loss occurs before JSON encoding, at `SharedValue` itself.

Proposed first contribution: preserve empty override lists for keys with inheritance
semantics, including the inherited-value export path; round-trip config/group/display
and validate behavior after `Prepare`. Audit all empty-list keys rather than globally
preserving every empty table. A change should not introduce invalid empty spell-ID lists.

## 2. Fractional counts pass import validation — offline reproduced

Locations: `Share.lua:38` (`Number` checks bounds but not integrality), specs at 178/286.
`max=1.5`, `wrap=1.5`, and `lineCap=1.5` all import successfully.

`max` is particularly concrete: `Chain.GroupOptions` forwards it as `maxFrameCount`,
and the pinned Blizzard `ValidateMaxFrameCount` requires a nonnegative integer or
infinity. A config can pass Share validation and later fail container construction.
Fractional wrap/cap values have misleading count semantics, but their native failure
behavior has not been established. Pixel sizes/offsets and durations need not all
be integers; do not replace every bounded-number validator with an integer validator.

Proposed contribution: a count-specific validator plus meaningful boundary fixtures,
preserving the import's all-or-nothing behavior. Review `layer` separately.

## 3. Priority-stack positioning after restrictions — high-confidence source risk

Follow-up: the larger priority icon disappeared after the user reported a combat
size change. A callback-timing regression failed before a local Chain.lua repair,
then passed afterwards. The repair is installed; reload and native retesting are
pending. See [priority-stack run](runs/2026-10-13-sharing/priority-stack.md).

Locations: `Chain.lua:1228` (`AddSlot`) and 1247 (`LevelSlots`). Slot anchoring and
frame levels are set through `pcall` **after** `AddAuraSlot` returns. The pinned
Blizzard slot constructor uses the same post-callback aura-secret access restrictions
as group buttons. Thus a stack created/rebuilt while auras are secret may refuse the
anchor/level operations. These failures are swallowed; the ordinary non-secret path
can look correct while the combat edit path is wrong.

Not marked client-confirmed. Reproduce by creating/editing a qualifying priority
stack in combat or a secret-but-out-of-combat PvP context, then compare with reload
outside secrecy. Potential repair: determine final order before construction and
set initial placement/levels inside initialization; reuse level updates still need
to respect secrecy. Check this against the actual client before implementation.

## 4. Silent native-call failures reduce observability — source confirmed

Styling, range, enabled-state and Masque calls often ignore a failed `pcall` or keep
only a success boolean. Some failures are expected during secrecy, but others can
leave empty displays or wrong styles without visible errors. Add a bounded,
opt-in diagnostics facility that counts operation categories and restriction state,
without logging secret values or probing forbidden descendants. Error strings may
contain secrets; do not assume arbitrary payloads are safe to stringify.

Acceptance: a real invalid setup produces an actionable diagnostic; normal combat
operation does not spam or materially affect performance. Prefer telemetry about
our own queues/settings/operations over aura identities/counts.

## 5. Performance accounting and lifecycle need measured baselines — source risks

- Button allocation scales by aura groups x hosts x batches; centering adds shadow
  groups, missing icons add presence/slide groups, combat glows add copies.
  `max=1` does not make a normal aura group cheap.
- Nameplate rows are prebuilt for 40 hosts; group hosts persist after first creation.
- Queues check time between hosts, so one host is an indivisible burst.
- Retired-container warnings do not count all retained/spare objects or memory.
- Repeated secret-state edits can retire many frames; reload is the actual reclamation.
- `GroupJSON` uses string fingerprints; verify equivalent-table serialization stability
  with Blizzard's JSON utility before treating serialization churn as a bug.
- A runtime LibGetFrame different from bundled minor 79 may change scan behavior.

Measure before optimizing: idle CPU, populated raid/nameplate CPU, per-host build
time, queue depth, edit latency, retained containers, and post-reload memory recovery.
The maintainer's historical FPS comments are not measurements on this machine.

## 6. Repository/tooling gaps — source confirmed

No CI/tests, rank-generation script, reproducible release package definition, or
client-build compatibility manifest were present in the cloned tree. The changelog
is broad and does not encode regression scenarios. This research directory adds
initial executable probes and API inventories, but not an engine simulator or CI.

The web-rendered GitHub README was stale versus the Git checkout (it still described
loss-of-control support and future frame-addon support). Prefer `git` commit-pinned
source for technical claims. Do not cite cached README text as current behavior.

## Sensible sequence

1. Turn the export/count probes into desired-behavior regression tests and contribute
   one small fix at a time.
2. Capture installed build and test the priority-stack secret-state path.
3. Add bounded diagnostics and lifecycle/queue measurements.
4. Prototype an engine-managed duration bar or native label with a compatibility gate.
5. Expand test matrices and CI once the harness models the relevant contracts.

These are contribution candidates, not filed issues, completed fixes, or external
promises. Keep new features small enough that their restriction assumptions can be
verified directly.
