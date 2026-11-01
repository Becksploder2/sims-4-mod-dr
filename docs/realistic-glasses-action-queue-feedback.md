# Realistic Glasses — Action Queue feedback

## Required player experience
When choosing **Realistic Glasses → Regular Glasses → Take Off Glasses**, show an actual action in the Sims 4 action queue:
- **Take Off Glasses** text, with the appropriate interaction icon (or fallback).
- Brief action duration and, where available, a natural glasses-removal gesture animation.
- Perform the visible CAS glasses removal at the action's execution point, not when opening the menu.
- After a successful CAS appearance refresh, give a short confirmation notification (optional).
- If removal fails, cancel/fail gracefully and show an explicit failure notification. Never imply success if the glasses are still visible.
- Show matching **Put On Glasses** interaction in the queue; use the same approach for reading glasses.
- If adding a real Glasses Case to personal inventory is enabled, show the case only when a valid definition exists and inventory insertion succeeds.
- Preserve ModGuard compatibility; no arbitrary filesystem writes or third-party S4CL dependency.

## Engineering implications
Current v2.3 actions extend ImmediateSuperInteraction. Immediate interactions may execute without a meaningful queued affordance or animation. A properly tuned queued SuperInteraction and tested basic-content animation sequence are required for a genuine queue cue.
The XML Injector interaction registrations are known to display in-game. Do not remove them until replacement has been tested.
Do not fake queue feedback with a successful status message; switching must be visibly verified.

## Status
**Specification only; not implemented in the v2.3 binary.**
