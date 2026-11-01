# Realistic Glasses v3.4 — Pie Menu Redesign (staging)

**Not a downloadable game release.** v3.3 is the last compiled/test candidate. This folder is source-only until the custom menu category **binary SimData** is generated and tested. Do not put the generated XML in the user's Mods folder.

## In-game navigation goal

**Realistic Glasses**
- **My Glasses Collection:** capture/choose pairs, assign or intentionally replace Regular, Reading, Alternate 1/2.
- **Wear or Remove Glasses:** put on regular/reading/alternate, cycle, take off.
- **Glasses Chains:** remember chain, assign to a pair, manual put on/remove, behavior Follow / Keep / Manual, universal-chain controls and hanging-frame actions.
  - **Chain Fit:** four independent fit controls.
- **Sports and Cheerleading:** mark sport or cheer outfit.
- **Vision and Preferences:** regular-as-readers toggle, inventory experiment.

Keep the existing `VisionEyewear...` classes and interaction tuning IDs unchanged to avoid breaking functionality; only change labels and `category` references.

## Build steps

1. Run `python tools/eyewear_v3_4_menu_staging/generate_categories.py`. This checks every v3.3 interaction is assigned exactly once to a category and generates seven category XML resources, seven SimData **XML authoring specs**, and `menu_mapping.json`.
2. With Tdesc Builder / Sims 4 Studio, create seven matching `PieMenuCategory` tunings with associated **binary SimData** and the instance IDs, parent references, and strings from the mapping. Ensure the root uses no parent, subcategories use the root, and Chain Fit uses the Chains parent.
3. Export **real game-compatible binary SimData resources**. Never substitute the textual `.simdata.xml` files as a raw SimData resource; they are documentation/input specs, not runtime binaries. Ensure XML and SimData agree on all category fields.
4. Update the package build generator to add the new PIE_MENU_CATEGORY resources, SimData resources and localization strings, and assign interaction categories using `menu_mapping.json`. Remove the repeated `Vision & Eyewear -` and `Glasses Collection -` prefixes from interaction display labels.
5. Add checks: all 51 original interactions remain present; all 7 categories have XML+binary SimData; all 51 actions have non-zero valid category references, correct parents and distinct IDs. Keep XML Injector as sole dependency.
6. On an **isolated backup save**, confirm clicking Karli-Rae shows one Realistic Glasses root, submenu navigation works, and Take Off Glasses / Put On Reading Glasses / four-slot assignment / chain behavior still function. Do not ship to playtest as complete until menu category resources are validated in the game.

Why not ship XML-only? A custom Sims 4 pie menu category requires correct SimData paired with the tuning, and missing/mismatched SimData can silently break menus. See: https://thesims4moddersreference.org/tutorials/creating-a-pie-menu/

## Known unfinished features unchanged

Chain-fitting variants, true hanging eyeglass meshes, permanent collection persistence, and inventory glasses case objects are still unimplemented. This redesign is menu organization, not an implicit fix for those features.
