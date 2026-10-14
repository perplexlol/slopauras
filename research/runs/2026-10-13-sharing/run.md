# First live iteration: sharing reliability

Date: 2026-10-13, America/Los_Angeles.
Base addon commit: `41369a9738d100135256e962f60c377ac53518dd`.
Local branch: `fix/share-roundtrip-validation`; changes are uncommitted.
Client-verified GetBuildInfo: 1.60.1, build 70338, Oct 9 2026, interface 16001.

## Live baseline

- Native WoW window was captured and controlled through the computer-use skill.
- `/slop` opened the editor successfully; there were no groups initially.
- Created one group (default name `New group`) and one default `HELPFUL` player display.
- Closing the editor showed a row of real player buff icons and countdowns.
- After deploying the patch, the user performed `/reload` and confirmed completion.
- The player-buff row still appeared after reload; no popup Lua error was observed.
  Absence of a popup is not proof of zero internal errors.

## Change and local tests

`Share.lua` now preserves empty class, unitPower and target lists; a legacy empty
class string exports as an empty list. It validates max/wrap/lineCap/lineMax/layer
as bounded integers, while continuous pixel/duration settings keep accepting fractions.

The desired empty-override assertion failed against original source, then passed
after the fix. Fourteen recorded checks pass, covering config/group/display exports,
inheritance into a different group, integer limits, continuous settings, empty ID
sets, unknown keys, rank expansion and legacy newline migration. All 36 Lua files
compile in Lua 5.1. See `research/regression-results.json` for execution evidence.

## Deployment

Original installed addon backup:
`C:/Users/user/Documents/github_clones/.slopauras-backups/before-share-validation-20261013-155951/SlopAuras`.
Changed `Share.lua` and `AGENTS.md` were copied to the installed addon and SHA256
verified against the repository. The base addon version remains 0.5.0 with local
unreleased fixes; no GitHub contribution has been published.

## Client-verified sharing checks

The initial diagnostic opened WoW's custom-script permission dialog. The user
accepted it manually and told the agent to continue. The agent did not operate
the permission dialog. Subsequent local slash commands executed successfully.

Checks used the existing AceConfig option callbacks, through
`LibStub("AceConfigRegistry-3.0"):GetOptionsTable("SlopAuras", "dialog", "SlopAurasQA-1.0")`.
These exercise the same import/export handlers as the editor, although they do
not verify text-box interaction or layout.

- Importing the invalid fractional-count fixture printed
  `Not imported. group.displays[1].max: should be a whole number`.
- Imported `QA sharing (disabled)` with `neverLoad=true`, an empty target list,
  group class PRIEST and power MANA, and explicit empty display class/power lists.
- Exported the full config through `shareExportBox.get()` and parsed its JSON
  with the actual client `C_EncodingUtil.DeserializeJSON`.
- Assertions verified all three exported empty lists remained present and empty.
  Actual client serialization emitted `[]` for these lists.
- Reimporting that export through `shareImportBox1.set` reached the choice stage:
  `Empty overrides PASS Found 2 total groups:` appeared in chat. The pending
  full-config preview was canceled without applying a replacement or addition.
- Temporary diagnostic globals were cleared; chat printed `Sharing QA complete`.

The original `New group` player-buff row continued rendering. The disabled QA
group remains available for repeatable testing and selects no units. These checks
were out of combat; combat, PvP secrecy, full-config apply choices and display-only
native roundtrips remain unverified. Input fixtures are in `research/fixtures/`.

## User-run combat smoke test, approximately 16:13–16:14 PDT

The user explicitly requires manual gameplay: the agent must not automate movement,
targeting or fighting. Combat observation used only window enumeration and screenshots;
no activation, clicks, keyboard input or slash commands were sent during this check.

After the user reported being in combat, screenshots showed an active enemy, damage
numbers and changing target health. The default player HELPFUL row remained visible,
with five icons in the observed states. Short-duration timer text changed between
captures (including a countdown near 9 then 3 seconds, followed by a refreshed timer).
The row remained visible in a later capture after the fight/loot. No Lua error popup
was visible. This is a visual smoke pass for this configuration, not proof of no
internal errors or universal secret-state compatibility. ShouldAurasBeSecret was
not queried, and editor mutations, priority stacks and PvP were not exercised.
