"""Realistic Glasses menu actions (requires Sims4CommunityLibrary installed).
Only available on Sims; changes only currently equipped glasses.
"""
from sims4communitylib.classes.interactions.common_immediate_super_interaction import CommonImmediateSuperInteraction
from sims4communitylib.classes.testing.common_test_result import CommonTestResult
from sims4communitylib.classes.testing.common_execution_result import CommonExecutionResult
from realistic_glasses import outfit_change, _profile

class VisionEyewearRemember(CommonImmediateSuperInteraction):
    @classmethod
    def on_test(cls, interaction_sim, interaction_target, interaction_context, **kwargs):
        return CommonTestResult.TRUE

    def on_started(self, interaction_sim, interaction_target):
        try:
            _, part = outfit_change(interaction_sim, "read")
            if part is None:
                return CommonExecutionResult.FALSE
            _profile(interaction_sim)["glasses_part"] = part
            return CommonExecutionResult.TRUE
        except Exception:
            return CommonExecutionResult.FALSE

class VisionEyewearRemove(CommonImmediateSuperInteraction):
    @classmethod
    def on_test(cls, interaction_sim, interaction_target, interaction_context, **kwargs):
        return CommonTestResult.TRUE

    def on_started(self, interaction_sim, interaction_target):
        try:
            changed, previous = outfit_change(interaction_sim, "off")
            if previous is not None:
                _profile(interaction_sim)["glasses_part"] = previous
            return CommonExecutionResult.TRUE if changed else CommonExecutionResult.FALSE
        except Exception:
            return CommonExecutionResult.FALSE

class VisionEyewearPutOn(CommonImmediateSuperInteraction):
    @classmethod
    def on_test(cls, interaction_sim, interaction_target, interaction_context, **kwargs):
        return CommonTestResult.TRUE

    def on_started(self, interaction_sim, interaction_target):
        try:
            remembered = _profile(interaction_sim).get("glasses_part")
            if remembered is None:
                return CommonExecutionResult.FALSE
            changed, _ = outfit_change(interaction_sim, "on", remembered)
            return CommonExecutionResult.TRUE if changed else CommonExecutionResult.FALSE
        except Exception:
            return CommonExecutionResult.FALSE
