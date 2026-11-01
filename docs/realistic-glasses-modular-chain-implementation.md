# Realistic Glasses — Reusable Frame-and-Chain System

Status (2026-11-01): implementation plan; NOT in a tested .package or .ts4script.

## Goal
Any Sim can assign separately:
- regular on-face CAS glasses part
- reading on-face CAS glasses part
- optional style of glasses chain for each pair
- a matching hanging-accessory CAS part for each (face-frame + chain), validated and registered in a manifest.

Support face reading glasses while regular glasses hang around neck, vice versa, and a no-glasses state. Preserve selected swatches and existing necklaces as far as accessory slot conflicts permit. Never substitute the unrelated glasses already built into a generic necklace.

## What can be automated versus authored
The script can find, remember and switch CAS part IDs once registered; the script CANNOT dynamically separate an arbitrary 3D frame from a necklace, attach it to another chain, rig it, and emit new CAS resources during gameplay.
We need a **CC content-building pipeline** for matched frame-and-chain accessories. A chain-only mesh is useful as an independently authored input, but a hanging state still requires a visibly matching frame mesh to be placed at its end and exported with the chain as a valid necklace CAS mesh. When on face, use original face part and (if desired) separately authored on-face chain segments compatible with slot limitations.

## First deliverable: Karli-Rae prototype
1. Identify exact frame part in her existing CAS (export/reference its permitted EA geometry if applicable), chosen frame swatch, and chain style.
2. Use Sims 4 Studio CAS > Create 3D Mesh to create **new CC**, not override EA CAS part. Export source mesh + textures and a necklace mesh template as compatible .blend files.
3. In Blender, separate any existing frame geometry from the necklace's chain. Position a copy of Karli-Rae's circular frame below the neck at the chain ends, with correct scale/UV/material and skin weights to torso rig. Avoid clipped hair/clothes, unnatural stretching, and high polygon counts.
4. Export all required LOD meshes, create swatches and check texture resources; import through S4S. Produce a **valid CAS .package** with separate resource IDs. Do not release fake tuning/placeholder packages.
5. Inspect in CAS on female and male eligible frames/body shapes; verify compatibility with hair, high collars, movement and other accessories.
6. Add verified manifest entry mapping (face part ID, chain style ID, hanging necklace part ID, swatches). Never map arbitrary face frames automatically to an unrelated necklace.
7. Add UI: Realistic Glasses > Chains > Assign Chain for Regular / Assign Chain for Reading / Hang Regular / Hang Reading / Wear From Neck / Wear Both Pairs.
8. Use v2.7 proven reading switch and v2.5 proven removal. Preserve outgoing face pair and previous necklace. Perform face/off -> hanging/on or reverse with readback; on failure attempt rollback and report via eyewear.last.
9. Persist assignments using game-native reliable mechanisms before public release; current in-memory profile resets on restart. No external file writes, no banned third-party library.
10. Test disposable save, reload, outfits, EA + permitted CC, different Sims, glasses on face vs around neck. Only after successful tests describe as working.

## Scale to reusable system
- Asset manifest pairs the selected face frame with an available authored neck version and chain style.
- Unsupported frame: show 'No matching hanging version installed' rather than swapping to an unrelated pair.
- A desktop/offline 'asset builder' may assist with Blender mesh positioning and batch creation, but must NOT claim to create good game-compatible meshes solely from a screenshot; requires actual source mesh files and Sims 4 Studio/Blender QA.
- For CC source, obtain creator permission for editing and redistribution as required. EA content should be used as reference / permitted game-derived clone without distributing unauthorized extracted assets.
- One set of rigged assets per compatible frame/chain combination; chain-only component reused in the asset authoring process, not dynamically composed in Live Mode.
- Beware CAS slots: face glasses slot 11, necklace slot 12 in current script. Existing necklace will conflict when hanging pair uses slot 12; restore it after use. An on-face chain accessory may need another compatible accessory slot and collision testing.

## Dependencies
Sims 4 Studio and a compatible Blender workflow for CAS mesh authoring; XML Injector for Sims interaction menus. No Sims4CommunityLibrary. Keep ModGuard compatible.

## Acceptance criteria
In one live-game test, Karli-Rae's chosen round reading frames visibly move from face to a matching hanging mesh without changing shape/style, then return to face. Regular frame remains separately remembered. The same mechanism works for a second Sim with a different authored pair. No queue hang, missing-data errors, invisible necklace, or unrelated frames.
