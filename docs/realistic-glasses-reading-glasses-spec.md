# Realistic Glasses — Reading Glasses Behavior Specification

## Selected defaults
- **Reading glasses mode:** Automatic
- **Enabled activity triggers:** Reading books, homework and studying, computer use, detailed crafting, and phone/tablet use.
- Applies per Sim only when a reading-glasses pair has been assigned and the player has enabled its use. Unassigned Sims are not automatically fitted with arbitrary CAS glasses.

## Assigning eyewear
- **Set Regular Glasses:** Capture currently worn glasses as the regular pair.
- **Set Reading Glasses:** Capture currently worn glasses as a separate reading pair.
- **Use Regular Glasses for Reading:** Optional setting when one prescription pair serves both purposes.
- Allow any compatible glasses CAS part, including CC.
- Preserve glasses identifiers and any available variant information; never modify unrelated CAS parts.

## Automatic activity behavior
- When an enabled near-work activity begins, switch to the designated reading pair, or retain regular glasses if **Use Regular Glasses for Reading** is selected.
- When near work ends, restore whatever eyewear state was active beforehand, subject to the current outfit and wearing rules.
- Multiple simultaneous activities use an activity counter/state tracker: do not repeatedly remove/reapply glasses or restore them until all relevant activities end.
- Reading: book and reading interactions.
- Homework: homework, studying and applicable school assignments.
- Computer: computer-use interactions.
- Crafting: close-up crafting and detail-oriented hobby interactions, mapped to verified in-game affordances.
- Phone: phone and tablet interactions, where start/stop events can be detected reliably.
- Observe activities through game-native interaction start/finish hooks, not periodic external screen scans. Exact affordance mappings require in-game verification.
- Automatic switching must not repeatedly interrupt Sim actions.

## Precedence / conflicts
1. Explicit player action (Put On Regular / Put On Reading / Take Off) until the manual override is cleared.
2. Reading activity while automatic mode is on and a reading pair is assigned.
3. Designated cheerleading outfit rule for regular prescription glasses.
4. Other configured regular-glasses schedule rules.
5. Default no glasses, unless configured otherwise.

If a Sim wears regular glasses only for cheerleading and begins homework in that outfit, the temporary reading pair takes precedence; when homework ends, the cheerleading regular pair returns. Outside a cheer outfit, the reading pair comes off when the activity ends.

## Pie menu (proposed)
- Vision & Eyewear → Put On Regular Glasses
- Vision & Eyewear → Put On Reading Glasses
- Vision & Eyewear → Take Off Glasses
- Vision & Eyewear → Assign Current Glasses as Regular
- Vision & Eyewear → Assign Current Glasses as Reading
- Vision & Eyewear → Reading Glasses: Automatic / Manual
- Vision & Eyewear → Use Regular Glasses for Reading (toggle)
- Vision & Eyewear → Automatic Activities (five individual toggles)
- Vision & Eyewear → Mark/Unmark Current Outfit as Cheerleading

## Persistence and compatibility
- Avoid arbitrary filesystem writes, executable calls, network operations or ModGuard bypasses.
- Long-term per-Sim and per-outfit persistence requires a supported game-native save mechanism, not the discarded external JSON mechanism.
- The integration target is XML Injector for pie-menu injection, with game-native script actions and **no Sims4CommunityLibrary dependency**.
- No package should be declared game-ready solely because DBPF/XML validates: actual menu injection, CAS mutation and activity callbacks must pass in-game tests.

## Implementation status
**Design specification only.** The activity detectors, reading-glasses switching, pie-menu settings and reliable persistence are not yet implemented or verified in a playable build.
