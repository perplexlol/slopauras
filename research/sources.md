# Source registry and freshness

Checked 2026-10-12 (America/Los_Angeles). Source content, local code, executed probes,
and inference are deliberately kept distinct.

## Primary references used

| Reference | Why it matters | Limits |
|---|---|---|
| [SlopAuras source](https://github.com/its-riece/slopauras/tree/41369a9) | Actual addon behavior and maintenance intent | Local Git checkout is newer than the web-rendered README encountered |
| [SlopAuras maintenance guide](https://github.com/its-riece/slopauras/blob/41369a9/SlopAuras/AGENTS.md) | Invariants, editor labels, feature-change checklist | Maintainer claims need source/client confirmation for consequential assumptions |
| [Blizzard addon-disarmament explanation](https://news.blizzard.com/en-us/article/24246290/combat-philosophy-and-addon-disarmament-in-midnight) | Policy direction: presentation versus combat computation | Historical explanation, not a current per-build contract |
| [Forever UI source snapshot](https://github.com/Gethe/wow-ui-source/tree/943764493e6b16d63ded3ab304150d1f05e58b57) | Actual Blizzard UI implementation and generated contracts for 1.60.1.70338 | Community-maintained mirror of primary source; native engine implementation is absent |
| [Retail UI source snapshot](https://github.com/Gethe/wow-ui-source/tree/09b9db7948abc9b9648dedaab51eb0cf3ee67b31) | Concrete comparison with 12.1.0.69933 | Branch tip is not proof of current installed or newest retail release |
| [Forever official deep dive](https://news.blizzard.com/en-us/article/24303313/world-of-warcraft-forever-deep-dive-panel-recap) | First-party game context | The retrieved text did not describe addon restrictions; do not cite it for API parity |
| [Talent data provider](https://talentsforever.com/) | Rank-data provenance stated by the addon | Regeneration data endpoint/tooling not recovered or verified |
| [WeakAuras project](https://github.com/WeakAuras/WeakAuras2) | Upstream project, rather than an unofficial fork | Retrieved README did not establish current Midnight support status; do not overstate it |

Search also surfaced September 2026 reports of Forever carrying Midnight restrictions
and older WeakAuras developer statements. Those are discovery leads, not the technical
authority for this notebook. The exact Blizzard UI Discord statement was not directly
retrieved. We accept the player's Forever context and corroborate concrete mechanisms
with the Forever UI snapshot rather than claiming every retail API matches.

Direct `worldofwarcraft.blizzard.com` article fetches returned 403; the equivalent
`news.blizzard.com` primary pages were readable. Some search results mixed unrelated
Classic/retail/Forever content. Cached web content was not treated as a repository HEAD.

## Local source locations

- `../wow-ui-source-forever/version.txt`: `1.60.1.70338`.
- `../wow-ui-source-retail/version.txt`: `12.1.0.69933`.
- Under each `Interface/AddOns/Blizzard_AuraContainer/`: trusted container/button
  implementation, inbound interfaces, frame providers, flow layout and templates.
- `Blizzard_APIDocumentationGenerated/`: generated API names, parameters, restrictions,
  secret tags, predicates, and event timing.
- `Blizzard_FrameXMLUtil/AuraUtil.lua`: filter tokens, comparators, colors/classification.
- `Blizzard_NamePlates/Blizzard_NamePlateAuras.lua`: built-in filter/layout use.
- `Blizzard_CooldownViewer/`: native cooldown presentation and alerts.

## Refresh procedure

Follow-up 2026-10-13: [Wowless](https://github.com/wowless/wowless/tree/f25a8db40c4dd6d6193ade67f2097b8184d77f36)
was cloned and evaluated as a possible headless integration harness. See
[wowless.md](wowless.md) for architecture, coverage gaps, source locations and the
distinction between source analysis and actual execution.

1. Record current addon/UI commits and manifests before updating anything.
2. Confirm the installed client's build; select matching source if obtainable.
3. Fetch reference branches only when refreshing evidence is useful. Read their
   `version.txt`, commit date, and diffs rather than assuming branch names guarantee parity.
4. Regenerate inventories to a **new** filename so the old comparison survives.
5. Re-check relevant preconditions, secret tags, widget access restrictions, and
   behavior in-client. Keep native enforcement unknown where source is insufficient.
6. Update conclusions and mark which old claims are superseded. Do not silently rewrite
   a historical client-verified result into a universal claim.

First follow-up should obtain the player's installed build, current export, class/spec,
frame addons, and the first concrete display/feature they want improved.
