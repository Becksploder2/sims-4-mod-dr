"""XML Injector immediate eyewear actions and direct on-mark application; diagnostic candidate."""
from interactions.base.immediate_interaction import ImmediateSuperInteraction
from realistic_glasses import outfit_change, _profile

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
                profile["reading_part" if action == "read_reading" else "glasses_part"] = part
                profile["last_action"] = "Successfully remembered glasses"
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
                    profile["glasses_part"] = previous
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
