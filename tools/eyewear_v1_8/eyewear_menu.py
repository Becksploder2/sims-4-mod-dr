"""Realistic Glasses v1.8 native Sims 4 immediate interactions.
XML Injector injects the tuning; no Sims4CommunityLibrary or disk I/O.
"""
from interactions.base.immediate_interaction import ImmediateSuperInteraction
from realistic_glasses import outfit_change, _profile

class _EyewearAction(ImmediateSuperInteraction):
    ACTION = "read"

    def _run_interaction_gen(self, timeline):
        super()._run_interaction_gen(timeline)
        try:
            # The clicked Sim is the target, not necessarily the actor.
            sim = self.target
            if not hasattr(sim, "sim_info"):
                return False
            profile = _profile(sim)
            if self.ACTION == "read":
                _, part = outfit_change(sim, "read")
                if part is None:
                    return False
                profile["glasses_part"] = part
                return True
            if self.ACTION == "off":
                changed, previous = outfit_change(sim, "off")
                if previous is not None:
                    profile["glasses_part"] = previous
                return bool(changed)
            if self.ACTION == "on":
                remembered = profile.get("glasses_part")
                if remembered is None:
                    return False
                changed, _ = outfit_change(sim, "on", remembered)
                return bool(changed)
        except Exception:
            return False
        return False

class VisionEyewearRemember(_EyewearAction):
    ACTION = "read"

class VisionEyewearRemove(_EyewearAction):
    ACTION = "off"

class VisionEyewearPutOn(_EyewearAction):
    ACTION = "on"
