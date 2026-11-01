"""XML Injector immediate eyewear actions and direct on-mark application; diagnostic candidate."""
from interactions.base.immediate_interaction import ImmediateSuperInteraction
from realistic_glasses import outfit_change, necklace_part_change, verified_neck_part, _profile

class _EyewearAction(ImmediateSuperInteraction):
    ACTION = "read"
    def _run_interaction_gen(self, timeline):
        sim = self.target
        if not hasattr(sim, "sim_info"):
            return False
        profile = _profile(sim)
        profile["last_action"] = "Started " + self.ACTION
        try:
            sim = self.target
            if not hasattr(sim, "sim_info"):
                return False
            profile = _profile(sim)
            action = self.ACTION
            if action in ("read", "read_reading"):
                _, part = outfit_change(sim, "read")
                if part is None:
                    return False
                destination = "reading_part" if action == "read_reading" else "glasses_part"
                profile[destination] = part
                profile["active_pair"] = "reading" if action == "read_reading" else "regular"
                profile["selected_pair"] = profile["active_pair"]
                profile["last_action"] = "Assigned {} pair: {}".format(profile["active_pair"], hex(part))
                return True
            if action == "store":
                from inventory_bridge import store_glasses_case, rollback_case
                _, wearing = outfit_change(sim, "read")
                if wearing is None:
                    profile["last_action"] = "No glasses equipped to store"
                    return False
                okay, case, message = store_glasses_case(sim)
                if not okay:
                    profile["last_action"] = "Cannot store glasses: " + message
                    return False
                try:
                    changed, previous = outfit_change(sim, "off")
                    if not changed:
                        rollback_case(case)
                        profile["last_action"] = "Could not remove glasses; inventory case rolled back"
                        return False
                    profile["glasses_part"] = previous
                    profile["inventory_case"] = case
                    profile["last_action"] = "Glasses removed and case added to inventory"
                    return True
                except Exception as exc:
                    rollback_case(case)
                    profile["last_action"] = "Stored eyewear rollback: " + str(exc)
                    return False
            if action == "off":
                changed, previous = outfit_change(sim, "off")
                if previous is not None:
                    if previous == profile.get("reading_part") and previous != profile.get("glasses_part"):
                        profile["active_pair"] = "reading"
                    elif previous == profile.get("glasses_part"):
                        profile["active_pair"] = "regular"
                    elif profile.get("glasses_part") is None:
                        # First-use convenience, without overwriting already assigned glasses.
                        profile["glasses_part"] = previous
                        profile["active_pair"] = "regular"
                _, visible_part = outfit_change(sim, "read")
                profile["last_action"] = ("Removed glasses; outfit readback=" + ("none" if visible_part is None else hex(visible_part))) if changed else "No glasses found in active outfit"
                return bool(changed)
            if action in ("on", "on_reading"):
                chosen = (profile.get("reading_part") if action == "on_reading"
                          else profile.get("glasses_part"))
                if action == "on_reading" and profile.get("use_regular_for_reading"):
                    chosen = profile.get("glasses_part")
                if chosen is None:
                    profile["last_action"] = "No glasses assigned. Wear glasses in CAS and select Remember Glasses first."
                    return False
                changed, _ = outfit_change(sim, "on", chosen)
                _, visible_part = outfit_change(sim, "read")
                if visible_part == chosen:
                    profile["active_pair"] = "reading" if action == "on_reading" else "regular"
                    profile["selected_pair"] = profile["active_pair"]
                if visible_part == chosen and action == "on":
                    case = profile.pop("inventory_case", None)
                    if case is not None:
                        try:
                            case.destroy()
                        except Exception as exc:
                            profile["last_action"] = "Glasses restored; inventory case removal failed: " + str(exc)
                            return True
                profile["last_action"] = "Put on glasses: {} (outfit readback={})".format("updated" if changed else "unchanged", hex(visible_part) if visible_part else "none")
                return bool(changed)
            if action in ("capture_alt_1", "capture_alt_2"):
                _, part = outfit_change(sim, "read")
                if part is None:
                    profile["last_action"] = "Equip alternate glasses in CAS before assigning them"
                    return False
                pair = "alternate_1" if action == "capture_alt_1" else "alternate_2"
                profile[pair + "_part"] = part
                profile["selected_pair"] = pair
                profile["active_pair"] = pair
                profile["last_action"] = "Saved {}: {}".format(pair, hex(part))
                return True
            if action in ("wear_alt_1", "wear_alt_2", "cycle_pairs"):
                pairs = (("regular", "glasses_part"), ("reading", "reading_part"),
                         ("alternate_1", "alternate_1_part"), ("alternate_2", "alternate_2_part"))
                if action == "cycle_pairs":
                    available = [(name, profile.get(key)) for name, key in pairs if profile.get(key) is not None]
                    if not available:
                        profile["last_action"] = "No pairs assigned"
                        return False
                    _, current = outfit_change(sim, "read")
                    pos = next((i for i, (_, part) in enumerate(available) if part == current), -1)
                    pair, chosen = available[(pos + 1) % len(available)]
                else:
                    pair = "alternate_1" if action == "wear_alt_1" else "alternate_2"
                    chosen = profile.get(pair + "_part")
                if chosen is None:
                    profile["last_action"] = "No {} pair assigned".format(pair)
                    return False
                outfit_change(sim, "on", chosen)
                _, current = outfit_change(sim, "read")
                if current != chosen:
                    profile["last_action"] = "Could not switch to {} pair".format(pair)
                    return False
                profile["selected_pair"] = pair
                profile["active_pair"] = pair
                profile["last_action"] = "Now wearing {}: {}".format(pair, hex(chosen))
                return True
            if action in ("neck_capture", "chain_regular", "chain_reading"):
                _, part = necklace_part_change(sim, "read")
                if part is None:
                    profile["last_action"] = "Choose a plain necklace without a pendant in CAS before assigning its chain style"
                    return False
                # Captures a style reference, NOT a replacement glasses necklace.
                kind = "reading" if action == "chain_reading" else "regular"
                profile[kind + "_chain_style"] = part
                profile["last_action"] = "Assigned {} chain style {}. A matching hanging-glasses CAS mesh must be installed before Hang can work.".format(kind, hex(part))
                return True
            if action in ("neck_hang", "neck_both", "neck_hang_reading", "neck_hang_regular"):
                kind = "reading" if action == "neck_hang_reading" else "regular"
                if action in ("neck_hang", "neck_both"):
                    kind = "reading" if profile.get("active_pair") == "reading" else "regular"
                face_part = profile.get("reading_part") if kind == "reading" else profile.get("glasses_part")
                _, on_face = outfit_change(sim, "read")
                if face_part is None and on_face is not None and kind == "regular":
                    face_part = on_face
                    profile["glasses_part"] = on_face
                chain_style = profile.get(kind + "_chain_style")
                matched_hanging_part = verified_neck_part(face_part, chain_style)
                # Absolutely no change when a true matching pair is unavailable.
                if matched_hanging_part is None:
                    profile["last_action"] = "No matching hanging version installed for {} glasses and selected chain. Nothing changed; unrelated glasses necklaces will NOT appear.".format(kind)
                    return False
                _, current_neck = necklace_part_change(sim, "read")
                if current_neck not in (None, chain_style, matched_hanging_part):
                    profile["last_action"] = "Current necklace conflicts with hanging glasses; no accessories changed"
                    return False
                if profile.get("neck_active"):
                    profile["last_action"] = "A hanging pair is already active; restore it before switching"
                    return False
                profile["neck_previous_part"] = current_neck
                profile["neck_face_part"] = on_face
                profile["neck_pair_kind"] = kind
                profile["neck_hanging_part"] = matched_hanging_part
                necklace_part_change(sim, "on", matched_hanging_part)
                try:
                    if action != "neck_both" and on_face == face_part:
                        outfit_change(sim, "off")
                except Exception:
                    if current_neck is None:
                        necklace_part_change(sim, "off")
                    else:
                        necklace_part_change(sim, "on", current_neck)
                    profile["neck_pair_kind"] = None
                    profile["neck_hanging_part"] = None
                    raise
                profile["neck_active"] = True
                profile["last_action"] = "{} glasses hanging from selected chain{}".format(kind, " with face glasses unchanged" if action == "neck_both" else "")
                return True
            if action in ("neck_wear", "neck_remove"):
                if not profile.get("neck_active"):
                    profile["last_action"] = "No neck-hanging glasses currently active"
                    return False
                _, now_neck = necklace_part_change(sim, "read")
                if now_neck != profile.get("neck_hanging_part"):
                    profile["last_action"] = "Hanging accessory changed externally; refusing to remove unrelated jewelry"
                    return False
                previous_neck = profile.get("neck_previous_part")
                saved_face = profile.get("neck_face_part")
                if action == "neck_wear" and saved_face is not None:
                    outfit_change(sim, "on", saved_face)
                if previous_neck is None:
                    necklace_part_change(sim, "off")
                else:
                    necklace_part_change(sim, "on", previous_neck)
                profile["neck_active"] = False
                profile["neck_previous_part"] = None
                profile["neck_face_part"] = None
                profile["neck_pair_kind"] = None
                profile["neck_hanging_part"] = None
                profile["last_action"] = "Matched hanging accessory removed and previous necklace restored"
                return True
            if action == "reading_shared_toggle":
                profile["use_regular_for_reading"] = not profile.get("use_regular_for_reading", False)
                profile["last_action"] = "Use regular pair for reading: " + ("ON" if profile["use_regular_for_reading"] else "OFF")
                return True
            if action in ("mark_sports", "mark_cheer"):
                category, index = sim.sim_info.get_current_outfit()
                key = "sports_outfits" if action == "mark_sports" else "cheer_outfits"
                identifier = "{}:{}".format(int(category), int(index))
                profile[key] = sorted(set(profile.get(key, [])) | {identifier})
                # Marking a sports/cheer uniform should apply remembered regular glasses now.
                chosen = profile.get("glasses_part")
                if chosen is None:
                    _, already_worn = outfit_change(sim, "read")
                    if already_worn is not None:
                        profile["glasses_part"] = already_worn
                        chosen = already_worn
                if chosen is None:
                    profile["last_action"] = "{} marked {}, but no regular glasses assigned. Wear glasses in CAS, select Remember Glasses, then mark again.".format(key, identifier)
                    return True
                changed, _ = outfit_change(sim, "on", chosen)
                _, active_part = outfit_change(sim, "read")
                profile["last_action"] = "{} marked {}; visual glasses {} (readback={})".format(
                    key, identifier, "applied" if changed else "already equipped",
                    hex(active_part) if active_part else "none")
                return True
        except Exception as exc:
            profile["last_action"] = "{} failed: {}: {}".format(self.ACTION, type(exc).__name__, str(exc))
            return False
        return False

class VisionEyewearRemember(_EyewearAction): ACTION = "read"
class VisionEyewearRemove(_EyewearAction): ACTION = "off"
class VisionEyewearPutOn(_EyewearAction): ACTION = "on"
class VisionEyewearRememberReading(_EyewearAction): ACTION = "read_reading"
class VisionEyewearPutOnReading(_EyewearAction): ACTION = "on_reading"
class VisionEyewearMarkSports(_EyewearAction): ACTION = "mark_sports"
class VisionEyewearMarkCheer(_EyewearAction): ACTION = "mark_cheer"

class VisionEyewearStoreInInventory(_EyewearAction): ACTION = "store"

class VisionEyewearUseRegularForReading(_EyewearAction): ACTION = "reading_shared_toggle"

class VisionEyewearAssignNeck(_EyewearAction): ACTION = "neck_capture"
class VisionEyewearHangNeck(_EyewearAction): ACTION = "neck_hang"
class VisionEyewearPutOnFromNeck(_EyewearAction): ACTION = "neck_wear"
class VisionEyewearFaceAndNeck(_EyewearAction): ACTION = "neck_both"
class VisionEyewearRemoveNeck(_EyewearAction): ACTION = "neck_remove"

class VisionEyewearAssignRegularChain(_EyewearAction): ACTION = "chain_regular"
class VisionEyewearAssignReadingChain(_EyewearAction): ACTION = "chain_reading"
class VisionEyewearHangReading(_EyewearAction): ACTION = "neck_hang_reading"
class VisionEyewearHangRegular(_EyewearAction): ACTION = "neck_hang_regular"

class VisionEyewearCaptureAlternate1(_EyewearAction): ACTION = "capture_alt_1"
class VisionEyewearCaptureAlternate2(_EyewearAction): ACTION = "capture_alt_2"
class VisionEyewearWearAlternate1(_EyewearAction): ACTION = "wear_alt_1"
class VisionEyewearWearAlternate2(_EyewearAction): ACTION = "wear_alt_2"
class VisionEyewearCyclePairs(_EyewearAction): ACTION = "cycle_pairs"
