"""XML Injector immediate eyewear actions; no Sims4CommunityLibrary dependency."""
from interactions.base.immediate_interaction import ImmediateSuperInteraction
from realistic_glasses import outfit_change, _profile

class _EyewearAction(ImmediateSuperInteraction):
    ACTION = "read"
    def _run_interaction_gen(self, timeline):
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
                return True
            if action == "off":
                changed, previous = outfit_change(sim, "off")
                if previous is not None:
                    profile["glasses_part"] = previous
                return bool(changed)
            if action in ("on", "on_reading"):
                chosen = (profile.get("reading_part") if action == "on_reading"
                          else profile.get("glasses_part"))
                if action == "on_reading" and profile.get("use_regular_for_reading"):
                    chosen = profile.get("glasses_part")
                if chosen is None:
                    return False
                changed, _ = outfit_change(sim, "on", chosen)
                return bool(changed)
            if action in ("mark_sports", "mark_cheer"):
                category, index = sim.sim_info.get_current_outfit()
                key = "sports_outfits" if action == "mark_sports" else "cheer_outfits"
                identifier = "{}:{}".format(int(category), int(index))
                profile[key] = sorted(set(profile.get(key, [])) | {identifier})
                return True
        except Exception:
            return False
        return False

class VisionEyewearRemember(_EyewearAction): ACTION = "read"
class VisionEyewearRemove(_EyewearAction): ACTION = "off"
class VisionEyewearPutOn(_EyewearAction): ACTION = "on"
class VisionEyewearRememberReading(_EyewearAction): ACTION = "read_reading"
class VisionEyewearPutOnReading(_EyewearAction): ACTION = "on_reading"
class VisionEyewearMarkSports(_EyewearAction): ACTION = "mark_sports"
class VisionEyewearMarkCheer(_EyewearAction): ACTION = "mark_cheer"
