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

## New mandatory compatibility rules: plain chains and no unwanted accessory spawn

**A — Use compatible existing necklaces as chain styles.**
- The user can assign a necklace that has no pendant/object already hanging from its center as the **source chain style** for regular or reading glasses.
- Classification as "plain" must be through a reviewed compatibility manifest or a creator opt-in. A CAS necklace-slot ID alone cannot tell the script whether its mesh has a pendant, nor guarantee the chain connects to the temples or is long enough.
- In the asset-creation pipeline, clone/rebuild the necklace mesh with a compatible hanging version of the selected frames; create proper attachment points and rigging. A chain-only necklace is not itself a valid glasses-around-neck appearance unless a matching glasses mesh is included.
- If the user has another non-glasses necklace equipped in the same slot, warn about the conflict; don't silently replace it. Keep an original necklace to restore after removing the hanging glasses.
- Allow distinct regular-pair and reading-pair chain assignments, but use only currently installed verified combinations.

**B — Never spawn or automatically substitute an unrelated glasses-and-chain accessory.**
- Selecting Hang Glasses must **NOT** equip the stock EA/CC necklace containing a different frame merely because that necklace was previously captured.
- Require an exact registered match of `face_glasses_part_id + chain_style_id + desired_hanging_part_id` (and supported swatch) before doing *any* face/off or necklace/on operation.
- If there is no match, leave the current face glasses and necklace **unchanged** and display: "No matching hanging version for this frame and chain is installed."
- Make necklace generation a separate offline CAS mesh authoring step, **not a Live Mode auto-spawn**. Do not duplicate accessory instances, and do not show two visible glasses-and-chain assemblies when a pair is already hanging.
- When putting glasses on again, remove only the mod's tracked hanging part; restore the original necklace if appropriate. Never strip unrelated jewelry.
- Test repeated Hang/Put On actions, outfit changes, two-pair swaps and missing CC. Ensure no duplicate eyewear, no chain popping into view unrelated to the selected frame, and no inventory case appearing unless independently enabled.

**Current status:** specifications approved for implementation; these protections must be applied to the next code/build before claiming support for arbitrary plain necklaces or correct hanging-frame visuals.

## Frame-shape-aware regular/reading chain selection

- Treat regular and reading glasses as **independent** exact CAS-part assignments, including frame swatch. A Sim may have square readers and a completely different shape for regular glasses.
- Resolve the matching hanging part by exact face-glasses CAS part ID, chosen chain style, and compatible swatch. Record optional human-readable frame-shape metadata (square, round, rectangle, oval, cat-eye, etc.) for UI and asset generation **only**.
- Do not infer 3D frame geometry from a part ID's number or shape label. Shape alone cannot produce a rigged necklace accessory; validated authored hanging variants are required.
- If a user changes frames from round to square, invalidate the prior hanging-pair mapping until a matching square-frame asset is installed. Never reuse the former shape or auto-equip stock glasses from an unrelated necklace.
- For mixed arrangements, resolve **face-worn regular part** separately from **hanging reading part**, and vice versa. Do not overwrite either saved pair when toggling.
- Frame shape should drive the offline mesh-authoring pipeline (frame width, rim contours, bridge, temples, scale and pose), not live-game arbitrary deformation.
- Acceptance: Karli-Rae can wear regular frames on her face and matching **square** readers on a plain chosen chain at her neck, with no unrelated pair appearing. If matching square asset missing, show a clear unavailable message without changing CAS.
