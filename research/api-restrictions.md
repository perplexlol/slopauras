# API restrictions and available extension paths

Baseline: pinned Forever mirror **1.60.1.70338**. These are source observations;
the player's installed build has not been inspected. `SlopAuras/AGENTS.md` explicitly
asks us to check with the player before relying on a consequential mirror detail.
Before implementing a feature that depends on one, confirm it through the player's
client `/api search`, build information, extracted UI source, and an actual scenario.

## Policy and technical enforcement

Blizzard's stated direction preserves UI presentation while restricting addons'
ability to process live combat data into decisions. The technical boundary is
per value, API, object, and context; it is not a blanket ban on custom displays.
Supported native widgets/delegates can consume information addon Lua cannot inspect.
[Blizzard's explanation](https://news.blizzard.com/en-us/article/24246290/combat-philosophy-and-addon-disarmament-in-midnight).

Keep these concepts separate:

| Mechanism | Practical consequence |
|---|---|
| Secret value | A value may be passed to a documented consumer; ordinary comparisons, arithmetic, indexing, branching, or stringification can fail. Checking secrecy does not reveal its content. |
| API precondition | Access can error or return no values, even before a secret result exists. Read `Requires*` and their failure modes. |
| Secret object aspect | Text, geometry, alpha, shown state, bar value, etc. can be restricted separately. |
| Forbidden object/access restriction | A post-initialization aura button or descendant can become inaccessible to addon code. |
| Secure/protected actions and taint | Protected UI actions retain their own rules. Secret-aware display support does not grant permission to cast spells or mutate protected frames. |

`SecretReturns`, `SecretWhen*`, `SecretArguments`, `HasRestrictions`, `MayReturnNothing`,
and `Requires*` all matter. A function lacking `SecretReturns` can still have conditional
secrecy or a precondition. Never copy unrestricted secure Blizzard implementation
logic into addon Lua and expect the same privileges.

## Secrecy is not combat lockdown

Forever's generated predicates describe aura/cooldown restriction contexts including
combat, encounters, challenge mode, and PvP matches, with spell-specific exceptions.
Not all these game modes necessarily exist in Forever. The maintenance guide reports
PvP secrecy throughout a battleground, including between fights; validate this on the
actual build. `C_Secrets.ShouldAurasBeSecret()` is the relevant broad runtime query.

`ADDON_RESTRICTION_STATE_CHANGED` is documented as occurring before activation or
after deactivation. SlopAuras uses that pre-activation opportunity to hold range glows,
then checks again a frame later. `PLAYER_REGEN_ENABLED` alone is not permission to
restyle aura buttons. A reload while already fighting is another distinct case.

Evidence: [secret predicates](https://github.com/Gethe/wow-ui-source/blob/943764493e6b16d63ded3ab304150d1f05e58b57/Interface/AddOns/Blizzard_APIDocumentationGenerated/SecretPredicatesDocumentation.lua),
[restriction lifecycle](https://github.com/Gethe/wow-ui-source/blob/943764493e6b16d63ded3ab304150d1f05e58b57/Interface/AddOns/Blizzard_APIDocumentationGenerated/RestrictedActionsDocumentation.lua).

## Aura matching matrix

The trusted container evaluates filters. Exact identity filtering is generally
eligible for friendly helpful auras and non-assistable harmful auras, plus never-secret
exceptions. Helpful player/group/pet auras have an explicit eligibility override for
edge cases such as mind control. The gate is not merely the player's faction.

| Aura context | Explicit include IDs | Explicit exclude IDs |
|---|---|---|
| Eligible helpful/friendly or harmful/non-assistable aura | Evaluated by Blizzard | Evaluated first by Blizzard |
| Ineligible aura, such as most friendly debuffs or enemy buffs | Aura rejected | Exclusion ignored |
| Spell marked NeverSecret | Identity gate permits matching | Identity gate permits matching |

Those rules apply in the container evaluator itself, not only in combat. An empty
display may be an intentional restriction result. A missing icon built on an
ineligible include filter could consequently appear permanently missing: never
interpret it as proof of actual absence.

Broader aura flags and allowed candidate filters can still express useful displays:
crowd control, dispellable types, player-origin filters, important/defensive groups,
and engine-defined sorting. SlopAuras exposes IDs/ranks, dispel types, max total
duration, and filter strings. Duration filtering excludes permanent auras and does
not mean "remaining time below X". Filter strings need a helpful/harmful type even
when token validation accepts an otherwise meaningful string.

Evidence: [candidate evaluator](https://github.com/Gethe/wow-ui-source/blob/943764493e6b16d63ded3ab304150d1f05e58b57/Interface/AddOns/Blizzard_AuraContainer/Blizzard_AuraContainerUtil.lua),
[candidate validation](https://github.com/Gethe/wow-ui-source/blob/943764493e6b16d63ded3ab304150d1f05e58b57/Interface/AddOns/Blizzard_AuraContainer/Blizzard_CustomAuraContainer.lua).

## Initialization, layout, and display consumers

`AddAuraGroup` creates ten frames up front. Its frame provider calls `initializeFrame`,
then applies `DenyTaintedAccessWhenAurasAreSecret`, then refreshes the display. Aura
slots use one frame but the same access restriction. Registration belongs inside the
callback when constructing during secrecy. Container geometry carries aura counts;
addon scripts must not infer counts by reading dimensions or observing size callbacks.

SlopAuras opts frames anchored to container geometry into
`DisableUntrustedLayoutScriptsTemplate`. It registers icon, duration cooldown, stack
count, dispel textures, and aura-shown animations with Blizzard. Regions get specific
secret aspects; parent/animation mutation permissions are also restricted. Native
formatter configuration can describe duration text without addon code inspecting time.

Evidence: [frame provider](https://github.com/Gethe/wow-ui-source/blob/943764493e6b16d63ded3ab304150d1f05e58b57/Interface/AddOns/Blizzard_AuraContainer/Blizzard_AuraContainerFrameProviders.lua),
[button display interface](https://github.com/Gethe/wow-ui-source/blob/943764493e6b16d63ded3ab304150d1f05e58b57/Interface/AddOns/Blizzard_AuraContainer/Blizzard_CustomAuraButton.lua).

## Current non-aura conditions

In the snapshot, the APIs SlopAuras branches on for hostility, dead/offline/visible
state, resting/mounted state, and known spells do not carry secret-return tags.
`UnitPowerType` may return nothing; it describes the power type, not its amount.
`UnitInRange` carries `SecretReturns`; SlopAuras passes the result to
`SetAlphaFromBoolean`. `UnitIsUnit` has a comparison precondition and conditional
secrecy; `UnitGUID` has identity restrictions. Amount-of-health or resource thresholds
must be evaluated separately; these APIs are not interchangeable with type/death checks.

[Unit contracts](https://github.com/Gethe/wow-ui-source/blob/943764493e6b16d63ded3ab304150d1f05e58b57/Interface/AddOns/Blizzard_APIDocumentationGenerated/UnitDocumentation.lua),
[spellbook contracts](https://github.com/Gethe/wow-ui-source/blob/943764493e6b16d63ded3ab304150d1f05e58b57/Interface/AddOns/Blizzard_APIDocumentationGenerated/SpellBookDocumentation.lua).

## Feature candidates, not promises

| Idea | Documented route | Required validation |
|---|---|---|
| Aura duration bars | Register `SetDurationBar` in button initialization; native duration updates | Permanent/expired auras, geometry, styles, secrecy, sort behavior |
| Stack bars | `SetApplicationBar`, with configured min/max | Actual spell stack behavior, visibility, secrecy |
| Aura labels | `SetSpellName`; optional native caster name display | Readability/localization and text restrictions; never read the rendered text back |
| Duration text with color progression | `SetDurationText` and native duration binding/color options | Installed build availability, allowed curves, timer lifetime and rendering |
| Refresh-window visuals | `AddPandemicRegion` and enter/active/leave animation registration | Whether Forever spell mechanics provide carry-over data; no assumption that retail pandemic rules apply |
| Extra aura candidate checkboxes | Candidate booleans such as `isStealable`, `canApplyAura`, player/pet origin | Actual Forever classification and differences from existing filter tokens |
| Own loss-of-control display | `C_LossOfControl` has a player-specific path; other-unit data has conditional secrecy | Runtime contract and product scope; current addon removed this old mode |
| Personal cooldown view | `C_Spell.GetSpellCooldownDuration` -> native duration consumer; cooldown-viewer availability query | Viewer data availability in Forever, cooldown secrecy, charges/GCD; separate from aura architecture |
| Native aura sounds | `C_UnitAuras.AddAuraSound`, flagged `HasRestrictions` | Restriction rules, eligible spell IDs, registration/removal, trigger limits; function existence alone is insufficient |

The native duration/caster/pandemic features are in the pinned custom-button source.
Additional API contracts: [duration binding](https://github.com/Gethe/wow-ui-source/blob/943764493e6b16d63ded3ab304150d1f05e58b57/Interface/AddOns/Blizzard_APIDocumentationGenerated/DurationTextBindingSharedDocumentation.lua),
[loss of control](https://github.com/Gethe/wow-ui-source/blob/943764493e6b16d63ded3ab304150d1f05e58b57/Interface/AddOns/Blizzard_APIDocumentationGenerated/LossOfControlDocumentation.lua),
[spell cooldowns](https://github.com/Gethe/wow-ui-source/blob/943764493e6b16d63ded3ab304150d1f05e58b57/Interface/AddOns/Blizzard_APIDocumentationGenerated/SpellDocumentation.lua),
[cooldown viewer](https://github.com/Gethe/wow-ui-source/blob/943764493e6b16d63ded3ab304150d1f05e58b57/Interface/AddOns/Blizzard_APIDocumentationGenerated/CooldownViewerDocumentation.lua),
[aura sounds](https://github.com/Gethe/wow-ui-source/blob/943764493e6b16d63ded3ab304150d1f05e58b57/Interface/AddOns/Blizzard_APIDocumentationGenerated/UnitAuraDocumentation.lua).

Arbitrary aura/resource/cooldown boolean combinations, custom combat recommendations,
enemy buff identity classification, and Lua actions based on secret values do not
follow from any of these display APIs. Treat every proposal by its actual data flow.
Combat-log reconstruction is not a generic workaround: the snapshot exposes combat-log
restriction state, and SlopAuras has no CLEU-based trigger engine.

## Retail comparison warning

The downloaded retail branch is `12.1.0.69933`, not a confirmed match for the latest
live release. Six compared critical files all differ from Forever. One consequential
difference: that retail snapshot skips identity checks for ineligible auras without
Forever's explicit include-list rejection branch. Forever also includes newer custom
button animation/pandemic support. This establishes version drift, not that all retail
clients today behave differently. Prefer installed-client contracts and pinned sources
over search snippets or old migration guides.
