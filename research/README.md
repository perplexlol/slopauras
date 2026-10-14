# SlopAuras research notebook

Last researched: **2026-10-13, America/Los_Angeles**. Source and offline findings are
separated from the specific client checks below. The objective is to grow a restriction-aware addon,
then turn real observations into repeatable tests and small contributions.

Follow-up **2026-10-13**: [Wowless evaluation](wowless.md), with a reproducible
[static coverage audit](wowless-audit.json). Wowless is a promising integration
harness with significant current Forever/aura/secrecy gaps; no Wowless runtime was
built or executed on this machine.

Computer use was verified on 2026-10-13: native window enumeration, activation and
stable screenshot capture now work. See [diagnostic evidence](computer-use-diagnostics.md).
GetBuildInfo confirms Forever Beta 1.60.1.70338, interface 16001. The first live
iteration verified player-buff rendering and the patched sharing callbacks.
The user-run combat smoke check also observed buff timers updating during a fight.
Gameplay remains manual: do not automate character movement, targeting or combat.
See the [priority-stack test preparation](runs/2026-10-13-sharing/priority-stack.md)
for the next targeted reproduction.

## Start here next time

1. Read `SlopAuras/AGENTS.md`, then [architecture.md](architecture.md).
2. Read [api-restrictions.md](api-restrictions.md) before proposing combat-dependent features.
3. Check [findings.md](findings.md) for reproduced problems versus unverified risks.
4. Follow [testing-flywheel.md](testing-flywheel.md) to capture evidence and advance the loop.
5. Record new observations with the installed client build, addon commit, config, context,
   reproduction, evidence, and conclusion. A new patch can invalidate an old conclusion.

## Evidence anchors

| Component | Snapshot |
|---|---|
| SlopAuras | `41369a9` on `main`, version `0.5.0`, TOC interface `16001` |
| Forever UI mirror | `943764493e6b16d63ded3ab304150d1f05e58b57`, `1.60.1.70338`, commit dated 2026-10-10 UTC |
| Retail UI mirror | `09b9db7948abc9b9648dedaab51eb0cf3ee67b31`, `12.1.0.69933` |
| Wowless | `f25a8db40c4dd6d6193ade67f2097b8184d77f36`; static review only; see `wowless.md` |
| Local Lua probes | `lupa==2.6`, Lua 5.1, 36 Lua files compiled, four passing behavioral checks and four reproduced observations |
| Installed WoW Forever | GetBuildInfo confirms `1.60.1.70338`, interface `16001`; scoped checks in the live run record |

The mirror checkouts are siblings of this repo: `../wow-ui-source-forever` and
`../wow-ui-source-retail`. They are reference material, not addon dependencies.
The downloaded branches are the branch tips returned during this research; that does
not establish that they match today's newest released patch or this player's build.

Evidence vocabulary:

- **Source-confirmed:** observed in the pinned addon or Blizzard UI/API source.
- **Offline-reproduced:** executed against actual addon Lua with documented mocks.
- **Client-verified:** reproduced on the identified live client; player-buff rendering, fractional-count import rejection and empty-list native JSON sharing checks are recorded in the first live iteration.
- **Candidate:** plausible feature or risk requiring further investigation.

## Files and tools

- `probes.py`: compiles Lua and executes actual rank, migration, and sharing code under mocks.
- `probe-results.json`: recorded output; reproduced defects are baseline observations,
  not passing assertions of desired behavior.
- `regression-results.json`: current desired-behavior checks after the first sharing fixes.
- [First live iteration](runs/2026-10-13-sharing/run.md): deployment, observed UI behavior,
  test evidence and remaining client checks.
- `api_inventory.py`: extracts generated API header metadata and hashes relevant UI files.
- `forever-api-baseline.json` / `retail-api-baseline.json`: versioned contract snapshots.
- [sources.md](sources.md): primary references, provenance, and refresh instructions.

PowerShell commands for this Windows workspace:

```powershell
$researchPython = 'C:/Users/user/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $researchPython research/probes.py --dependency-path C:/Users/user/Documents/github_clones/.research-tools/python
& $researchPython research/api_inventory.py ../wow-ui-source-forever research/forever-api-baseline.json
& $researchPython research/api_inventory.py ../wow-ui-source-retail research/retail-api-baseline.json
```

The optional interpreter package was installed only into
`C:/Users/user/Documents/github_clones/.research-tools/python`, not global Python.
On another machine install `lupa==2.6` into a dedicated environment and omit
`--dependency-path` if that environment already supplies it. The API inventory needs
only Python's standard library and Git. Its header scanner is deliberately limited;
hash changes are an invitation to review the full contracts, not an automatic safety verdict.

The initial research baseline changed no gameplay source. The 2026-10-13 live iteration
adds tested sharing fixes and drives the client; see its run record above.
On 2026-10-14 the user authorized publishing our commits to the fork
`https://github.com/perplexlol/slopauras`, on `fix/share-roundtrip-validation`.
The current suite records 16 passing observations and compiles 36 addon Lua files.
The user confirmed the supplied reload/combat-resize retest passed on 2026-10-14;
this retest was user-reported, without an independent agent capture.
No upstream pull request or recurring job has been created.
