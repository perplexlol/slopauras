# Wowless evaluation for SlopAuras

Research date: **2026-10-13, America/Los_Angeles**.
Wowless snapshot: **f25a8db40c4dd6d6193ade67f2097b8184d77f36**.
SlopAuras snapshot: `41369a9738d100135256e962f60c377ac53518dd`.
Cloned into `C:/Users/user/Documents/github_clones/wowless`.

## Verdict

**Relevant and worth keeping as a testing reference and possible integration layer.**
It is not currently a turnkey Forever/SlopAuras emulator or a reliable verdict on
secret-value compliance. Prioritize the existing small SlopAuras behavioral tests,
then a bounded Wowless integration experiment, while retaining real-client verification.

The project is an unusually good match for the long-term testing objective: it loads
real addon Lua/FrameXML, simulates much of the UI environment, models older taint
behavior with its own Lua VM, generates tests, and has a test addon usable in a client.
Its architecture teaches us how to turn API observations into repeatable fixtures.
Its gaps matter most in exactly the native aura/security machinery SlopAuras uses.

Evidence is **static source review and a reproducible text inventory**, not a compiled
or executed Wowless run. Its own guide says to execute through its built elune runtime,
not system Lua/LuaJIT. We followed that distinction; the earlier Lupa probes execute
SlopAuras only and do not establish Wowless behavior.

## Architecture

| Layer | What it does | Relevance |
|---|---|---|
| `elune/` | Vendored Lua 5.1 VM with taint tracking and secure-call extensions | More realistic addon execution context than ordinary Lua; distinct from Midnight secret values |
| `data/products/<product>/` | YAML API/event/UI-object/build data | Explicit versioned contracts and searchable coverage |
| `tools/docs.lua` | Reads extracted Blizzard docs and rewrites product data, with correction layers | Useful precedent for API-drift tracking; current rewrite does not retain secret/precondition enforcement metadata |
| `tools/prep.lua` | Generates product runtime data and C-backed API/method stubs | Declarations can exist without behavior; output defaults matter |
| `wowless/modules.lua`, `data/modules.yaml` | Topologically sorted dependency-injected modules | Modular environment; scenario state can be supplied through a custom harness |
| `loader.lua`, `toc.lua`, `xmleval.lua` | Addon dependency/load-order resolution, secure/global environments, TOC and XML processing | Exercises real addon loading and bundled libraries |
| `events.lua`, `mainloop.lua`, `time.lua` | Event delivery, virtual time, visible-frame updates, timer queue | Good basis for deterministic asynchronous tests, subject to current timing limits |
| UI object registry, geometry/visibility modules | Creates frames, regions, parent relationships, points and script dispatch | Useful for configuration/editor and structural layout tests |
| `runner.lua`, `wowless.lua` | CLI/programmatic runner, login sequence, predefined UI sweeps | Smoke tests and controlled custom runner integration |
| `addon/Wowless`, `tools/gentest.lua`, `spec/` | Generated and hand-authored API/object tests, async tests, state-machine tests | A model for a shared emulator/client behavioral corpus |
| `render.lua`, SDL renderer | Frame/region snapshots and limited texture rendering | Structural diagnostics and rough images; not WoW-quality visual regression |

Lua modules are embedded into C-backed binaries during the CMake build. Runtime
APIs generally come from generated product-specific stubs rather than the installed
game. CASC/Tactless extraction and database definitions provide Blizzard UI files and
data; merely copying a mirror checkout into the runner cannot supply missing native
objects or a missing product schema.

## Loader and runner behavior

The loader resolves product-specific TOCs, required/optional dependencies, load-on-demand
addons, bindings and secure-environment files. Untrusted addons load into the public
environment; signed Blizzard modules can use the separate secure environment.
SavedVariables load before `ADDON_LOADED` and are written under
`out/<product>/SavedVariables/<addon>.lua` after the logout sequence.

`--addondir` can be repeated. Its parent folder is scanned to discover addon siblings;
use a dedicated test installation folder rather than assuming only one requested
directory participates. An isolated config is needed because runner actions can
mutate saved data and persist it to `out/`.

The CLI supports product, log level, addon directories, max errors, predefined scripts,
output, lite mode, profiling and frame0 diagnostics. `--scripts` is a comma-separated
selection of **predefined actions**, not a path to arbitrary scenario Lua. Unknown
action names are silently ignored. Custom precise scenarios fit a programmatic
`runner.run` wrapper or a companion test addon better than the default CLI sweep.

Default actions click visible buttons, send combat events, advance frames, run mouse
enter/leave, loot, macro text, bindings, slash commands, emotes, and nullary events.
These are broad exploratory smoke actions, not player-specific acceptance tests.
The fixed login sequence is not proof of all actual client event orderings.

## Concrete SlopAuras blockers

| Requirement | Observed Wowless support | Consequence |
|---|---|---|
| Forever build/product | Nine product tags; no Forever/camelot product | Product data, TOC family resolution and extracted source do not match Forever |
| Native `AuraContainer`, `AuraButton` | Neither type is in retail `uiobjects.yaml`; source search found no implementation | SlopAuras construction and Blizzard aura templates have fundamental missing support |
| `C_Secrets.ShouldAurasBeSecret` | Signature only, no `impl`, boolean output | Generated default is false; secret-state rebuild path is not exercised faithfully |
| `issecretvalue` | Signature only, boolean output | Generated default is false; real secrets cannot be validated by this predicate |
| `secretwrap` | Identity function in `data/impl/secretwrap.lua` | Does not produce native secret primitives |
| Object access/secret aspects | `AddAccessRestrictions`, `AddForbiddenAspects`, `AddSecretAspect` are unimplemented generated stubs | Post-initialization aura-button restrictions are not enforced by these methods |
| XML forbidden aspects | Evaluator explicitly leaves `forbiddenaspects` as a no-op | Parsing a restriction tag does not enforce its behavior |
| `SetAlphaFromBoolean`, native cooldown-duration/formatter methods | Selected methods have signatures but no behavior implementation | Range/timer UI tests can appear to run without applying the intended visuals |
| JSON serialization/deserialization | Both declared without an `impl` link in this product | Generated empty-string/nil defaults cannot test Share's real round-trip behavior |
| Known spells and aura provider switch | Relevant calls are signature stubs | Class/spell load decisions and test-provider restoration need explicit scenario modeling |
| Unit population | `units.GetUnit` returns only a fixed player record | No built-in populated party/raid/nameplate world for our host scenarios |

These are snapshot-specific findings. Adding the missing types is more work than
renaming a product: methods, object semantics, XML integration, candidate processing,
provider updates, layout and restrictions all need faithful implementation.

Why boolean stubs matter: `tools/prep.lua`'s `coutdefaults.boolean` returns false,
and `emit_stub_outputs` uses it when no explicit output stub/default/implementation
exists. Likewise the generic string default is empty and nilable outputs default
to nil. This is source-confirmed generation behavior, not an observed execution.

`tools/docs.lua`'s API rewrite preserves selected signature, environment and manual
protected flags, but does not copy `SecretReturns`, `SecretWhen*`, `SecretArguments`
or `Requires*` into an executable secrecy/precondition model. The schema likewise
does not currently express those contracts. Do not equate a fresh API dump with
fresh restriction fidelity.

The generated inventory [wowless-audit.json](wowless-audit.json) records selected
SlopAuras direct C-API calls plus explicitly named critical APIs, missing native types,
product list and method status. Its scanner is intentionally limited: it is neither
a full YAML interpreter nor complete call-graph/library coverage. `impl-linked`
means only that a behavior implementation is selected, not that it is faithful.

## Automation traps to handle before adoption

1. **A zero CLI exit code is not a clean-test verdict.** `errors.lua` increments/logs
   errors and exits with code zero when the max-error threshold is reached. The normal
   CLI also does not assert the returned error count. In contrast, `spec/wowless/addon_spec.lua`
   explicitly asserts test completion, an empty failure table, and zero errors.
   Our wrapper must enforce those assertions and its own expected scenario completion.
2. **Timer behavior differs from our expectations.** `time.lua` defaults
   `C_Timer.NewTicker` to one iteration if omitted; native indefinite polling should
   not be assumed. Expiration is tested with `< stamp`, and callbacks reschedule from
   the current stamp rather than backfilling every missed interval. SlopAuras relies
   on a repeating 0.25-second ticker, so this is a material coverage gap.
3. **Combat events are not an engine-state transition.** The runner's combat action
   sends REGEN events, while `InCombatLockdown` remains a generated false stub and
   aura-secrecy queries stay false. SlopAuras' local combat flag may change, but its
   native restrictions and secret rebuild behavior do not follow automatically.
4. **Persistence can contaminate runs.** Use fresh per-case SavedVariables and output
   directories; assert intended post-state. Keep real player exports separate.
5. **No world simulator is supplied.** Fixtures must identify exactly which unit,
   aura, known-spell, frame discovery and restriction behavior they provide.

These are engineering constraints for the harness, not claims that Wowless is useless
or that every emitted addon error is a real addon defect.

## Visual testing limits

Frame snapshots record geometry and region content. The SDL tool reads those snapshots,
fetches textures, sorts draw layers/strata, and renders texture geometry to PNG.
Its current `render(region)` handles textures, skips highlight layers, and does not
draw the captured FontString content. It does not establish the game's text metrics,
animation, clipping, cooldown effects or secret-aware layout fidelity.

Useful assertions could inspect parent/anchor structure, draw order, configuration
controls and visibility in modeled scenarios. Real WoW screenshots are still needed
for SlopAuras timer fonts, borders, glows, clipping, compact-frame integration and
combat-only restrictions. Avoid approving UI changes based solely on emulator pictures.

## Test design worth adopting

`addon/Wowless/statemachine.lua` constructs a state graph, checks reachability to/from
the initial state, and exercises every declared transition with state assertions.
That is a strong fit for SlopAuras lifecycle cases: real/preview provider, combat/no
combat, secret/non-secret, pending apply/restoration, missing/present host frames,
retained/retired rows. It tests declared transitions rather than every possible
arbitrary-length history, so add explicit sequence regressions when bugs depend on
multiple edits or delayed callbacks.

The test addon organizes nested named checks and async `done` patterns. Generated
API/object checks and client-facing tests give a path to differential validation:
observe the same selected behavior in the client and emulator, then upgrade a model
only with evidence. Save client build and emulator commit alongside results.

## Windows build feasibility

The root README still says Docker-only development, but `CLAUDE.md` describes native
builds, CMake has Windows configuration, and CI contains Windows Visual Studio/Ninja
build-and-test jobs. Native Windows is therefore a supported build path in source/CI,
not something ruled out by the old README.

This machine currently has no `docker`, `cmake`, `ninja`, or C/C++ compiler on PATH.
`wsl.exe` exists, but reports WSL is not installed. The Git clone has 17 uninitialized
submodules. No dependency build or test execution was attempted; installing a complete
toolchain is unnecessary to establish the source coverage gaps.

Native setup would require a compiler, CMake >=3.24, an appropriate generator, initialized
submodules and vcpkg dependencies. CI uses C++17; libraries include SQLite, Expat,
libyaml, CURL/OpenSSL, CASC and SDL. Test data builds may require CASC network fetching.
Pin dependency/submodule commits and product build hashes before measuring reproducibility.

Once a build environment exists, the source-guided route is:

```text
git submodule update --init --depth 1
cmake --preset default
cmake --build --preset default --target test
```

For client-source evaluation, build both the product-specific binary and its product
data target; the project's Bash `bin/run.sh wow` does this. On native Windows use
the equivalent CMake targets and generated executable location. The addon path is
`.../slopauras/SlopAuras`, not the repository root. These are future instructions,
not commands run during this evaluation.

## Recommended integration sequence

1. **Now:** keep our small SlopAuras probes and use Wowless' contract/state-machine
   architecture as a reference. Add desired-behavior tests for identified defects.
2. **Bounded proof of concept:** build upstream unchanged and run its own tests;
   establish a wrapper that fails on errors/incomplete scenarios. Test a tiny companion
   addon with deterministic timers/events, then isolated SlopAuras sharing logic with
   explicit JSON adapters. Label all adapters.
3. **Partial addon integration:** model only the non-secret container/editor behavior
   necessary for a specified scenario; separately record which APIs remain simulated.
   Do not claim restriction compliance from that adapter layer.
4. **Potential upstream contribution:** consider a Forever product, JSON implementation,
   ticker improvements, native aura-object support, and restricted-object contracts.
   Start with small independently verified improvements rather than a private sprawling
   emulator fork.
5. **Final gate:** real-client scenario and visual evidence, particularly for secrecy,
   taint, aura identity eligibility and frame-addon interaction.

The long-term loop should distinguish **pure tests**, **modeled integration tests**,
and **client-verified tests**. Wowless can materially strengthen the middle layer as
coverage improves; it does not remove the need for the third layer.

## Evidence links and refresh

- [Pinned project tree](https://github.com/wowless/wowless/tree/f25a8db40c4dd6d6193ade67f2097b8184d77f36).
- `data/products.yaml`, `data/products/wow/build.yaml`: product/version coverage.
- `tools/prep.lua`: generated defaults and stub emission.
- `data/products/wow/apis.yaml`, `uiobjects.yaml`: implementation links and missing types.
- `data/impl/secretwrap.lua`: identity wrapper.
- `wowless/modules/security.c`, `elune/README.md`: taint execution model.
- `tools/docs.lua`, `data/schemas/function.yaml`: retained contract fields.
- `wowless/modules/time.lua`, `errors.lua`, `runner.lua`: scheduling/error semantics.
- `.github/workflows/test.yml`, `CMakeLists.txt`: native Windows build evidence.
- `addon/Wowless/statemachine.lua`, `spec/wowless/addon_spec.lua`: useful test patterns.

Refresh by pinning a new Wowless commit, rerunning the static audit to a new output
filename, checking these files' diffs, then running its actual built runtime when
available. New declarations alone do not establish implemented support.
