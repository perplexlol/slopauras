# Priority-stack test preparation

Client: Forever Beta 1.60.1.70338 / interface 16001; local sharing patch installed.
Prepared 2026-10-13 around 16:17 PDT. A subsequent Chain.lua fix is installed;
reload and client retesting remain pending while the user is AFK.

## Fixture and offline check

`research/fixtures/priority-stack.txt` defines a player group anchored to the screen
160 UI units right of center, with 48-unit icons, RIGHT growth, firstLine=true,
and max=1. Two lines contain: all ranks of Power Word: Shield (rankSpellIDs 17),
then a HELPFUL fallback. The second line may match the shield too; first-slot
priority should put the specifically selected shield on top.

The actual import/Prepare/StackDisplays functions selected two ordered slots in
the offline harness. Centered growth and max=2 controls instead selected the regular
container path. Fifteen regression observations now pass; this added check does
not simulate frame access restrictions or rendering.

## Client baseline

The user confirmed out of combat before setup. Imported through the real editor's
Import a group text box and Accept button. `QA priority stack` appeared in the group
list. After closing the editor, one larger fallback icon with a long timer appeared
to the right of the original small buff row. No gameplay movement, targeting or
ability use was automated. No error popup was visible.

## Next manual tests

1. User casts Power Word: Shield on self; observe shield taking priority.
2. User enters combat; observe priority continuing while shield is active and
   fallback returning after shield is removed. Agent takes screenshots only.
3. Separately test rebuilding the stack during secrecy by changing its icon size
   in the editor during combat. Coordinate this explicitly with the user; do not
   interrupt gameplay with automated UI inputs while they are fighting.
4. Compare the same change outside combat. Query restriction state only through a
   deliberately coordinated diagnostic, not by assuming combat proves every API state.

Source risk under investigation: AddSlot sets the slot anchor after AddAuraSlot
returns; LevelSlots also adjusts protected slot frame levels afterwards. The pinned
Forever frame provider applies aura-secret restrictions after initializeFrame.
These later calls are wrapped in pcall and may fail silently. The current baseline
does not establish that failure on the live client.

## Priority observation, approximately 16:18–16:19 PDT

After the user reported ready, three screenshots were captured without any game
input. The larger icon showed the shield graphic and a short countdown (15 then
1) while an enemy was alive and damage numbers/target health showed active combat.
The third screenshot showed the enemy dead and the larger icon back to its prior
long-duration fallback graphic (53m). The small buff row also persisted. No Lua
error popup appeared.

Conclusion: the stack built outside combat displayed shield priority during the
fight and returned to fallback afterwards. The exact shield-to-fallback transition
was not captured while the player was still in combat. This does not validate a
stack built/rebuilt during secrecy, or prove no internal errors. The next targeted
test remains changing the group's shared icon size during a user-run fight.

## Combat resize failure and repair, approximately 16:20–16:23 PDT

The user reported changing the shared icon size during combat. Two captures showed
an active fight with the ordinary buff row still updating, but the larger priority
icon absent from its prior location. A later capture after an enemy died also showed
it absent. There was no error popup. The reported setting change and disappearance
are client-observed; the exact saved value and restriction flag were not queried.

Added `research/stack-restriction.lua`, which exercises actual NewStack/Resize code
with a deliberately narrow frame-access contract: slot buttons become inaccessible
after initializeFrame. Decorative styling and frame creation are substituted. The
new assertion failed before the fix with `Secret stack accessed a slot after initialization`.

Chain.AddSlot now sets the anchor and final priority frame level inside initializeFrame,
before creating styled children. NewStack no longer calls LevelSlots after creation.
Outside-secrecy resizing still updates existing frame levels; growing and shrinking
checks preserve slot order and disable spare slots. Sixteen observations pass, and
all 36 addon Lua files compile in Lua 5.1. Native repair verification is pending.

Installed Chain.lua SHA256:
`9460D8F92A387D8F4BDE24CC953BED263FCD81C22A214E73C341F137B483EB91`.
Previous installed Chain.lua and AGENTS.md were backed up to
`C:/Users/user/Documents/github_clones/.slopauras-backups/before-stack-initialization-20261013`.
Source and installed hashes matched after deployment. User chose to go AFK before
reload. No further game input should be sent until they return.

Resume: user runs /reload outside combat; confirm the larger icon returns. Then user
repeats a combat shared-size change (64 to 48 or another value), and the agent observes
whether the icon remains anchored, changes size and preserves shield priority.
