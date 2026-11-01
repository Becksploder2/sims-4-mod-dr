# Realistic Glasses — Inventory eyewear feature

## Requested player behavior
When a Sim chooses **Realistic Glasses → Regular Glasses → Take Off Glasses**:
1. Store the exact assigned CAS glasses (part ID and, where accessible, color swatch) on the Sim's eyewear record.
2. Remove the glasses CAS part from the active outfit and refresh the Sim's appearance.
3. Create a real inventory-compatible **Glasses Case** object in the Sim's personal inventory, linked to that Sim's saved eyewear record.
4. On **Put On Glasses**, read the inventory item's assigned pair, restore the actual CAS part, and remove/consume the inventory representation.
5. Prevent duplicate cases if the same pair is taken off repeatedly; allow separate regular and reading pairs.
6. Support base-game and custom-content glasses when possible.
7. Handle full inventories, missing/swapped CC, changed outfits and game reload gracefully.
8. No additional library dependency besides XML Injector, and no external profile writes.

## Technical constraint
CAS eyewear is not a live object and **cannot be moved directly into the inventory**. The mod needs separate tested object definition/tuning and a proxy inventory object. Avoid promising that an arbitrary CAS part is itself inventory-compatible.

## Implementation/testing milestones
- First verify actual visual removal and restoration using the existing CAS switcher in a disposable save.
- Source/build a structurally valid Sims 4 inventory item with separate object definition/tuning and a unique resource ID.
- Create inventory object through native game services; link to the saved pair via supported game-native state.
- Confirm persistence and save/reload behavior (current v2.1 profiles are memory-only).
- Verify no duplicated/lost eyewear and no incompatibility with ModGuard.

**Status: design only; inventory item and creation logic are not implemented in v2.1.**
